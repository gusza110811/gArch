import sys
from executor import *
import time

import tkinter as tk
from tkinter import ttk

class HALT(Exception):
    "Program is halted"
    def __init__(self, *args):
        super().__init__(*args)

class GUI:
    def __init__(self):
        self.tk = tk.Tk()
        self.tk.title("gProcessor Emulation")
        self.tk.geometry("800x600")

        self.running = True
        self.INT = False

        self.tk.protocol("WM_DELETE_WINDOW",self.onClose)

        self._build_layout()

    def onClose(self):
        self.running = False
        sys.exit(0)

    def _build_layout(self):
        # ====== Top Frame: Registers and Status ======
        self.reg_frame = ttk.LabelFrame(self.tk, text="Registers")
        self.reg_frame.pack(fill="x", padx=10, pady=5)

        self.register_labels = {}
        for reg, value in enumerate(emulator.registers):
            if reg == 0: name = "A"
            elif reg == 1: name = "X"
            elif reg == 2: name = "Y"
            lbl = ttk.Label(self.reg_frame, text=f"{name}: {value}")
            lbl.pack(side="left", padx=5)
            self.register_labels[reg] = lbl

        # ====== Middle Frame: Console ======
        self.output_frame = ttk.LabelFrame(self.tk, text="Console Output")
        self.output_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.output_text = tk.Text(self.output_frame, height=10, wrap="word", bg="#111", fg="#fff",state=tk.DISABLED)
        self.output_text.pack(fill="both", expand=True)

        self.input_frame = ttk.LabelFrame(self.tk,text="Control")
        self.input_frame.pack(fill='x',expand=True, padx=10, pady=5)

        self.input = tk.Entry(self.input_frame)
        self.input.pack(side=tk.LEFT,expand=True,fill="x")
        self.input_button = tk.Button(self.input_frame,text="Enter")
        self.input_button.pack(side=tk.LEFT)
        self.echo_button = tk.Button(self.input_frame,text="Input Echo: OFF ")
        self.echo_button.pack(side=tk.LEFT)

        def interrupt():
            self.INT = True
        self.int_button = tk.Button(self.input_frame,text="End execution now",command=interrupt)
        self.int_button.pack(side=tk.LEFT)

        # ====== Bottom Frame: Memory View ======
        self.memory_frame = ttk.LabelFrame(self.tk, text="Memory")
        self.memory_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.memory_list = tk.Listbox(self.memory_frame, font=("Courier", 10))
        self.memory_list.pack(side="left", fill="both", expand=True)

        self.scrollbar = ttk.Scrollbar(self.memory_frame, orient="vertical", command=self.memory_list.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.memory_list.config(yscrollcommand=self.scrollbar.set)

    def update_registers(self, registers: list):
        for reg, value in enumerate(registers):
            name = 'A' if reg==0 else 'X' if reg==1 else 'Y'
            if reg in self.register_labels:
                self.register_labels[reg].config(text=f"{name}: {value:02X}")

    def update_memory(self, memory: list):
        scroll_fraction = self.memory_list.yview()[0]
        self.memory_list.delete(0, "end")
        for value in memory:
            self.memory_list.insert("end", value)
        self.memory_list.yview_moveto(scroll_fraction)

    def softupdate(self):
        self.tk.update()

    def update(self,registers:list=None,truncated_memory:list=None):
        if registers:
            self.update_registers(registers)
        if truncated_memory:
            self.update_memory(truncated_memory)
        self.tk.update_idletasks()

    def run(self):
        self.tk.mainloop()


class CONSOLE:
    def __init__(self,gui:GUI):
        self.gui = gui
        self.console = gui.output_text
        self.echo = False
        self.text = None
        gui.input_button.config(command=self.inputEnter)
        gui.input.bind('<Return>', self.inputEnter)
        gui.echo_button.config(command=self.toggleEcho)
    
    def write(self,text):
        self.gui.output_text.config(state=tk.NORMAL)
        self.console.insert(tk.END,text)
        self.console.see(tk.END)
        self.gui.output_text.config(state=tk.DISABLED)

    def flush(self):

        return
    
    def readline(self):

        while not self.text:
            self.gui.softupdate()
            if (not gui.running) or gui.INT:
                return "\n"
        text = self.text
        self.text = None
        return text

    def inputEnter(self,event=None):
        self.text = self.gui.input.get()
        self.gui.input.delete(0,tk.END)
        if self.echo:
            print(self.text)

        return
    
    def toggleEcho(self):
        self.echo = not self.echo

        if self.echo:
            gui.echo_button.config(text="Input Echo:  ON ")
        else:
            gui.echo_button.config(text="Input Echo: OFF ")

        return

class emulator:
    debug = False

    memory = bytearray(2**16)
    registers = [0,0,0] # A, X, Y respectively
    counter = 0

    iostateaddr = 0xFFF0
    ioaddr = range(0xFFF8,0xFFFF)

    stackbeginaddr = 0xFE00 # 256 bytes stack, 0xFE00 to 0xFEFF
    stackindex = 0

    updatedelay = 10

    update = True

    carry = False

    latencies = []

    guimode = True

    @staticmethod
    def main(code:bytes,gui:GUI=None):
        emulator.definitions()
        if gui:
            console = CONSOLE(gui)

            sys.stdout = console
            sys.stdin = console

        timetoupdate = 0

        for idx,byte in enumerate(code):
            emulator.memory[idx] = byte

        while emulator.counter < len(code):
            before = time.time()
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

            emulator.latencies.append(time.time() - before)
            if status == 1:
                continue
            elif status == 2:
                break
            else:
                emulator.counter +=1
            
            if gui:
                if emulator.update:
                    gui.update(emulator.registers,emulator.truncate_memory(emulator.memory,len(code)))
                    emulator.update=False
                else:
                    gui.update(emulator.registers)

                if not gui.running:
                    break

                if gui.INT:
                    raise HALT

                if timetoupdate <= 0:
                    gui.softupdate()
                    timetoupdate = emulator.updatedelay
                else:
                    timetoupdate -= 1

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
    def truncate_memory(mem:bytearray, start: int = 0, end: int = None):
        result = []
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
                            result.append(f"    ... {repeat_count} times")
                        else:
                            result.append("    ... repeated")
                        printed = True
                    repeat_count = 0

                result.append(f"{i:04X}: x{value:02X}")
                prev_value = value

        if repeat_count > 0:
            result.append(f"    ... repeated to {(end-1):04X}")
        
        return result

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
        emulator.define("MVXY", 0x52, 1, [], "Copy Register X to Y")
        emulator.define("MVXA", 0x53, 1, [], "Copy Register X to A")
        emulator.define("MVYX", 0x54, 1, [], "Copy Register Y to X")
        emulator.define("MVYA", 0x55, 1, [], "Copy Register Y to A")

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
    
    for _,arg in enumerate(sys.argv[1:]):
        if arg.startswith("-"):
            arg = arg[1:]
            if arg == "c":
                emulator.guimode = False
            elif arg == "d":
                emulator.debug = True
            continue
        if _==0:
            source = arg
    
    if source == "":
        source = "main.bin"
    
    print(source)

    with open(source,"rb") as sourcefile:
        code = sourcefile.read()
    
    executor.init(emulator)


    if emulator.guimode:
        try:
            gui = GUI()
        except tk.TclError:
            print("Unable to start GUI mode, try using `-c` to start without graphical stat")
    else:
        gui = None
    stdout = sys.stdout

    try:
        emulator.main(code,gui)
    except HALT:
        pass
    except KeyboardInterrupt:
        sys.stdout = stdout
        if not gui:
            print("INT")
    except tk.TclError as error:
        sys.stdout = stdout
        sys.exit(f"Unknown error: {error}")
    print("Halted")
    if emulator.debug:
        print("\n\n")
        print(f"Counter: {hex(emulator.counter)}")
        emulator.dump_registers()
        emulator.dump_memory(len(code))
        delay = min(emulator.latencies)
        print(f"Latency: {(delay*(10**9)):.3f}ns")
        print(f"Or an execution speed of {1/delay}Hz")
    
    if emulator.guimode:
        gui.run()