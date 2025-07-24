import sys
import math

class assembler:
    TESTING = True
    result = b""
    constants:dict[str,bytes] = {}
    mnemonicToOP = {
        "nop":0x00,
        # Load and store
        "lda":0x10,
        "ldx":0x11,
        "ldy":0x12,
        "sta":0x13,
        "stx":0x14,
        "sty":0x15,
        "mov":0x16,

        # arithmetic not yet complete
        "add":0x20,

        # bitwise-logic not yet

        # Control flow not yet complete)
        "jmp":0x30,
        "jz":0x31,

        "jc":0x33,
        "jnc":0x33,

        # Load Immediate
        "ldai":0x47,
        "ldxi":0x48,
        "ldyi":0x49,

        # Register move
        "mvax":0x50,
        "mvay":0x51,
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
                result = assembler.decode_value(word,idx,line)
                if result:
                    assembler.result += result
                else:
                    break
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
        elif word[0] == ";":
            return False
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