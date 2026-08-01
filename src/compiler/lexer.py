"""
Lexical analyzer (tokenizer) for assembly source code.
"""

from src.compiler.tokens import Token, TokenType

OPCODES = {
    "MOV", "ADD", "SUB", "MUL", "DIV", "MOD",
    "JMP", "LDR", "STR", "BEQ", "BNE", "BGT", "BLT", "MSG"
}

class Lexer:
    """Scans assembly source code and produces a sequence of tokens."""

    def __init__(self, source_code: str):
        self.source = source_code
        self.tokens: list[Token] = []

    def tokenize(self) -> list[Token]:
        lines = self.source.splitlines()
        for line_num, line in enumerate(lines, start=1):
            self._tokenize_line(line, line_num)
        self.tokens.append(Token(TokenType.EOF, None, len(lines) + 1, 1))
        return self.tokens

    def _tokenize_line(self, line: str, line_num: int) -> None:
        # First check if the line (stripped of comments) ends with ':'
        # To do this safely, let's find the comment sign first (not inside quotes).
        in_quote = False
        comment_idx = -1
        for idx, char in enumerate(line):
            if char == '"':
                in_quote = not in_quote
            elif char == ';' and not in_quote:
                comment_idx = idx
                break

        code_part = line[:comment_idx] if comment_idx != -1 else line
        code_part_stripped = code_part.strip()

        if not code_part_stripped:
            return

        if code_part_stripped.endswith(':'):
            label_name = code_part_stripped[:-1].strip()
            self.tokens.append(Token(TokenType.LABEL_DEF, label_name, line_num, 1))
            return

        # Tokenize code_part character by character
        i = 0
        col = 1
        length = len(code_part)

        while i < length:
            # Skip spaces and commas
            while i < length and (code_part[i].isspace() or code_part[i] == ','):
                if code_part[i] == '\t':
                    col += 4
                else:
                    col += 1
                i += 1

            if i >= length:
                break

            # String literal
            if code_part[i] == '"':
                start_col = col
                i += 1
                col += 1
                val = []
                while i < length and code_part[i] != '"':
                    val.append(code_part[i])
                    if code_part[i] == '\t':
                        col += 4
                    else:
                        col += 1
                    i += 1
                if i < length:  # found closing quote
                    i += 1
                    col += 1
                self.tokens.append(Token(TokenType.STRING, "".join(val), line_num, start_col))
                continue

            # Identifier, Register, Immediate, or Opcode
            start_col = col
            start_i = i
            while i < length and not code_part[i].isspace() and code_part[i] not in (',', '"'):
                col += 1
                i += 1
            part = code_part[start_i:i]
            upper_part = part.upper()

            if upper_part in OPCODES:
                self.tokens.append(Token(TokenType.OPCODE, upper_part, line_num, start_col))
            elif upper_part.startswith('R') and upper_part[1:].isdigit():
                self.tokens.append(Token(TokenType.REGISTER, upper_part, line_num, start_col))
            elif self._is_number(part):
                self.tokens.append(Token(TokenType.IMMEDIATE, int(part), line_num, start_col))
            else:
                self.tokens.append(Token(TokenType.IDENTIFIER, part, line_num, start_col))

    @staticmethod
    def _is_number(s: str) -> bool:
        try:
            int(s)
            return True
        except ValueError:
            return False
