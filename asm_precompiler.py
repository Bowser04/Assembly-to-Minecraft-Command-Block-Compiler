import argparse
import os
import emulator

class Precompiler:
    def __init__(self, register_count=10):
        self.register_count = register_count
        self.var = ["SYS.OPR.TEMP"]
        self.library_script = ""

    def precompile(self, input_path, output_path,script_prefix=""):
        with open(input_path, "r") as f:
            script = f.read().splitlines()
        precompile_script = self._init_var()
        for line in script:
            line = line.replace("  ","").replace("   ","").strip()
            # Organize handlers in a dictionary for readability
            def handle_comment_or_empty(line,*kwargs):
                return ""

            def handle_call(line,*kwargs):
                _, target = line.split(" ", 1)
                return f"TAG {script_prefix}{target}\nSLF\nCALL\n"

            def handle_if(line,*kwargs):
                _, A, op, B, label = line.split(" ", 4)
                line = f"IF {A} {op} {B} :{script_prefix}{label}"
                return f"{line}\nELSE\nCLR\n"

            def handle_opr(line,*kwargs):
                parts = line.split(" ")
                if len(parts) != 5:
                    raise ValueError(f"Invalid OPR instruction: {line}")
                _, op, r, a, b = parts
                return (
                    f"SET SYS.OPR.TEMP {a}\n"
                    f"{op} SYS.OPR.TEMP {b}\n"
                    f"SET {r} SYS.OPR.TEMP\n"
                )
            def handle_import(line,*kwargs):
                _, module = line.split(" ", 1)
                if os.path.exists(module+".sasm"):
                    imported_script = f":{script_prefix}{module}_IMPORT\n"
                    imported_script += self.precompile(module+".sasm", module+".asm", script_prefix=script_prefix+module+".")
                    self.library_script += imported_script+"\n"
                    res = handle_call(f"CALL :{script_prefix}{module}_IMPORT")
                    return res
            def handle_label(line,*kwargs):
                label = line.lstrip(":")
                return f":{script_prefix}{label}\n"
            def handle_end(line,*kwargs):
                return "RET\n"
            def handle_default(line,*kwargs):
                return f"{line}\n"
            def handle_goto(line,*kwargs):
                _, label = line.split(" ", 1)
                label = label.lstrip(":")
                return f"GOTO :{script_prefix}{label}\n"
            # Handler selection based on instruction prefix
            prefix_handlers = {
                "CALL": handle_call,
                "IF": handle_if,
                "OPR": handle_opr,
                "IMPORT": handle_import,
                "END": handle_end,
                ":": handle_label,
                "GOTO": handle_goto,
            }

            if line.startswith("--") or not line:
                precompile_script += handle_comment_or_empty(line)
            else:
                for prefix, handler in prefix_handlers.items():
                    if line.startswith(prefix):
                        precompile_script += handler(line)
                        break
                else:
                    precompile_script += handle_default(line)
        # remove trailing newlines
        precompile_script = precompile_script.strip() + "\n" + self.library_script.strip()

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