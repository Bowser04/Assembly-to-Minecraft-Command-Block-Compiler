from instructions import get_command_class
from context import CompilerContext

def parse_source_code(source_code):
    ctx = CompilerContext()
    instruction_list = [] # Liste de tuples (id, InstructionObject)
    
    lines = source_code.splitlines()
    current_id = 0
    
    for line in lines:
        line = line.strip()
        # Ignorer lignes vides et commentaires
        if not line or line.startswith(';'):
            continue
            
        # 1. Gestion des Labels (ex: "START:")
        if line.endswith(':'):
            label_name = line[:-1]
            ctx.add_label(label_name, current_id)
            continue
            
        # 2. Parsing des instructions
        parts = line.split()
        opcode = parts[0].upper()
        args = parts[1:]

        # check if ; is in args (comment)
        if ';' in args:
            comment_index = args.index(';')
            args = args[:comment_index]
        
        instr_obj = get_command_class(opcode)(args)
            
        if instr_obj:
            instruction_list.append((current_id, instr_obj))
            current_id += 1
        else:
            print(f"Attention: Impossible de créer l'instruction pour '{line}'")
            
    return instruction_list, ctx

# Exemple d'utilisation
if __name__ == "__main__":
    sample_code = open("sample.asm").read()
    instructions, context = parse_source_code(sample_code)
    for id_instr, instr in instructions:
        print(f"Line: {id_instr}, Instruction: {instr.__class__.__name__}, Args: {instr.args}")
    for label, id_instr in context.labels.items():
        print(f"Label: {label}, Line: {id_instr}")