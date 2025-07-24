import sys
import math

""" quick reference from emulator.py
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
    constants:dict[str,bytes] = {}
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

        # Control flow (incomplete)
        "jmp":0x30,

        # Load Immediate
        "ldai":0x37,
        "ldxi":0x37,
        "ldyi":0x38,
    }

    def main(code:list[str]):

        length = 0
        # Label
        for idx,line in enumerate(code):
            line = line.strip()

            if line.lower().startswith("label"):
                words = line.split()[1:]
                assembler.constants[words[0]] = length.to_bytes(2)
            for word in line.split():
                if assembler.decode_helpers(line,idx): continue
                length += len(assembler.decode_value(word,idx,line))

        # Main
        for idx,line in enumerate(code):

            line = line.strip()
            
            if assembler.decode_helpers(line,idx): continue

            # Word decoder
            for word in line.split():
                assembler.result += assembler.decode_value(word,idx,line)
        return assembler.result

    def decode_helpers(line:str,idx):
        if line.lower().startswith("const"):
            words = line.split()[1:]
            assembler.constants[words[0]] = assembler.decode_value(words[1],idx,line)
            return True
        if line.lower().startswith("label"):
            return True
        if line.lower().startswith(";"):
            return True

    def decode_value(word:str,idx=0,line=""):
        if word.lower() in list(assembler.mnemonicToOP.keys()):
            return assembler.mnemonicToOP[word.lower()].to_bytes()
        elif word.lower() in list(assembler.constants.keys()):
            return assembler.constants[word.lower()]
        elif word[0] == "'":
            return bytes(word[1],"ascii")
        elif word[0] == '"':
            return bytes(word[1:],"ascii")
        elif word[0] == "x":
            try:
                return int(word[1:],base=16).to_bytes(math.ceil(len(word[1:])/2))
            except ValueError:
                sys.exit(f"Line {idx+1} '{line}': invalid hex '{word}'")
        elif word[0] == "b":
            try:
                return int(word[1:],base=2).to_bytes(math.ceil(len(word[1:])/8))
            except ValueError:
                sys.exit(f"Line {idx+1} '{line}': invalid binary '{word}'")
        else:
            try:
                return bytes([int(word)])
            except ValueError:
                sys.exit(f"Line {idx+1} '{line}': can't decode `{word}`!")

def is_ascii_printable_byte(byte_value):
    """Checks if an integer byte value is an ASCII printable character."""
    return 32 <= byte_value <= 126

if __name__ == "__main__":
    source = ""
    code:str
    dest = ""
    if not assembler.TESTING:
        source = sys.argv[1]
        dest = sys.argv[2]
    else:
        source = "main.asm"
        dest = "main.bin"
        simple = True
    with open(source, "r") as sourcefile:
        code = sourcefile.readlines()
    
    result = assembler.main(code)
    print("\nConstants used:")
    for idx, (name,value) in enumerate(assembler.constants.items()):
        if is_ascii_printable_byte(int.from_bytes(value)):
            print(f"{str(idx).zfill(len(assembler.constants))}: {name} = {int.from_bytes(value)} (`{value.decode("ascii")}`)")
        elif int.from_bytes(value) > 255:
            print(f"{str(idx).zfill(len(assembler.constants))}: {name} = {int.from_bytes(value)} ({hex(int.from_bytes(value))})")
        else:
            print(f"{str(idx).zfill(len(assembler.constants))}: {name} = {int.from_bytes(value)}")
    print("<","="*len(assembler.constants)*2,">",sep="=")
    with open(dest, "wb") as destfile:
        destfile.write(result)