#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "cpu.h"
#include "safe_alloc.h"
#include "word_util.h"
#include "instruction.h"

/* 
    NOTE: Incrementing the stack pointer: cpu->sp -= N
          Decrementing the stack pointer: cpu->sp += N
*/
#define INCREMENT_STACK_PTR(stack_ptr) stack_ptr -= WORD_SIZE
#define DECREMENT_STACK_PTR(stack_ptr) stack_ptr += WORD_SIZE
#define NEXT_STACK_ELEM(stack_ptr) stack_ptr - WORD_SIZE
#define PREV_STACK_ELEM(stack_ptr) stack_ptr + WORD_SIZE
#define STACK_PTR_OFFSET(stack_ptr, offset) stack_ptr - offset

#define GET_IMMEDIATE_ARG() \
    ( cpu->ip += WORD_SIZE, bytes_to_word(cpu->ip - WORD_SIZE) )
#define POP_WORD_FROM_STACK() \
    ( cpu->sp += WORD_SIZE, bytes_to_word(cpu->sp - WORD_SIZE) )
#define PUSH_WORD_TO_STACK(n) {                       \
        temp_bytes.word = n;                          \
        cpu->sp -= WORD_SIZE;                         \
        memcpy(cpu->sp, temp_bytes.bytes, WORD_SIZE); \
    }


void print_memory(CPU_t *cpu, size_t lbound, size_t ubound);

void init_cpu(CPU_t *cpu, size_t memory_size) {
    if (memory_size == 0) {
        fprintf(stderr, "Error: Invalid memory size!\n");
        exit(EXIT_FAILURE);
    }

    *cpu = (CPU_t){
        .state=HALT_SUCCESS,
        .mem_size=memory_size,
        .prog_bounds={ NULL, NULL },
        .ip=NULL,
        .sp=NULL,
        .fp=NULL
    };
    cpu->state_msg = safe_calloc(END_STATE_MSG_LEN + 1,
                                 sizeof(*cpu->state_msg));
    cpu->memory = safe_malloc(sizeof(*cpu->memory) * (memory_size));
}

void cpu_load_program(CPU_t *cpu, uint8_t *prog_bytecode, size_t prog_size) {
    if (prog_size > cpu->mem_size) {
        fprintf(stderr, "Error: Program size exceeds the CPU memory!\n");
        exit(EXIT_FAILURE);
    }

    /* Copy the program to memory */
    memcpy(cpu->memory, prog_bytecode, prog_size);

    /* Initialize the instruction pointer and memory section bounds */
    cpu->ip = cpu->memory;
    cpu->prog_bounds[0] = cpu->ip;
    cpu->prog_bounds[1] = cpu->ip + prog_size - WORD_SIZE;
    
    /* Initialize the stack pointers */
    cpu->sp = cpu->memory + (cpu->mem_size - 1);
    cpu->fp = cpu->sp;
}

CPUState_t cpu_run(CPU_t *cpu) {
    /* Utility/temporary variables */
    word_t mem_addr, mem_val, mem_size, tos_val, ptr_val;
    word_t op1, op2, op_result;
    word_t user_input, output;

    union word_bytes temp_bytes = { .word=0 };
    uint8_t size_idx, instr_type;

    for (;;) {
        Instruction_t instr = *(cpu->ip++);

        switch (instr) {
        case OP_ABORT:
            cpu->state = HALT_FAILED;
            sprintf(cpu->state_msg, "Abort instruction encountered");
        case OP_DONE:
            goto exit_loop;
        case OP_NOP:
            break;
        
        /* Stack manipulation instructions */
        case OP_LOAD8_CONST:
        case OP_LOAD16_CONST:
        case OP_LOAD32_CONST:
        case OP_LOAD64_CONST:
            size_idx   = instr & 0x0F;

            /* Shorten the immediate to its supposed size. */
            memcpy(temp_bytes.bytes, cpu->ip, data_sizes[size_idx]);
            temp_bytes.word &= data_bitmasks[size_idx];

            /* Push the immediate argument from the program to stack */
            INCREMENT_STACK_PTR(cpu->sp);
            memcpy(cpu->sp, temp_bytes.bytes, WORD_SIZE);

            /* Jump IP towards the end of the word sized argument */
            cpu->ip += WORD_SIZE;
            break;

        case OP_LOAD8_ADDR:
        case OP_LOAD16_ADDR:
        case OP_LOAD32_ADDR:
        case OP_LOAD64_ADDR:
        case OP_LOAD8:
        case OP_LOAD16:
        case OP_LOAD32:
        case OP_LOAD64:
            instr_type = instr & 0xF0;
            size_idx   = instr & 0x0F;

            if (instr_type == OP_LOAD8_ADDR) {
                mem_addr = GET_IMMEDIATE_ARG();
            } else if (instr_type == OP_LOAD8) {
                mem_addr = POP_WORD_FROM_STACK();
            } else {
                fprintf(stderr, "Internal error: Unknown LOAD instruction\n");
                exit(EXIT_FAILURE);
            }

            memcpy(temp_bytes.bytes, cpu->memory + mem_addr, WORD_SIZE);
            temp_bytes.word &= data_bitmasks[size_idx];

            /* Push the value from the memory to stack */
            INCREMENT_STACK_PTR(cpu->sp);
            memcpy(cpu->sp, temp_bytes.bytes, WORD_SIZE);
            break;

        case OP_STORE8_ADDR:
        case OP_STORE16_ADDR:
        case OP_STORE32_ADDR:
        case OP_STORE64_ADDR:
        case OP_STORE8:
        case OP_STORE16:
        case OP_STORE32:
        case OP_STORE64:
            instr_type = instr & 0xF0;
            size_idx   = instr & 0x0F;

            if (instr_type == OP_STORE8_ADDR) {
                mem_addr = GET_IMMEDIATE_ARG();
            } else if (instr_type == OP_STORE8) {
                mem_addr = POP_WORD_FROM_STACK();
            } else {
                fprintf(stderr, "Internal error: Unknown LOAD instruction\n");
                exit(EXIT_FAILURE);
            }

            /* Pop the top value off the stack */
            memcpy(temp_bytes.bytes, cpu->sp, WORD_SIZE);
            temp_bytes.word &= data_bitmasks[size_idx];
            DECREMENT_STACK_PTR(cpu->sp);

            /* Write the popped value from the stack to memory */
            memcpy(cpu->memory + mem_addr, temp_bytes.bytes,
                   data_sizes[size_idx]);
            break;
        
        case OP_LOAD8_OFF_FP:
        case OP_LOAD16_OFF_FP:
        case OP_LOAD32_OFF_FP:
        case OP_LOAD64_OFF_FP:
            size_idx = instr & 0x0F;
            tos_val = GET_IMMEDIATE_ARG();
            
            memcpy(
                temp_bytes.bytes,
                STACK_PTR_OFFSET(cpu->fp, -((int64_t)tos_val)),
                WORD_SIZE
            );
            temp_bytes.word &= data_bitmasks[size_idx];

            /* Push the value from the memory to stack */
            INCREMENT_STACK_PTR(cpu->sp);
            memcpy(cpu->sp, temp_bytes.bytes, WORD_SIZE);
            break;
        

        case OP_STORE8_OFF_FP :
        case OP_STORE16_OFF_FP:
        case OP_STORE32_OFF_FP:
        case OP_STORE64_OFF_FP:
            size_idx = instr & 0x0F;
            tos_val = GET_IMMEDIATE_ARG();

            /* Pop the top value off the stack */
            memcpy(temp_bytes.bytes, cpu->sp, WORD_SIZE);
            temp_bytes.word &= data_bitmasks[size_idx];
            DECREMENT_STACK_PTR(cpu->sp);

            /* Write the popped value from the stack to memory */
            memcpy(
                STACK_PTR_OFFSET(cpu->fp, -((int64_t)tos_val)),
                temp_bytes.bytes,
                data_sizes[size_idx]
            );
            break;

        case OP_LOAD_IP:
        case OP_LOAD_SP:
        case OP_LOAD_FP:
            ptr_val = (instr == OP_LOAD_IP)? (word_t)cpu->ip :
                      (instr == OP_LOAD_SP)? (word_t)cpu->sp :
                                             (word_t)cpu->fp ;
            ptr_val -= (word_t)cpu->memory;
            PUSH_WORD_TO_STACK(ptr_val);
            break;

        case OP_POP_RES:
            tos_val = POP_WORD_FROM_STACK();
            if (CPU_STATE_UBOUND <= tos_val)
                cpu->state = STATE_UNKNOWN;
            else
                cpu->state = tos_val;
            break;
        case OP_DISCARD:
            DECREMENT_STACK_PTR(cpu->sp);
            break;
        case OP_DUP:
            INCREMENT_STACK_PTR(cpu->sp);
            memcpy(cpu->sp, cpu->sp + WORD_SIZE, WORD_SIZE);
            break;
        case OP_SWAP_TOP:
        case OP_SWAP: {
            word_t offset = (instr == OP_SWAP_TOP)? 1 : GET_IMMEDIATE_ARG();

            /* Copy the top element to a temporary storage */
            memcpy(temp_bytes.bytes, cpu->sp, WORD_SIZE);

            /* Swap the two elements */
            memcpy(cpu->sp, cpu->sp + offset, WORD_SIZE);
            memcpy(cpu->sp + offset, temp_bytes.bytes, WORD_SIZE);
        }
        break;

        /* Binary operations */
        case OP_ADD:
        case OP_SUB:
        case OP_MUL:
        case OP_DIV:
        case OP_OR:
        case OP_AND:
        case OP_NOR:
        case OP_NAND:
        case OP_XOR:
        case OP_LSH:
        case OP_RSH:
        case OP_EQ:
        case OP_LT:
        case OP_LEQ:
        case OP_GT:
        case OP_GEQ: {
            op1 = POP_WORD_FROM_STACK();
            op2 = POP_WORD_FROM_STACK();

            switch (instr) {
            case OP_ADD:  op_result =   op1 + op2;  break;
            case OP_SUB:  op_result =   op1 - op2;  break;
            case OP_MUL:  op_result =   op1 * op2;  break;
            case OP_DIV:  op_result =   op1 / op2;  break;
            case OP_OR:   op_result =   op1 | op2;  break;
            case OP_XOR:  op_result =   op1 ^ op2;  break;
            case OP_AND:  op_result =   op1 & op2;  break;
            case OP_NOR:  op_result = ~(op1 | op2); break;
            case OP_NAND: op_result = ~(op1 & op2); break;
            case OP_LSH:  op_result =   op1 << op2; break;
            case OP_RSH:  op_result =   op1 >> op2; break;
            case OP_EQ:   op_result =   op1 == op2; break;
            case OP_LT:   op_result =   op1 <  op2; break;
            case OP_LEQ:  op_result =   op1 <= op2; break;
            case OP_GT:   op_result =   op1 >  op2; break;
            case OP_GEQ:  op_result =   op1 >= op2; break;
            }
            PUSH_WORD_TO_STACK(op_result);
        }
        break;

        /* In-place binary operations */
        case OP_ADD_CONST:
            op1 = GET_IMMEDIATE_ARG();
            tos_val = POP_WORD_FROM_STACK();
            PUSH_WORD_TO_STACK(op1 + tos_val);
            break;

        /* Unary operations */
        case OP_UN_NEGATIVE:
        case OP_NOT: {
            op1 = POP_WORD_FROM_STACK();

            switch (instr) {
            case OP_UN_NEGATIVE: op_result = ~op1 + 1; break;
            case OP_NOT:         op_result = ~op1; break;
            }
            PUSH_WORD_TO_STACK(op_result);
        }
        case OP_UN_POSITIVE:
            /* NOTE: This does nothing to the operand */
            // TODO: CHECK IF THERE'S AN OPERAND ON TOP OF THE STACK
            break;
        

        /* IO instructions */
        case OP_IN:
            user_input = getchar();
            PUSH_WORD_TO_STACK(user_input);
            break;
        case OP_OUT_CHAR:
        case OP_OUT_NUM:
            output = POP_WORD_FROM_STACK();
            if (instr == OP_OUT_CHAR)
                printf("%c", (char)(output & 0xFF));
            else
                printf("0x%lx", output);
            break;
        case OP_OUT_IP:
            printf("IP: %p", cpu->ip);
            break;
        case OP_OUT_SP:
            printf("SP: %p", cpu->sp);
            break;
        case OP_OUT_ADDR:
            mem_addr = GET_IMMEDIATE_ARG();
            output = bytes_to_word(cpu->memory + mem_addr);
            printf("@0x%16.16lx: 0x%lx", mem_addr, output);
            break;
        
        /* Jump instructions */
        case OP_JUMP_ADDR:
        case OP_JUMP:
            if (instr == OP_JUMP_ADDR)
                mem_addr = GET_IMMEDIATE_ARG();
            else
                mem_addr = POP_WORD_FROM_STACK();

            cpu->ip = cpu->memory + mem_addr;
            break;
        case OP_JMPZ_ADDR:
        case OP_JMPNZ_ADDR:
        case OP_JMPZ:
        case OP_JMPNZ:
            if (instr == OP_JMPZ_ADDR || instr == OP_JMPNZ_ADDR)
                mem_addr = GET_IMMEDIATE_ARG();
            else
                mem_addr = POP_WORD_FROM_STACK();

            tos_val = bytes_to_word(cpu->sp);
            if ((instr == OP_JMPZ || instr == OP_JMPZ_ADDR) && tos_val == 0)
                cpu->ip = cpu->memory + mem_addr;
            if ((instr == OP_JMPNZ || instr == OP_JMPNZ_ADDR) && tos_val != 0)
                cpu->ip = cpu->memory + mem_addr;
            break;

        /* Function instructions */
        case OP_CALL: {
            word_t func_struct_addr = GET_IMMEDIATE_ARG();

            /*
                Push the number of arguments to stack
                NOTE: Address to the value is `func_struct_addr`
            */
            INCREMENT_STACK_PTR(cpu->sp);
            memcpy(cpu->sp, cpu->memory + func_struct_addr, WORD_SIZE);

            /*
                Allocate space for the local variable section by incrementing
                the stack pointer with the section size in bytes.
                NOTE: Address to the value is `func_struct_addr + W`
            */
            word_t lcl_var_sect_size = 
                bytes_to_word(cpu->memory + func_struct_addr + WORD_SIZE);
            cpu->sp = STACK_PTR_OFFSET(cpu->sp, +lcl_var_sect_size);

            /* Push the size of the local variable section to stack */
            INCREMENT_STACK_PTR(cpu->sp);
            memcpy(cpu->sp, cpu->memory + func_struct_addr + WORD_SIZE,
                   WORD_SIZE);

            /* Push the return address to the stack. */
            mem_addr = (cpu->ip - cpu->memory) + WORD_SIZE;
            PUSH_WORD_TO_STACK(mem_addr);

            /* Update the frame pointer so it points to the end of call frame */
            cpu->fp = cpu->sp;

            /* 
                Jump to the function code.
                NOTE: Address to the value is `func_struct_addr + 2 * W`
            */
            mem_addr =
                bytes_to_word(cpu->memory + func_struct_addr + 2 * WORD_SIZE);
            cpu->ip = cpu->memory + mem_addr;
            break;
        }
        case OP_RETURN: {
            /* Set the instruction pointer to the return address */
            cpu->ip = cpu->memory + bytes_to_word(cpu->fp);

            /* Pop off the local variable section. */
            DECREMENT_STACK_PTR(cpu->fp);
            word_t lcl_var_sect_size = bytes_to_word(NEXT_STACK_ELEM(cpu->fp));
            cpu->fp = STACK_PTR_OFFSET(cpu->fp, -lcl_var_sect_size);

            /* Pop off the function argument section. */
            DECREMENT_STACK_PTR(cpu->fp);
            word_t arg_num = bytes_to_word(NEXT_STACK_ELEM(cpu->fp));
            cpu->fp = STACK_PTR_OFFSET(cpu->fp, -(arg_num * WORD_SIZE));

            /* Push the return value to the new top of the stack */
            memcpy(cpu->fp, cpu->sp, WORD_SIZE);
            cpu->sp = cpu->fp;
            break;
        }
        default:
            cpu->state = HALT_FAILED;
            sprintf(cpu->state_msg, "Unknown opcode (0x%2.2x)", instr);
            goto exit_loop;
        }
    }

exit_loop:
    return cpu->state;
}

void cpu_clear_memory(CPU_t *cpu) {
    if (cpu == NULL || cpu->memory == NULL || cpu->state == UNINITIALIZED) {
        fprintf(stderr, "Error: Attempted to clear the memory of an "
                        "uninitialized CPU\n");
    }
    memset(cpu->memory, 0, cpu->mem_size);
}

void free_cpu(CPU_t *cpu) {
    free(cpu->state_msg);
    free(cpu->memory);
    *cpu = (CPU_t){
            .state=UNINITIALIZED,
            .mem_size=0,
            .prog_bounds={ NULL, NULL },
            .ip=NULL,
            .sp=NULL,
            .fp=NULL
        };
}

void print_memory(CPU_t *cpu, size_t lbound, size_t ubound) {
    int n = 0;
    printf("\nMEMORY:\n");
    for (size_t i = lbound; i < ubound; ++i) {
        if ((n % WORD_SIZE) == 0 && n != 0)
            printf("----------\n");
        n++;
        printf("[%lx]: %2.2x\n", i, cpu->memory[i]);
    }
}