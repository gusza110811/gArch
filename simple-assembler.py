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
        "ldv":0x17,
        "stv":0x18,

        # arithmetic not yet complete
        "add":0x20,

        # bitwise-logic not yet

        # Control flow
        "jmp":0x30,
        "jz":0x31,
        "jnz":0x32,
        "jc":0x33,
        "jnc":0x34,
        "jeq":0x35,
        "jne":0x36,

        # Function flow
        "ret":0x37,
        "call":0x38,

        # Load Immediate
        "ldai":0x47,
        "ldxi":0x48,
        "ldyi":0x49,

        # Register move
        "mvax":0x50,
        "mvay":0x51,

        # Stack
        "pusha":0x60,
        "popa":0x61,
        "pushx":0x62,
        "popx":0x63,
        "pushy":0x64,
        "popy":0x65,

        # HALT
        "halt":0xFF,
    }

    def main(code:list[str]):

        # Prelabel
        for idx,line in enumerate(code):
            line = line.strip()
            if line.lower().startswith("label"):
                words = line.split()[1:]
                assembler.constants[words[0]] = bytes([0,0])
                assembler.constants["^"+words[0]] = bytes(1) # high byte
                assembler.constants[words[0]+"^"] = bytes(1) # low byte
        length = 0
        # Label and stuff
        for idx,line in enumerate(code):
            line = line.strip()

            if line.lower().startswith("label"):
                words = line.split()[1:]
                value = length.to_bytes(2)
                assembler.constants[words[0]] = value
                # so its possible to use labels as separate byte
                assembler.constants["^"+words[0]] = value[0].to_bytes(1) # high byte
                assembler.constants[words[0]+"^"] = value[1].to_bytes(1) # low byte
            for word in line.split():
                if assembler.decode_helpers(line,idx):
                    code[idx]=""
                    continue
                if line.startswith("."):
                    length += len(assembler.decode_literal(line))
                    break
                length += len(assembler.decode_value(word,idx,line))

        # Main
        for idx,line in enumerate(code):

            line = line.strip()
            
            if assembler.decode_helpers(line,idx):
                continue

            if line.startswith("."):
                assembler.result += assembler.decode_literal(line)
                continue

            # Word decoder
            for word in line.split():
                result = assembler.decode_value(word,idx,line)
                if result:
                    assembler.result += result
                else:
                    break
        return assembler.result

    def decode_literal(line):
        if line.lower().startswith(".ascii"):
            return bytes(line[7:],encoding="ascii")+(0).to_bytes(1)

        return

    def decode_helpers(line:str,idx):
        if line.lower().startswith("const"):
            words = line.split()[1:]
            value:bytes = assembler.decode_value(words[1],idx,line)
            assembler.constants[words[0]] = value
            # so its possible to use the addresses as separate bytes
            if len(value) == 2:
                assembler.constants["^"+words[0]] = value[0].to_bytes(1) # high byte
                assembler.constants[words[0]+"^"] = value[1].to_bytes(1) # low byte
            return True
        if line.lower().startswith("label"):
            return True
        if line.lower().startswith(";"):
            return True
        
        return False

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
    try:
        source = sys.argv[1]
        dest = sys.argv[2]
    except:
        source = "main.asm"
        dest = "main.bin"
        simple = True
    with open(source, "r") as sourcefile:
        code = sourcefile.readlines()
    
    result = assembler.main(code)
    print("\nConstants used:")
    maxlen = len(str(len(assembler.constants)))
    for idx, (name,value) in enumerate(assembler.constants.items()):
        if is_ascii_printable_byte(int.from_bytes(value)):
            print(f"{str(idx).zfill(maxlen)}: {name} = {int.from_bytes(value)} (`{value.decode("ascii")}` or {int.from_bytes(value):02X})")
        else:
            print(f"{str(idx).zfill(maxlen)}: {name} = {int.from_bytes(value)} ({int.from_bytes(value):02X})")
    print("<","="*len(assembler.constants)*2,">",sep="=")
    with open(dest, "wb") as destfile:
        destfile.write(result)