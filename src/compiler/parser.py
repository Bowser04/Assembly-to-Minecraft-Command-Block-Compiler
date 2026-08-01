"""
Parser module for building AST nodes and populating the symbol table.
"""

from src.compiler.tokens import Token, TokenType
from src.compiler.symbols import SymbolTable
from src.compiler.ast import (
    InstructionNode,
    Operand,
    RegisterOperand,
    ImmediateOperand,
    LabelOperand,
    StringOperand,
)

class Parser:
    """Parses a sequence of tokens into AST instruction nodes and resolves label definitions."""

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.symbol_table = SymbolTable()
        self.instructions: list[InstructionNode] = []

    def parse(self) -> tuple[list[InstructionNode], SymbolTable]:
        current_instruction_id = 0
        i = 0

        while i < len(self.tokens):
            token = self.tokens[i]

            if token.type == TokenType.EOF:
                break

            if token.type == TokenType.LABEL_DEF:
                self.symbol_table.add_label(token.value, current_instruction_id)
                i += 1
                continue

            if token.type == TokenType.OPCODE:
                opcode = token.value
                line = token.line
                i += 1
                operands: list[Operand] = []

                # Collect operands until next OPCODE, LABEL_DEF, or EOF
                while i < len(self.tokens) and self.tokens[i].type not in (TokenType.OPCODE, TokenType.LABEL_DEF, TokenType.EOF):
                    op_token = self.tokens[i]
                    if op_token.type == TokenType.REGISTER:
                        reg_idx = int(op_token.value[1:])
                        operands.append(RegisterOperand(name=op_token.value, index=reg_idx))
                    elif op_token.type == TokenType.IMMEDIATE:
                        operands.append(ImmediateOperand(value=op_token.value))
                    elif op_token.type == TokenType.IDENTIFIER:
                        operands.append(LabelOperand(name=op_token.value))
                    elif op_token.type == TokenType.STRING:
                        operands.append(StringOperand(value=op_token.value))
                    i += 1

                node = InstructionNode(
                    opcode=opcode,
                    operands=operands,
                    instruction_id=current_instruction_id,
                    line_number=line,
                )
                self.instructions.append(node)
                current_instruction_id += 1
                continue

            i += 1

        return self.instructions, self.symbol_table
