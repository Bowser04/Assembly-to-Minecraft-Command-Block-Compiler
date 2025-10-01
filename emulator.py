import time
class Emulator:
    def __init__(self, reg_size):
        self.REGISTERS = {f"R{i}": 0 for i in range(reg_size)}
        self.STACK = []
        self.line = 0
        self.end = False
        self.labels = {}
        self.script = None
        self.target = None

    def execute_script(self, script):
        script = script.splitlines()
        self.find_labels(script)
        self.script = script
        while not self.end:
            self.execute_line(script[self.line])

    def execute_line(self, line):
        #print(f"Executing line {self.line}: {line.strip()}")
        match line.split(" ")[0]:
            case "ADD":
                self.handle_add(line)
                self.line += 1
            case "SUB":
                self.handle_sub(line)
                self.line += 1
            case "MUL":
                self.handle_mul(line)
                self.line += 1
            case "DIV":
                self.handle_div(line)
                self.line += 1
            case "SET":
                self.handle_set(line)
                self.line += 1
            case "SAY":
                self.handle_say(line)
                self.line += 1
            case "GOTO":
                time.sleep(1/20)
                self.handle_goto(line)
            case "TAG":
                self.handle_tag(line)
                self.line += 1
            case "SLF":
                self.handle_slf(line)
                self.line += 1
            case "CALL":
                time.sleep(1/20)
                self.handle_call(line)
            case "RET":
                time.sleep(1/20)
                self.handle_ret(line)
            case "IF":
                time.sleep(2/20)
                self.handle_if(line)
            case _:
                self.end=True
                
    def find_labels(self, script):
        for i, line in enumerate(script):
            if line.startswith(":"):
                label = line.split(":")[1].strip()
                self.labels[label] = i
                #print(f"Found label '{label}' at line {i}")

    def handle_add(self, line):
        _, reg1, value = line.split()
        reg1 = reg1.replace(",", "")
        if value.startswith("R"):
            self.REGISTERS[reg1] += self.REGISTERS[value]
        else:
            self.REGISTERS[reg1] += int(value.replace("#", ""))
    def handle_sub(self, line):
        _, reg1, value = line.split()
        reg1 = reg1.replace(",", "")
        if value.startswith("R"):
            self.REGISTERS[reg1] -= self.REGISTERS[value]
        else:
            self.REGISTERS[reg1] -= int(value.replace("#", ""))
    def handle_mul(self, line):
        _, reg1, value = line.split()
        reg1 = reg1.replace(",", "")
        if value.startswith("R"):
            self.REGISTERS[reg1] *= self.REGISTERS[value]
        else:
            self.REGISTERS[reg1] *= int(value.replace("#", ""))
    def handle_div(self, line):
        _, reg1, value = line.split()
        reg1 = reg1.replace(",", "")
        if value.startswith("R"):
            self.REGISTERS[reg1] //= self.REGISTERS[value]
        else:
            self.REGISTERS[reg1] //= int(value.replace("#", ""))
    def handle_set(self, line):
        _, reg, value = line.split()
        reg = reg.replace(",", "")
        if value.startswith("R"):
            self.REGISTERS[reg] = self.REGISTERS[value]
        else:
            self.REGISTERS[reg] = int(value.replace("#", ""))
    def handle_say(self, line):
        text = line.split('"')[1]
        text = text.replace("{", "ùVAR:").replace("}", "ù").split("ù")
        final_text = ""
        for i in range(len(text)):
            if text[i].startswith("VAR:"):
                var_name = text[i][len("VAR:"):]
                final_text += str(self.REGISTERS.get(var_name, 0))
            else:
                final_text += text[i]
        print(final_text)
    def handle_goto(self, line):
        _, label = line.split()
        label = label.replace(":", "")
        if label in self.labels:
            self.line = self.labels[label]+1
        else:
            raise AssertionError("Label not found")
    def handle_tag(self, line):
        _, label = line.split()
        label = label.replace(":", "")
        self.target = label
    def handle_slf(self, line):
        self.STACK.append(self.line+2)
    def handle_call(self, line):
        if self.target in self.labels:
            self.line = self.labels[self.target]+1
        else:
            raise AssertionError("Label not found")
    def handle_ret(self, line):
        if self.STACK:
            self.line = self.STACK.pop()
        else:
            raise AssertionError("Stack is empty")
    def handle_if(self, line):
        _, A, op, B, label = line.split(" ", 4)
        label = label.replace(":", "")
        res = None
        if self.script[self.line+1].startswith("ELSE") and  self.script[self.line+2].startswith("CLR"):
            if op == "=":
                res = self.REGISTERS[A] == self.REGISTERS[B]
            elif op == "!=":
                res = self.REGISTERS[A] != self.REGISTERS[B]
            elif op == "<":
                res = self.REGISTERS[A] < self.REGISTERS[B]
            elif op == "<=":
                res = self.REGISTERS[A] <= self.REGISTERS[B]
            elif op == ">":
                res = self.REGISTERS[A] > self.REGISTERS[B]
            elif op == ">=":
                res = self.REGISTERS[A] >= self.REGISTERS[B]

            if res:
                if self.labels.get(label):
                    self.line = self.labels[label] + 1
                else:
                    raise AssertionError(f"Label not found: {label} in IF line {self.line}")
            else:
                self.line += 3
        else:
            if not self.script[self.line+1].startswith("ELSE"):
                raise AssertionError("ELSE not found after IF")
            else:
                raise AssertionError("CLR not found after ELSE")

import argparse

def main():
    parser = argparse.ArgumentParser(description="Assembly Emulator")
    parser.add_argument("--input", required=True, help="Input .asm file")
    parser.add_argument("--registers", type=int, default=8, help="Number of registers")
    args = parser.parse_args()

    emulator = Emulator(args.registers)
    with open(args.input, "r") as f:
        script = f.read()
    emulator.execute_script(script)

if __name__ == "__main__":
    main()