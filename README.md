# Assembly to Minecraft Command Block Compiler

[![Stargazers over time](https://starchart.cc/Bowser04/Assembly-to-Minecraft-Command-Block-Compiler.svg)](https://starchart.cc/Bowser04/Assembly-to-Minecraft-Command-Block-Compiler)

> **⚠️ Development Status**: This project is currently under active development. Features and syntax may change.

A Python-based compiler that converts custom assembly language into Minecraft command blocks and exports them as WorldEdit schematics.

## Features

- **Custom Assembly Language**: Support for arithmetic operations, flow control, and memory management
- **Command Line Interface**: Easy-to-use CLI with multiple configuration options  
- **Visual Output**: Display generated command block layouts using matplotlib
- **WorldEdit Integration**: Export directly to `.schem` files for use in Minecraft
- **Stack Management**: Built-in stack operations with configurable size
- **Register System**: Configurable number of registers for calculations

## Installation

### Prerequisites

```bash
pip install matplotlib numpy mcschematic
```

### File Structure
```
Assembly-to-Minecraft-Command-Block-Compiler
├── compiler.py      # Main compiler with CLI
├── component.py     # Core components and utilities
├── exponential.asm  # Example assembly program
└── README.md        # This file
```

## Usage

### Command Line Interface

```bash
# Basic compilation
python compiler.py input.asm

# Specify output file
python compiler.py input.asm -o my_output.schem

# Custom stack and register sizes
python compiler.py input.asm -s 20 -r 16

# Display command blocks after compilation
python compiler.py input.asm --display

# Verbose output
python compiler.py input.asm --verbose
```

### Arguments

| Argument | Short | Description | Default |
|----------|--------|-------------|---------|
| `input` | - | Input assembly file (.asm) | Required |
| `--output` | `-o` | Output schematic file | `command_blocks.schem` |
| `--stack-size` | `-s` | Stack size for memory setup | 15 |
| `--register-size` | `-r` | Number of registers to create | 8 |
| `--display` | - | Display command blocks after compilation | False |
| `--verbose` | `-v` | Enable verbose output | False |

## Assembly Language Reference

### Registers
- `R0` to `R7` (default) - General purpose registers
- Custom register count configurable via `-r` flag

### Commands

#### Arithmetic Operations
```
ADD R0, R1      # R0 = R0 + R1 (register addition)
ADD R0, #5      # R0 = R0 + 5 (immediate value)
SUB R0, R1      # R0 = R0 - R1
SUB R0, #3      # R0 = R0 - 3
MUL R0, R1      # R0 = R0 * R1 (registers only)
DIV R0, R1      # R0 = R0 / R1 (registers only)
SET R0, #10     # R0 = 10 (immediate value)
SET R0, R1      # R0 = R1 (register copy)
```

#### Display Commands
```
SHOW R0         # Display register value
SAY "Hello"     # Display text message
SAY "Value: {R0}"  # Display text with register interpolation
```

#### Flow Control
```
:LABEL          # Define a label
GOTO :LABEL     # Jump to label
IF R0 > R1 :LABEL   # Conditional jump (>, <, =, !=, <=, >=)
ELSE            # Execute if previous IF condition was false
CLR             # Clear top redstone block to be able to reuse save later
```

#### Stack Operations
```
TAG :LABEL      # Mark destination for stack operations
SLF             # Mark current position for stack operations
CALL            # Call subroutine/function (uses stack)
RET             # Return from subroutine/function
```

#### Utility Commands
```
VAR myVar       # Create a new variable
```

### Example Program

```
# Calculate 3^6 using recursive multiplication
SAY "Starting exponential calculations"
SET R0, #3
SET R1, #6
SAY "Result of {R0}^{R1} is:"
TAG :POWER_FUNC
SLF
CALL
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
ELSE
CLR
GOTO :POWER_LOOP

:POWER_RETURN
SET R0, R2
RET
```

## Technical Details

### Command Block Generation
- **Impulse blocks**: Used for initial commands (empty type parameter)
- **Chain blocks**: Used for sequential execution (type="chain")
- **Conditional execution**: Generated using Minecraft's `execute` command
- **Redstone activation**: Automatic block placement for flow control

### Memory Management
- **Scoreboard objectives**: Used for register storage
- **Armor stands**: Used for position tracking in stack operations
- **Dynamic sizing**: Automatic grid expansion when needed

### Export Format
- **WorldEdit schematics**: Compatible with WorldEdit plugin
- **Minecraft version**: Targets 1.18.2
- **Block positioning**: Maintains spatial relationships for proper execution

## Limitations

- MUL and DIV commands don't support immediate values (# prefix)
- Stack size is limited by block organization
- GOTO, IF and CALL are slow due to redstone activation (1 tick)

## Development

### Project Structure
- `AssemblerCompiler` class: Main compilation logic
- `CommandBlock` class: Represents individual command blocks
- `memory_setup()`: Initializes the command surface and stack
- `export_to_schematic()`: Handles WorldEdit schematic generation

### Adding New Commands
1. Add command name to `self.EX` list in `AssemblerCompiler.__init__()`
2. Implement command logic in `compile_line()` method
3. Update this README with command documentation

## Contributing

When contributing:
1. Follow existing code style and structure
2. Add appropriate error handling
3. Update documentation for new features
4. Test with sample assembly programs

Exceptions:
- If you want to reorganize/change structure of the code, ask me for agreement

## License

This project is open source. Feel free to modify, fork and distribute.
