import argparse
import emulator

class Precompiler:
    def __init__(self, register_count=10):
        self.register_count = register_count

    def precompile(self, input_path, output_path):
        with open(input_path, "r") as f:
            script = f.read().splitlines()
        precompile_script = ""
        for line in script:
            line = line.replace("    ","")
            if line.startswith("--"):
                continue
            elif line.startswith("CALL"):
                target = line.split(" ")[1]
                precompile_script += f"TAG {target}\nSLF\nCALL\n"
            elif line.startswith("IF"):
                precompile_script += line + "\nELSE\nCLR\n"
            else:
                precompile_script += line + "\n"
        with open(output_path, "w") as f:
            f.write(precompile_script)
        return precompile_script

def main():
    parser = argparse.ArgumentParser(description="Assembly Precompiler")
    parser.add_argument("--input", required=True, help="Input .sasm file")
    parser.add_argument("--output", required=True, help="Output .asm file")
    parser.add_argument("--registers", type=int, default=10, help="Number of registers for emulator")
    parser.add_argument("--emulate", action="store_true", help="Run emulator after precompiling")
    args = parser.parse_args()

    precompiler = Precompiler(args.registers)
    precompiled_script = precompiler.precompile(args.input, args.output)

    if args.emulate:
        emu = emulator.Emulator(args.registers)
        emu.execute_script(precompiled_script)

if __name__ == "__main__":
    main()