# Assembly to Minecraft Command Block Compiler

[![Star History Chart](https://api.star-history.com/svg?repos=Bowser04/Assembly-to-Minecraft-Command-Block-Compiler&type=Date)](https://www.star-history.com/#Bowser04/Assembly-to-Minecraft-Command-Block-Compiler&Date)

> **⚠️ Development Status**: This project is currently under active development. Features and syntax may change.

A Python-based toolkit for compiling custom assembly language into Minecraft command blocks, now featuring a modular precompiler and emulator with CLI support.

## Showcase Video

[![Showcase Video](showcase.mp4)](showcase.mp4)

## Features

- **Custom Assembly Language**: Arithmetic, flow control, memory management
- **Precompiler**: Converts `.sasm` scripts to `.asm` format for advanced macro and control flow support
- **Emulator**: Simulates assembly execution in Python for rapid testing
- **Command Line Interface**: Both precompiler and emulator are now CLI tools
- **WorldEdit Integration**: Export to `.schem` files for Minecraft
- **Stack & Register System**: Configurable stack/register sizes

## Installation

```bash
pip install matplotlib numpy mcschematic
```

## File Structure

```
Assembly-to-Minecraft-Command-Block-Compiler
├── asm_compiler.py      # Main compiler
├── asm_precompiler.py   # Precompiler
├── emulator.py          # Emulator
├── exponential.sasm     # Example source (precompiled)
├── exponential.asm      # Example output (compiled)
├── README.md            # This file
```

## Precompiler Usage


The precompiler transforms `.sasm` files into `.asm` files, expanding macros and control flow. It is now implemented as a class with CLI arguments:

### CLI Arguments

- `--input`: Source `.sasm` file (required)
- `--output`: Destination `.asm` file (required)
- `--registers`: Number of registers for the emulator (optional, default: 10)
- `--emulate`: Run the emulator after precompiling (optional)

### Example CLI Usage

```bash
python asm_precompiler.py --input exponential.sasm --output temp.asm --registers 10 --emulate
```

## Emulator Usage


The emulator simulates the execution of `.asm` files. It is now implemented as a class with CLI arguments:

### CLI Arguments

- `--input`: Source `.asm` file (required)
- `--registers`: Number of registers (optional, default: 8)

### Example CLI Usage

```bash
python emulator.py --input temp.asm --registers 10
```

## Example Workflow

1. **Precompile**: Convert your `.sasm` to `.asm`
   ```bash
   python asm_precompiler.py --input exponential.sasm --output temp.asm --registers 10
   ```
2. **Emulate**: Run the `.asm` file in the emulator
   ```bash
   python emulator.py --input temp.asm --registers 10
   ```
3. **Compile**: Use `asm_compiler.py` to generate Minecraft schematics
   ```bash
   python asm_compiler.py temp.asm -o output.schem
   ```

## Example `.sasm` and `.asm` Files

See `exponential.sasm` and `exponential.asm` for sample scripts.

---

## Custom Assembly Language Syntax

Your `.sasm` source files use a custom assembly language for arithmetic, flow control, and memory operations. Below are the main commands and their usage in `.sasm` files:

### Registers & Values
- Registers are named `R0`, `R1`, ..., `Rn`.
- Immediate values are prefixed with `#` (e.g., `#10`).

### Commands

| Command      | Syntax                              | Description                                 |
|------------- |-------------------------------------|---------------------------------------------|
| SET          | SET R0, #5                          | Set register R0 to value 5                  |
| ADD          | ADD R0, #2 / ADD R0, R1             | Add value/register to R0                    |
| SUB          | SUB R0, #1 / SUB R0, R1             | Subtract value/register from R0             |
| MUL          | MUL R0, R1                          | Multiply R0 by register                     |
| DIV          | DIV R0, R1                          | Integer divide R0 by register               |
| SAY          | SAY "text {R0}"                     | Print text, `{R0}` replaced by register     |
| CALL         | CALL :LABEL                         | Call a function at label                    |
| RET          | RET                                 | Return from function                        |
| IF           | IF R0 = R1 :LABEL                   | Conditional jump to label                   |
| GOTO         | GOTO :LABEL                         | Unconditional jump to label                 |
| :LABEL       | :LABEL                              | Define a label                              |
| --           | -- comment                          | Line comment                                |

### Example

```sasm
SAY "Starting exponential calculations"
SET R0, #3
SET R1, #10
CALL :POWER_FUNC
SAY "{R0}"
:POWER_FUNC
   SET R2 R0
   SUB R1, #1
   SET R3 #0
   GOTO :POWER_LOOP
:POWER_LOOP
   MUL R2, R0
   SUB R1, #1
   IF R1 = R3 :POWER_RETURN
   GOTO :POWER_LOOP
:POWER_RETURN
   SET R0, R2
   RET
```

---

## License
MIT
This project is open source. Feel free to modify, fork and distribute.

## Emulator

An in-repo emulator (`emulator.py`) lets you run and debug assembly code quickly without generating command blocks.

