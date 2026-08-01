"""
Abstract Syntax Tree (AST) node representations for assembly instructions and operands.
"""

from dataclasses import dataclass
from typing import Union, List

@dataclass
class RegisterOperand:
    name: str          # e.g., "R0", "R1"
    index: int         # e.g., 0, 1

@dataclass
class ImmediateOperand:
    value: int         # e.g., 10, 0

@dataclass
class LabelOperand:
    name: str          # e.g., "loop_sum", "end_sum"

@dataclass
class StringOperand:
    value: str         # e.g., "La somme est R0"

Operand = Union[RegisterOperand, ImmediateOperand, LabelOperand, StringOperand]

@dataclass
class InstructionNode:
    opcode: str             # e.g., "MOV", "ADD", "JMP", "BEQ"
    operands: List[Operand] # Operands list
    instruction_id: int     # Absolute zero-based instruction index
    line_number: int        # Source code line number

    def __repr__(self) -> str:
        ops = ", ".join(str(op) for op in self.operands)
        return f"[{self.instruction_id}] {self.opcode} {ops}"
