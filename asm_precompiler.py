import argparse
import emulator

class Precompiler:
    def __init__(self, register_count=10):
        self.register_count = register_count
        self.var = ["SYS.OPR.TEMP"]

    def precompile(self, input_path, output_path):
        with open(input_path, "r") as f:
            script = f.read().splitlines()
        precompile_script = self._init_var()
        for line in script:
            line = line.replace("  ","").replace("   ","").strip()
            if line.startswith("--") or not line:
                continue
            elif line.startswith("CALL"):
                target = line.split(" ")[1]
                precompile_script += f"TAG {target}\nSLF\nCALL\n"
            elif line.startswith("IF"):
                precompile_script += line + "\nELSE\nCLR\n"
            elif line.startswith("OPR"):
                op,r,a,b = line.split(" ")[1:]
                precompile_script+="SET SYS.OPR.TEMP "+a+"\n"
                precompile_script+=op+" SYS.OPR.TEMP "+b+"\n"
                precompile_script+="SET "+r+" "+"SYS.OPR.TEMP\n"
            else:
                precompile_script += line + "\n"
        with open(output_path, "w") as f:
            f.write(precompile_script)
        return precompile_script
    def _init_var(self):
        precompile_script = ""
        for var in self.var:
            precompile_script+="VAR "+var+"\n"
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