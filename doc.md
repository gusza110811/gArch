# ASSEMBLY DOCS

## Syntax
### Prefixes
| Prefix | Use |
| --- | --- |
| `x` | Hexadecimal number |
| `b` | Binary number |
| `'` | Ascii character |
| `"` | Ascii string of character (Cannot include space, as it marks the beginning of a new word) |

### Defining

| Command | Usage|
| --- | ---
| `CONST [name] [value]` | Define `name` as `value` |
| `ALIAS [name] [value]` | Define `name` as `value` but only for this environment, other program importing will not have these definition |
| `LABEL [name]` | Define `name` as the byte address of the next command. Used for JMP/CALL etc |

Note that usage of defined `name` will be case-sensitive, but the `Command`s itself is not.

#### Misc
`.ascii [text]` -> Raw `text` encoded in ascii, can include space unlike `"` prefix
`.include [module]` -> Import `module` globally

## Virtual Hardware Specification
### I/O mode
Located at xFFF0, define the I/O state of each IO addresses (xFFF8 to xFFFF).

Least Significant (Rightmost) bit represent the state for xFFF8

0 is output mode, 1 is input mode

### The Console
Located at memory address xFFF8 , defaults to output mode.
#### Output mode:
Prints to console. prompt user input when `2` is sent, user input is saved to a buffer where it can be used elsewhere
#### Input mode:
The value at this address will be the next character in the input buffer, 'popped' from the buffer once read

### The *Numeric* Console
Located at memory address xFFF9 , Output only

Print to console as Number.

For example; If xF0 (16) as written to this address, `16` will be printed to the console

## Predefined Instruction Definitions
These are case-insensitive
| Instruction | Usage |
| --- | ---|
| **Memory** |
| `LDA [addr*2B]` | Load value at `addr` to register A |
| `LDX [addr*2B]` | Load value at `addr` to register X |
| `LDY [addr*2B]` | Load value at `addr` to register Y |
| `STA [addr*2B]` | Store value in register A to `addr` |
| `STX [addr*2B]` | Store value in register X to `addr` |
| `STY [addr*2B]` | Store value in register Y to `addr` |
| `MOV [dest-addr*2B source-addr*2B]` | Copy value from `source-addr` to `dest-addr` |
| `LDV` | Use value in register X(as hibyte) and Y(as lobyte) as memory address and from value from there to register A |
| `STV` | Use value in register X(as hibyte) and Y(as lobyte) as memory address and store value from register A to there |
| **Arithmetic** |
| `ADD` | Add register X and Y and save to register A |
| `SUB` | Subtract register X and Y and save to register A |
| `MUL` | Multiply register X and Y and save to register A |
| `DIV` | Floor Divide register X and Y and save to register A |
| **Bitwise Logic** |
| `AND` | Bitwise AND register X and Y and save to register A |
| `OR` | Bitwise OR register X and Y and save to register A |
| `XOR` | Bitwise XOR register X and Y and save to register A |
| `NOT` | Bitwise NOT register X and save to register A |
| **Flow Control** |
| `JMP [addr*2B]` | Jump to `addr` |
| `JZ [addr*2B]` | Jump to `addr` if register A is 0 |
| `JNZ [addr*2B]` | Jump to `addr` if register A is not 0 |
| `JC [addr*2B]` | Jump to `addr` if previous arithmetic resulted in overflow |
| `JNC [addr*2B]` | Jump to `addr` if previous arithmetic did not result in overflow |
| `JEQ [addr*2B]` | Jump to `addr` if register X is equal to register Y |
| `JNE [addr*2B]` | Jump to `addr` if register X is not equal to register Y |
| **Subroutine** |
| `RET` | Return from subroutine |
| `CALL [addr*2B]` | Branch to subroutine at `addr` |
| `BZ [addr*2B]` | Branch to `addr` if register A is 0 |
| `BNZ [addr*2B]` | Branch to `addr` if register A is not 0 |
| `BC [addr*2B]` | Branch to `addr` if previous arithmetic resulted in overflow |
| `BNC [addr*2B]` | Branch to `addr` if previous arithmetic did not result in overflow |
| `BEQ [addr*2B]` | Branch to `addr` if register X is equal to register Y |
| `BNE [addr*2B]` | Branch to `addr` if register X is not equal to register Y |
| **Load Immediate** |
| `LDAI [value]` | load `value` to register A |
| `LDXI [value]` | load `value` to register X |
| `LDYI [value]` | load `value` to register Y |
| **Register-Register Copy** |
| `MVAX` | Copy register A to register X |
| `MVAY` | Copy register A to register Y |
| **Stack** |
| `PUSHA` | Push register A to stack |
| `POPA` | Pop from stack to register A |
| `PUSHX` | Push register X to stack |
| `POPX` | Pop from stack to register X |
| `PUSHY` | Push register Y to stack |
| `POPY` | Pop from stack to register Y |
| **Halt** |
| `HALT` | Stop Execution Immediately |