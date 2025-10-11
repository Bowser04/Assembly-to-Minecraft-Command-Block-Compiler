import argparse
import sys
import os
import component

class AssemblerCompiler:
    def __init__(self):
        self.EX = ["ADD", "SUB", "MUL", "DIV", "SET", "SHOW", "SAY", "CLR", "TAG", "SLF", "CALL", "RET", "IF", "ELSE", "GOTO", "VAR"]
        self.goto = {}
        self.last_parts = None
        self.temp = True
        
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

    def advance_position(self, x, y, mod, command_surface):
        """
        Advance to the next position in the command surface.
        Handles line wrapping and ensures enough rows exist.
        
        Args:
            x: Current x position
            y: Current y position
            mod: Current direction (1 = right, -1 = left)
            command_surface: The 2D grid of command blocks
        
        Returns:
            tuple: (new_x, new_y, new_mod, new_orientation, wrap_pos)
        """
        x += mod
        orientation = "south" if mod == 1 else "north"
        
        # Ensure we have enough rows
        if y > len(command_surface) - 1:
            component.add_line(command_surface)
        
        # Check if we need to wrap to next line
        if len(command_surface[y]) <= x + 1 or x < 1:
            # Store position for rotation blocks (this is where the turn happens)
            turn_x = x
            turn_y = y
            
            # Move to next line
            y += 1             # Move to next row
            mod = -mod         # Reverse direction
            orientation = "south" if mod == 1 else "north"
            
            # Start at the beginning of new direction
            # The x position stays at turn_x (where the rotation block is)
            # Don't advance x here - we'll place rotation blocks at turn_x
            
            # Ensure new row exists
            while y >= len(command_surface):
                component.add_line(command_surface)
            
            return turn_x, y, mod, orientation, (turn_x, turn_y)
        
        return x, y, mod, orientation, None

    def find_labels(self, script, command_surface, x, y):
        """First pass: find all labels and their positions."""
        w, z = x, y
        print(y)
        mod = 1
        
        for line in script:
            if not line.strip():  # Skip empty lines
                continue
                
            if line.startswith(":"):
                label = line.split(":")[1].strip()
                self.goto[label] = (z, w)
                print(f"Label {label} found at ({z}, {w})")
            
            if line.split()[0] in self.EX or line.startswith(":"):
                # Advance position
                result = self.advance_position(w, z, mod, command_surface)
                w, z, mod, orientation, wrap_pos = result
                if wrap_pos:
                    w+=mod
            else:
                print(f"Warning: Unknown command '{line}'")

    def compile_line(self, line, command_surface, x, y, chained, orientation, line_number=None):
        """Compile a single line of assembly code."""
        #match line.split(" ")[0]
        if line.startswith("ADD"):
            parts = line.split()
            if parts[2].startswith("#"):
                parts[2] = parts[2].split("#")[1]
                command_surface[y][x] = component.CommandBlock(f"/scoreboard players add REG {parts[1].replace(',', '')} {parts[2].replace(',', '')}", "" if not chained else "chain",orientation=orientation, source_line=line_number, source_code=line)
            else:
                command_surface[y][x] = component.CommandBlock(f"/scoreboard players operation REG {parts[1].replace(',', '')} += REG {parts[2].replace(',', '')}", "" if not chained else "chain",orientation=orientation, source_line=line_number, source_code=line)
            print(f"Processed ADD: {parts[1].replace(',', '')} + {parts[2].replace(',', '')}")
        
        elif line.startswith("SUB"):
            parts = line.split()
            if parts[2].startswith("#"):
                parts[2] = parts[2].split("#")[1]
                command_surface[y][x] = component.CommandBlock(f"/scoreboard players remove REG {parts[1].replace(',', '')} {parts[2].replace(',', '')}", "" if not chained else "chain",orientation=orientation, source_line=line_number, source_code=line)
            else:
                command_surface[y][x] = component.CommandBlock(f"/scoreboard players operation REG {parts[1].replace(',', '')} -= REG {parts[2].replace(',', '')}", "" if not chained else "chain",orientation=orientation, source_line=line_number, source_code=line)
            print(f"Processed SUB: {parts[1].replace(',', '')} - {parts[2].replace(',', '')}")
        
        elif line.startswith("MUL"):
            parts = line.split()
            if parts[2].startswith("#"):
                AssertionError("MUL command does not support immediate values")
            else:
                command_surface[y][x] = component.CommandBlock(f"/scoreboard players operation REG {parts[1].replace(',', '')} *= REG {parts[2].replace(',', '')}", "" if not chained else "chain",orientation=orientation, source_line=line_number, source_code=line)
            print(f"Processed MUL: {parts[1].replace(',', '')} * {parts[2].replace(',', '')}")
        
        elif line.startswith("SHOW"):
            parts = line.split()
            command_surface[y][x] = component.CommandBlock('/tellraw @a {"text":": ","color":"gold","extra":[{"score":{"name":"REG","objective":"'+parts[1].replace(',', '')+'"},"color":"aqua"}]}', "" if not chained else "chain",orientation=orientation, source_line=line_number, source_code=line)
            print(f"Processed SHOW: {parts[1].replace(',', '')}")
        
        elif line.startswith(":"):
            label = line.split(":")[1].strip()
            command_surface[y][x] = component.CommandBlock(f"setblock ~ ~1 ~ minecraft:air", "",orientation=orientation, source_line=line_number, source_code=line)
            print(f"Label found: {label} at ({y}, {x})")
        
        elif line.startswith("GOTO"):
            label = line.split()[1].strip().replace(":", "")
            if label in self.goto:
                target_y, target_x = self.goto[label]
                command_surface[y][x] = component.CommandBlock(f"setblock ~{target_y-y} ~1 ~{target_x-x} minecraft:redstone_block", "" if not chained else "chain",orientation=orientation, source_line=line_number, source_code=line)
                print(f"GOTO found: {label} at ({target_y}, {target_x})")
            else:
                AssertionError(f"Error: GOTO label {label} not defined")
        
        elif line.startswith("SET"):
            parts = line.split()
            if parts[2].startswith("#"):
                parts[2] = parts[2].split("#")[1]
                command_surface[y][x] = component.CommandBlock(f"/scoreboard players set REG {parts[1].replace(',', '')} {parts[2].replace(',', '')}", "" if not chained else "chain",orientation=orientation, source_line=line_number, source_code=line)
            else:
                command_surface[y][x] = component.CommandBlock(f"/scoreboard players operation REG {parts[1].replace(',', '')} = REG {parts[2].replace(',', '')}", "" if not chained else "chain",orientation=orientation, source_line=line_number, source_code=line)

            print(f"Processed SET: {parts[1].replace(',', '')} = {parts[2].replace(',', '')}")

        elif line.startswith("TAG"):
            parts = line.split()
            target_y, target_x = self.goto[parts[1].replace(":", "")]
            command_surface[y][x] = component.CommandBlock(f"execute as @e[type=armor_stand,tag=temp_destination] run tp @s ~{target_y-y} ~1 ~{target_x-x}", "" if not chained else "chain",orientation=orientation, source_line=line_number, source_code=line)
            print(f"TAG found: {parts[1].replace(':', '')} at ({target_y}, {target_x})")
        
        elif line.startswith("SLF"):
            target_y, target_x = self.predict_pos(x,y,2,orientation,command_surface)
            command_surface[y][x] = component.CommandBlock(f"execute as @e[type=armor_stand,tag=temp_origin] run tp @s ~{target_y-y} ~1 ~{target_x-x}", "" if not chained else "chain",orientation=orientation, source_line=line_number, source_code=line)

        elif line.startswith("CALL"):
            command_surface[y][x] = component.CommandBlock(f"setblock ~{1-y} ~1 ~{1-x} minecraft:redstone_block", "" if not chained else "chain",orientation=orientation, source_line=line_number, source_code=line)
            self.temp = False

        elif line.startswith("RET"):
            command_surface[y][x] = component.CommandBlock(f"setblock ~{2-y} ~1 ~{0-x} minecraft:redstone_block", "" if not chained else "chain",orientation=orientation, source_line=line_number, source_code=line)

        elif line.startswith("IF"):
            parts = line.split()
            self.last_parts = parts
            op = parts[2]
            target_y, target_x = self.goto[parts[4].replace(":", "")]
            match op:
                case ">":
                    command_surface[y][x] = component.CommandBlock(f"execute if score REG {parts[1].replace(',', '')} > REG {parts[3].replace(',', '')} run setblock ~{target_y-y} ~1 ~{target_x-x} minecraft:redstone_block", "" if not chained else "chain",orientation=orientation, source_line=line_number, source_code=line)
                case "<":
                    command_surface[y][x] = component.CommandBlock(f"execute if score REG {parts[1].replace(',', '')} < REG {parts[3].replace(',', '')} run setblock ~{target_y-y} ~1 ~{target_x-x} minecraft:redstone_block", "" if not chained else "chain",orientation=orientation, source_line=line_number, source_code=line)
                case "=":
                    command_surface[y][x] = component.CommandBlock(f"execute if score REG {parts[1].replace(',', '')} = REG {parts[3].replace(',', '')} run setblock ~{target_y-y} ~1 ~{target_x-x} minecraft:redstone_block", "" if not chained else "chain",orientation=orientation, source_line=line_number, source_code=line)
                case "!=":
                    command_surface[y][x] = component.CommandBlock(f"execute unless score REG {parts[1].replace(',', '')} = REG {parts[3].replace(',', '')} run setblock ~{target_y-y} ~1 ~{target_x-x} minecraft:redstone_block", "" if not chained else "chain",orientation=orientation, source_line=line_number, source_code=line)
                case "<=":
                    command_surface[y][x] = component.CommandBlock(f"execute if score REG {parts[1].replace(',', '')} <= REG {parts[3].replace(',', '')} run setblock ~{target_y-y} ~1 ~{target_x-x} minecraft:redstone_block", "" if not chained else "chain",orientation=orientation, source_line=line_number, source_code=line)
                case ">=":
                    command_surface[y][x] = component.CommandBlock(f"execute if score REG {parts[1].replace(',', '')} >= REG {parts[3].replace(',', '')} run setblock ~{target_y-y} ~1 ~{target_x-x} minecraft:redstone_block", "" if not chained else "chain",orientation=orientation, source_line=line_number, source_code=line)
                case _:
                    AssertionError(f"Unknown operator: {op}")
            print(f"Processed IF: {parts[1].replace(',', '')} {op} {parts[3].replace(',', '')} GOTO {parts[4].replace(':', '')}")
        
        elif line.startswith("ELSE"):
            target_y, target_x = self.predict_pos(x,y,1,orientation,command_surface)
            parts = self.last_parts
            op = parts[2]
            if op == ">":
                command_surface[y][x] = component.CommandBlock(f"execute unless score REG {parts[1].replace(',', '')} > REG {parts[3].replace(',', '')} run setblock ~{target_y-y} ~1 ~{target_x-x} minecraft:redstone_block", "" if not chained else "chain",orientation=orientation, source_line=line_number, source_code=line)
            elif op == "<":
                command_surface[y][x] = component.CommandBlock(f"execute unless score REG {parts[1].replace(',', '')} < REG {parts[3].replace(',', '')} run setblock ~{target_y-y} ~1 ~{target_x-x} minecraft:redstone_block", "" if not chained else "chain",orientation=orientation, source_line=line_number, source_code=line)
            elif op == "=":
                command_surface[y][x] = component.CommandBlock(f"execute unless score REG {parts[1].replace(',', '')} = REG {parts[3].replace(',', '')} run setblock ~{target_y-y} ~1 ~{target_x-x} minecraft:redstone_block", "" if not chained else "chain",orientation=orientation, source_line=line_number, source_code=line)
            elif op == "!=":
                command_surface[y][x] = component.CommandBlock(f"execute if score REG {parts[1].replace(',', '')} = REG {parts[3].replace(',', '')} run setblock ~{target_y-y} ~1 ~{target_x-x} minecraft:redstone_block", "" if not chained else "chain",orientation=orientation, source_line=line_number, source_code=line)
            elif op == "<=":
                command_surface[y][x] = component.CommandBlock(f"execute unless score REG {parts[1].replace(',', '')} <= REG {parts[3].replace(',', '')} run setblock ~{target_y-y} ~1 ~{target_x-x} minecraft:redstone_block", "" if not chained else "chain",orientation=orientation, source_line=line_number, source_code=line)
            elif op == ">=":
                command_surface[y][x] = component.CommandBlock(f"execute unless score REG {parts[1].replace(',', '')} >= REG {parts[3].replace(',', '')} run setblock ~{target_y-y} ~1 ~{target_x-x} minecraft:redstone_block", "" if not chained else "chain",orientation=orientation, source_line=line_number, source_code=line)
            self.temp = False
        elif line.startswith("CLR"):
            command_surface[y][x] = component.CommandBlock(f"setblock ~ ~1 ~ minecraft:air", "" if not chained else "chain",orientation=orientation, source_line=line_number, source_code=line)
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
                command_surface[y][x] = component.CommandBlock(command, "" if not chained else "chain",orientation=orientation, source_line=line_number, source_code=line)
                print(f"Processed SAY: {" ".join(parts[1:])}")
            else:
                AssertionError("SAY command requires a message")
        
        elif line.startswith("DIV"):
            parts = line.split()
            if parts[2].startswith("#"):
                AssertionError("DIV command does not support immediate values")
            else:
                command_surface[y][x] = component.CommandBlock(f"/scoreboard players operation REG {parts[1].replace(',', '')} /= REG {parts[2].replace(',', '')}", "" if not chained else "chain",orientation=orientation, source_line=line_number, source_code=line)
            print(f"Processed DIV: {parts[1].replace(',', '')} / {parts[2].replace(',', '')}")
        
        elif line.startswith("VAR"):
            parts = line.split()
            if len(parts) != 2:
                AssertionError("VAR command requires a variable name")
            var_name = parts[1].replace(",", "")
            command_surface[y][x] = component.CommandBlock(f"/scoreboard objectives add {var_name} dummy", "" if not chained else "chain",orientation=orientation, source_line=line_number, source_code=line)
            print(f"Processed VAR: {var_name}")
        
        else:
            AssertionError(f"Unknown command: {line}")
        
        return True
    

    def predict_pos(self, x, y, offset, orientation, command_surface):
        """
        Predict the next position based on current coordinates and movement.
        Uses advance_position method directly for consistency.
        
        Args:
            x: Current x position
            y: Current y position
            offset: Number of steps to move forward
            orientation: Current direction ('south' = moving right, 'north' = moving left)
            command_surface: The 2D grid of command blocks
        
        Returns:
            tuple: (predicted_y, predicted_x)
        """
        # Direction: 1 = moving right (east), -1 = moving left (west)
        mod = 1 if orientation == "south" else -1
        
        print(f"Predicting from ({y}, {x}), offset={offset}, direction={'→' if mod == 1 else '←'}")
        
        # Use advance_position for each step to ensure exact consistency
        for step in range(offset):
            x, y, mod, orientation, wrap_pos = self.advance_position(x, y, mod, command_surface)
            
            if wrap_pos:
                x+=mod
                print(f"  Step {step + 1}: Wrapped to new line ({y}, {x}), new direction={'→' if mod == 1 else '←'}")
            else:
                print(f"  Step {step + 1}: Moved to ({y}, {x})")
        
        print(f"Final predicted position: ({y}, {x})")
        return y, x

    def compile_script(self, script, output_file, stack_size=15, regex_size=8, display=False):
        """Main compilation function."""
        print(f"Compiling script with {len(script)} lines...")
        mod = 1

        # Setup memory and registers
        command_surface, x, y = self.setup_memory(stack_size, regex_size)
        
        # First pass: find labels
        self.find_labels(script, command_surface,x,y)
        orientation = "south"  # Initial orientation   
        # Second pass: compile commands
        chained = True
        self.temp = True
        index = 0
        
        for line in script:
            if not line.strip():  # Skip empty lines
                continue
                
            # try:
            self.compile_line(line, command_surface, x, y, chained, orientation=orientation, line_number=index+1)
            
            # Advance position
            result = self.advance_position(x, y, mod, command_surface)
            x, y, mod, orientation, wrap_pos = result
            
            # Handle rotation blocks at line wrap
            if wrap_pos:
                turn_x, turn_y = wrap_pos
                # Place rotation block on previous line at turn position
                command_surface[turn_y][turn_x] = component.CommandBlock("", orientation="east")
                # Place directional block on new line at same x position
                command_surface[y][turn_x] = component.CommandBlock("", orientation=orientation)
                # Now advance x by one step in the new direction
                print(f"Line wrap at y={y}, turn_x={turn_x}")
                x += mod

            # Update chaining state
            if not chained:
                chained = True
                print(f"Chained set to True at line {index}")
            if not self.temp:
                self.temp = True
                chained = False
                    
            # except Exception as e:
            #     print(f"Error compiling line {index + 1}: '{line}' - {e}")
            #     print(x,y,a,b)
            #     sys.exit(1)
                
            index += 1
        
        # Export and display
        component.export_to_schematic(command_surface, output_file)
        if display:
            component.display_command_block(command_surface, script_lines=script)
        
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
    
    # try:
    compiler.compile_script(
        script, 
        args.output, 
        stack_size=args.stack_size, 
        regex_size=args.register_size,
        display=args.display
    )
    # except KeyboardInterrupt:
    #     print("\nCompilation interrupted by user.")
    #     sys.exit(1)
    # except Exception as e:
    #     print(f"Compilation failed: {e}")
    #     sys.exit(1)

if __name__ == "__main__":
    main()

