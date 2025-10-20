# Assembly to Minecraft Command Block Compiler

[![Star History Chart](https://api.star-history.com/svg?repos=Bowser04/Assembly-to-Minecraft-Command-Block-Compiler&type=date&legend=top-left)](https://www.star-history.com/#Bowser04/Assembly-to-Minecraft-Command-Block-Compiler&type=date&legend=top-left)

> **⚠️ Development Status**: This project is currently under active development. Features and syntax may change.

A Python-based toolkit for compiling custom assembly language into Minecraft command blocks, featuring a modular precompiler, emulator, interactive debugger, and visual command block viewer.

## Showcase Video

currently broken sorry
you can check 
showcase.mp4 in the repo



## Features

- **Custom Assembly Language**: Arithmetic, flow control, memory management, function calls
- **Precompiler**: Converts `.sasm` scripts to `.asm` format with macro and control flow expansion
- **Emulator**: Fast Python-based simulation for testing assembly code
- **Interactive Debugger**: GUI debugger with step-by-step execution, breakpoints, and register inspection
- **Visual Command Block Viewer**: Interactive Tkinter UI showing compiled command blocks with:
  - Click-to-explore navigation between assembly code and command blocks
  - Flow visualization with colored arrows (red arrows highlight abnormal flows)
  - Syntax highlighting and line-to-block mapping
- **WorldEdit Integration**: Export to `.schem` files for direct import into Minecraft
- **Stack & Register System**: Configurable stack/register sizes with function call support
- **Command Line Interface**: Full CLI support for all tools

## Installation

```bash
pip install matplotlib numpy mcschematic
```

## File Structure

```
Assembly-to-Minecraft-Command-Block-Compiler
├── asm_compiler.py      # Main compiler - converts .asm to Minecraft schematics
├── asm_precompiler.py   # Precompiler - expands .sasm macros to .asm
├── emulator.py          # Emulator - simulates assembly execution
├── debugger.py          # Interactive GUI debugger with step execution
├── component.py         # Command block components and visual viewer
├── test_asm/            # Example .asm files
│   ├── exponential.asm
│   ├── exponential_lib_call.asm
│   └── libs/            # Library functions
├── test_sasm/           # Example .sasm source files
│   ├── exponential.sasm
│   └── exponential_lib_call.sasm
├── test_emu.py          # Emulator test suite
└── README.md            # This file
```

## Usage

### Compiler

The main compiler converts `.asm` files into Minecraft WorldEdit schematics (`.schem`).

#### CLI Arguments

```bash
python asm_compiler.py input.asm [options]
```

**Options:**
- `-o, --output`: Output schematic file (default: `command_blocks.schem`)
- `-s, --stack-size`: Stack size for memory setup (default: 15)
- `-r, --register-size`: Number of registers to create (default: 8)
- `--display`: Display interactive command block viewer after compilation
- `-v, --verbose`: Enable verbose output

#### Examples

```bash
# Basic compilation
python asm_compiler.py test_asm/exponential.asm

# Custom output and settings
python asm_compiler.py test_asm/exponential.asm -o my_program.schem -s 20 -r 16

# Compile and view in interactive UI
python asm_compiler.py test_asm/exponential.asm --display
```

### Precompiler

The precompiler transforms `.sasm` files into `.asm` files, expanding macros and control flow.

#### CLI Arguments

```bash
python asm_precompiler.py --input source.sasm --output dest.asm [options]
```

**Options:**
- `--input`: Source `.sasm` file (required)
- `--output`: Destination `.asm` file (required)
- `--registers`: Number of registers (default: 10)
- `--emulate`: Run the emulator after precompiling

#### Examples

```bash
# Basic precompilation
python asm_precompiler.py --input test_sasm/exponential.sasm --output temp.asm

# Precompile and emulate
python asm_precompiler.py --input test_sasm/exponential.sasm --output temp.asm --emulate
```

### Emulator

The emulator simulates assembly execution without generating command blocks.

#### CLI Arguments

```bash
python emulator.py --input program.asm [options]
```

**Options:**
- `--input`: Source `.asm` file (required)
- `--registers`: Number of registers (default: 8)

#### Examples

```bash
# Run emulator
python emulator.py --input test_asm/exponential.asm --registers 10
```

### Debugger

The debugger provides an interactive GUI for step-by-step execution with breakpoints and register inspection.

```bash
python debugger.py
```

Then load your `.asm` file through the GUI to:
- Set breakpoints
- Step through code line by line
- Inspect register values in real-time
- View output as it's generated

## Complete Workflow Example

```bash
# 1. Write your program in .sasm format
# 2. Precompile to .asm
python asm_precompiler.py --input test_sasm/exponential.sasm --output temp.asm

# 3. Test with emulator
python emulator.py --input temp.asm --registers 10

# 4. Debug if needed
python debugger.py  # Load temp.asm in GUI

# 5. Compile to Minecraft schematic with visual viewer
python asm_compiler.py temp.asm -o output.schem --display

# 6. Import output.schem into Minecraft using WorldEdit
```

## Example Files

See the `test_sasm/` and `test_asm/` directories for sample programs demonstrating various features.

---

## Custom Assembly Language Syntax

Your `.sasm` source files use a custom assembly language for arithmetic, flow control, and memory operations. Below are the main commands and their usage in `.sasm` files:

### Registers & Values
- Registers are named `R0`, `R1`, ..., `Rn`.
- Immediate values are prefixed with `#` (e.g., `#10`).

### Commands

| Command      | Syntax                              | Description                                 |
|------------- |-------------------------------------|---------------------------------------------|
| **Arithmetic & Data** |                           |                                             |
| SET          | `SET R0, #5` / `SET R0, R1`        | Set register R0 to value or another register |
| ADD          | `ADD R0, #2` / `ADD R0, R1`        | Add value/register to R0                    |
| SUB          | `SUB R0, #1` / `SUB R0, R1`        | Subtract value/register from R0             |
| MUL          | `MUL R0, R1`                        | Multiply R0 by register                     |
| DIV          | `DIV R0, R1`                        | Integer divide R0 by register               |
| VAR          | `VAR myVar`                         | Declare a variable/objective                |
| **Output** |                                     |                                             |
| SAY          | `SAY "text {R0}"`                   | Print text, `{R0}` replaced by register value |
| SHOW         | `SHOW R0`                           | Display register value                      |
| **Control Flow** |                               |                                             |
| :LABEL       | `:LABEL`                            | Define a label for jumps/calls              |
| GOTO         | `GOTO :LABEL`                       | Unconditional jump to label                 |
| IF           | `IF R0 = R1 :LABEL`                 | Conditional jump (supports =, !=, <, >, <=, >=) |
| ELSE         | `ELSE`                              | Execute if previous IF was false            |
| **Functions** |                                    |                                             |
| CALL         | `CALL :FUNCTION`                    | Call a function at label (uses stack)       |
| RET          | `RET`                               | Return from function                        |
| TAG          | `TAG :LABEL`                        | Tag destination for return                  |
| SLF          | `SLF`                               | Set self reference                          |
| **Utility** |                                     |                                             |
| CLR          | `CLR`                               | Clear current block                         |
| --           | `-- comment`                        | Line comment (ignored)                      |

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

## Visual Command Block Viewer

When using the `--display` flag with the compiler, an interactive Tkinter UI opens showing:

### Features
- **Interactive Grid**: Click on command blocks to see details
- **Assembly Code Panel**: View original assembly code side-by-side
- **Bidirectional Navigation**: Click assembly lines to highlight corresponding blocks, or click blocks to see source code
- **Flow Visualization**: 
  - Brown arrows: Normal impulse block jumps
  - Cyan arrows: Normal chain block flow
  - **Red arrows**: Abnormal flow (pointing to chain blocks - potential issues)
- **Block Information**: Hover/click for full command details, line numbers, and coordinates
- **Color Coding**:
  - Brown blocks: Impulse command blocks
  - Green blocks: Chain command blocks

This viewer helps you understand and debug your compiled command block structure before importing into Minecraft.

---

## Architecture

The compiler uses a "snake pattern" layout for command blocks:
- Line 1: Left → Right
- Line 2: Right → Left (reversed)
- Line 3: Left → Right (reversed)
- And so on...

This creates efficient execution chains while maintaining spatial locality. Rotation blocks are automatically placed at line boundaries to maintain signal flow.

---

## License

MIT

This project is open source. Feel free to modify, fork and distribute.

---

## Contributing

Contributions are welcome! Areas for improvement:
- Additional assembly instructions
- Optimization passes
- Better error messages
- More example programs
- Documentation improvements

