.include stdio

LDAI 0
LDXI 0
LDYI 1

label loop
    STA nconsole
    ADD
    MVXY
    MVAX

JNC loop