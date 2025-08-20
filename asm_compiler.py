import argparse
import sys
import os
import component

class AssemblerCompiler:
    def __init__(self):
        self.EX = ["ADD", "SUB", "MUL", "DIV", "SET", "SHOW", "SAY", "CLR", "TAG", "SLF", "CALL", "RET", "IF", "ELSE", "GOTO", "VAR"]
        self.goto = {}
        self.last_parts = None
        
    def read_script(self, input_file):
        """Read and parse the assembly script file."""
        try:
            with open(input_file, "r") as f:
                script = f.read().splitlines()
            return script
        except FileNotFoundError:
            print(f"Error: Input file '{input_file}' not found.")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file '{input_file}': {e}")
            sys.exit(1)
    
    def setup_memory(self, stack_size, regex_size):
        """Initialize command surface and registers."""
        command_surface = component.memory_setup(stack_size=stack_size)
        x, y = 1, 5
        
        command_surface[y][x] = component.CommandBlock("say start assembler ...", "")
        x += 1
        
        # Setup registers
        for i in range(regex_size):
            command_surface[y][x] = component.CommandBlock(f"/scoreboard objectives add R{i} dummy")
            command_surface[y][x+1] = component.CommandBlock(f"/scoreboard players set REG R{i} 0")
            x += 2
            
        return command_surface, x, y
    
    def find_labels(self, script, command_surface):
        """First pass: find all labels and their positions."""
        w, z = 1, 5
        
        for line in script:
            if line.startswith(":"):
                label = line.split(":")[1].strip()
                self.goto[label] = (z, w)
                print(f"Label {label} found at ({z}, {w})")
            
            if line.split()[0] in self.EX or line.startswith(":"):
                w += 1
                
            if z == len(command_surface)-1:
                component.add_line(command_surface)
                component.add_line(command_surface)
                
            if len(command_surface[z]) <= w+2:
                print(f"Adding new line at ({z}, {w})")
                w = 0
                z += 2
    
    def compile_line(self, line, command_surface, x, y, chained):
        """Compile a single line of assembly code."""
        if line.startswith("ADD"):
            parts = line.split()
            if parts[2].startswith("#"):
                parts[2] = parts[2].split("#")[1]
                command_surface[y][x] = component.CommandBlock(f"/scoreboard players add REG {parts[1].replace(',', '')} {parts[2].replace(',', '')}", "" if not chained else "chain")
            else:
                command_surface[y][x] = component.CommandBlock(f"/scoreboard players operation REG {parts[1].replace(',', '')} += REG {parts[2].replace(',', '')}", "" if not chained else "chain")
            print(f"Processed ADD: {parts[1].replace(',', '')} + {parts[2].replace(',', '')}")
        
        elif line.startswith("SUB"):
            parts = line.split()
            if parts[2].startswith("#"):
                parts[2] = parts[2].split("#")[1]
                command_surface[y][x] = component.CommandBlock(f"/scoreboard players remove REG {parts[1].replace(',', '')} {parts[2].replace(',', '')}", "" if not chained else "chain")
            else:
                command_surface[y][x] = component.CommandBlock(f"/scoreboard players operation REG {parts[1].replace(',', '')} -= REG {parts[2].replace(',', '')}", "" if not chained else "chain")
            print(f"Processed SUB: {parts[1].replace(',', '')} - {parts[2].replace(',', '')}")
        
        elif line.startswith("MUL"):
            parts = line.split()
            if parts[2].startswith("#"):
                AssertionError("MUL command does not support immediate values")
            else:
                command_surface[y][x] = component.CommandBlock(f"/scoreboard players operation REG {parts[1].replace(',', '')} *= REG {parts[2].replace(',', '')}", "" if not chained else "chain")
            print(f"Processed MUL: {parts[1].replace(',', '')} * {parts[2].replace(',', '')}")
        
        elif line.startswith("SHOW"):
            parts = line.split()
            command_surface[y][x] = component.CommandBlock('/tellraw @a {"text":": ","color":"gold","extra":[{"score":{"name":"REG","objective":"'+parts[1].replace(',', '')+'"},"color":"aqua"}]}', "" if not chained else "chain")
            print(f"Processed SHOW: {parts[1].replace(',', '')}")
        
        elif line.startswith(":"):
            label = line.split(":")[1].strip()
            command_surface[y][x] = component.CommandBlock(f"setblock ~ ~1 ~ minecraft:air", "")
            print(f"Label found: {label} at ({y}, {x})")
        
        elif line.startswith("GOTO"):
            label = line.split()[1].strip().replace(":", "")
            if label in self.goto:
                target_y, target_x = self.goto[label]
                command_surface[y][x] = component.CommandBlock(f"setblock ~{target_y-y} ~1 ~{target_x-x} minecraft:redstone_block", "" if not chained else "chain")
                print(f"GOTO found: {label} at ({target_y}, {target_x})")
            else:
                AssertionError(f"Error: GOTO label {label} not defined")
        
        elif line.startswith("SET"):
            parts = line.split()
            if parts[2].startswith("#"):
                parts[2] = parts[2].split("#")[1]
                command_surface[y][x] = component.CommandBlock(f"/scoreboard players set REG {parts[1].replace(',', '')} {parts[2].replace(',', '')}", "" if not chained else "chain")
            else:
                command_surface[y][x] = component.CommandBlock(f"/scoreboard players operation REG {parts[1].replace(',', '')} = REG {parts[2].replace(',', '')}", "" if not chained else "chain")
            
            print(f"Processed SET: {parts[1].replace(',', '')} = {parts[2].replace(',', '')}")

        elif line.startswith("TAG"):
            parts = line.split()
            target_y, target_x = self.goto[parts[1].replace(":", "")]
            command_surface[y][x] = component.CommandBlock(f"execute as @e[type=armor_stand,tag=temp_destination] run tp @s ~{target_y-y} ~1 ~{target_x-x}", "" if not chained else "chain")
            print(f"TAG found: {parts[1].replace(':', '')} at ({target_y}, {target_x})")
        
        elif line.startswith("SLF"):
            target_y, target_x = y, x+2
            if len(command_surface[y]) <= target_x+1:
                edit = target_x+2-len(command_surface[y])
                target_x = edit
                target_y+= 2
            command_surface[y][x] = component.CommandBlock(f"execute as @e[type=armor_stand,tag=temp_origin] run tp @s ~{target_y-y} ~1 ~{target_x-x}", "" if not chained else "chain")
        
        elif line.startswith("CALL"):
            command_surface[y][x] = component.CommandBlock(f"setblock ~{1-y} ~1 ~{1-x} minecraft:redstone_block", "" if not chained else "chain")
        
        elif line.startswith("RET"):
            command_surface[y][x] = component.CommandBlock(f"setblock ~{2-y} ~1 ~{0-x} minecraft:redstone_block", "" if not chained else "chain")
        
        elif line.startswith("IF"):
            parts = line.split()
            self.last_parts = parts
            op = parts[2]
            target_y, target_x = self.goto[parts[4].replace(":", "")]
            if op == ">":
                command_surface[y][x] = component.CommandBlock(f"execute if score REG {parts[1].replace(',', '')} > REG {parts[3].replace(',', '')} run setblock ~{target_y-y} ~1 ~{target_x-x} minecraft:redstone_block", "" if not chained else "chain")
            elif op == "<":
                command_surface[y][x] = component.CommandBlock(f"execute if score REG {parts[1].replace(',', '')} < REG {parts[3].replace(',', '')} run setblock ~{target_y-y} ~1 ~{target_x-x} minecraft:redstone_block", "" if not chained else "chain")
            elif op == "=":
                command_surface[y][x] = component.CommandBlock(f"execute if score REG {parts[1].replace(',', '')} = REG {parts[3].replace(',', '')} run setblock ~{target_y-y} ~1 ~{target_x-x} minecraft:redstone_block", "" if not chained else "chain")
            elif op == "!=":
                command_surface[y][x] = component.CommandBlock(f"execute unless score REG {parts[1].replace(',', '')} = REG {parts[3].replace(',', '')} run setblock ~{target_y-y} ~1 ~{target_x-x} minecraft:redstone_block", "" if not chained else "chain")
            elif op == "<=":
                command_surface[y][x] = component.CommandBlock(f"execute if score REG {parts[1].replace(',', '')} <= REG {parts[3].replace(',', '')} run setblock ~{target_y-y} ~1 ~{target_x-x} minecraft:redstone_block", "" if not chained else "chain")
            elif op == ">=":
                command_surface[y][x] = component.CommandBlock(f"execute if score REG {parts[1].replace(',', '')} >= REG {parts[3].replace(',', '')} run setblock ~{target_y-y} ~1 ~{target_x-x} minecraft:redstone_block", "" if not chained else "chain")
            else:
                AssertionError(f"Unknown operator: {op}")
            print(f"Processed IF: {parts[1].replace(',', '')} {op} {parts[3].replace(',', '')} GOTO {parts[4].replace(':', '')}")
        
        elif line.startswith("ELSE"):
            target_y, target_x = y,x+1
            if len(command_surface[y]) <= target_x+1:
                edit = target_x+2-len(command_surface[y])
                target_x = edit
                target_y+= 2
            parts = self.last_parts
            op = parts[2]
            if op == ">":
                command_surface[y][x] = component.CommandBlock(f"execute unless score REG {parts[1].replace(',', '')} > REG {parts[3].replace(',', '')} run setblock ~{target_y-y} ~1 ~{target_x-x} minecraft:redstone_block", "" if not chained else "chain")
            elif op == "<":
                command_surface[y][x] = component.CommandBlock(f"execute unless score REG {parts[1].replace(',', '')} < REG {parts[3].replace(',', '')} run setblock ~{target_y-y} ~1 ~{target_x-x} minecraft:redstone_block", "" if not chained else "chain")
            elif op == "=":
                command_surface[y][x] = component.CommandBlock(f"execute unless score REG {parts[1].replace(',', '')} = REG {parts[3].replace(',', '')} run setblock ~{target_y-y} ~1 ~{target_x-x} minecraft:redstone_block", "" if not chained else "chain")
            elif op == "!=":
                command_surface[y][x] = component.CommandBlock(f"execute if score REG {parts[1].replace(',', '')} = REG {parts[3].replace(',', '')} run setblock ~{target_y-y} ~1 ~{target_x-x} minecraft:redstone_block", "" if not chained else "chain")
            elif op == "<=":
                command_surface[y][x] = component.CommandBlock(f"execute unless score REG {parts[1].replace(',', '')} <= REG {parts[3].replace(',', '')} run setblock ~{target_y-y} ~1 ~{target_x-x} minecraft:redstone_block", "" if not chained else "chain")
            elif op == ">=":
                command_surface[y][x] = component.CommandBlock(f"execute unless score REG {parts[1].replace(',', '')} >= REG {parts[3].replace(',', '')} run setblock ~{target_y-y} ~1 ~{target_x-x} minecraft:redstone_block", "" if not chained else "chain")
        
        elif line.startswith("CLR"):
            command_surface[y][x] = component.CommandBlock(f"setblock ~ ~1 ~ minecraft:air", "" if not chained else "chain")
            print(f"Processed CLR at ({y}, {x})")
        
        elif line.startswith("SAY"):
            parts = line.split()
            if len(parts) > 1:
                text = " ".join(parts[1:])
                text = text.split("\"")[1]  # Ensure the text is properly formatted
                text = text.replace("{","ùVAR:").replace("}","ù").split("ù")  # split the text to handle variables
                command = "/tellraw @a ["
                for part in text:
                    if part.startswith("VAR:"):
                        command += f'{{"score":{{"name":"REG","objective":"{part[4:]}"}},"color":"aqua"}},'
                    else:
                        command += f'{{"text":"{part}","color":"gold"}},'
                command = command.rstrip(',') + ']'
                command_surface[y][x] = component.CommandBlock(command, "" if not chained else "chain")
                print(f"Processed SAY: {" ".join(parts[1:])}")
            else:
                AssertionError("SAY command requires a message")
        
        elif line.startswith("DIV"):
            parts = line.split()
            if parts[2].startswith("#"):
                AssertionError("DIV command does not support immediate values")
            else:
                command_surface[y][x] = component.CommandBlock(f"/scoreboard players operation REG {parts[1].replace(',', '')} /= REG {parts[2].replace(',', '')}", "" if not chained else "chain")
            print(f"Processed DIV: {parts[1].replace(',', '')} / {parts[2].replace(',', '')}")
        
        elif line.startswith("VAR"):
            parts = line.split()
            if len(parts) != 2:
                AssertionError("VAR command requires a variable name")
            var_name = parts[1].replace(",", "")
            command_surface[y][x] = component.CommandBlock(f"/scoreboard objectives add {var_name} dummy", "" if not chained else "chain")
            print(f"Processed VAR: {var_name}")
        
        else:
            AssertionError(f"Unknown command: {line}")
        
        return True
    
    def compile_script(self, script, output_file, stack_size=15, regex_size=8, display=False):
        """Main compilation function."""
        print(f"Compiling script with {len(script)} lines...")
        
        # Setup memory and registers
        command_surface, x, y = self.setup_memory(stack_size, regex_size)
        
        # First pass: find labels
        self.find_labels(script, command_surface)
        
        # Second pass: compile commands
        chained = True
        temp = True
        index = 0
        
        for line in script:
            if not line.strip():  # Skip empty lines
                continue
                
            try:
                self.compile_line(line, command_surface, x, y, chained)
                x += 1
                
                # Handle line wrapping
                if len(command_surface[y]) <= x+1:
                    a, b = x, y
                    x = 1
                    y += 2
                    command_surface[b][a] = component.CommandBlock(f"setblock ~{y-b} ~1 ~{x-a-1} minecraft:redstone_block")
                    command_surface[y][x-1] = component.CommandBlock(f"setblock ~ ~1 ~ minecraft:air", "")
                
                # Update chaining state
                if not chained:
                    chained = True
                    print(f"Chained set to True at line {index}")
                if not temp:
                    temp = True
                    chained = False
                    
            except Exception as e:
                print(f"Error compiling line {index + 1}: '{line}' - {e}")
                sys.exit(1)
                
            index += 1
        
        # Export and display
        component.export_to_schematic(command_surface, output_file)
        if display:
            component.display_command_block(command_surface)
        
        print(f"Compilation complete. Output saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(
        description="Assembly to Minecraft Command Block Compiler",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.asm                           # Compile with default settings
  %(prog)s input.asm -o output.schem           # Specify output file
  %(prog)s input.asm -s 20 -r 16              # Custom stack and register sizes
  %(prog)s input.asm --display                # Show command blocks after compilation
        """
    )
    
    parser.add_argument("input", help="Input assembly file (.asm)")
    parser.add_argument("-o", "--output", 
                       help="Output schematic file (default: command_blocks.schem)",
                       default="command_blocks.schem")
    parser.add_argument("-s", "--stack-size", type=int, default=15,
                       help="Stack size for memory setup (default: 15)")
    parser.add_argument("-r", "--register-size", type=int, default=8,
                       help="Number of registers to create (default: 8)")
    parser.add_argument("--display", action="store_true",
                       help="Display command blocks after compilation")
    parser.add_argument("-v", "--verbose", action="store_true",
                       help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' does not exist.")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except Exception as e:
            print(f"Error creating output directory '{output_dir}': {e}")
            sys.exit(1)
    
    # Initialize compiler and run
    compiler = AssemblerCompiler()
    script = compiler.read_script(args.input)
    
    if args.verbose:
        print(f"Input file: {args.input}")
        print(f"Output file: {args.output}")
        print(f"Stack size: {args.stack_size}")
        print(f"Register size: {args.register_size}")
        print(f"Script lines: {len(script)}")
    
    try:
        compiler.compile_script(
            script, 
            args.output, 
            stack_size=args.stack_size, 
            regex_size=args.register_size,
            display=args.display
        )
    except KeyboardInterrupt:
        print("\nCompilation interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Compilation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

