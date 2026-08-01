"""
Token definitions for lexical analysis.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Any

class TokenType(Enum):
    OPCODE = auto()       # MOV, ADD, JMP, BEQ, etc.
    REGISTER = auto()     # R0, R1, R2...
    IMMEDIATE = auto()    # 10, -5, 0
    LABEL_DEF = auto()    # loop_sum:
    IDENTIFIER = auto()   # loop_sum (as jump target)
    COMMA = auto()        # ,
    COMMENT = auto()      # ; comment
    STRING = auto()       # "hello world"
    EOF = auto()

@dataclass
class Token:
    type: TokenType
    value: Any
    line: int
    column: int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, L{self.line}:{self.column})"
