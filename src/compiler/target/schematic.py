"""
Exporting Architecture block matrices into Minecraft WorldEdit .schem files using mcschematic.
"""

import os
from mcschematic import MCSchematic, Version as MCVersion
from src.compiler.target.architecture import Architecture

def serialize_nbt(nbt_dict: dict) -> str:
    """
    Serializes a Python dict into valid Minecraft SNBT format.
    Ensures byte tags like auto: 0b / auto: 1b and string tags like Command: "..." are correctly formatted.
    """
    parts = []
    for key, val in nbt_dict.items():
        if isinstance(val, str) and (val.endswith('b') or val.endswith('s') or val.endswith('l')) and val[:-1].isdigit():
            # Primitive NBT byte/short/long tag (e.g., 0b, 1b)
            parts.append(f"{key}:{val}")
        elif isinstance(val, bool):
            parts.append(f"{key}:{'1b' if val else '0b'}")
        elif isinstance(val, (int, float)):
            parts.append(f"{key}:{val}")
        else:
            # String tag (e.g., Command)
            escaped_val = str(val).replace('"', '\\"')
            parts.append(f'{key}:"{escaped_val}"')
    return "{" + ",".join(parts) + "}"

def export_schematic(architecture: Architecture, output_filepath: str) -> str:
    """
    Exports the stack, memory, and program block matrices of an Architecture to a .schem file.
    """
    schematic = MCSchematic()

    for matrix in [architecture.stack, architecture.memory, architecture.program]:
        for i, row in enumerate(matrix.Block):
            for j, block in enumerate(row):
                if block:
                    x = matrix.Positions[0] + j
                    y = matrix.Positions[1]
                    z = matrix.Positions[2] + i

                    block_type = block[0]
                    nbt_data = block[1]

                    if nbt_data:
                        nbt_str = serialize_nbt(nbt_data)
                        block_data = f"{block_type}{nbt_str}"
                    else:
                        block_data = block_type

                    schematic.setBlock((x, y, z), block_data)

    # Normalize path and directory
    output_filepath = output_filepath.replace('\\', '/')
    if '/' in output_filepath:
        filefolder, filename = output_filepath.rsplit('/', 1)
    else:
        filefolder, filename = '.', output_filepath

    os.makedirs(filefolder, exist_ok=True)
    schematic.save(filefolder, filename, MCVersion.JE_1_18_2)
    return f"{filefolder}/{filename}.schem"
