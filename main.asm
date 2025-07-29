.include stdio

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