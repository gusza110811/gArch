const console xFFF8
const counter x8800

LDAI word^
STA counter

label printloop
    ; print
    LDXI 0
    LDY counter
    LDV
    STA console

    ; increment
    LDX counter
    LDYI 1
    ADD
    STA counter

    ; check loop condition
    LDXI 0
    LDY counter
    LDV

JNZ printloop
HALT

label word
.ascii The world is on fucking fire