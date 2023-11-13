## ---------- CPU State/Miscellaneous instructions ---------- ##
ABORT = 0x00
NOP   = 0x01
DONE  = 0x02

## ---------- Stack manipulation instructions ---------- ##
LOAD8_CONST    = 0x10
LOAD16_CONST   = 0x11
LOAD32_CONST   = 0x12
LOAD64_CONST   = 0x13

LOAD8_ADDR     = 0x20
LOAD16_ADDR    = 0x21
LOAD32_ADDR    = 0x22
LOAD64_ADDR    = 0x23

STORE8_ADDR    = 0x30
STORE16_ADDR   = 0x31
STORE32_ADDR   = 0x32
STORE64_ADDR   = 0x33

LOAD8          = 0x40
LOAD16         = 0x41
LOAD32         = 0x42
LOAD64         = 0x43

STORE8         = 0x50
STORE16        = 0x51
STORE32        = 0x52
STORE64        = 0x53

LOAD8_OFF_FP   = 0x60
LOAD16_OFF_FP  = 0x61
LOAD32_OFF_FP  = 0x62
LOAD64_OFF_FP  = 0x63

STORE8_OFF_FP  = 0x70
STORE16_OFF_FP = 0x71
STORE32_OFF_FP = 0x72
STORE64_OFF_FP = 0x73

LOAD_IP        = 0x80
LOAD_SP        = 0x81
LOAD_FP        = 0x82
POP_RES        = 0x83
DISCARD        = 0x84
DUP            = 0x85
SWAP_TOP       = 0x86
SWAP           = 0x87

## ---------- Arithmetic operations ---------- ##
ADD         = 0x90
ADD_CONST   = 0x91
SUB         = 0x92
MUL         = 0x93
DIV         = 0x94
UN_POSITIVE = 0x95
UN_NEGATIVE = 0x96
## ---------- Bitwise logical operations ---------- ##
OR          = 0x97
AND         = 0x98
NOR         = 0x99
NAND        = 0x9A
XOR         = 0x9B
LSH         = 0x9C
RSH         = 0x9D
NOT         = 0x9E
## ---------- Comparison operations ---------- ##
EQ          = 0xA0
LT          = 0xA1
LEQ         = 0xA2
GT          = 0xA3
GEQ         = 0xA4

## ---------- Input/Output instructions ---------- ##
IN       = 0xB0
OUT_CHAR = 0xB1
OUT_NUM  = 0xB2
OUT_IP   = 0xB3
OUT_SP   = 0xB4
OUT_ADDR = 0xB5

## ---------- Jump instructions ---------- ##
JUMP_ADDR  = 0xC0
JMPZ_ADDR  = 0xC1
JMPNZ_ADDR = 0xC2
JUMP       = 0xC3
JMPZ       = 0xC4
JMPNZ      = 0xC5

## ------- Function instructions ------- ##
CALL   = 0xD0
RETURN = 0xD1