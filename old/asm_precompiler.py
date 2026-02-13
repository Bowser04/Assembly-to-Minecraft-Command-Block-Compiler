import argparse
import os
import emulator

class Precompiler:
    def __init__(self, register_count=10):
        self.float_factory = 10000  # Factor to convert float to int representation its digits n°4 after decimal point
        self.register_count = register_count
        self.sys_var = {
                    "SYS.OPR.TEMP": None,
                    "SYS.OPR.IP": None,
                    "SYS.OPR.FP": None,
                    "SYS.FLOAT_FACTORY": self.float_factory
                    }
        self.sys_modules = ["SCREEN"]
        self.var = [*self.sys_var.keys()]
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
                # Remove leading colon from label if present
                label = label.lstrip(":")
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
                path = os.path.dirname(os.path.abspath(input_path))
                path = os.path.join(path, module+".sasm")
                out_path_temp = os.path.dirname(os.path.abspath(output_path))
                out_path_temp = os.path.join(out_path_temp, "libs")
                if not os.path.exists(out_path_temp):
                    os.makedirs(out_path_temp)
                out_path_temp = os.path.join(out_path_temp, module+".asm")
                print(f"Importing module: {module} from path: {path}")
                if os.path.exists(path):
                    imported_script = f":{script_prefix}{module}_IMPORT\n"
                    imported_script += self.precompile(path, out_path_temp, script_prefix=script_prefix+module+".")
                    self.library_script += imported_script+"\n"
                    res = handle_call(f"CALL :{script_prefix}{module}_IMPORT")
                    return res
                elif module in self.sys_modules:
                    print(f"Importing system module: {module}")
                    #get current path of the python file
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    lib_path = os.path.join(current_dir, "sys_modules", module+".sasm")
                    imported_script = f":{script_prefix}{module}_IMPORT\n"
                    imported_script += self.precompile(lib_path, out_path_temp, script_prefix=script_prefix+module+".")
                    self.library_script += imported_script+"\n"
                    res = handle_call(f"CALL :{script_prefix}{module}_IMPORT")
                    return res
                else:
                    assert False, f"Module {module} not found at path: {path}"
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
            def handle_fset(line,*kwargs):
                _, var, value = line.split(" ", 2)
                var = var.replace(",", "").strip()
                value = value.strip()
                if var not in self.var:
                    self.var.append(var)
                if value.startswith("#"):
                    float_value = int(float(value.lstrip("#")) * self.float_factory)
                    return f"SET {var} #{float_value}\n"
                else:
                    return f"SET {var} {value}\n"
            
            def handle_fadd(line,*kwargs):
                _, var, value = line.split(" ", 2)
                var = var.replace(",", "").strip()
                value = value.strip()
                if var not in self.var:
                    self.var.append(var)
                if value.startswith("#"):
                    float_value = int(float(value.lstrip("#")) * self.float_factory)
                    return f"SET SYS.OPR.TEMP #{float_value}\nADD {var} SYS.OPR.TEMP\n"
                else:
                    return f"ADD {var} {value}\n"
            
            def handle_fmul(line,*kwargs):
                _, var, value = line.split(" ", 2)
                var = var.replace(",", "").strip()
                value = value.strip()
                if var not in self.var:
                    self.var.append(var)
                if value.startswith("#"):
                    float_value = int(float(value.lstrip("#")) * self.float_factory)
                    return f"SET SYS.OPR.TEMP #{float_value}\nMUL {var} SYS.OPR.TEMP\nSET SYS.OPR.TEMP SYS.FLOAT_FACTORY\nDIV {var} SYS.OPR.TEMP\n"
                else:
                    return f"MUL {var} {value}\nSET SYS.OPR.TEMP SYS.FLOAT_FACTORY\nDIV {var} SYS.OPR.TEMP\n"
            
            def handle_fdiv(line,*kwargs):
                _, var, value = line.split(" ", 2)
                var = var.replace(",", "").strip()
                value = value.strip()
                if var not in self.var:
                    self.var.append(var)
                if value.startswith("#"):
                    float_value = int(float(value.lstrip("#")) * self.float_factory)
                    return f"SET SYS.OPR.TEMP SYS.FLOAT_FACTORY\nMUL {var} SYS.OPR.TEMP\nSET SYS.OPR.TEMP #{float_value}\nDIV {var} SYS.OPR.TEMP\n"
                else:
                    return f"SET SYS.OPR.TEMP SYS.FLOAT_FACTORY\nMUL {var} SYS.OPR.TEMP\nDIV {var} {value}\n"
            
            def handle_fshow(line,*kwargs):
                _, message = line.split(" ", 1)
                formatted_message = message.replace("{", "{FLOAT").split("FLOAT")
                res = ""
                for var in formatted_message[1:]:
                    var_name, rest = var.split("}", 1)
                    if var_name in self.var:
                        # Extract integer part: var / 10000
                        float_int_part = f"SET SYS.OPR.IP {var_name}\nSET SYS.OPR.TEMP SYS.FLOAT_FACTORY\nDIV SYS.OPR.IP SYS.OPR.TEMP\n"
                        # Calculate what integer part represents: IP * 10000
                        float_temp_calc = f"SET SYS.OPR.TEMP SYS.OPR.IP\nSET SYS.OPR.FP SYS.FLOAT_FACTORY\nMUL SYS.OPR.TEMP SYS.OPR.FP\n"
                        # Extract fractional part: var - (IP * 10000)
                        float_frac_part = f"SET SYS.OPR.FP {var_name}\nSUB SYS.OPR.FP SYS.OPR.TEMP\n"
                        
                        res += float_int_part
                        res += float_temp_calc
                        res += float_frac_part
                        
                        # Replace {var_name} with {SYS.OPR.IP}.{SYS.OPR.FP}
                        formatted_message[formatted_message.index(var_name+'}'+rest)] = "SYS.OPR.IP" + "}" +"."+ "{" + "SYS.OPR.FP" + "}" + rest
                final_message = "".join(formatted_message)
                return f"{res}SAY {final_message}\n"
            # Handler selection based on instruction prefix
            prefix_handlers = {
                "CALL": handle_call,
                "IF": handle_if,
                "OPR": handle_opr,
                "IMPORT": handle_import,
                "END": handle_end,
                ":": handle_label,
                "GOTO": handle_goto,
                "FSET": handle_fset,
                "FADD": handle_fadd,
                "FMUL": handle_fmul,
                "FDIV": handle_fdiv,
                "FSHOW": handle_fshow
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
        for var in self.sys_var.keys():
            precompile_script+="VAR "+var+"\n"
            if self.sys_var[var] is not None:
                precompile_script+=f"SET {var} #{self.sys_var[var]}\n"
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