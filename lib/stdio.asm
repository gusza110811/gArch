alias highcounter xFDFE
alias counter xFDFF
alias inputstart xFF

const input xFC00
const iostate xFFF0

const console xFFF8
const nconsole xFFF9

label getinput
    ; preserve state
    PUSHA
    PUSHX
    PUSHY

    ; initialize
    LDYI inputstart
    LDAI 2
    STA console
    LDAI 1
    STA iostate

    ; loop
    label inputloop
        LDXI 1
        ADD
        MVAY
        LDA console
        LDXI xFC
        STV
    JNZ inputloop

    ; end
    LDAI 0
    STA iostate

    ; return to previous state
    POPY
    POPX
    POPA
RET

label println
    ; To preserve state
    PUSHA
    PUSHX
    PUSHY

    ; Get source
    STA counter
    STX highcounter

    CALL printloop

    ; Print new line
    LDAI 10
    STA console

    ; Revert to previous state
    POPY
    POPX
    POPA
RET

label print
    ; To preserve state
    PUSHA
    PUSHX
    PUSHY

    ; Get source
    STA counter
    STX highcounter

    CALL printloop

    ; Revert to previous state
    POPY
    POPX
    POPA
RET

label printloop
    ; print
    LDX highcounter
    LDY counter
    LDV
    STA console

    ; increment
    LDX counter
    LDYI 1
    ADD
    STA counter

    ; check carry
    JNC nocarry
    LDX highcounter
    LDYI 1
    ADD
    STA highcounter

    label nocarry

    ; check loop condition
    LDX highcounter
    LDY counter
    LDV

    JNZ printloop
RET