import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
from mcschematic import MCSchematic
import mcschematic

class CommandBlock:
    def __init__(self, command, command_type="chain"):
        self.command = command
        self.type = command_type

def display_command_block(command_block_matrix):
    '''Displays the command block matrix 2d on a plot.'''
    rows = len(command_block_matrix)
    cols = len(command_block_matrix[0])
    
    # Calculate figure size to maintain 1:1 aspect ratio for blocks (reduced by 2)
    fig, ax = plt.subplots(figsize=(cols/2, rows/2))
        
    # Create a grid to visualize the command blocks
    grid = np.zeros((rows, cols))
    
    for i in range(rows):
        for j in range(cols):
            if command_block_matrix[i][j] is not None:
                grid[i][j] = 1
    
    # Display the grid with 1:1 aspect ratio
    ax.imshow(grid, cmap='gray', aspect='equal')
    
    # Add borders around command blocks
    for i in range(rows):
        for j in range(cols):
            if command_block_matrix[i][j] is not None:
                # Create a rectangle border around the block
                rect = Rectangle((j-0.5, i-0.5), 1, 1, linewidth=2, 
                               edgecolor='red', facecolor='none')
                ax.add_patch(rect)
    
    # Add text annotations for command blocks
    for i in range(rows):
        for j in range(cols):
            if command_block_matrix[i][j] is not None:
                # Get only the first word of the command
                first_word = command_block_matrix[i][j].command.split()[0]
                ax.text(j, i, first_word.replace("/", ""),
                        ha='center', va='center', fontsize=8, color='black')
    
    ax.set_title('Command Block Matrix')
    ax.set_xlabel('X Position')
    ax.set_ylabel('Y Position')
    plt.tight_layout()
    plt.show()

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
    command_surface[1][index+2] = CommandBlock("/tellraw @a {\"text\":\"Index Pile: \",\"color\":\"gold\",\"extra\":[{\"score\":{\"name\":\"#currentPileIndex\",\"objective\":\"pileIndex\"},\"color\":\"aqua\"}]}")
    index += 3

    #### initialize regex remove pile
    command_surface[2][0] = CommandBlock("setblock ~ ~1 ~ minecraft:air", "")
    index = 1
    for i in range(stack_size):
        command_surface[2][index+i] = CommandBlock(f"execute at @e[type=armor_stand,tag=pile_{i}] if score #currentPileIndex pileIndex matches {i} run tp @e[type=armor_stand,tag=temp_origin] ~ ~ ~")
    index += stack_size
    command_surface[2][index] = CommandBlock("/scoreboard players remove #currentPileIndex pileIndex 1")
    command_surface[2][index+1] = CommandBlock("execute at @e[type=armor_stand,tag=temp_origin] run setblock ~ ~ ~ minecraft:redstone_block")
    command_surface[2][index+2] = CommandBlock("execute at @e[type=armor_stand,tag=temp_origin] run setblock ~ ~ ~ minecraft:air")
    command_surface[2][index+3] = CommandBlock("/tellraw @a {\"text\":\"Index Pile: \",\"color\":\"gold\",\"extra\":[{\"score\":{\"name\":\"#currentPileIndex\",\"objective\":\"pileIndex\"},\"color\":\"aqua\"}]}")
    index += 4
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
                # Determine block type (first block is impulse, rest are chain)
                if command_block_matrix[i][j].type == "":
                    block_type = "minecraft:command_block"
                    auto = 0
                elif command_block_matrix[i][j].type == "chain":
                    block_type = "minecraft:chain_command_block"
                    auto = 1
                
                # Set command block at position with proper NBT data
                command = command_block_matrix[i][j].command.replace("'", "\\'")
                block_string = f"{block_type}[facing=south]{{Command:'{command}',auto:{auto},UpdateLastExecution:0b}}"

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