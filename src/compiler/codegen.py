"""
Code Generator module translating AST instruction nodes to Minecraft command blocks.

Execution model (Option A – Impulse + Redstone):
──────────────────────────────────────────────────
- The program is divided into segments (basic blocks), split at labels and
  after every jump/branch instruction.
- Each segment starts with an Impulse command block (needs redstone to activate).
- Subsequent blocks in a segment are Chain command blocks (auto=true, propagate).
- JMP places a redstone block *above* the target segment's Impulse block to
  trigger it on the next game tick.
- Conditional branches (BEQ, BGT, …) set a _BRANCH_TAKEN flag and
  conditionally place redstone at the target.
- Fall-through between consecutive segments only fires if _BRANCH_TAKEN == 0.
- Each segment's Impulse block cleans up the redstone above itself on activation.
"""

from src.compiler.ast import (
    InstructionNode,
    RegisterOperand,
    ImmediateOperand,
    LabelOperand,
    StringOperand,
)
from src.compiler.symbols import SymbolTable
from src.compiler.target.architecture import Architecture
from src.compiler.target.layout import ID_to_coord
from src.compiler.config import SCOREBOARD_OBJ, DEFAULT_REG_SIZE

IMPULSE = "minecraft:command_block"
CHAIN = "minecraft:chain_command_block"


class CodeGenerator:
    """Emits Minecraft scoreboard and redstone commands into the Architecture."""

    def __init__(self, architecture: Architecture, reg_size: int = DEFAULT_REG_SIZE):
        self.architecture = architecture
        self.reg_size = reg_size
        self.cols = architecture.program_lenght

    # ─────────────────────────── Public entry ───────────────────────────

    def generate(self, instructions: list[InstructionNode], symbol_table: SymbolTable) -> int:
        """Full compilation: register init → activation → program segments."""

        # 1. Register initialisation chain
        reg_block_count = self._init_registers()

        if not instructions:
            return 0

        # 2. Determine segment boundaries (basic-block splitting)
        jump_target_ids: set[int] = set()
        for name in symbol_table.labels:
            jump_target_ids.add(symbol_table.get_label_id(name))

        # Handle terminal labels (e.g. "done:" with no instruction after it)
        max_id = instructions[-1].instruction_id
        for label_id in sorted(jump_target_ids):
            if label_id > max_id:
                instructions.append(InstructionNode(
                    opcode="NOP", operands=[], instruction_id=label_id, line_number=-1
                ))
                max_id = label_id

        # Split at labels AND after every branch / jump
        all_instr_ids = {n.instruction_id for n in instructions}
        segment_starts: set[int] = {0} | jump_target_ids
        for node in instructions:
            op = node.opcode.upper()
            if op in ("JMP", "BEQ", "BNE", "BGT", "BLT"):
                nxt = node.instruction_id + 1
                if nxt in all_instr_ids:
                    segment_starts.add(nxt)

        # 3. Build segments (ordered lists of InstructionNodes)
        segments = self._build_segments(instructions, segment_starts)
        if not segments:
            return 0

        # 4. Reserve 1 block for activation (register-init → first segment)
        activation_phys = reg_block_count
        program_start = reg_block_count + 1

        # 5. ──── First pass: compute physical layout ────
        seg_start_phys: dict[int, int] = {}   # seg_idx → physical ID of Impulse block
        instr_phys_map: dict[int, int] = {}   # instruction_id → physical ID
        instr_to_seg: dict[int, int] = {}     # first-instr-id → seg_idx

        current_phys = program_start
        for seg_idx, segment in enumerate(segments):
            seg_start_phys[seg_idx] = current_phys
            instr_to_seg[segment[0].instruction_id] = seg_idx
            current_phys += 2  # overhead: Impulse (cleanup) + Chain (reset flag)

            for node in segment:
                instr_phys_map[node.instruction_id] = current_phys
                current_phys += self._count_commands(node)

            # Fall-through if segment doesn't end with JMP and isn't last
            last_op = segment[-1].opcode.upper()
            if last_op != "JMP" and seg_idx + 1 < len(segments):
                current_phys += 1

        # 6. Emit activation block (register-init chain → first segment)
        self._emit_activation(activation_phys, seg_start_phys[0])

        # 7. ──── Second pass: emit program blocks ────
        for seg_idx, segment in enumerate(segments):
            block_id = seg_start_phys[seg_idx]

            # ── Overhead 1: Impulse – cleanup redstone above self ──
            self._emit_block(block_id, "/setblock ~0 ~1 ~0 minecraft:air",
                             block_type=IMPULSE, auto=False)
            block_id += 1

            # ── Overhead 2: Chain – reset _BRANCH_TAKEN ──
            self._emit_block(
                block_id,
                f"/scoreboard players set {SCOREBOARD_OBJ} _BRANCH_TAKEN 0",
                block_type=CHAIN, auto=True)
            block_id += 1

            # ── Instruction blocks ──
            for node in segment:
                commands = self._gen_instruction(
                    node, block_id, symbol_table, seg_start_phys, instr_to_seg
                )
                for cmd in commands:
                    self._emit_block(block_id, cmd, block_type=CHAIN, auto=True)
                    block_id += 1

            # ── Fall-through activation ──
            last_op = segment[-1].opcode.upper()
            if last_op != "JMP" and seg_idx + 1 < len(segments):
                next_seg_phys = seg_start_phys[seg_idx + 1]
                coords = self._relative_coords(block_id, next_seg_phys, y_offset=1)
                self._emit_block(
                    block_id,
                    f"/execute if score {SCOREBOARD_OBJ} _BRANCH_TAKEN matches 0 "
                    f"run setblock {coords} minecraft:redstone_block",
                    block_type=CHAIN, auto=True)
                block_id += 1

        return len(instructions)

    # ───────────────────────── Internal helpers ─────────────────────────

    def _build_segments(self, instructions, segment_starts):
        """Group instructions into segments, splitting at each segment_starts id."""
        segments: list[list[InstructionNode]] = []
        current: list[InstructionNode] = []
        for node in instructions:
            if node.instruction_id in segment_starts and current:
                segments.append(current)
                current = []
            current.append(node)
        if current:
            segments.append(current)
        return segments

    def _count_commands(self, node: InstructionNode) -> int:
        """How many physical command blocks a single instruction needs."""
        opcode = node.opcode.upper()
        ops = node.operands
        if opcode in ("LDR", "STR"):
            raise NotImplementedError(
                f"Compilation Error: '{opcode}' at line {node.line_number} "
                "requires RAM barrel memory, not yet implemented!"
            )
        if opcode == "NOP":
            return 0
        if opcode == "MOV":
            return 1
        if opcode == "MSG":
            return 1
        if opcode in ("ADD", "SUB", "MUL", "DIV", "MOD"):
            return 3 if isinstance(ops[2], ImmediateOperand) else 2
        if opcode == "JMP":
            return 1
        if opcode in ("BEQ", "BNE", "BGT", "BLT"):
            base = 2  # set _BRANCH_TAKEN + conditional setblock
            if isinstance(ops[1], ImmediateOperand):
                base += 1  # must set _TEMP first
            return base
        return 1

    # ─── Register init ─────────────────────────────────────────────────

    def _init_registers(self) -> int:
        """Emit Impulse(block 0) + Chain blocks for register init + internal objectives."""
        block_id = 0
        for i in range(self.reg_size):
            b_type = IMPULSE if block_id == 0 else CHAIN
            auto = block_id != 0
            self._emit_block(
                block_id,
                f"/scoreboard objectives add R{i} dummy",
                block_type=b_type, auto=auto)
            block_id += 1

            self._emit_block(
                block_id,
                f"/scoreboard players set {SCOREBOARD_OBJ} R{i} 0",
                block_type=CHAIN, auto=True)
            block_id += 1

        # _BRANCH_TAKEN (used for conditional jump logic)
        self._emit_block(
            block_id, "/scoreboard objectives add _BRANCH_TAKEN dummy",
            block_type=CHAIN, auto=True)
        block_id += 1
        self._emit_block(
            block_id,
            f"/scoreboard players set {SCOREBOARD_OBJ} _BRANCH_TAKEN 0",
            block_type=CHAIN, auto=True)
        block_id += 1

        # _TEMP (used for arithmetic with immediate values)
        self._emit_block(
            block_id, "/scoreboard objectives add _TEMP dummy",
            block_type=CHAIN, auto=True)
        block_id += 1

        return block_id

    # ─── Block emission ────────────────────────────────────────────────

    def _emit_block(self, physical_id: int, command: str,
                    block_type: str, auto: bool) -> None:
        """Place a single command block into the program matrix."""
        x, _, z, facing = ID_to_coord(physical_id, cols=self.cols)
        self.architecture.program.add_command(
            command, x, z,
            orientation=facing,
            block_type=block_type,
            auto_active=auto,
        )

    def _relative_coords(self, from_phys: int, to_phys: int,
                         y_offset: int = 0) -> str:
        """Compute ~X ~Y ~Z relative coordinates between two physical block IDs.

        Accounts for the matrix-storage ↔ world coordinate mapping:
            world_X = Positions[0] + z_from_ID_to_coord
            world_Z = Positions[2] + x_from_ID_to_coord
        """
        fx, fy, fz, _ = ID_to_coord(from_phys, cols=self.cols)
        tx, ty, tz, _ = ID_to_coord(to_phys, cols=self.cols)
        dx = tz - fz          # world X offset
        dy = (ty - fy) + y_offset
        dz = tx - fx          # world Z offset
        return f"~{dx} ~{dy} ~{dz}"

    def _emit_activation(self, from_phys: int, target_seg_phys: int) -> None:
        """Chain block that places redstone above the target segment's Impulse block."""
        coords = self._relative_coords(from_phys, target_seg_phys, y_offset=1)
        self._emit_block(
            from_phys,
            f"/setblock {coords} minecraft:redstone_block",
            block_type=CHAIN, auto=True)

    # ─── Per-instruction codegen ───────────────────────────────────────

    def _gen_instruction(self, node: InstructionNode, current_phys: int,
                         symbol_table: SymbolTable,
                         seg_start_phys: dict[int, int],
                         instr_to_seg: dict[int, int]) -> list[str]:
        """Translate one InstructionNode into a list of Minecraft commands."""
        opcode = node.opcode.upper()
        ops = node.operands

        if opcode in ("LDR", "STR"):
            raise NotImplementedError(
                f"Compilation Error: '{opcode}' at line {node.line_number} "
                "requires RAM barrel memory, not yet implemented!"
            )

        if opcode == "NOP":
            return []

        # ── MOV ────────────────────────────────────────────────────────
        if opcode == "MOV":
            dest = ops[0].name
            if isinstance(ops[1], ImmediateOperand):
                return [f"/scoreboard players set {SCOREBOARD_OBJ} {dest} {ops[1].value}"]
            elif isinstance(ops[1], RegisterOperand):
                return [
                    f"/scoreboard players operation {SCOREBOARD_OBJ} {dest} "
                    f"= {SCOREBOARD_OBJ} {ops[1].name}"
                ]

        # ── Arithmetic (ADD, SUB, MUL, DIV, MOD) ──────────────────────
        elif opcode in ("ADD", "SUB", "MUL", "DIV", "MOD"):
            dest = ops[0].name
            src = ops[1].name  # always a register
            sym = {"ADD": "+", "SUB": "-", "MUL": "*", "DIV": "/", "MOD": "%"}[opcode]

            cmds = [
                f"/scoreboard players operation {SCOREBOARD_OBJ} {dest} "
                f"= {SCOREBOARD_OBJ} {src}"
            ]
            if isinstance(ops[2], ImmediateOperand):
                cmds.append(
                    f"/scoreboard players set {SCOREBOARD_OBJ} _TEMP {ops[2].value}"
                )
                cmds.append(
                    f"/scoreboard players operation {SCOREBOARD_OBJ} {dest} "
                    f"{sym}= {SCOREBOARD_OBJ} _TEMP"
                )
            elif isinstance(ops[2], RegisterOperand):
                cmds.append(
                    f"/scoreboard players operation {SCOREBOARD_OBJ} {dest} "
                    f"{sym}= {SCOREBOARD_OBJ} {ops[2].name}"
                )
            return cmds

        # ── JMP ────────────────────────────────────────────────────────
        elif opcode == "JMP":
            label = ops[0].name if isinstance(ops[0], LabelOperand) else str(ops[0])
            target_id = symbol_table.get_label_id(label)
            target_seg = instr_to_seg[target_id]
            target_phys = seg_start_phys[target_seg]
            coords = self._relative_coords(current_phys, target_phys, y_offset=1)
            return [f"/setblock {coords} minecraft:redstone_block"]

        # ── Branches (BEQ, BNE, BGT, BLT) ─────────────────────────────
        elif opcode in ("BEQ", "BNE", "BGT", "BLT"):
            reg1 = ops[0].name
            label = ops[2].name if isinstance(ops[2], LabelOperand) else str(ops[2])

            target_id = symbol_table.get_label_id(label)
            target_seg = instr_to_seg[target_id]
            target_phys = seg_start_phys[target_seg]

            cmds: list[str] = []
            cmd_offset = 0

            # Handle immediate comparison operand
            if isinstance(ops[1], ImmediateOperand):
                cmds.append(
                    f"/scoreboard players set {SCOREBOARD_OBJ} _TEMP {ops[1].value}"
                )
                cmp_target = "_TEMP"
                cmd_offset += 1
            else:
                cmp_target = ops[1].name

            # Condition string
            cond_map = {
                "BEQ": f"if score {SCOREBOARD_OBJ} {reg1} = {SCOREBOARD_OBJ} {cmp_target}",
                "BNE": f"unless score {SCOREBOARD_OBJ} {reg1} = {SCOREBOARD_OBJ} {cmp_target}",
                "BGT": f"if score {SCOREBOARD_OBJ} {reg1} > {SCOREBOARD_OBJ} {cmp_target}",
                "BLT": f"if score {SCOREBOARD_OBJ} {reg1} < {SCOREBOARD_OBJ} {cmp_target}",
            }
            cond = cond_map[opcode]

            # Set _BRANCH_TAKEN flag
            cmds.append(
                f"/execute {cond} run scoreboard players set "
                f"{SCOREBOARD_OBJ} _BRANCH_TAKEN 1"
            )
            cmd_offset += 1

            # Place redstone at target (relative from THIS block's position)
            setblock_phys = current_phys + cmd_offset
            coords = self._relative_coords(setblock_phys, target_phys, y_offset=1)
            cmds.append(
                f"/execute {cond} run setblock {coords} minecraft:redstone_block"
            )
            return cmds

        # ── MSG ────────────────────────────────────────────────────────
        elif opcode == "MSG":
            msg_val = ops[0].value
            import re
            import json
            parts = re.split(r'(\bR\d+\b)', msg_val)
            json_components = [""]
            for idx, part in enumerate(parts):
                if idx % 2 == 0:
                    if part:
                        json_components.append({"text": part})
                else:
                    json_components.append({"score": {"name": SCOREBOARD_OBJ, "objective": part}})
            raw_json = json.dumps(json_components)
            return [f"/tellraw @a {raw_json}"]

        raise ValueError(
            f"Compilation Error: Unknown instruction '{opcode}' at line {node.line_number}"
        )
