import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle, FancyArrowPatch
from mcschematic import MCSchematic
import mcschematic
import re
import tkinter as tk
from tkinter import ttk, scrolledtext

class CommandBlock:
    def __init__(self, command, command_type="chain", orientation="south", source_line=None, source_code=""):
        self.command = command
        self.type = command_type
        self.orientation = orientation  # e.g., "south", "north", etc.
        self.source_line = source_line  # Line number in assembly code
        self.source_code = source_code  # Original assembly code

def display_command_block_tk(command_block_matrix, script_lines=None):
    """Display command blocks in a Tkinter window with interactive features."""
    rows = len(command_block_matrix)
    cols = len(command_block_matrix[0])
    
    # Create main window
    root = tk.Tk()
    root.title("Assembly to Minecraft Command Block Viewer")
    root.geometry("1400x800")
    
    # Create main container
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Left panel: Command blocks visualization
    left_frame = ttk.Frame(main_frame)
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
    
    # Canvas for command blocks
    canvas_frame = ttk.Frame(left_frame)
    canvas_frame.pack(fill=tk.BOTH, expand=True)
    
    # Add scrollbars
    h_scroll = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
    h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
    v_scroll = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
    v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Canvas
    block_size = 40  # pixels per block
    canvas = tk.Canvas(canvas_frame, bg='white', 
                      xscrollcommand=h_scroll.set,
                      yscrollcommand=v_scroll.set,
                      width=800, height=600)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    h_scroll.config(command=canvas.xview)
    v_scroll.config(command=canvas.yview)
    
    # Info label at the top
    info_label = ttk.Label(left_frame, text="Click on blocks or assembly lines to explore", 
                          relief=tk.SUNKEN, padding=5)
    info_label.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))
    
    # Right panel: Assembly code (if provided)
    if script_lines:
        right_frame = ttk.Frame(main_frame, width=400)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        right_frame.pack_propagate(False)
        
        # Title
        ttk.Label(right_frame, text="Assembly Code (Click to highlight blocks)", 
                 font=('Courier', 10, 'bold')).pack(pady=5)
        
        # Text widget with scrollbar
        text_frame = ttk.Frame(right_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        text_scroll = ttk.Scrollbar(text_frame)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        code_text = tk.Text(text_frame, font=('Courier', 9), 
                           yscrollcommand=text_scroll.set,
                           bg='#f5f5f5', selectbackground='yellow',
                           wrap=tk.NONE, cursor='hand2')
        code_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_scroll.config(command=code_text.yview)
        
        # Populate assembly code
        for idx, line in enumerate(script_lines, 1):
            code_text.insert(tk.END, f"{idx:4d}  {line}\n")
        
        code_text.config(state=tk.DISABLED)
    else:
        code_text = None
    
    # Draw command blocks
    block_items = {}  # Store canvas items for each block
    arrow_items = []  # Store arrow items
    highlighted_items = []  # Store highlighted rectangles
    
    def draw_blocks():
        """Draw all command blocks on canvas."""
        canvas.delete("all")
        block_items.clear()
        arrow_items.clear()
        
        # Draw grid and blocks
        for i in range(rows):
            for j in range(cols):
                # Reverse x-coordinate (mirror horizontally)
                x1 = (cols - 1 - j) * block_size
                y1 = i * block_size
                x2 = x1 + block_size
                y2 = y1 + block_size
                
                if command_block_matrix[i][j] is not None:
                    cb = command_block_matrix[i][j]
                    
                    # Determine color based on type
                    if cb.type == "":
                        color = '#8B4513'  # Brown for impulse
                    else:
                        color = '#4CAF50'  # Green for chain
                    
                    # Draw block
                    rect = canvas.create_rectangle(x1, y1, x2, y2, 
                                                  fill=color, outline='black', 
                                                  width=2, tags=f"block_{i}_{j}")
                    
                    # Add text
                    if cb.command:
                        first_word = cb.command.split()[0].replace('/', '')[:6]
                    else:
                        # Show arrow based on orientation
                        arrow_map = {
                            "east": "↓",
                            "south": "←",
                            "north": "→",
                        }
                        first_word = arrow_map.get(cb.orientation, "→")
                    
                    text = canvas.create_text((x1+x2)/2, (y1+y2)/2, 
                                             text=first_word, 
                                             fill='white', font=('Arial', 8, 'bold'),
                                             tags=f"block_{i}_{j}")
                    
                    block_items[(i, j)] = (rect, text)
        
        # Draw arrows
        draw_arrows()
        
        # Set scroll region
        canvas.config(scrollregion=(0, 0, cols * block_size, rows * block_size))
    
    def draw_arrows():
        """Draw arrows for GOTO, CALL, RET, IF commands."""
        for i in range(rows):
            for j in range(cols):
                if command_block_matrix[i][j] is not None:
                    cb = command_block_matrix[i][j]
                    command = cb.command
                    
                    if "setblock" in command and "redstone_block" in command:
                        match = re.search(r'setblock ~(-?\d+) ~\d+ ~(-?\d+)', command)
                        if match:
                            rel_y = int(match.group(1))
                            rel_x = int(match.group(2))
                            
                            target_i = i + rel_y
                            target_j = j + rel_x
                            
                            # Check if target is a chain command block (abnormal)
                            is_abnormal = False
                            if (0 <= target_i < rows and 0 <= target_j < cols and 
                                command_block_matrix[target_i][target_j] is not None):
                                target_cb = command_block_matrix[target_i][target_j]
                                if target_cb.type == "chain":
                                    is_abnormal = True
                            
                            # Color: red if pointing to chain (abnormal), otherwise match source block
                            if is_abnormal:
                                color = '#FF0000'  # Red for abnormal flow (pointing to chain)
                            elif cb.type == "":
                                color = '#8B4513'  # Brown for impulse
                            else:
                                color = '#00CED1'  # Cyan/turquoise for chain
                            
                            # Calculate arrow coordinates (reversed x)
                            x1 = (cols - 1 - j) * block_size + block_size/2
                            y1 = i * block_size + block_size/2
                            x2 = (cols - 1 - target_j) * block_size + block_size/2
                            y2 = target_i * block_size + block_size/2
                            
                            # Draw arrow in foreground
                            arrow = canvas.create_line(x1, y1, x2, y2, 
                                                      arrow=tk.LAST, fill=color,
                                                      width=2, tags="arrow")
                            arrow_items.append(arrow)
                            canvas.tag_raise(arrow)  # Bring arrows to front
    
    def on_block_click(event):
        """Handle click on command block."""
        # Get clicked position
        x = canvas.canvasx(event.x)
        y = canvas.canvasy(event.y)
        
        # Reverse x-coordinate to get actual j position
        j = cols - 1 - int(x // block_size)
        i = int(y // block_size)
        
        if 0 <= i < rows and 0 <= j < cols and command_block_matrix[i][j] is not None:
            cb = command_block_matrix[i][j]
            
            # Update info label
            info_text = f"Position: ({i}, {j})"
            if cb.source_line:
                info_text += f" | Line: {cb.source_line} | ASM: {cb.source_code}"
            info_text += f" | CMD: {cb.command[:60]}..."
            info_label.config(text=info_text)
            
            # Highlight block (with reversed x)
            clear_highlights()
            x1 = (cols - 1 - j) * block_size
            y1 = i * block_size
            x2 = x1 + block_size
            y2 = y1 + block_size
            highlight = canvas.create_rectangle(x1, y1, x2, y2, 
                                               outline='yellow', width=4,
                                               tags="highlight")
            highlighted_items.append(highlight)
            
            # Highlight corresponding assembly line
            if code_text and cb.source_line:
                highlight_assembly_line(cb.source_line)
            
            print(f"\n{'='*60}")
            print(f"Selected Block at ({i}, {j})")
            if cb.source_line:
                print(f"Assembly Line {cb.source_line}: {cb.source_code}")
            print(f"Command: {cb.command}")
            print(f"{'='*60}\n")
    
    def on_code_click(event):
        """Handle click on assembly code."""
        if not code_text:
            return
        
        # Get line number from click position
        index = code_text.index(f"@{event.x},{event.y}")
        line_num = int(index.split('.')[0])
        
        # Highlight assembly line
        highlight_assembly_line(line_num)
        
        # Highlight corresponding blocks
        clear_highlights()
        count = 0
        for i in range(rows):
            for j in range(cols):
                if command_block_matrix[i][j] is not None:
                    cb = command_block_matrix[i][j]
                    if cb.source_line == line_num:
                        # Reversed x-coordinate
                        x1 = (cols - 1 - j) * block_size
                        y1 = i * block_size
                        x2 = x1 + block_size
                        y2 = y1 + block_size
                        highlight = canvas.create_rectangle(x1, y1, x2, y2, 
                                                           outline='cyan', 
                                                           fill='cyan',
                                                           stipple='gray50',
                                                           width=3,
                                                           tags="highlight")
                        highlighted_items.append(highlight)
                        count += 1
        
        if count > 0:
            info_label.config(text=f"Assembly Line {line_num}: {script_lines[line_num-1].strip()} → {count} block(s)")
            print(f"Highlighted {count} command block(s) for assembly line {line_num}")
    
    def highlight_assembly_line(line_num):
        """Highlight a line in the assembly code text widget."""
        if not code_text:
            return
        
        code_text.config(state=tk.NORMAL)
        code_text.tag_remove("highlight", "1.0", tk.END)
        code_text.tag_add("highlight", f"{line_num}.0", f"{line_num}.end")
        code_text.tag_config("highlight", background="yellow", foreground="black")
        code_text.see(f"{line_num}.0")
        code_text.config(state=tk.DISABLED)
    
    def clear_highlights():
        """Clear all highlights."""
        for item in highlighted_items:
            canvas.delete(item)
        highlighted_items.clear()
    
    # Bind events
    canvas.bind("<Button-1>", on_block_click)
    if code_text:
        code_text.bind("<Button-1>", on_code_click)
    
    # Draw everything
    draw_blocks()
    
    # Legend
    legend_frame = ttk.LabelFrame(left_frame, text="Legend", padding=5)
    legend_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))
    
    ttk.Label(legend_frame, text="� Brown: Impulse Block  ", foreground="#8B4513").pack(side=tk.LEFT, padx=5)
    ttk.Label(legend_frame, text="� Green: Chain Block  ", foreground="#4CAF50").pack(side=tk.LEFT, padx=5)
    ttk.Label(legend_frame, text="� Red Arrow: Abnormal flow (pointing to chain)  ", foreground="#FF0000").pack(side=tk.LEFT, padx=5)
    ttk.Label(legend_frame, text="Other arrows show normal GOTO/CALL/IF/RET flow", foreground="gray").pack(side=tk.LEFT, padx=5)
    
    root.mainloop()

def display_command_block(command_block_matrix, script_lines=None):
    '''Displays the command block matrix using Tkinter for better interactivity.'''
    display_command_block_tk(command_block_matrix, script_lines)

def add_line(command_surface):
    '''Adds a line to the command surface.'''
    command_surface.append([None for _ in range(len(command_surface[0]))])


def memory_setup(stack_size=3):
    '''Sets up the command surface in memory.'''
    #### initialize regex
    command_surface = [[None for _ in range(40)] for _ in range(6)]
    index = 0
    command_surface[0][index]  = CommandBlock("say initializing regex ...", "")
    command_surface[0][index+1]  = CommandBlock("/kill @e[type=armor_stand,tag=temp_origin]")
    command_surface[0][index+2]  = CommandBlock("/kill @e[type=armor_stand,tag=temp_destination]")

    index += 3
    for i in range(stack_size):
        command_surface[0][i+index] = CommandBlock(f"/kill @e[type=armor_stand,tag=pile_{i}]")
    index += stack_size
    command_surface[0][index] = CommandBlock('/scoreboard objectives add pileIndex dummy "Index Pile"')
    index += 1
    for i in range(stack_size):
        command_surface[0][index+i] = CommandBlock(f"/summon minecraft:armor_stand ~ ~ ~ {{Tags:[\"pile_{i}\"],NoGravity:1b}}")
    index += stack_size-1
    command_surface[0][index+1] = CommandBlock("/scoreboard players set #currentPileIndex pileIndex -1")
    command_surface[0][index+2] = CommandBlock("""/tellraw @a {"text":"Index Pile: ","color":"gold","extra":[{"score":{"name":"#currentPileIndex","objective":"pileIndex"},"color":"aqua"}]}""")
    command_surface[0][index+3] = CommandBlock("/summon minecraft:armor_stand ~ ~ ~ {Tags:[\"temp_origin\"],NoGravity:1b}")
    command_surface[0][index+4] = CommandBlock("/summon minecraft:armor_stand ~ ~ ~ {Tags:[\"temp_destination\"],NoGravity:1b}")
    index += 5

    #### initialize regex add pile
    command_surface[1][1] = CommandBlock("setblock ~ ~1 ~ minecraft:air", "")
    index = 2
    command_surface[1][index] = CommandBlock("/scoreboard players add #currentPileIndex pileIndex 1")
    index += 1
    for i in range(stack_size):
        command_surface[1][index+i] = CommandBlock(f"execute at @e[type=armor_stand,tag=temp_origin] if score #currentPileIndex pileIndex matches {i} run tp @e[type=armor_stand,tag=pile_{i}] ~ ~ ~")
    index += stack_size
    command_surface[1][index] = CommandBlock("execute at @e[type=armor_stand,tag=temp_destination] run setblock ~ ~ ~ minecraft:redstone_block")
    command_surface[1][index+1] = CommandBlock("execute at @e[type=armor_stand,tag=temp_destination] run setblock ~ ~ ~ minecraft:air")
    #command_surface[1][index+2] = CommandBlock("/tellraw @a {\"text\":\"Index Pile: \",\"color\":\"gold\",\"extra\":[{\"score\":{\"name\":\"#currentPileIndex\",\"objective\":\"pileIndex\"},\"color\":\"aqua\"}]}")
    index += 3-1

    #### initialize regex remove pile
    command_surface[2][0] = CommandBlock("setblock ~ ~1 ~ minecraft:air", "")
    index = 1
    for i in range(stack_size):
        command_surface[2][index+i] = CommandBlock(f"execute at @e[type=armor_stand,tag=pile_{i}] if score #currentPileIndex pileIndex matches {i} run tp @e[type=armor_stand,tag=temp_origin] ~ ~ ~")
    index += stack_size
    command_surface[2][index] = CommandBlock("/scoreboard players remove #currentPileIndex pileIndex 1")
    command_surface[2][index+1] = CommandBlock("execute at @e[type=armor_stand,tag=temp_origin] run setblock ~ ~ ~ minecraft:redstone_block")
    command_surface[2][index+2] = CommandBlock("execute at @e[type=armor_stand,tag=temp_origin] run setblock ~ ~ ~ minecraft:air")
    #command_surface[2][index+3] = CommandBlock("/tellraw @a {\"text\":\"Index Pile: \",\"color\":\"gold\",\"extra\":[{\"score\":{\"name\":\"#currentPileIndex\",\"objective\":\"pileIndex\"},\"color\":\"aqua\"}]}")
    index += 4-1
    return command_surface

def export_to_schematic(command_block_matrix, filename="command_blocks.schem"):
    '''Converts the command block matrix to a WorldEdit schematic file using mcschematic.'''
    rows = len(command_block_matrix)
    cols = len(command_block_matrix[0])
    
    # Create a new schematic
    schem = MCSchematic()
    
    # Fill the schematic with command blocks
    for i in range(rows):
        for j in range(cols):
            if command_block_matrix[i][j] is not None:
                command_block = command_block_matrix[i][j]
                # Determine block type (first block is impulse, rest are chain)
                if command_block.type == "":
                    block_type = "minecraft:command_block"
                    auto = 0
                elif command_block.type == "chain":
                    block_type = "minecraft:chain_command_block"
                    auto = 1
                
                # Set command block at position with proper NBT data
                command = command_block.command.replace("'", "\\'")
                block_string = f"{block_type}[facing={command_block.orientation}]{{Command:'{command}',auto:{auto},UpdateLastExecution:0b}}"

                schem.setBlock((i, 0, j), block_string)

    # Save the schematic file
    try:
        import os
        # Extract path and filename from the filename argument
        output_path = os.path.dirname(filename)
        schem_name = os.path.basename(filename).replace(".schem", "")
        
        schem.save(outputFolderPath=output_path, schemName=schem_name, 
                  version=mcschematic.Version.JE_1_18_2)
        print(f"Schematic saved as {schem_name}.schem in {output_path}")
        return True
    except Exception as e:
        print(f"Error saving schematic: {e}")
        return False

if __name__ == "__main__":
    # Initialize the command surface
    command_surface = memory_setup(stack_size=15)

    # Display the command block matrix
    display_command_block(command_surface)

    # Export the command block matrix to a schematic file
    export_to_schematic(command_surface, "command_blocks.schem")