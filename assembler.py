import sys
import math

"""
        # --- Register Loads ---
        emulator.define('LDA', 0x10, 3, ['addr'], 'Load from address into A')
        emulator.define('LDX', 0x11, 3, ['addr'], 'Load from address into X')
        emulator.define('LDY', 0x12, 3, ['addr'], 'Load from address into Y')

        # --- Register Stores ---
        emulator.define('STA', 0x13, 3, ['addr'], 'Store A into address')
        emulator.define('STX', 0x14, 3, ['addr'], 'Store X into address')
        emulator.define('STY', 0x15, 3, ['addr'], 'Store Y into address')

        # --- Memory to Memory ---
        emulator.define('MOV', 0x16, 5, ['addr_dst', 'addr_src'], 'Copy from addr_src to addr_dst')

        # --- Arithmetic ---
        emulator.define('ADD', 0x20, 1, [], 'A = X + Y')
        emulator.define('SUB', 0x21, 1, [], 'A = X - Y')
        emulator.define('MUL', 0x22, 1, [], 'A = X * Y')
        emulator.define('DIV', 0x23, 1, [], 'A = X / Y (int)')

        # --- Bitwise/Logic (Optional) ---
        emulator.define('AND', 0x24, 1, [], 'A = X & Y')
        emulator.define('OR',  0x25, 1, [], 'A = X | Y')
        emulator.define('XOR', 0x26, 1, [], 'A = X ^ Y')
        emulator.define('NOT', 0x27, 1, [], 'A = ~X')

        # --- Control Flow ---
        emulator.define('JMP', 0x30, 3, ['addr'], 'Jump to address')
        emulator.define('JZ',  0x31, 3, ['addr'], 'Jump if A == 0')
        emulator.define('JNZ', 0x32, 3, ['addr'], 'Jump if A != 0')
        emulator.define('JG',  0x33, 3, ['addr'], 'Jump if A > 0')
        emulator.define('JL',  0x34, 3, ['addr'], 'Jump if A < 0')
        emulator.define('JEQ', 0x35, 3, ['addr'], 'Jump if X == Y')
        emulator.define('JNE', 0x36, 3, ['addr'], 'Jump if X != Y')

        # Load immediate
        emulator.define("LDAI", 0x37, 2, ["imm8"], "Load immediate 8-bit value into A")
        emulator.define("LDXI", 0x38, 2, ["imm8"], "Load immediate 8-bit value into X")
        emulator.define("LDYI", 0x39, 2, ["imm8"], "Load immediate 8-bit value into Y")

        # --- System ---
        emulator.define('HALT', 0xFF, 1, [], 'Stop execution')
"""

class assembler:
    TESTING = True
    result = b""
    mnemonicToOP = {
        # Load and store
        "lda":0x10,
        "ldx":0x11,
        "ldy":0x12,
        "sta":0x13,
        "stx":0x14,
        "sty":0x15,
        "mov":0x16,

        # arithmetic not yet

        # logic not yet

        # control flow not yet

        # Load Immediate
        "ldai":0x37,
        "ldxi":0x37,
        "ldyi":0x37,
    }

    def simple(code:list[str]):
        for idx,line in enumerate(code):
            for word in line.split():
                if word.lower() in list(assembler.mnemonicToOP.keys()):
                    assembler.result += assembler.mnemonicToOP[word.lower()].to_bytes()
                elif word[0] == "'":
                    assembler.result += bytes(word[1],"ascii")
                elif word[0] == '"':
                    assembler.result += bytes(word[1:],"ascii")
                elif word[0] == "x":
                    try:
                        assembler.result += int(word[1:],base=16).to_bytes(math.ceil(len(word[1:])/2))
                    except ValueError:
                        quit(f"Line {idx}: invalid hex value")
                elif word[0] == "b":
                    try:
                        assembler.result += int(word[1:],base=2).to_bytes(math.ceil(len(word[1:])/8))
                    except ValueError:
                        quit(f"Line {idx}: invalid binary value")
                else:
                    try:
                        assembler.result += bytes([int(word[1:])])
                    except ValueError:
                        quit(f"Line {idx}: can't decode `{word}`!")
        return assembler.result

if __name__ == "__main__":
    source = ""
    code:str
    dest = ""
    simple:bool
    if not assembler.TESTING:
        source = sys.argv[1]
        dest = sys.argv[2]
        try:
            simple = sys.argv[3].lower != "a"
        except IndexError:
            simple = True
    else:
        source = "test.asm"
        dest = "test.bin"
        simple = True
    
    with open(source,"r") as sourcefile:
        code = sourcefile.readlines()
    if simple:
        result = assembler.simple(code)
    else:
        sys.exit("ok chill this part's not done")
    
    with open(dest, "wb") as destfile:
        destfile.write(result)