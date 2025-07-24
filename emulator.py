import sys

class command:
    @staticmethod
    def loadimm(value,reg):
        emulator.registers[reg] = value
    @staticmethod
    def load(addr,reg):
        if not (addr in emulator.ioaddr):
            emulator.registers[reg] = emulator.memory[addr]
        else:
            ionum = emulator.ioaddr.index(addr)
            iostates = command.get_io_states(emulator.memory[emulator.iostateaddr])
            if iostates[ionum]:
                io.handlein(emulator.registers[reg],ionum)
    @staticmethod
    def store(reg,addr):
        if not (addr in emulator.ioaddr):
            emulator.memory[addr] = emulator.registers[reg]
        else:
            ionum = emulator.ioaddr.index(addr)
            iostates = command.get_io_states(emulator.memory[emulator.iostateaddr])
            if not iostates[ionum]:
                io.handleout(emulator.registers[reg],ionum)

    @staticmethod
    def move(addr1,addr2): # FIRST ONE IS THE DESTINATION GOD DAMN IT I DESIGNED THIS SHIT AND I KEEP FORGETTING
        iostates = command.get_io_states(emulator.memory[emulator.iostateaddr])
        if addr1 in emulator.ioaddr:
            ionum = emulator.ioaddr.index(addr1)
            if not iostates[ionum]:
                io.handleout(emulator.memory[addr2],ionum)
        elif addr2 in emulator.ioaddr:
            ionum = emulator.ioaddr.index(addr2)
            if not iostates[ionum]:
                io.handlein(ionum)
        else:
            emulator.memory[addr2] = emulator.memory[addr1]

    # 0 is output mode, 1 is input mode
    @staticmethod
    def get_io_states(statebyte):
        iostates = []
        for i in range(8):
            iostates.append((statebyte & 1)==1)
            statebyte = statebyte >> 1
        return iostates

class io:

    @staticmethod
    def handleout(value,ionum):
        if ionum == 0:
            print(chr(value),end="")
        if ionum == 1:
            print(value,end="")
        # the rest are unused for now
    
    @staticmethod
    def handlein(ionum):
        raise NotImplementedError

class emulator:
    TESTING=True

    memory = bytearray(2**16)
    registers = [0,0,0] # A, X, Y respectively
    counter = 0

    iostateaddr = 0xFFF0
    ioaddr = range(0xFFF8,0xFFFF)

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

            #print(name,", ".join([hex(byte) for byte in parambytes]))
            
            if name[:2] == "ld":
                targetreg=None
                if name[2] == "a":targetreg=A
                elif name[2] == "x":targetreg=X
                elif name[2] == "y":targetreg=Y
                if name[-1] != "i":
                    address = emulator.bytes_to_double(parambytes[0],parambytes[1])
                    command.load(address,targetreg)
                else:
                    value = parambytes[0]
                    command.loadimm(value,targetreg)
            if name[:2] == "st":
                sourcereg=None
                if name[2] == "a":sourcereg=A
                elif name[2] == "x":sourcereg=X
                elif name[2] == "y":sourcereg=Y
                address = emulator.bytes_to_double(parambytes[0],parambytes[1])
                command.store(sourcereg,address)
            elif name == "mov":
                addr1 = emulator.bytes_to_double(parambytes[0], parambytes[1])
                addr2 = emulator.bytes_to_double(parambytes[2], parambytes[3])
                command.move(addr1,addr2) # for consistency even though it doesnt make a lot of sense
            
            elif name == "jmp":
                emulator.counter = emulator.bytes_to_double(parambytes[0],parambytes[1])
                continue # the counter is not supposed to increase after a jump
            elif name == "jz":
                if emulator.registers[A] == 0:
                    emulator.counter = emulator.bytes_to_double(parambytes[0],parambytes[1])
                    continue # the counter is not supposed to increase after a jump
            elif name == "jc":
                if emulator.carry:
                    emulator.counter = emulator.bytes_to_double(parambytes[0],parambytes[1])
                    continue # the counter is not supposed to increase after a jump
            elif name == "jnc":
                if not emulator.carry:
                    emulator.counter = emulator.bytes_to_double(parambytes[0],parambytes[1])
                    continue # the counter is not supposed to increase after a jump
            
            elif name == "add":
                emulator.registers[A] = emulator.registers[X] + emulator.registers[Y]
                if emulator.registers[A] > 255:
                    emulator.carry = True
                    emulator.registers[A] = emulator.registers[A] % 256
                else:
                    emulator.carry = False

            elif name == "halt":
                break
            emulator.counter +=1

        return

    @staticmethod
    def bytes_to_double(highbyte:int,lowbyte:int): return (highbyte << 8) + lowbyte

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
        emulator.define('JC',  0x33, 3, ['addr'], 'Jump if Carry')
        emulator.define('JNC',  0x33, 3, ['addr'], 'Jump if not Carry')
        emulator.define('JEQ', 0x35, 3, ['addr'], 'Jump if X == Y')
        emulator.define('JNE', 0x36, 3, ['addr'], 'Jump if X != Y')

        # Load immediate
        emulator.define("LDAI", 0x47, 2, ["imm8"], "Load immediate 8-bit value into A")
        emulator.define("LDXI", 0x48, 2, ["imm8"], "Load immediate 8-bit value into X")
        emulator.define("LDYI", 0x49, 2, ["imm8"], "Load immediate 8-bit value into Y")

        # Register-register
        emulator.define("MVAX", 0x50, 1, ["imm8"], "Load immediate 8-bit value into Y")
        emulator.define("MVAY", 0x51, 1, ["imm8"], "Load immediate 8-bit value into Y")

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
    
    try:
        emulator.main(code)
    except KeyboardInterrupt:
        print("INT")
    if emulator.TESTING:
        print("\n\n")
        emulator.dump_registers()
        emulator.dump_memory()