#ifndef _OPCODES_H
#define _OPCODES_H

typedef enum {
    OP_ABORT = 0x00,
    OP_NOP   = 0x01,
    OP_DONE  = 0x02,


    /* ---------- Memory manipulating instructions ---------- */
    OP_LOAD8_CONST    = 0x10,
    OP_LOAD16_CONST   = 0x11,
    OP_LOAD32_CONST   = 0x12,
    OP_LOAD64_CONST   = 0x13,

    OP_LOAD8_ADDR     = 0x20,
    OP_LOAD16_ADDR    = 0x21,
    OP_LOAD32_ADDR    = 0x22,
    OP_LOAD64_ADDR    = 0x23,

    OP_STORE8_ADDR    = 0x30,
    OP_STORE16_ADDR   = 0x31,
    OP_STORE32_ADDR   = 0x32,
    OP_STORE64_ADDR   = 0x33,

    OP_LOAD8          = 0x40,
    OP_LOAD16         = 0x41,
    OP_LOAD32         = 0x42,
    OP_LOAD64         = 0x43,

    OP_STORE8         = 0x50,
    OP_STORE16        = 0x51,
    OP_STORE32        = 0x52,
    OP_STORE64        = 0x53,

    OP_LOAD8_OFF_FP   = 0x60,
    OP_LOAD16_OFF_FP  = 0x61,
    OP_LOAD32_OFF_FP  = 0x62,
    OP_LOAD64_OFF_FP  = 0x63,

    OP_STORE8_OFF_FP  = 0x70,
    OP_STORE16_OFF_FP = 0x71,
    OP_STORE32_OFF_FP = 0x72,
    OP_STORE64_OFF_FP = 0x73,

    OP_LOAD_IP        = 0x80,
    OP_LOAD_SP        = 0x81,
    OP_LOAD_FP        = 0x82,
    OP_POP_RES        = 0x83,
    OP_DISCARD        = 0x84,
    OP_DUP            = 0x85,
    OP_SWAP_TOP       = 0x86,
    OP_SWAP           = 0x87,
    OP_COPY           = 0x88,


    /* ---------- Arithmetic integer operations ---------- */
    OP_ADD         = 0x90,
    OP_ADD_CONST   = 0x91,
    OP_SUB         = 0x92,
    OP_MUL         = 0x93,
    OP_DIV         = 0x94,
    OP_MOD         = 0X95,
    OP_UN_POSITIVE = 0x96,
    OP_UN_NEGATIVE = 0x97,
    /* ---------- Arithmetic floating point operations ---------- */
    OP_ADD_F32     = 0x98,
    OP_ADD_F64     = 0x99,
    OP_SUB_F32     = 0x9A,
    OP_SUB_F64     = 0x9B,
    OP_MUL_F32     = 0x9C,
    OP_MUL_F64     = 0x9D,
    OP_DIV_F32     = 0x9E,
    OP_DIV_F64     = 0x9F,
    /* ---------- Type casting operations ---------- */
    OP_INT_TO_F32  = 0xA0,
    OP_INT_TO_F64  = 0xA1,
    OP_F32_TO_INT  = 0xA2,
    OP_F64_TO_INT  = 0xA3,
    /* ---------- Bitwise logical operations ---------- */
    OP_OR          = 0xA4,
    OP_AND         = 0xA5,
    OP_NOR         = 0xA6,
    OP_NAND        = 0xA7,
    OP_XOR         = 0xA8,
    OP_LSH         = 0xA9,
    OP_RSH         = 0xAA,
    OP_NOT         = 0xAB,
    /* ---------- Comparison operations ---------- */
    OP_EQ          = 0xAC,
    OP_LT          = 0xAD,
    OP_LEQ         = 0xAE,
    OP_GT          = 0xAF,
    OP_GEQ         = 0xB0,


    /* ---------- Input/Output instructions ---------- */
    OP_IN       = 0xC0,
    OP_OUT_CHAR = 0xC1,
    OP_OUT_NUM  = 0xC2,
    OP_OUT_F32  = 0xC3,
    OP_OUT_F64  = 0xC4,

    /* ---------- Jump instructions ---------- */
    OP_JUMP_ADDR  = 0xD0,
    OP_JMPZ_ADDR  = 0xD1,
    OP_JMPNZ_ADDR = 0xD2,
    OP_JUMP       = 0xD3,
    OP_JMPZ       = 0xD4,
    OP_JMPNZ      = 0xD5,


    /* ------- Function instructions ------- */
    OP_CALL   = 0xE0,
    OP_RETURN = 0xE1
} Instruction_t;
 
#endif