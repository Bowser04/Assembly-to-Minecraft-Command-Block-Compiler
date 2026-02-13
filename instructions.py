from consts import *
class Instruction:
    def __init__(self, raw_args):
        self.args = raw_args

    def generate(self, current_id, context):
        """Retourne une liste de commandes Minecraft (str)"""
        raise NotImplementedError()

class CmdMov(Instruction):
    pass
class CmdAdd(Instruction):
    pass
class CmdSub(Instruction):
    pass
class CmdMul(Instruction):
    pass
class CmdDiv(Instruction):
    pass
class CmdJmp(Instruction):
    pass
class CmdLdr(Instruction):
    pass
class CmdStr(Instruction):
    pass
class CmdBEQ(Instruction):
    pass
class CmdBNE(Instruction):
    pass
class CmdBGT(Instruction):
    pass
class CmdBLT(Instruction):
    pass
class CmdMOD(Instruction):
    pass



mapping = {
    'MOV': CmdMov,
    'ADD': CmdAdd,
    'SUB': CmdSub,
    'MUL': CmdMul,
    'DIV': CmdDiv,
    'JMP': CmdJmp,
    'LDR': CmdLdr,
    'STR': CmdStr,
    'BEQ': CmdBEQ,
    'BNE': CmdBNE,
    'BGT': CmdBGT,
    'BLT': CmdBLT,
    'MOD': CmdMOD,
}
def get_command_class(name):
    """
    Return the Instruction subclass for the given command name.
    Usage: cls = get_command_class('MOV'); inst = cls(raw_args)
    """
    try:
        return mapping[name.upper()]
    except KeyError:
        raise KeyError(f"Unknown command: {name}")