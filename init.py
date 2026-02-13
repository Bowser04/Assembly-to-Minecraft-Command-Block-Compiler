from mcschematic import MCSchematic,Version as MCVersion

class BlockMatrix:
    def __init__(self,positions):
        self.Block = [[]]
        self.Positions = positions
    def add_command(self,command,row,col,attributes=None,orientation=None):
        while len(self.Block) <= row:
            self.Block.append([])
        while len(self.Block[row]) <= col:
            self.Block[row].append(None)
        nbt = attributes if attributes else {}
        nbt["Command"] = command
        propertys = "[facing=north]" if orientation == "north" else "[facing=south]" if orientation == "south" else "[facing=east]" if orientation == "east" else "[facing=west]" if orientation == "west" else ""
        self.Block[row][col] = ("minecraft:command_block"+propertys,nbt)
    def get_command(self,row,col):
        if row < len(self.Block) and col < len(self.Block[row]):
            return self.Block[row][col][1]["Command"]
        assert False, "Index out of range for CommandMatrix"
    def add_block(self,block,row,col,attributes=None,orientation=None):
        while len(self.Block) <= row:
            self.Block.append([])
        while len(self.Block[row]) <= col:
            self.Block[row].append(None)
        nbt = attributes if attributes else {}
        propertys = "[facing=west]" if orientation == "facing west" else "[facing=east]" if orientation == "facing east" else ""
        block = f"{block}{propertys}"
        if orientation:
            nbt["Rotation"] = orientation
        self.Block[row][col] = (block,nbt)
    def get_block(self,row,col):
        if row < len(self.Block) and col < len(self.Block[row]):
            return self.Block[row][col]
        assert False, "Index out of range for CommandMatrix"

class CodeBlockMatrix(BlockMatrix):
    def add_next_to_command(self,command,attributes=None):
        row = len(self.Block) - 1
        col = 0
        while col < len(self.Block[row]) and self.Block[row][col] is not None:
            col += 1
        if col >= 9:
            row += 1
            col = 0
        self.add_command(command,(row,col),attributes)

class Architecture:
    def __init__(self,stack_size,memory_size):
        self.stack_size = stack_size
        stack_rows = stack_size // 9 + (1 if stack_size % 9 != 0 else 0)
        memory_rows = memory_size // 9 + (1 if memory_size % 9 != 0 else 0)
        self.memory_size = memory_size
        self.stack_lenght = 9
        self.memory_lenght = 9
        self.program_lenght = 9
        self.stack = BlockMatrix((0,0,0))
        # for i in range(stack_rows):
        #     for j in range(9):
        #         if i*9 + j < stack_size:
        #             self.stack.add_block("minecraft:barrel",i,j)
        self.memory = BlockMatrix((0,0,stack_rows+1))
        # for i in range(memory_rows):
        #     for j in range(9):
        #         if i*9 + j < memory_size:
        #             self.memory.add_block("minecraft:barrel",i,j)
        self.program = CodeBlockMatrix((10,0,0))
        # for i in range(11):
        #     for j in range(9):
        #         self.program.add_command("Empty Program Slot",i,j)
    def export_schematic(self,filename):
        schematic = MCSchematic()
        for matrix in [self.stack, self.memory, self.program]:
                    for i, row in enumerate(matrix.Block):
                        for j, block in enumerate(row):
                            if block:
                                x = matrix.Positions[0] + j
                                y = matrix.Positions[1]
                                z = matrix.Positions[2] + i
                                # Construct blockData string with NBT data if present
                                block_type = block[0]
                                nbt_data = block[1]
                                if nbt_data:
                                    # Simple NBT serialization for the example, assuming MCSchematic handles complex strings or we format it here
                                    # However, based on the prompt showing setBlock takes a string, we need to format it.
                                    # The previous code passed block[0] and block[1] separately, which seems incorrect based on the doc provided.
                                    # Let's format it as "block_id{nbt}"
                                    nbt_str = str(nbt_data).replace("'", '"') # Basic JSON-like conversion for NBT
                                    block_data = f"{block_type}{nbt_str}"
                                else:
                                    block_data = block_type
                                
                                schematic.setBlock((x, y, z), block_data)
        filefolder = filename.rsplit('/',1)[0] if '/' in filename else '.'
        filename = filename.rsplit('/',1)[-1]
        schematic.save(filefolder, filename, MCVersion.JE_1_18_2)

if __name__ == "__main__":
    arch = Architecture(20,100)
    print(f"memory ({arch.memory.Positions}) {len(arch.memory.Block[0])}x{len(arch.memory.Block)}\nstack ({arch.stack.Positions}) {len(arch.stack.Block[0])}x{len(arch.stack.Block)}\nprogram ({arch.program.Positions}) {len(arch.program.Block[0])}x{len(arch.program.Block)}")
    arch.export_schematic("C:\\Users\\cedric\\Music\\minecraft serv\\config\\worldedit\\schematics/test")