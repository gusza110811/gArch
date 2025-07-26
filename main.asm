const console xFFF8
const nconsole xFFF9
const counter x8800

label main
    LDAI fire^
    CALL println
    LDAI world^
    CALL println
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