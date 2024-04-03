from dataclasses import dataclass


@dataclass(frozen=True)
class Instruction:
    code: int
    name: str


## ---------- CPU State/Miscellaneous instructions ---------- ##
ABORT = Instruction(0x00, "abort")
NOP   = Instruction(0x01, "nop")
DONE  = Instruction(0x02, "done")

## ---------- Memory manipulating instructions ---------- ##
LOAD8_CONST    = Instruction(0x10, "load8_const")
LOAD16_CONST   = Instruction(0x11, "load16_const")
LOAD32_CONST   = Instruction(0x12, "load32_const")
LOAD64_CONST   = Instruction(0x13, "load64_const")

LOAD8_ADDR     = Instruction(0x20, "load8_addr")
LOAD16_ADDR    = Instruction(0x21, "load16_addr")
LOAD32_ADDR    = Instruction(0x22, "load32_addr")
LOAD64_ADDR    = Instruction(0x23, "load64_addr")

STORE8_ADDR    = Instruction(0x30, "store8_addr")
STORE16_ADDR   = Instruction(0x31, "store16_addr")
STORE32_ADDR   = Instruction(0x32, "store32_addr")
STORE64_ADDR   = Instruction(0x33, "store64_addr")

LOAD8          = Instruction(0x40, "load8")
LOAD16         = Instruction(0x41, "load16")
LOAD32         = Instruction(0x42, "load32")
LOAD64         = Instruction(0x43, "load64")

STORE8         = Instruction(0x50, "store8")
STORE16        = Instruction(0x51, "store16")
STORE32        = Instruction(0x52, "store32")
STORE64        = Instruction(0x53, "store64")

LOAD8_OFF_FP   = Instruction(0x60, "load8_off_fp")
LOAD16_OFF_FP  = Instruction(0x61, "load16_off_fp")
LOAD32_OFF_FP  = Instruction(0x62, "load32_off_fp")
LOAD64_OFF_FP  = Instruction(0x63, "load64_off_fp")

STORE8_OFF_FP  = Instruction(0x70, "store8_off_fp")
STORE16_OFF_FP = Instruction(0x71, "store16_off_fp")
STORE32_OFF_FP = Instruction(0x72, "store32_off_fp")
STORE64_OFF_FP = Instruction(0x73, "store64_off_fp")

LOAD_IP        = Instruction(0x80, "load_ip")
LOAD_SP        = Instruction(0x81, "load_sp")
LOAD_FP        = Instruction(0x82, "load_fp")
POP_RES        = Instruction(0x83, "pop_res")
DISCARD        = Instruction(0x84, "discard")
DUP            = Instruction(0x85, "dup")
SWAP_TOP       = Instruction(0x86, "swap_top")
SWAP           = Instruction(0x87, "swap")
COPY           = Instruction(0x88, "copy")

## ---------- Arithmetic operations ---------- ##
ADD           = Instruction(0x90, "add")
ADD_CONST     = Instruction(0x91, "add_const")
SUB           = Instruction(0x92, "sub")
MUL           = Instruction(0x93, "mul")
DIV           = Instruction(0x94, "div")
MOD           = Instruction(0x95, "mod")
UN_POSITIVE   = Instruction(0x96, "un_positive")
UN_NEGATIVE   = Instruction(0x97, "un_negative")
## ---------- Arithmetic floating point operations ---------- ##
ADD_F32       = Instruction(0x98, "add_f32")
ADD_F64       = Instruction(0x99, "add_f64")
SUB_F32       = Instruction(0x9A, "sub_f32")
SUB_F64       = Instruction(0x9B, "sub_f64")
MUL_F32       = Instruction(0x9C, "mul_f32")
MUL_F64       = Instruction(0x9D, "mul_f64")
DIV_F32       = Instruction(0x9E, "div_f32")
DIV_F64       = Instruction(0x9F, "div_f64")
## ---------- Type casting operations ---------- ##
OP_INT_TO_F32 = Instruction(0xA0, "op_int_to_f32")
OP_INT_TO_F64 = Instruction(0xA1, "op_int_to_f64")
OP_F32_TO_INT = Instruction(0xA2, "op_f32_to_int")
OP_F64_TO_INT = Instruction(0xA3, "op_f64_to_int")
## ---------- Bitwise logical operations ---------- ##
OR            = Instruction(0xA4, "or")
AND           = Instruction(0xA5, "and")
NOR           = Instruction(0xA6, "nor")
NAND          = Instruction(0xA7, "nand")
XOR           = Instruction(0xA8, "xor")
LSH           = Instruction(0xA9, "lsh")
RSH           = Instruction(0xAA, "rsh")
NOT           = Instruction(0xAB, "not")
## ---------- Comparison operations ---------- ##
EQ            = Instruction(0xAC, "eq")
LT            = Instruction(0xAD, "lt")
LEQ           = Instruction(0xAE, "leq")
GT            = Instruction(0xAF, "gt")
GEQ           = Instruction(0xB0, "geq")

## ---------- Input/Output instructions ---------- ##
IN       = Instruction(0xC0, "in")
OUT_CHAR = Instruction(0xC1, "out_char")
OUT_NUM  = Instruction(0xC2, "out_num")
OUT_F32  = Instruction(0xC3, "out_f32")
OUT_F64  = Instruction(0xC4, "out_f64")

## ---------- Jump instructions ---------- ##
JUMP_ADDR  = Instruction(0xD0, "jump_addr")
JMPZ_ADDR  = Instruction(0xD1, "jmpz_addr")
JMPNZ_ADDR = Instruction(0xD2, "jmpnz_addr")
JUMP       = Instruction(0xD3, "jump")
JMPZ       = Instruction(0xD4, "jmpz")
JMPNZ      = Instruction(0xD5, "jmpnz")

## ------- Function instructions ------- ##
CALL   = Instruction(0xE0, "call")
RETURN = Instruction(0xE1, "return")