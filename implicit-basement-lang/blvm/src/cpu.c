#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "cpu.h"
#include "opcode.h"
#include "word_util.h"
#include "safe_alloc.h"


#define GET_IMMEDIATE_ARG() \
    ( cpu->ip += WORD_SIZE, bytes_to_word(cpu->ip - WORD_SIZE) )
#define TOS_PTR cpu->sp - 1

#define STACK_OVERFLOW_CHECK(cpu)                       \
    if ((cpu->sp - cpu->op_stack) >= cpu->stack_size) { \
        sprintf(cpu->state_msg, "Stack overflow");      \
        cpu->state = STATE_HALT_FAILURE;                \
        break;                                          \
    }

#define STACK_UNDERFLOW_CHECK(cpu, offset) \
    if ((cpu->sp - cpu->op_stack) < offset) {       \
        sprintf(cpu->state_msg, "Stack underflow"); \
        cpu->state = STATE_HALT_FAILURE;            \
        break;                                      \
    }

#define CALL_STACK_OVERFLOW_CHECK(cpu, offset) \
    if ((word_t)(cpu->fp - cpu->call_stack) + offset >= cpu->stack_size) { \
        sprintf(cpu->state_msg, "Call stack overflow");                    \
        cpu->state = STATE_HALT_FAILURE;                                   \
        break;                                                             \
    }

#define CALL_STACK_UNDERFLOW_CHECK(cpu, offset) \
    if ((cpu->fp - cpu->call_stack) < offset) {          \
        sprintf(cpu->state_msg, "Call stack underflow"); \
        cpu->state = STATE_HALT_FAILURE;                 \
        break;                                           \
    }

#define MEM_BOUND_CHECK(mem_addr, mem_size) \
    if (mem_addr >= mem_size) {                                       \
        sprintf(cpu->state_msg,                                       \
            "Memory address out of bounds (max addr:0x%lx <= 0x%lx)", \
            mem_size - 1, mem_addr                                    \
        );                                                            \
        cpu->state = STATE_HALT_FAILURE;                              \
        break;                                                        \
    }


void print_memory(CPU_t *cpu, size_t lbound, size_t ubound);
void print_instruction(CPU_t *cpu);
void print_stack(CPU_t *cpu);


void init_cpu(CPU_t *cpu, size_t memory_size, size_t stack_size) {
    if (memory_size == 0) {
        fprintf(stderr, "Error: Invalid memory size!\n");
        exit(EXIT_FAILURE);
    }

    *cpu = (CPU_t){ 0 };
    cpu->mem_size = memory_size;
    cpu->stack_size = stack_size;

    cpu->memory = safe_malloc(sizeof(*cpu->memory) * (memory_size));
    cpu->op_stack = safe_malloc(sizeof(*cpu->op_stack) * (stack_size));
    cpu->call_stack = safe_malloc(sizeof(*cpu->call_stack) * (stack_size));

    cpu->state_msg = safe_calloc(
                        END_STATE_MSG_LEN + 1,
                        sizeof(*cpu->state_msg)
                    );

    /* Initialize the CPU state as not running without error */
    cpu->state = STATE_HALT_SUCCESS;
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
    cpu->prog_ubound = cpu->memory + prog_size - WORD_SIZE;
    
    /* Initialize the stack pointers */
    cpu->sp = cpu->op_stack;
    cpu->fp = cpu->call_stack;
}

CPUState_t cpu_run(CPU_t *cpu) {
    cpu->state = STATE_RUNNING;

    /*
        Variable for translating from an array of bytes to a single integer and
        vice versa.
    */
    union word_bytes temp_bytes = { .word=0 };

    while (cpu->state == STATE_RUNNING) {
        Instruction_t instr = *(cpu->ip++);

        switch (instr) {
        case OP_ABORT:
            cpu->state = STATE_HALT_FAILURE;
            sprintf(cpu->state_msg, "Abort instruction encountered");
            break;
        case OP_DONE:
            if (cpu->state == STATE_RUNNING)
                cpu->state = STATE_HALT_SUCCESS;
        case OP_NOP:
            break;
        
        /* Stack manipulation instructions */
        case OP_LOAD8_CONST:
        case OP_LOAD16_CONST:
        case OP_LOAD32_CONST:
        case OP_LOAD64_CONST: {
            uint8_t size_idx = instr & 0x0F;

            /* Shorten the immediate argument to its supposed size. */
            memcpy(temp_bytes.bytes, cpu->ip, data_sizes[size_idx]);
            temp_bytes.word &= data_bitmasks[size_idx];

            /* Push the immediate argument from the program to stack */
            STACK_OVERFLOW_CHECK(cpu);
            *(cpu->sp++) = temp_bytes.word;

            /* Jump IP towards the end of the word sized argument */
            cpu->ip += WORD_SIZE;
            break;
        }
        case OP_LOAD8_ADDR:
        case OP_LOAD16_ADDR:
        case OP_LOAD32_ADDR:
        case OP_LOAD64_ADDR:
        case OP_LOAD8:
        case OP_LOAD16:
        case OP_LOAD32:
        case OP_LOAD64: {
            uint8_t instr_type = instr & 0xF0;
            uint8_t size_idx   = instr & 0x0F;
            word_t mem_addr;

            if (instr_type == OP_LOAD8_ADDR) {
                mem_addr = GET_IMMEDIATE_ARG();
            } else if (instr_type == OP_LOAD8) {
                /* Pop the memory address from the stack */
                STACK_UNDERFLOW_CHECK(cpu, 1);
                mem_addr = *(--cpu->sp);
            } else {
                fprintf(stderr, "Internal error: Unknown LOAD instruction\n");
                exit(EXIT_FAILURE);
            }

            MEM_BOUND_CHECK(mem_addr, cpu->mem_size);
            memcpy(temp_bytes.bytes, cpu->memory + mem_addr, WORD_SIZE);
            temp_bytes.word &= data_bitmasks[size_idx];

            /* Push the value from the memory to stack */
            STACK_OVERFLOW_CHECK(cpu);
            *(cpu->sp++) = temp_bytes.word;
            break;
        }

        case OP_STORE8_ADDR:
        case OP_STORE16_ADDR:
        case OP_STORE32_ADDR:
        case OP_STORE64_ADDR:
        case OP_STORE8:
        case OP_STORE16:
        case OP_STORE32:
        case OP_STORE64: {
            uint8_t instr_type = instr & 0xF0;
            uint8_t size_idx   = instr & 0x0F;
            word_t mem_addr;

            if (instr_type == OP_STORE8_ADDR) {
                mem_addr = GET_IMMEDIATE_ARG();
            } else if (instr_type == OP_STORE8) {
                /* Pop the memory address from the stack */
                STACK_UNDERFLOW_CHECK(cpu, 1);
                mem_addr = *(--cpu->sp);
            } else {
                fprintf(stderr, "Internal error: Unknown LOAD instruction\n");
                exit(EXIT_FAILURE);
            }
            MEM_BOUND_CHECK(mem_addr, cpu->mem_size);

            /* Pop the top value off the stack */
            STACK_UNDERFLOW_CHECK(cpu, 1);
            temp_bytes.word = *(--cpu->sp) & data_bitmasks[size_idx];

            /* Write the popped value from the stack to memory */
            memcpy(cpu->memory + mem_addr, temp_bytes.bytes,
                   data_sizes[size_idx]);
            break;
        }
        
        case OP_LOAD8_OFF_FP:
        case OP_LOAD16_OFF_FP:
        case OP_LOAD32_OFF_FP:
        case OP_LOAD64_OFF_FP: {
            uint8_t size_idx = instr & 0x0F;
            word_t mem_offset = GET_IMMEDIATE_ARG();

            CALL_STACK_UNDERFLOW_CHECK(cpu, mem_offset);
            memcpy(temp_bytes.bytes, cpu->fp - mem_offset, WORD_SIZE);
            temp_bytes.word &= data_bitmasks[size_idx];

            /* Push the value from the memory to stack */
            STACK_OVERFLOW_CHECK(cpu);
            *(cpu->sp++) = temp_bytes.word;
            break;
        }

        case OP_STORE8_OFF_FP :
        case OP_STORE16_OFF_FP:
        case OP_STORE32_OFF_FP:
        case OP_STORE64_OFF_FP: {
            uint8_t size_idx = instr & 0x0F;
            word_t mem_offset = GET_IMMEDIATE_ARG();

            /* Pop the top value off the stack */
            STACK_UNDERFLOW_CHECK(cpu, 1);
            temp_bytes.word = *(--cpu->sp) & data_bitmasks[size_idx];

            /* Write the popped value from the stack to memory */
            CALL_STACK_OVERFLOW_CHECK(cpu, mem_offset);
            memcpy(
                cpu->fp - mem_offset, temp_bytes.bytes, data_sizes[size_idx]
            );
            break;
        }

        case OP_LOAD_IP:
        case OP_LOAD_SP:
        case OP_LOAD_FP: {
            word_t ptr_val;
            ptr_val = (instr == OP_LOAD_IP)? (word_t)(cpu->ip - cpu->memory):
                      (instr == OP_LOAD_SP)? (word_t)cpu->sp :
                                             (word_t)cpu->fp ;

            /* Push the pointer, i.e. the raw address value, to the stack */
            STACK_OVERFLOW_CHECK(cpu);
            *(cpu->sp++) = ptr_val;
            break;
        }

        case OP_POP_RES: {
            /* Pop the state value from the stack. */
            STACK_UNDERFLOW_CHECK(cpu, 1);
            word_t state_val = *(--cpu->sp);

            if (CPU_STATE_UBOUND <= state_val)
                cpu->state = STATE_UNKNOWN;
            else
                cpu->state = state_val;
            break;
        }
        case OP_DISCARD:
            STACK_UNDERFLOW_CHECK(cpu, 1);
            cpu->sp -= 1;
            break;
        case OP_DUP:
            STACK_OVERFLOW_CHECK(cpu);
            *(cpu->sp) = *(TOS_PTR);
            cpu->sp += 1;
            break;
        case OP_SWAP_TOP:
        case OP_SWAP: {
            word_t offset = (instr == OP_SWAP_TOP)? 1 : GET_IMMEDIATE_ARG();

            STACK_UNDERFLOW_CHECK(cpu, offset);

            /* Copy the top element to a temporary storage */
            temp_bytes.word = *(TOS_PTR);

            /* Swap the two elements */
            *(TOS_PTR) = *(TOS_PTR - offset);
            *(TOS_PTR - offset) = temp_bytes.word;
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
            /* Pop two operands from the stack */
            STACK_UNDERFLOW_CHECK(cpu, 2);
            word_t op1 = *(--cpu->sp);
            word_t op2 = *(--cpu->sp);
            word_t op_result;

            switch (instr) {
            case OP_ADD:  op_result =   op2 + op1;  break;
            case OP_SUB:  op_result =   op2 - op1;  break;
            case OP_MUL:  op_result =   op2 * op1;  break;
            case OP_DIV:  op_result =   op2 / op1;  break;
            case OP_OR:   op_result =   op2 | op1;  break;
            case OP_XOR:  op_result =   op2 ^ op1;  break;
            case OP_AND:  op_result =   op2 & op1;  break;
            case OP_NOR:  op_result = ~(op2 | op1); break;
            case OP_NAND: op_result = ~(op2 & op1); break;
            case OP_LSH:  op_result =   op2 << op1; break;
            case OP_RSH:  op_result =   op2 >> op1; break;
            case OP_EQ:   op_result =   op2 == op1; break;
            case OP_LT:   op_result =   op2 <  op1; break;
            case OP_LEQ:  op_result =   op2 <= op1; break;
            case OP_GT:   op_result =   op2 >  op1; break;
            case OP_GEQ:  op_result =   op2 >= op1; break;
            }
            *(cpu->sp++) = op_result;
        }
        break;

        /* In-place binary operations */
        case OP_ADD_CONST: {
            /* 
                NOTE: Checking for stack overflow is unnecessary since this only
                requires at least 1 value on the stack.
            */
            STACK_UNDERFLOW_CHECK(cpu, 1);

            word_t op1 = GET_IMMEDIATE_ARG();
            word_t tos_val = *(--cpu->sp);
            *(cpu->sp++) = tos_val + op1;
            break;
        }

        /* Unary operations */
        case OP_UN_NEGATIVE:
        case OP_NOT: {
            /* 
                NOTE: Checking for stack overflow is unnecessary since this only
                requires at least 1 value on the stack.
            */
            STACK_UNDERFLOW_CHECK(cpu, 1);

            word_t op1 = *(--cpu->sp);
            word_t op_result;

            switch (instr) {
            case OP_UN_NEGATIVE: op_result = ~op1 + 1; break;
            case OP_NOT:         op_result = ~op1; break;
            }
            *(cpu->sp++) = op_result;
        }
        case OP_UN_POSITIVE:
            /*
                NOTE: The unary positive sign just returns the operand value as
                      is. This effectively does nothing to the operand.
            */
            STACK_UNDERFLOW_CHECK(cpu, 1);
            break;
        

        /* IO instructions */
        case OP_IN:
            /* Push the user's input from stdin to the stack */
            STACK_OVERFLOW_CHECK(cpu);
            *(cpu->sp++) = getchar();
            break;
        case OP_OUT_CHAR:
        case OP_OUT_NUM: {
            /* Pop the output to be written to stdout */
            STACK_UNDERFLOW_CHECK(cpu, 1);
            word_t output = *(--cpu->sp);

            if (instr == OP_OUT_CHAR)
                printf("%c", (char)(output & 0xFF));
            else
                printf("%ld", output);
            break;
        }
        case OP_OUT_IP:
            printf("IP: %p", cpu->ip);
            break;
        case OP_OUT_SP:
            printf("SP: %p", cpu->sp);
            break;
        case OP_OUT_ADDR: {
            word_t mem_addr = GET_IMMEDIATE_ARG();

            /* Fetch the value addressed by the memory and print it to stdout */
            MEM_BOUND_CHECK(mem_addr, cpu->mem_size);
            word_t output = bytes_to_word(cpu->memory + mem_addr);
            printf("@0x%16.16lx: 0x%lx", mem_addr, output);
            break;
        }
        
        /* Jump instructions */
        case OP_JUMP_ADDR:
        case OP_JUMP: {
            word_t target_mem_addr;
            if (instr == OP_JUMP_ADDR) {
                target_mem_addr = GET_IMMEDIATE_ARG();
            } else {
                STACK_UNDERFLOW_CHECK(cpu, 1);
                target_mem_addr = *(--cpu->sp);
            }
            MEM_BOUND_CHECK(target_mem_addr, cpu->mem_size);
            cpu->ip = cpu->memory + target_mem_addr;
            break;
        }
        case OP_JMPZ_ADDR:
        case OP_JMPNZ_ADDR:
        case OP_JMPZ:
        case OP_JMPNZ: {
            word_t target_mem_addr;
            if (instr == OP_JMPZ_ADDR || instr == OP_JMPNZ_ADDR) {
                target_mem_addr = GET_IMMEDIATE_ARG();
            } else {
                STACK_UNDERFLOW_CHECK(cpu, 1);
                target_mem_addr = *(--cpu->sp);
            }

            MEM_BOUND_CHECK(target_mem_addr, cpu->mem_size);
            STACK_UNDERFLOW_CHECK(cpu, 1);

            word_t tos_val = *(--cpu->sp);
            if ((instr == OP_JMPZ || instr == OP_JMPZ_ADDR) && tos_val == 0)
                cpu->ip = cpu->memory + target_mem_addr;
            if ((instr == OP_JMPNZ || instr == OP_JMPNZ_ADDR) && tos_val != 0)
                cpu->ip = cpu->memory + target_mem_addr;
            break;
        }

        /* Function instructions */
        case OP_CALL: {
            word_t func_struct_addr = GET_IMMEDIATE_ARG();

            MEM_BOUND_CHECK(func_struct_addr + 2 * WORD_SIZE, cpu->mem_size);

            /* Obtain the pertinent information about the function call */
            word_t arg_num =
                bytes_to_word(cpu->memory + func_struct_addr);
            word_t lcl_var_sec_size = 
                bytes_to_word(cpu->memory + func_struct_addr + WORD_SIZE);
            word_t func_code_addr =
                bytes_to_word(cpu->memory + func_struct_addr + 2 * WORD_SIZE);

            /*
                In total the size of the call frame is as follows:
                  arg_num * WORD_SIZE  (function argument array)
                + WORD_SIZE            (argument number)
                + lcl_var_seg_size     (local variable segment)
                + WORD_SIZE            (size of the local variable segment)
                + WORD_SIZE            (return address)
            */
            CALL_STACK_OVERFLOW_CHECK(
                cpu, (arg_num + 4) * WORD_SIZE + lcl_var_sec_size
            );

            /*
                Pop the arguments off the argument stack and push them to the
                call stack.
            */
            STACK_UNDERFLOW_CHECK(cpu, arg_num);
            for (word_t i = 0; i < arg_num; ++i) {
                temp_bytes.word = *(--cpu->sp);
                memcpy(cpu->fp, temp_bytes.bytes, WORD_SIZE);
                cpu->fp += WORD_SIZE;
            }

            /* Push the number of arguments to the call stack */
            memcpy(cpu->fp, cpu->memory + func_struct_addr, WORD_SIZE);
            cpu->fp += WORD_SIZE;

            /*
                Allocate space for the local variable section by incrementing
                the frame stack pointer with the section size in bytes.
            */
            cpu->fp += lcl_var_sec_size;

            /* Push the size of the local variable section to the call stack */
            memcpy(
                cpu->fp, cpu->memory + func_struct_addr + WORD_SIZE, WORD_SIZE
            );
            cpu->fp += WORD_SIZE;

            /* Push the return address to the call stack. */
            temp_bytes.word = (cpu->ip - cpu->memory);
            memcpy(cpu->fp, temp_bytes.bytes, WORD_SIZE);
            cpu->fp += WORD_SIZE;

            /* Jump to the function code. */
            cpu->ip = cpu->memory + func_code_addr;
            break;
        }
        case OP_RETURN: {
            /* Set the instruction pointer to the return address */
            CALL_STACK_UNDERFLOW_CHECK(cpu, WORD_SIZE);
            cpu->fp -= WORD_SIZE;
            cpu->ip = cpu->memory + bytes_to_word(cpu->fp);

            /* Pop off the local variable section. */
            CALL_STACK_UNDERFLOW_CHECK(cpu, WORD_SIZE);
            cpu->fp -= WORD_SIZE;
            word_t lcl_var_sec_size = bytes_to_word(cpu->fp);
            CALL_STACK_UNDERFLOW_CHECK(cpu, lcl_var_sec_size);
            cpu->fp -= lcl_var_sec_size;

            /* Remove the function arguments from the OPERAND STACK */
            CALL_STACK_UNDERFLOW_CHECK(cpu, WORD_SIZE);
            cpu->fp -= WORD_SIZE;
            word_t arg_num = bytes_to_word(cpu->fp);
            CALL_STACK_UNDERFLOW_CHECK(cpu, arg_num * WORD_SIZE);
            cpu->fp -= (arg_num * WORD_SIZE);
            break;
        }
        default:
            cpu->state = STATE_HALT_FAILURE;
            sprintf(cpu->state_msg, "Unknown opcode (0x%2.2x)", instr);
        }
    }

    return cpu->state;
}

void cpu_clear_memory(CPU_t *cpu) {
    if (cpu == NULL
        || cpu->memory == NULL
        || cpu->op_stack == NULL
        || cpu->call_stack == NULL
        || cpu->state == STATE_UNINITIALIZED
        || cpu->state == STATE_UNKNOWN)
    {
        fprintf(stderr, "Error: Attempted to clear the memory of an "
                        "uninitialized CPU\n");
        exit(EXIT_FAILURE);
    }
    memset(cpu->memory, 0, cpu->mem_size);
}

void free_cpu(CPU_t *cpu) {
    free(cpu->state_msg);
    free(cpu->memory);
    free(cpu->op_stack);
    free(cpu->call_stack);

    *cpu = (CPU_t){ 0 };
    cpu->state = STATE_UNINITIALIZED;
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

void print_instruction(CPU_t *cpu) {    
    /* Print header */
    printf("    ");
    for (size_t i = 0x00; i < 0x10; ++i)
        printf(" %2.2lx ", i);
    printf("\n");

    printf(
        "--|----------------------------------------------------------------"
    );
    for (uint8_t *ptr = cpu->memory; ptr <= cpu->prog_ubound; ++ptr){
        size_t idx = ptr - cpu->memory;
        if (idx % 16 == 0)
            printf("\n%2.2lx| ", idx);
        
        char c_front = (ptr == (cpu->ip - 1))? '[' : ' ';
        char c_back  = (ptr == (cpu->ip - 1))? ']' : ' ';
        printf("%c%2.2x%c", c_front, *ptr, c_back);
    }
    printf("\n\n");
}

void print_stack(CPU_t *cpu) {
    word_t *op_ptr = cpu->op_stack;
    uint8_t *call_ptr = cpu->call_stack;
    printf("Operand Stack:\n");
    while (op_ptr < cpu->sp) {
        printf("%16.16lx ", *(op_ptr++));
    }

    printf("\nCall Stack:\n");
    while (call_ptr < cpu->fp) {
        printf("%2.2x ", *(call_ptr++));
    }
    printf("\n");
}