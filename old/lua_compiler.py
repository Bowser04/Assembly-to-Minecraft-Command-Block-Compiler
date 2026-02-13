import asm_precompiler
import asm_compiler
import argparse
class LuaCompiler:
    def __init__(self, registers=10):
        self.registers = registers
        self.precompiler = asm_precompiler.Precompiler()
        self.compiler = asm_compiler.AssemblerCompiler()

    def __compile_asm(self, input_path, output_path):
        precompiled_script = self.precompiler.precompile(input_path, "temp.asm")
        compiled_script = self.compiler.compile("temp.asm", output_path)
        return compiled_script
    
    def compile_lua_to_asm(self, input_path, output_path):
        lua_operations = {"function":self.__handle_function, "end":self.__handle_end, "if":self.__handle_if, "else":self.__handle_else, "elseif":self.__handle_elseif, "while":self.__handle_while, "do":self.__handle_do, "return":self.__handle_return, "--":self.__handle_comment, "local":self.__handle_local}
        script = open(input_path, "r").readlines()
        asm_script = ""
        for line in script:
            line = line.strip()
            if not line:
                continue
            handled = False
            for key, handler in lua_operations.items():
                if line.startswith(key):
                    asm_script += handler(line)
                    handled = True
                    break
            if not handled:
                asm_script += self.__handle_default(line)
        script_output = open(output_path, "w")
        script_output.write(asm_script)
        script_output.close()

    def __handle_default(self, line):
        if line.split()[1] == "=":
            var, value = line.split("=", 1)
            var = var.strip()
            value = value.strip()
            if value.isdigit():
                return f"VAR {var}\n"
            value_script = self.__handle_calculation(value,output_var=var)
            return f"{value_script}"
        return f"-- Unhandled line: {line}\n"
    def __handle_calculation(self, expression, output_var):
        # Simple calculation handler (handles + , - , * , //)
        expression = expression.strip().replace(" ", "")
        tokens = expression.replace("+", " + ").replace("-", " - ").replace("*", " * ").replace("//", " // ").split(" ")
        asm_script = ""
        temp_var_1 = output_var
        temp_var_2 = f"LUA.CALC.temp_calc"
        asm_script += f"VAR {temp_var_1}\n"
        asm_script += f"VAR {temp_var_2}\n"
        current_op = None
        
        for token in tokens:
            if token not in ["+", "-", "*", "//"]:
                if current_op is None:
                    asm_script += self.__calculation(token,output_var=temp_var_1)
                else:
                    asm_script += self.__calculation(token,output_var=temp_var_2)
                    if current_op == "+":
                        asm_script += f"ADD {temp_var_1} {temp_var_2}\n"
                    elif current_op == "-":
                        asm_script += f"SUB {temp_var_1} {temp_var_2}\n"
                    elif current_op == "*":
                        asm_script += f"MUL {temp_var_1} {temp_var_2}\n"
                    elif current_op == "//":
                        asm_script += f"DIV {temp_var_1} {temp_var_2}\n"
            else:
                current_op = token
        return asm_script
    def __calculation(self, token, output_var, op=None):
        if token.isdigit():
            return f"SET {output_var} #{token}\n"
        else:
            return f"SET {output_var} {token}\n"
    def __handle_function(self, line):
        pass
    def __handle_end(self, line):
        pass
    def __handle_if(self, line):
        pass
    def __handle_else(self, line):  
        pass
    def __handle_elseif(self, line):
        pass
    def __handle_while(self, line):
        pass
    def __handle_do(self, line):
        pass
    def __handle_return(self, line):
        pass
    def __handle_comment(self, line):
        pass
    def __handle_local(self, line):
        pass
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compile Lua-like script to Minecraft Assembly.")
    parser.add_argument("input", help="Path to the input Lua-like script file.")
    parser.add_argument("output", help="Path to the output Assembly file.")
    args = parser.parse_args()

    compiler = LuaCompiler()
    compiler.compile_lua_to_asm(args.input, args.output)