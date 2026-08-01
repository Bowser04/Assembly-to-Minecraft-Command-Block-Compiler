"""
Spatial layout and coordinate calculation for Minecraft block placement.
"""

def ID_to_coord(instruction_id: int, start_xyz: tuple[int, int, int] = (0, 0, 0), cols: int = 16) -> tuple[int, int, int, str]:
    """
    Converts an instruction ID into Minecraft coordinates (x, y, z) and orientation.
    Serpentine path layout: every row increment reverses direction along X axis.
    Returns: (x, y, z, facing_direction_string)
    """
    cols = int(cols)
    if cols <= 0:
        raise ValueError("cols must be a positive integer")

    x0, y0, z0 = start_xyz
    col = instruction_id % cols
    row = instruction_id // cols
    z = z0 + row

    if row % 2 == 0:
        x = x0 + col
        orientation_num = 0 # left to right
    else:
        x = x0 + cols - col - 1
        orientation_num = 1 # right to left

    if x == cols - 1 and row % 2 == 0:
        orientation_num = 3 # turn
    elif x == 0 and row % 2 == 1:
        orientation_num = 3 # turn

    facing = "south" if orientation_num == 0 else "north" if orientation_num == 1 else "east"
    return (x, y0, z, facing)
