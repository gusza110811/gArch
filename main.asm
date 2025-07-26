const console xFFF8
const nconsole xFFF9
const counter x8800
const iostatus xFFF0
const begininput 2

label main
    LDAI fire^
    CALL println

label loop
    LDAI begininput
    STA console
    LDAI 1
    STA iostatus

    LDA console
    LDXI 0
    STX iostatus
    STA console

JMP loop

HALT

label println
    ; To preserve state
    PUSHA
    PUSHX
    PUSHY

    ; Get source
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
    ; Print new line
    LDAI 10
    STA console

    ; Revert to previous state
    POPY
    POPX
    POPA
RET

HALT

label fire
.ascii The world is on fire

label world
.ascii HELLO WORLD!!!

label keyboard
0