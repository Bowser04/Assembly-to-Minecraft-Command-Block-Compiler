import consts
import context
import init
import instructions
import parser


def ID_to_coord(id, start_xyz=(0,0,0), cols=16):
    """Convertit un ID d'instruction en coordonnées Minecraft (x,y,z) et renvoie l'orientation.
    Parcours en serpent : chaque augmentation de z inverse la direction sur x.
    cols définit le nombre de colonnes par ligne (au lieu de la valeur fixe 16).
    Orientation: 0 = gauche->droite, 1 = droite->gauche
    """
    cols = int(cols)
    if cols <= 0:
        raise ValueError("cols must be a positive integer")
    x0, y0, z0 = start_xyz
    col = id % cols
    row = id // cols
    z = z0 + row
    if row % 2 == 0:
        x = x0 + col
        orientation = 0
    else:
        x = x0 + cols -col-1
        orientation = 1
    if x == cols -1 and row %2 ==0:
        orientation = 3
    elif x ==0 and row %2 ==1:
        orientation = 3
    return (x, y0, z, orientation)

def compiler_main(source_code,architecture:init.Architecture):
    instruction_list,ctx = parser.parse_source_code(source_code)
    cols = architecture.program_lenght
    start_pos = architecture.program.Positions
    offset = init_reg(REG_SIZE,architecture.program,cols)
    print(f"Total Instructions Parsed: {len(instruction_list)}")
    # for id_instr, instr in instruction_list:
    #     coord = ID_to_coord(id_instr+offset,cols=cols)
    #     print(f"ID: {id_instr+offset}, Coord: {coord}, Instruction: {instr.__class__.__name__}, Args: {instr.args}")
    #     architecture.program.add_command("Placeholder",*coord[:2])  # Placeholder for actual instruction compilation
    return instruction_list

def init_reg(size,program:init.BlockMatrix,cols):
    for i in range(0,size*2,2):
        row,_,col,orientation = ID_to_coord(i,cols=cols)
        print(f"Creating Reg {i//2} at ({col},{row})")
        orientation = "south" if orientation == 0 else "north" if orientation == 1 else "east"
        program.add_command(f"/scoreboard objectives add R{i//2} dummy",row,col,orientation=orientation)
        row,_,col,orientation = ID_to_coord(i+1,cols=cols)
        orientation = "south" if orientation == 0 else "north" if orientation == 1 else "east"
        print(f"Setting Reg {i//2} to 0 at ({col},{row})")
        program.add_command(f"/scoreboard players set {consts.SCOREBOARD_OBJ} R{i//2} 0",row,col,orientation=orientation)
        print(f"Init Reg {i//2} at ({col},{row})")
    return size*2



REG_SIZE = 20
STACK_SIZE = 20
MEMORY_SIZE = 100
code = open("sample.asm").read()
architecture = init.Architecture(STACK_SIZE,MEMORY_SIZE)
parsed_code = compiler_main(code,architecture)
architecture.export_schematic("C:\\Users\\cedric\\Music\\minecraft serv\\config\\worldedit\\schematics/test")
