"""
Minecraft target architecture models: BlockMatrix, CodeBlockMatrix, and Architecture.
"""

from typing import Any

class BlockMatrix:
    """Represents a 3D grid matrix of Minecraft blocks."""

    def __init__(self, positions: tuple[int, int, int]):
        self.Block: list[list[Any]] = [[]]
        self.Positions = positions

    def add_command(
        self,
        command: str,
        row: int,
        col: int,
        attributes: dict | None = None,
        orientation: str | None = None,
        block_type: str = "minecraft:command_block",
        auto_active: bool = False,
        conditional: bool = False,
    ) -> None:
        while len(self.Block) <= row:
            self.Block.append([])
        while len(self.Block[row]) <= col:
            self.Block[row].append(None)

        nbt = attributes.copy() if attributes else {}
        nbt["Command"] = command
        nbt["auto"] = "1b" if auto_active else "0b"

        cond_str = "conditional=true" if conditional else "conditional=false"
        facing_str = f"facing={orientation}" if orientation in ("north", "south", "east", "west") else ""

        props = [p for p in [facing_str, cond_str] if p]
        properties = f"[{','.join(props)}]" if props else ""

        self.Block[row][col] = (f"{block_type}{properties}", nbt)

    def get_command(self, row: int, col: int) -> str:
        if row < len(self.Block) and col < len(self.Block[row]) and self.Block[row][col]:
            return self.Block[row][col][1]["Command"]
        raise IndexError("Index out of range for CommandMatrix")

    def add_block(self, block: str, row: int, col: int, attributes: dict | None = None, orientation: str | None = None) -> None:
        while len(self.Block) <= row:
            self.Block.append([])
        while len(self.Block[row]) <= col:
            self.Block[row].append(None)

        nbt = attributes.copy() if attributes else {}
        properties = "[facing=west]" if orientation == "facing west" else "[facing=east]" if orientation == "facing east" else ""
        block_str = f"{block}{properties}"
        if orientation:
            nbt["Rotation"] = orientation
        self.Block[row][col] = (block_str, nbt)

    def get_block(self, row: int, col: int) -> Any:
        if row < len(self.Block) and col < len(self.Block[row]):
            return self.Block[row][col]
        raise IndexError("Index out of range for CommandMatrix")


class CodeBlockMatrix(BlockMatrix):
    """Specialized BlockMatrix for sequential code execution blocks."""

    def add_next_to_command(
        self,
        command: str,
        attributes: dict | None = None,
        block_type: str = "minecraft:command_block",
        auto_active: bool = False,
    ) -> None:
        row = len(self.Block) - 1
        col = 0
        while col < len(self.Block[row]) and self.Block[row][col] is not None:
            col += 1
        if col >= 9:
            row += 1
            col = 0
        self.add_command(command, row, col, attributes, block_type=block_type, auto_active=auto_active)


class Architecture:
    """Target hardware layout for Stack, Memory (Barrels), and Program block matrices."""

    def __init__(self, stack_size: int = 20, memory_size: int = 100, program_length: int = 16):
        self.stack_size = stack_size
        self.memory_size = memory_size
        self.program_lenght = program_length
        self.stack_lenght = 9
        self.memory_lenght = 9

        stack_rows = stack_size // 9 + (1 if stack_size % 9 != 0 else 0)
        memory_rows = memory_size // 9 + (1 if memory_size % 9 != 0 else 0)

        # 1. Stack physical barrels (minecraft:barrel)
        self.stack = BlockMatrix((0, 0, 0))
        for i in range(stack_rows):
            for j in range(9):
                if i * 9 + j < stack_size:
                    self.stack.add_block("minecraft:barrel", i, j)

        # 2. RAM Memory physical barrels (minecraft:barrel)
        self.memory = BlockMatrix((0, 0, stack_rows + 1))
        for i in range(memory_rows):
            for j in range(9):
                if i * 9 + j < memory_size:
                    self.memory.add_block("minecraft:barrel", i, j)

        # 3. Program code command blocks
        self.program = CodeBlockMatrix((10, 0, 0))
