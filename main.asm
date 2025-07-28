.include stdio

const counter x8800
const iostatus xFFF0
const begininput 2

label main
    LDAI fire^
    CALL println

label loop
    CALL getinput

    LDAI input^
    LDXI ^input
    CALL println

JMP loop

HALT

label fire
.ascii The world is on fire