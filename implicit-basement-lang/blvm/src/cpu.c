#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "cpu.h"
#include "safe_alloc.h"
#include "word_util.h"
#include "instruction.h"

/* NOTE: Incrementing the stack pointer: cpu->sp -= N
         Decrementing the stack pointer: cpu->sp += N */

#define INCREMENT_STACK_PTR(stack_ptr) stack_ptr -= WORD_SIZE
#define DECREMENT_STACK_PTR(stack_ptr) stack_ptr += WORD_SIZE

#define GET_IMMEDIATE_ARG() \
    ( cpu->ip += WORD_SIZE, bytes_to_word(cpu->ip - WORD_SIZE) )
#define POP_WORD_FROM_STACK() \
    ( cpu->sp += WORD_SIZE, bytes_to_word(cpu->sp - WORD_SIZE) )

/* Get data from memory as a word sized integer */
#define GET_MEMORY(addr) \
    bytes_to_word(cpu->memory + addr)

/* Push a word sized integer to stack */
#define PUSH_WORD_TO_STACK(word) {              \
        word_to_bytes(temp_bytes, word);        \
        cpu->sp -= WORD_SIZE;                   \
        memcpy(cpu->sp, temp_bytes, WORD_SIZE); \
    }
/* Push word number of bytes to stack */
#define PUSH_BYTES_TO_STACK(bytes) \
    memcpy(cpu->sp, temp_bytes, WORD_SIZE)
/* Store word number of bytes to a temporary array */
#define TEMP_STORE_BYTES(dest_temp_bytes, src_bytes) \
    memcpy(dest_temp_bytes, src_bytes, WORD_SIZE)

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
        .heap_ptr=NULL,
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
    cpu->heap_ptr = cpu->prog_bounds[1] + 1;
    
    /* Initialize the stack pointers */
    cpu->sp = cpu->memory + (cpu->mem_size - 1);
    cpu->fp = cpu->sp;
}

CPUState_t cpu_run(CPU_t *cpu) {
    /* Utility/temporary variables */
    word_t mem_addr, mem_val, tos_val, ptr_val;
    word_t op1, op2, op_result;
    word_t user_input, output;
    uint8_t temp_bytes[WORD_SIZE];

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
        case OP_LOAD_CONST:
            INCREMENT_STACK_PTR(cpu->sp);
            /* Push the immediate argument from the program to stack */
            memcpy(cpu->sp, cpu->ip, WORD_SIZE);
            /* Jump IP towards the end of the word sized argument */
            cpu->ip += WORD_SIZE;
            break;
        case OP_LOAD_ADDR:
        case OP_LOAD:
            mem_addr = (instr == OP_LOAD_ADDR)? GET_IMMEDIATE_ARG() : 
                                                POP_WORD_FROM_STACK();

            TEMP_STORE_BYTES(temp_bytes, cpu->memory + mem_addr);

            /* Push the vavlue from the memory to stack */
            INCREMENT_STACK_PTR(cpu->sp);
            memcpy(cpu->sp, temp_bytes, WORD_SIZE);
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
        case OP_STORE_ADDR:
        case OP_STORE:
            mem_addr = (instr == OP_STORE_ADDR)? GET_IMMEDIATE_ARG() :
                                                 POP_WORD_FROM_STACK();

            TEMP_STORE_BYTES(temp_bytes, cpu->sp);

            /* Write the popped value from the stack to memory */
            memcpy(cpu->memory + mem_addr, temp_bytes, WORD_SIZE);
            DECREMENT_STACK_PTR(cpu->sp);
            break;
        case OP_POP_RES:
            tos_val = POP_WORD_FROM_STACK();
            if (CPU_STATE_MAX <= tos_val)
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
            memcpy(temp_bytes, cpu->sp, WORD_SIZE);

            /* Swap the two elements */
            memcpy(cpu->sp, cpu->sp + offset, WORD_SIZE);
            memcpy(cpu->sp + offset, temp_bytes, WORD_SIZE);
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
            case OP_ADD:  op_result = op1 + op2; break;
            case OP_SUB:  op_result = op1 - op2; break;
            case OP_MUL:  op_result = op1 * op2; break;
            case OP_DIV:  op_result = op1 / op2; break;
            case OP_OR:   op_result = op1 | op2; break;
            case OP_AND:  op_result = op1 & op2; break;
            case OP_NOR:  op_result = ~(op1 | op2); break;
            case OP_NAND: op_result = ~(op1 & op2); break;
            case OP_XOR:  op_result = op1 ^ op2; break;
            case OP_LSH:  op_result = op1 << op2; break;
            case OP_RSH:  op_result = op1 >> op2; break;
            case OP_EQ:   op_result = op1 == op2; break;
            case OP_LT:   op_result = op1 <  op2; break;
            case OP_LEQ:  op_result = op1 <= op2; break;
            case OP_GT:   op_result = op1 >  op2; break;
            case OP_GEQ:  op_result = op1 >= op2; break;
            }
            PUSH_WORD_TO_STACK(op_result);
        }
        break;

        /* In-place binary operations */
        case OP_ADD_CONST:
        case OP_SUB_CONST:
            op1 = GET_IMMEDIATE_ARG();
            tos_val = POP_WORD_FROM_STACK();

            if (instr == OP_ADD_CONST)
                tos_val += op1;
            else
                tos_val -= op1;
            
            PUSH_WORD_TO_STACK(tos_val);
            break;
        case OP_ADD_ADDR:
        case OP_SUB_ADDR:
            mem_addr = GET_IMMEDIATE_ARG();
            op1 = GET_MEMORY(mem_addr);
            tos_val = POP_WORD_FROM_STACK();

            if (instr == OP_ADD_ADDR)
                tos_val += op1;
            else
                tos_val -= op1;

            PUSH_WORD_TO_STACK(tos_val);
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
            output = GET_MEMORY(mem_addr);
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
        case OP_CALL:
            /* Push the return address, the current instruction pointer */
            mem_addr = cpu->ip - cpu->memory;
            mem_addr += WORD_SIZE;   // Skip the immediate argument
            PUSH_WORD_TO_STACK(mem_addr);

            // Get the function address
            mem_addr = GET_IMMEDIATE_ARG();

            cpu->ip = cpu->memory + mem_addr;
            cpu->fp = cpu->sp;
            break;
        case OP_RET: {
            /* Set the instruction pointer to the return address */
            cpu->ip = cpu->memory + bytes_to_word(cpu->fp);

            /* Decrement frame pointer to point to the number of args */
            DECREMENT_STACK_PTR(cpu->fp);
            /* Get the number of function arguments */
            word_t arg_num = bytes_to_word(cpu->fp);

            /* Pop off the arguments such that the frame pointer points to the
               return value.
               NOTE: "Decrementing stack pointers" is adding the offset to the
                     stack pointers. */
            cpu->fp += (arg_num + 1) * WORD_SIZE;

            /* Set the return value as the CURRENT top value of the stack */
            memcpy(cpu->fp, cpu->sp, WORD_SIZE);

            /* Move down the stack pointer effectively popping off the
               call frame.
               The top of the stack should be the return value of the function
            */
            cpu->sp = cpu->fp;
        }
            break;
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
            .heap_ptr=NULL,
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