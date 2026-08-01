"""
CLI entry point for the Assembly to Minecraft Command Block Compiler.
"""

import sys
import os
import argparse
from src.compiler.pipeline import CompilerPipeline
from src.compiler.config import DEFAULT_STACK_SIZE, DEFAULT_MEMORY_SIZE

def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="Assembly-to-Minecraft Command Block Compiler. Compiles Assembly (.asm) source files into Minecraft WorldEdit schematic (.schem) files.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "source",
        nargs="?",
        default="basic_sample.asm",
        help="Path to the input assembly source file (.asm)"
    )
    parser.add_argument(
        "-o", "--output",
        default="command_blocks",
        help="Output schematic filepath or name (without or with .schem extension)"
    )
    parser.add_argument(
        "-s", "--stack-size",
        type=int,
        default=DEFAULT_STACK_SIZE,
        help="Size of the hardware stack in slots"
    )
    parser.add_argument(
        "-m", "--memory-size",
        type=int,
        default=DEFAULT_MEMORY_SIZE,
        help="Size of the RAM memory in slots"
    )
    parser.add_argument(
        "-c", "--cols",
        type=int,
        default=16,
        help="Number of columns per row in the serpentine program layout"
    )

    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()

    asm_file = args.source
    if not os.path.exists(asm_file):
        print(f"Error: Source file '{asm_file}' not found.", file=sys.stderr)
        sys.exit(1)

    print(f"=== Compiling {asm_file} ===")
    print(f"Configuration: Stack={args.stack_size}, RAM={args.memory_size}, Layout Columns={args.cols}")

    pipeline = CompilerPipeline(
        stack_size=args.stack_size,
        memory_size=args.memory_size,
        program_length=args.cols,
    )

    output_path = args.output
    if output_path.endswith(".schem"):
        output_path = output_path[:-6]

    try:
        architecture = pipeline.compile_file(asm_file, output_path)
        out_full_path = os.path.abspath(f"{output_path}.schem")
        print(f"Compilation successful!")
        print(f"Output schematic saved to: {out_full_path}")
    except NotImplementedError as err:
        print(f"\n[Compilation Failure]: {err}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
