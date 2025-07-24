const console xFFF8
const num_console xFFF9
const num1 x8800
const num2 x8801
const sum x880F

; console input does not exist yet lol
LDAI 20
STA num1
LDAI 32
STA num2

; main
LDX num1
LDY num2
ADD
STA sum

MOV num_console num1
LDAI '+
STA console
MOV num_console num2
LDAI '=
STA console
MOV num_console sum