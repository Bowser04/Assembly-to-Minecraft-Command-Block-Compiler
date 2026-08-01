"""
Unit tests for the Assembly to Minecraft Command Block Compiler.
"""

import unittest
import os
import tempfile
from src.compiler.lexer import Lexer
from src.compiler.tokens import TokenType
from src.compiler.parser import Parser
from src.compiler.pipeline import CompilerPipeline

BASIC_ASM = """
MOV R0, 0
MOV R1, 1
loop_start:
ADD R0, R0, R1
JMP loop_start
"""

UNSUPPORTED_RAM_ASM = """
MOV R3, 10
STR R3, 0
LDR R0, 0
"""

class TestCompiler(unittest.TestCase):

    def test_lexer(self):
        lexer = Lexer(BASIC_ASM)
        tokens = lexer.tokenize()
        opcodes = [t.value for t in tokens if t.type == TokenType.OPCODE]
        labels = [t.value for t in tokens if t.type == TokenType.LABEL_DEF]

        self.assertIn("MOV", opcodes)
        self.assertIn("ADD", opcodes)
        self.assertIn("JMP", opcodes)
        self.assertEqual(labels, ["loop_start"])

    def test_pipeline_compilation_success(self):
        pipeline = CompilerPipeline(program_length=16)
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = os.path.join(tmpdir, "test_output")
            arch = pipeline.compile_string(BASIC_ASM, out_path)
            self.assertIsNotNone(arch.program)
            self.assertTrue(os.path.exists(out_path + ".schem"))

    def test_unsupported_ram_instructions_raise_error(self):
        pipeline = CompilerPipeline(program_length=16)
        with self.assertRaises(NotImplementedError):
            pipeline.compile_string(UNSUPPORTED_RAM_ASM)

    def test_msg_instruction(self):
        src = 'MSG "La somme est R0 et i est R1"'
        lexer = Lexer(src)
        tokens = lexer.tokenize()
        opcodes = [t for t in tokens if t.type == TokenType.OPCODE]
        strings = [t for t in tokens if t.type == TokenType.STRING]
        self.assertEqual(len(opcodes), 1)
        self.assertEqual(opcodes[0].value, "MSG")
        self.assertEqual(len(strings), 1)
        self.assertEqual(strings[0].value, "La somme est R0 et i est R1")

        parser = Parser(tokens)
        instructions, _ = parser.parse()
        self.assertEqual(len(instructions), 1)
        self.assertEqual(instructions[0].opcode, "MSG")
        self.assertEqual(len(instructions[0].operands), 1)

        from src.compiler.ast import StringOperand
        self.assertIsInstance(instructions[0].operands[0], StringOperand)
        self.assertEqual(instructions[0].operands[0].value, "La somme est R0 et i est R1")

        pipeline = CompilerPipeline(program_length=16)
        arch = pipeline.compile_string(src)
        # Verify the command is generated in the Block matrix
        cmd_found = False
        for row in arch.program.Block:
            for cell in row:
                if cell:
                    cmd = cell[1].get("Command", "")
                    if "/tellraw" in cmd:
                        cmd_found = True
                        self.assertIn('"score"', cmd)
                        self.assertIn('"R0"', cmd)
                        self.assertIn('"R1"', cmd)
        self.assertTrue(cmd_found)

if __name__ == "__main__":
    unittest.main()
