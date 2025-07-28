emulator:object

class command:
    @staticmethod
    def init(e:object):
        global emulator
        emulator = e

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
                emulator.registers[reg] = io.handlein(ionum)
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
            if iostates[ionum]:
                emulator.memory[addr1] = io.handlein(ionum)
        else:
            emulator.memory[addr2] = emulator.memory[addr1]
    
    @staticmethod
    def pop():
        value = emulator.memory[emulator.stackbeginaddr+emulator.stackindex]
        emulator.stackindex = (emulator.stackindex-1) % 256
        return value
    @staticmethod
    def push(value):
        emulator.stackindex = (emulator.stackindex+1) % 256
        emulator.memory[emulator.stackbeginaddr+emulator.stackindex] = value
        return

    # 0 is output mode, 1 is input mode
    @staticmethod
    def get_io_states(statebyte):
        iostates = []
        for i in range(8):
            iostates.append((statebyte & 1)==1)
            statebyte = statebyte >> 1
        return iostates

class io:

    inputbuffer = []

    @staticmethod
    def handleout(value,ionum):
        if ionum == 0:
            if value == 2:
                io.inputbuffer = list(input().encode('ascii'))
                io.inputbuffer.reverse()
            else:
                print(chr(value),end="")
        if ionum == 1:
            print(value,end=" ")
        # the rest are unused for now
    
    @staticmethod
    def handlein(ionum):
        if ionum == 0:
            try:
                return io.inputbuffer.pop()
            except:
                return 0