from command import *

emulator:object
class executor:
    @staticmethod
    def init(e:object):
        global emulator
        emulator = e
        command.init(e)
    
    @staticmethod
    def step(name:str,parambytes:list[int]):
        A=0;X=1;Y=2
        # --- LOAD/STORE/MOV ---
        if name[:2] == "ld":
            targetreg=None
            if name[2] == "a":targetreg=A
            elif name[2] == "x":targetreg=X
            elif name[2] == "y":targetreg=Y
            elif name[2] == "v":targetreg=A
            if name[-1] == "i":
                value = parambytes[0]
                command.loadimm(value,targetreg)
            elif name[-1] == "v":
                address = (emulator.registers[X] << 8) + emulator.registers[Y]
                command.load(address,targetreg)
            else:
                address = emulator.bytes_to_double(parambytes[0],parambytes[1])
                command.load(address,targetreg)
        if name[:2] == "st":
            sourcereg=None
            if name[2] == "a":sourcereg=A
            elif name[2] == "x":sourcereg=X
            elif name[2] == "y":sourcereg=Y
            if name[2] == "v":sourcereg=A
            if name[2] == "v":
                address = (emulator.registers[X] << 8) + emulator.registers[Y]
                command.store(sourcereg,address)
            else:
                address = emulator.bytes_to_double(parambytes[0],parambytes[1])
                command.store(sourcereg,address)
        elif name == "mov":
            addr1 = emulator.bytes_to_double(parambytes[0], parambytes[1])
            addr2 = emulator.bytes_to_double(parambytes[2], parambytes[3])
            command.move(addr1,addr2) # for consistency even though it doesnt make a lot of sense
        elif name == "mvax":
            emulator.registers[X] = emulator.registers[A]
        elif name == "mvay":
            emulator.registers[Y] = emulator.registers[A]
        elif name == "mvxy":
            emulator.registers[Y] = emulator.registers[X]
        elif name == "mvxa":
            emulator.registers[A] = emulator.registers[X]
        elif name == "mvyx":
            emulator.registers[X] = emulator.registers[Y]
        elif name == "mvya":
            emulator.registers[A] = emulator.registers[Y]
        
        # --- CONTROL FLOW ---
        elif name == "jmp":
            emulator.counter = emulator.bytes_to_double(parambytes[0],parambytes[1])
            return 1 # the counter is not supposed to increase after a jump
        elif name == "jz":
            if emulator.registers[A] == 0:
                emulator.counter = emulator.bytes_to_double(parambytes[0],parambytes[1])
                return 1 # the counter is not supposed to increase after a jump
        elif name == "jnz":
            if emulator.registers[A] != 0:
                emulator.counter = emulator.bytes_to_double(parambytes[0],parambytes[1])
                return 1 # the counter is not supposed to increase after a jump
        elif name == "jc":
            if emulator.carry:
                emulator.counter = emulator.bytes_to_double(parambytes[0],parambytes[1])
                return 1 # the counter is not supposed to increase after a jump
        elif name == "jnc":
            if not emulator.carry:
                emulator.counter = emulator.bytes_to_double(parambytes[0],parambytes[1])
                return 1 # the counter is not supposed to increase after a jump
        elif name == "jeq":
            if emulator.registers[X] == emulator.registers[Y]:
                emulator.counter = emulator.bytes_to_double(parambytes[0],parambytes[1])
                return 1 # the counter is not supposed to increase after a jump
        elif name == "jne":
            if emulator.registers[X] != emulator.registers[Y]:
                emulator.counter = emulator.bytes_to_double(parambytes[0],parambytes[1])
                return 1 # the counter is not supposed to increase after a jump
        
        # --- FUNCTION FLOW ---
        elif name == "ret":
            lowbyte = command.pop()
            highbyte = command.pop()
            emulator.counter = emulator.bytes_to_double(highbyte,lowbyte)
            # the counter is supposed to increase after a return
        elif name == "call":
            highbyte, lowbyte = emulator.double_to_bytes(emulator.counter)
            command.push(highbyte)
            command.push(lowbyte)
            emulator.counter = emulator.bytes_to_double(parambytes[0],parambytes[1])
            return 1 # the counter is not supposed to increase after a call
        elif name == "bz":
            if emulator.registers[A] != 0:
                return 1
            highbyte, lowbyte = emulator.double_to_bytes(emulator.counter)
            command.push(highbyte)
            command.push(lowbyte)
            emulator.counter = emulator.bytes_to_double(parambytes[0],parambytes[1])
            return 1 # the counter is not supposed to increase after a branch
        elif name == "bnz":
            if emulator.registers[A] == 0:
                return 1
            highbyte, lowbyte = emulator.double_to_bytes(emulator.counter)
            command.push(highbyte)
            command.push(lowbyte)
            emulator.counter = emulator.bytes_to_double(parambytes[0],parambytes[1])
            return 1 # the counter is not supposed to increase after a 
        elif name == "bc":
            if not emulator.carry:
                return 1
            highbyte, lowbyte = emulator.double_to_bytes(emulator.counter)
            command.push(highbyte)
            command.push(lowbyte)
            emulator.counter = emulator.bytes_to_double(parambytes[0],parambytes[1])
            return 1 # the counter is not supposed to increase after a branch
        elif name == "bnc":
            if emulator.carry:
                return 1
            highbyte, lowbyte = emulator.double_to_bytes(emulator.counter)
            command.push(highbyte)
            command.push(lowbyte)
            emulator.counter = emulator.bytes_to_double(parambytes[0],parambytes[1])
            return 1 # the counter is not supposed to increase after a branch
        elif name == "be":
            if emulator.registers[X] != emulator.registers[Y]:
                return 1
            highbyte, lowbyte = emulator.double_to_bytes(emulator.counter)
            command.push(highbyte)
            command.push(lowbyte)
            emulator.counter = emulator.bytes_to_double(parambytes[0],parambytes[1])
            return 1 # the counter is not supposed to increase after a branch
        elif name == "bne":
            if emulator.registers[X] != emulator.registers[Y]:
                return 1
            highbyte, lowbyte = emulator.double_to_bytes(emulator.counter)
            command.push(highbyte)
            command.push(lowbyte)
            emulator.counter = emulator.bytes_to_double(parambytes[0],parambytes[1])
            return 1 # the counter is not supposed to increase after a branch
        
        # --- ALGEBRA ---
        elif name == "add":
            emulator.registers[A] = emulator.registers[X] + emulator.registers[Y]
            if emulator.registers[A] > 255:
                emulator.carry = True
                emulator.registers[A] = emulator.registers[A] % 256
            else:
                emulator.carry = False
        elif name == "sub":
            emulator.registers[A] = emulator.registers[X] - emulator.registers[Y]
            if emulator.registers[A] < 255:
                emulator.carry = True
                emulator.registers[A] = emulator.registers[A] % 256
            else:
                emulator.carry = False
        elif name == "mul":
            emulator.registers[A] = emulator.registers[X] * emulator.registers[Y]
            if emulator.registers[A] > 255:
                emulator.carry = True
                emulator.registers[A] = emulator.registers[A] % 256
            else:
                emulator.carry = False
        elif name == "div":
            emulator.registers[A] = emulator.registers[X] // emulator.registers[Y]
            if emulator.registers[A] > 255:
                emulator.carry = True
                emulator.registers[A] = emulator.registers[A] % 256
            else:
                emulator.carry = False
        
        # --- BITWISE ---
        elif name == "and":
            emulator.registers[A] = emulator.registers[X] & emulator.registers[Y]
        elif name == "or":
            emulator.registers[A] = emulator.registers[X] | emulator.registers[Y]
        elif name == "xor":
            emulator.registers[A] = emulator.registers[X] ^ emulator.registers[Y]
        elif name == "not":
            emulator.registers[A] = ~emulator.registers[X]
        
        # --- STACK ---
        elif name[:4] == "push":
            if name[-1] == "a":
                target = A
            elif name[-1] == "x":
                target = X
            elif name[-1] == "y":
                target = Y

            command.push(emulator.registers[target])
        elif name[:3] == "pop":
            if name[-1] == "a":
                target = A
            elif name[-1] == "x":
                target = X
            elif name[-1] == "y":
                target = Y
            emulator.registers[target] = command.pop()

        elif name == "halt":
            return 2