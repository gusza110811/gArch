import sys
import os
import math

class assembler:
    TESTING = True
    def __init__(self):
        self.constants:dict[str,bytes] = {}
        self.aliases:dict[str,bytes] = {}
        self.mnemonicToOP = {
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

            # Arithmetic
            "add":0x20,
            "sub":0x21,
            "mul":0x22,
            "div":0x23,

            # Bitwise logic
            "and":0x24,
            "or" :0x25,
            "xor":0x26,
            "not":0x27,

            # Control flow
            "jmp":0x30,
            "jz" :0x31,
            "jnz":0x32,
            "jc" :0x33,
            "jnc":0x34,
            "jeq":0x35,
            "jne":0x36,

            # Function flow
            "ret" :0x37,
            "call":0x38,
            "bz"  :0x39,
            "bnz" :0x3A,
            "bc"  :0x3B,
            "bnc" :0x3C,
            "be"  :0x3D,
            "bne" :0x3E,

            # Load Immediate
            "ldai":0x47,
            "ldxi":0x48,
            "ldyi":0x49,

            # Register move
            "mvax":0x50,
            "mvay":0x51,
            "mvxy":0x52,
            "mvxa":0x52,
            "mvyx":0x54,
            "mvya":0x55,

            # Stack
            "pusha":0x60,
            "popa" :0x61,
            "pushx":0x62,
            "popx" :0x63,
            "pushy":0x64,
            "popy" :0x65,

            # HALT
            "halt":0xFF,
        }

    def main(self, code:list[str],modulename="main"):

        output = b""

        # Prelabel
        for idx,line in enumerate(code):
            line = line.strip()
            if line.lower().startswith("label"):
                words = line.split()[1:]
                self.constants[words[0]] = bytes([0,0])
                self.constants["^"+words[0]] = bytes(1) # high byte
                self.constants[words[0]+"^"] = bytes(1) # low byte
        length = 0
        # Label and stuff
        for idx,line in enumerate(code):
            line = line.strip()

            if line.lower().startswith("label"):
                words = line.split()[1:]
                value = length.to_bytes(2)
                self.constants[words[0]] = value
                # so its possible to use labels as separate byte
                self.constants["^"+words[0]] = value[0].to_bytes(1) # high byte
                self.constants[words[0]+"^"] = value[1].to_bytes(1) # low byte
            for word in line.split():
                if self.decode_helpers(line,idx):
                    code[idx]=""
                    continue
                if line.startswith("."):
                    length += len(self.decode_literal(line))
                    break
                try:
                    length += len(self.decode_value(word,idx,line))
                except ValueError as e:
                    print(f"An Error in {modulename}:")
                    print(f"    {e}")
                    sys.exit()

        # Main
        for idx,line in enumerate(code):

            line = line.strip()
            
            if self.decode_helpers(line,idx):
                continue

            if line.startswith("."):
                output += self.decode_literal(line)
                continue

            # Word decoder
            for word in line.split():
                try:
                    result = self.decode_value(word,idx,line)
                except ValueError as e:
                    print(f"An Error in {modulename}:")
                    print(f"    {e}")
                    sys.exit()
                if result:
                    output += result
                else:
                    break
        return output, self.constants

    def decode_literal(self, line:str):
        if line.lower().startswith(".ascii"):
            return bytes(line[7:],encoding="ascii")+(0).to_bytes(1)
        elif line.lower().startswith(".include"):
            lib = "/".join(os.path.abspath(__file__).split(os.sep)[:-1])+"/lib/"

            modulename = line[9:]
            try:
                with open(modulename+".asm","r") as modulefile:
                    module = modulefile.readlines()
                    module.insert(0,f"JMP {modulename}.END\n")
                    module.append(f"\nlabel {modulename}.END")
            except FileNotFoundError:
                with open(lib+modulename+".asm","r") as modulefile:
                    module = modulefile.readlines()
                    module.insert(0,f"JMP {modulename}.END\n")
                    module.append(f"\nlabel {modulename}.END")
            except FileNotFoundError:
                sys.exit(f"Unknown Module: {module}")
            
            result, constants = self.main(module,modulename)
            self.constants = self.constants | constants
            return result

        return

    def decode_helpers(self, line:str,idx):
        if line.lower().startswith("const"):
            words = line.split()[1:]
            value:bytes = self.decode_value(words[1],idx,line)
            self.constants[words[0]] = value
            # so its possible to use the addresses as separate bytes
            if len(value) == 2:
                self.constants["^"+words[0]] = value[0].to_bytes(1) # high byte
                self.constants[words[0]+"^"] = value[1].to_bytes(1) # low byte
            return True
        if line.lower().startswith("alias"):
            words = line.split()[1:]
            value:bytes = self.decode_value(words[1],idx,line)
            self.aliases[words[0]] = value
            # so its possible to use the addresses as separate bytes
            if len(value) == 2:
                self.aliases["^"+words[0]] = value[0].to_bytes(1) # high byte
                self.aliases[words[0]+"^"] = value[1].to_bytes(1) # low byte
            return True
        if line.lower().startswith("label"):
            return True
        if line.lower().startswith(";"):
            return True
        
        return False

    def decode_value(self, word:str,idx=0,line=""):
        if word.lower() in list(self.mnemonicToOP.keys()):
            return self.mnemonicToOP[word.lower()].to_bytes()
        elif word in list(self.constants.keys()):
            return self.constants[word]
        elif word in list(self.aliases.keys()):
            return self.aliases[word]
        elif word[0] == "'":
            return bytes(word[1],"ascii")
        elif word[0] == '"':
            return bytes(word[1:],"ascii")
        elif word[0] == "x":
            try:
                return int(word[1:],base=16).to_bytes(math.ceil(len(word[1:])/2))
            except ValueError:
                raise ValueError(f"Line {idx+1} '{line}': invalid hex '{word}'")
        elif word[0] == "b":
            try:
                return int(word[1:],base=2).to_bytes(math.ceil(len(word[1:])/8))
            except ValueError:
                raise ValueError(f"Line {idx+1} '{line}': invalid binary '{word}'")
        elif word[0] == ";":
            return False
        else:
            try:
                return bytes([int(word)])
            except ValueError:
                raise ValueError(f"Line {idx+1} '{line}': can't decode `{word}`!")

def is_ascii_printable_byte(byte_value):
    """Checks if an integer byte value is an ASCII printable character."""
    return 32 <= byte_value <= 126

if __name__ == "__main__":
    source = ""
    code:str
    dest = ""
    try:
        source = sys.argv[1]
    except IndexError:
        source = "main.asm"
    try:
        dest = sys.argv[2]
    except IndexError:
        dest = ".".join(source.split(".")[:-1])+".bin" if source.endswith(".asm") else source

    with open(source, "r") as sourcefile:
        code = sourcefile.readlines()

    main = assembler()
    
    result,constants = main.main(code,source)

    print("\nConstants used:")
    maxlen = len(str(len(constants)))
    for idx, (name,value) in enumerate(constants.items()):
        if is_ascii_printable_byte(int.from_bytes(value)):
            print(f"{str(idx).zfill(maxlen)}: {name} = {int.from_bytes(value)} (`{value.decode("ascii")}` or {int.from_bytes(value):02X})")
        else:
            print(f"{str(idx).zfill(maxlen)}: {name} = {int.from_bytes(value)} ({int.from_bytes(value):02X})")
    print("<","="*len(constants)*2,">",sep="=")
    with open(dest, "wb") as destfile:
        destfile.write(result)