import random
from emulator import Emulator

NUM_TESTS = 1000

def test_emulator_initialization():
    results = []
    for _ in range(NUM_TESTS):
        emu = Emulator(reg_size=4)
        results.append(("add", test_add(emu)))
        results.append(("sub", test_sub(emu)))
        results.append(("mul", test_mul(emu)))
        results.append(("div", test_div(emu)))
    emu = Emulator(reg_size=4)
    results.append(("goto", test_goto(emu)))
    show_results(results)

def test_add(emu: Emulator):
    a = random.randint(1, 100)
    b = random.randint(1, 100)
    emu.execute_line(f"SET R1 #{a}")
    emu.execute_line(f"SET R2 #{b}")
    emu.execute_line("ADD R1 R2")
    return emu.REGISTERS['R1'] == a + b

def test_sub(emu: Emulator):
    a = random.randint(1, 100)
    b = random.randint(1, 100)
    emu.execute_line(f"SET R1 #{a}")
    emu.execute_line(f"SET R2 #{b}")
    emu.execute_line("SUB R1 R2")
    return emu.REGISTERS['R1'] == a - b

def test_mul(emu: Emulator):
    a = random.randint(1, 100)
    b = random.randint(1, 100)
    emu.execute_line(f"SET R1 #{a}")
    emu.execute_line(f"SET R2 #{b}")
    emu.execute_line("MUL R1 R2")
    return emu.REGISTERS['R1'] == a * b

def test_div(emu: Emulator):
    a = random.randint(1, 100)
    b = random.randint(1, 100)
    # Avoid division by zero
    b = b if b != 0 else 1
    emu.execute_line(f"SET R1 #{a}")
    emu.execute_line(f"SET R2 #{b}")
    emu.execute_line("DIV R1 R2")
    return emu.REGISTERS['R1'] == a // b

def test_goto(emu: Emulator):
    script = """SET R1 #0
GOTO :LABEL1
SET R1 #1
:LABEL1"""
    emu.execute_script(script)
    return emu.REGISTERS['R1'] == 0


def show_results(results):
    op_results = {"add": [], "sub": [], "mul": [], "div": [], "goto": []}
    for op, result in results:
        op_results[op].append(result)
    total = len(results)
    passed = sum(result for _, result in results)
    print(f"Total tests: {total}, Passed: {passed}, Accuracy: {passed/total:.2%}")
    for op in op_results:
        op_total = len(op_results[op])
        op_passed = sum(op_results[op])
        print(f"{op.upper()} - Tests: {op_total}, Passed: {op_passed}, Accuracy: {op_passed/op_total:.2%}")

if __name__ == "__main__":
    test_emulator_initialization()
    print("All tests completed.")