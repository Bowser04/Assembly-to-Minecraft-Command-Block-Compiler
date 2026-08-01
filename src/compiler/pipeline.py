"""
Compiler Pipeline orchestrating Lexer, Parser, CodeGenerator, and Schematic Export.
"""

from src.compiler.lexer import Lexer
from src.compiler.parser import Parser
from src.compiler.codegen import CodeGenerator
from src.compiler.target.architecture import Architecture
from src.compiler.target.schematic import export_schematic
from src.compiler.config import DEFAULT_STACK_SIZE, DEFAULT_MEMORY_SIZE

class CompilerPipeline:
    """Orchestrates the multi-stage assembly compilation pipeline."""

    def __init__(
        self,
        stack_size: int = DEFAULT_STACK_SIZE,
        memory_size: int = DEFAULT_MEMORY_SIZE,
        program_length: int = 16,
    ):
        self.architecture = Architecture(
            stack_size=stack_size,
            memory_size=memory_size,
            program_length=program_length,
        )

    def compile_string(self, source_code: str, output_schem_path: str | None = None) -> Architecture:
        """
        Compiles an assembly source code string into an Architecture block matrix structure,
        and optionally exports it to a .schem file.
        """
        # Step 1: Lexical analysis
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()

        # Step 2: Parsing & Symbol Table construction
        parser = Parser(tokens)
        ast_nodes, symbol_table = parser.parse()

        # Step 3: Code generation
        codegen = CodeGenerator(self.architecture)
        codegen.generate(ast_nodes, symbol_table)

        # Step 4: Export to schematic if requested
        if output_schem_path:
            export_schematic(self.architecture, output_schem_path)

        return self.architecture

    def compile_file(self, asm_filepath: str, output_schem_path: str | None = None) -> Architecture:
        """Reads an assembly file and compiles it."""
        with open(asm_filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        return self.compile_string(code, output_schem_path)
