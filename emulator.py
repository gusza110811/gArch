import sys
from instruction import *

class emulator:
    TESTING=True

    memory = bytearray(2**16)
    registers = [0,0,0] # A, X, Y respectively
    counter = 0

    iostateaddr = 0xFFF0
    ioaddr = range(0xFFF8,0xFFFF)

    stackbeginaddr = 0xFE00 # 256 bytes stack, 0xFE00 to 0xFEFF
    stackindex = 0

    carry = False

    @staticmethod
    def main(code:bytes):
        emulator.definitions()

        for idx,byte in enumerate(code):
            emulator.memory[idx] = byte

        A=0;X=1;Y=2
        while emulator.counter < len(code):
            byte = emulator.memory[emulator.counter]
            parambytes = []
            instruction = emulator.OPCODES[byte]
            try:
                name:str = instruction["mnemonic"].lower()
            except TypeError:
                emulator.counter +=1
                continue
            paramslen:int = instruction["size"]

            for i in range(paramslen-1):
                emulator.counter +=1
                parambytes.append(code[emulator.counter])
            
            status = executor.step(name,parambytes)

            if status == 1:
                continue
            elif status == 2:
                break
            else:
                emulator.counter +=1

        return

    @staticmethod
    def bytes_to_double(highbyte:int,lowbyte:int): return (highbyte << 8) + lowbyte

    def double_to_bytes(double:int):
        lowbyte = double & 0xFF
        highbyte = double >> 8
        return lowbyte, highbyte

    @staticmethod
    def dump_registers():
        print(f"Register A: x{emulator.registers[0]:02X}")
        print(f"Register X: x{emulator.registers[1]:02X}")
        print(f"Register Y: x{emulator.registers[2]:02X}")

    @staticmethod
    def dump_addr(addr:int):
        print(f"{addr:04X}: x{emulator.memory[addr]:02X}")

    @staticmethod
    def dump_memory(start: int = 0, end: int = None):
        mem = emulator.memory
        if end is None:
            end = len(mem)

        prev_value = None
        repeat_count = 0
        printed = False

        for i in range(start, end):
            value = mem[i]

            if value == prev_value:
                repeat_count += 1
                printed = False
            else:
                if repeat_count > 0:
                    if not printed:
                        if repeat_count > 1:
                            print(f"... {repeat_count} times")
                        else:
                            print("... repeated")
                        printed = True
                    repeat_count = 0

                print(f"{i:04X}: x{value:02X}")
                prev_value = value

        if repeat_count > 0:
            print(f"... repeated to {(end-1):04X}")

    OPCODES:list[dict[str:str,str:int,str:list]] = [None] * 256  # Initialize with 256 empty slots

    # Helper function to insert opcodes into the list
    @staticmethod
    def define(op, code, size, operands, desc):
        emulator.OPCODES[code] = {
            'mnemonic': op,
            'opcode': code,
            'size': size,
            'operands': operands,
            'desc': desc
        }

    @staticmethod
    def definitions():
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

        # --- Variable Load/store ---
        emulator.define('LDV', 0x17, 1, [], 'Load value into register A, using X as high byte address and Y as low byte address')
        emulator.define('STV', 0x18, 1, [], 'Load value into register A, using X as high byte address and Y as low byte address')


        # --- Arithmetic ---
        emulator.define('ADD', 0x20, 1, [], 'A = X + Y')
        emulator.define('SUB', 0x21, 1, [], 'A = X - Y')
        emulator.define('MUL', 0x22, 1, [], 'A = X * Y')
        emulator.define('DIV', 0x23, 1, [], 'A = X // Y')

        # --- Bitwise Logic ---
        emulator.define('AND', 0x24, 1, [], 'A = X & Y')
        emulator.define('OR',  0x25, 1, [], 'A = X | Y')
        emulator.define('XOR', 0x26, 1, [], 'A = X ^ Y')
        emulator.define('NOT', 0x27, 1, [], 'A = ~X')

        # --- Control Flow ---
        emulator.define('JMP', 0x30, 3, ['addr'], 'Jump to address')
        emulator.define('JZ',  0x31, 3, ['addr'], 'Jump if A == 0')
        emulator.define('JNZ', 0x32, 3, ['addr'], 'Jump if A != 0')
        emulator.define('JC',  0x33, 3, ['addr'], 'Jump if Carry')
        emulator.define('JNC', 0x34, 3, ['addr'], 'Jump if not Carry')
        emulator.define('JEQ', 0x35, 3, ['addr'], 'Jump if X == Y')
        emulator.define('JNE', 0x36, 3, ['addr'], 'Jump if X != Y')

        # --- Function Flow ---
        emulator.define("RET",  0x37, 1, [], "Pop from stack twice, use the top value as lowbyte and bottom value as highbyte, and jump to that address")
        emulator.define("CALL", 0x38, 3, ['addr'], "Jump to address, pushing current line to stack (high byte first)")
        emulator.define('BZ',   0x39, 3, ['addr'], 'Call if A == 0')
        emulator.define('BNZ',  0x3A, 3, ['addr'], 'Call if A != 0')
        emulator.define('BC',   0x3B, 3, ['addr'], 'Call if Carry')
        emulator.define('BNC',  0x3C, 3, ['addr'], 'Call if not Carry')
        emulator.define('BEQ',  0x3D, 3, ['addr'], 'Call if X == Y')
        emulator.define('BNE',  0x3E, 3, ['addr'], 'Call if X != Y')

        # --- Load immediate ---
        emulator.define("LDAI", 0x47, 2, ["imm8"], "Load immediate 8-bit value into A")
        emulator.define("LDXI", 0x48, 2, ["imm8"], "Load immediate 8-bit value into X")
        emulator.define("LDYI", 0x49, 2, ["imm8"], "Load immediate 8-bit value into Y")

        # --- Register-register ---
        emulator.define("MVAX", 0x50, 1, [], "Copy Register A to X")
        emulator.define("MVAY", 0x51, 1, [], "Copy Register A to Y")

        # --- Stack ---
        emulator.define("PUSHA", 0x60, 1, [], "Push Register A to stack")
        emulator.define("POPA",  0x61, 1, [], "Pop from stack to Register A")
        emulator.define("PUSHX", 0x62, 1, [], "Push Register X to stack")
        emulator.define("POPX",  0x63, 1, [], "Pop from stack to Register X")
        emulator.define("PUSHY", 0x64, 1, [], "Push Register Y to stack")
        emulator.define("POPY",  0x65, 1, [], "Pop from stack to Register Y")

        # --- System ---
        emulator.define('HALT', 0xFF, 1, [], 'Stop execution')
        return


if __name__ == "__main__":
    source = ""
    code:bytes
    try:
        source = sys.argv[1]
    except IndexError:
        source = "main.bin"
    
    with open(source,"rb") as sourcefile:
        code = sourcefile.read()
    
    executor.init(emulator)

    try:
        emulator.main(code)
    except KeyboardInterrupt:
        print("INT")
    if emulator.TESTING:
        print("\n\n")
        emulator.dump_registers()
        emulator.dump_memory()