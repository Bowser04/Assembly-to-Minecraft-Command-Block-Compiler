from consts import *
from context import CompilerContext
from parser import parse_source_code

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
    return (x, y0, z, orientation)

def compiler_main(source_code):
    instruction_list,ctx = parse_source_code(source_code)
    print(f"Total Instructions Parsed: {len(instruction_list)}")
    for id_instr, instr in instruction_list:
        coord = ID_to_coord(id_instr)
        print(f"ID: {id_instr}, Coord: {coord}, Instruction: {instr.__class__.__name__}, Args: {instr.args}")

if __name__ == "__main__":
    sample_code = open("sample.asm").read()
    compiler_main(sample_code)