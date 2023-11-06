#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "cpu.h"
#include "safe_alloc.h"
#include "word_util.h"
#include "instruction.h"


#define GET_IMMEDIATE_ARG() \
    ( cpu->ip += WORD_SIZE, bytes_to_word(cpu->ip - WORD_SIZE) )
#define TOS_PTR cpu->sp - 1

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
    /* Utility/temporary variables */

    word_t mem_addr, mem_val, mem_size, ptr_val;
    word_t tos_val, imm_arg, op1, op2, op_result;
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
            size_idx = instr & 0x0F;

            /* Shorten the immediate argument to its supposed size. */
            memcpy(temp_bytes.bytes, cpu->ip, data_sizes[size_idx]);
            temp_bytes.word &= data_bitmasks[size_idx];

            /* Push the immediate argument from the program to stack */
            *(cpu->sp++) = temp_bytes.word;

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
                /* Pop the memory address from the stack */
                mem_addr = *(--cpu->sp);
            } else {
                fprintf(stderr, "Internal error: Unknown LOAD instruction\n");
                exit(EXIT_FAILURE);
            }

            memcpy(temp_bytes.bytes, cpu->memory + mem_addr, WORD_SIZE);
            temp_bytes.word &= data_bitmasks[size_idx];

            /* Push the value from the memory to stack */
            *(cpu->sp++) = temp_bytes.word;
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
                /* Pop the memory address from the stack */
                mem_addr = *(--cpu->sp);
            } else {
                fprintf(stderr, "Internal error: Unknown LOAD instruction\n");
                exit(EXIT_FAILURE);
            }

            /* Pop the top value off the stack */
            temp_bytes.word = *(--cpu->sp) & data_bitmasks[size_idx];

            /* Write the popped value from the stack to memory */
            memcpy(cpu->memory + mem_addr, temp_bytes.bytes,
                   data_sizes[size_idx]);
            break;
        
        case OP_LOAD8_OFF_FP:
        case OP_LOAD16_OFF_FP:
        case OP_LOAD32_OFF_FP:
        case OP_LOAD64_OFF_FP:
            size_idx = instr & 0x0F;
            imm_arg = GET_IMMEDIATE_ARG();
            
            memcpy(temp_bytes.bytes, cpu->fp - imm_arg, WORD_SIZE);
            temp_bytes.word &= data_bitmasks[size_idx];

            /* Push the value from the memory to stack */
            *(cpu->sp++) = temp_bytes.word;
            break;
        

        case OP_STORE8_OFF_FP :
        case OP_STORE16_OFF_FP:
        case OP_STORE32_OFF_FP:
        case OP_STORE64_OFF_FP:
            size_idx = instr & 0x0F;
            imm_arg = GET_IMMEDIATE_ARG();

            /* Pop the top value off the stack */
            temp_bytes.word = *(--cpu->sp) & data_bitmasks[size_idx];

            /* Write the popped value from the stack to memory */
            memcpy(cpu->fp - imm_arg, temp_bytes.bytes, data_sizes[size_idx]);
            break;

        case OP_LOAD_IP:
        case OP_LOAD_SP:
        case OP_LOAD_FP:
            ptr_val = (instr == OP_LOAD_IP)? (word_t)(cpu->ip - cpu->memory ):
                      (instr == OP_LOAD_SP)? (word_t)cpu->sp :
                                             (word_t)cpu->fp ;

            *(cpu->sp++) = ptr_val;
            break;

        case OP_POP_RES:
            tos_val = *(--cpu->sp);
            if (CPU_STATE_UBOUND <= tos_val)
                cpu->state = STATE_UNKNOWN;
            else
                cpu->state = tos_val;
            break;
        case OP_DISCARD:
            cpu->sp -= 1;
            break;
        case OP_DUP:
            *(cpu->sp) = *(TOS_PTR);
            cpu->sp += 1;
            break;
        case OP_SWAP_TOP:
        case OP_SWAP: {
            word_t offset = (instr == OP_SWAP_TOP)? 1 : GET_IMMEDIATE_ARG();

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
            op1 = *(--cpu->sp);
            op2 = *(--cpu->sp);

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
        case OP_ADD_CONST:
            op1 = GET_IMMEDIATE_ARG();
            tos_val = *(--cpu->sp);
            *(cpu->sp++) = tos_val + op1;
            break;

        /* Unary operations */
        case OP_UN_NEGATIVE:
        case OP_NOT: {
            op1 = *(--cpu->sp);

            switch (instr) {
            case OP_UN_NEGATIVE: op_result = ~op1 + 1; break;
            case OP_NOT:         op_result = ~op1; break;
            }
            *(cpu->sp++) = op_result;
        }
        case OP_UN_POSITIVE:
            /* NOTE: This does nothing to the operand */
            // TODO: CHECK IF THERE'S AN OPERAND ON TOP OF THE STACK
            break;
        

        /* IO instructions */
        case OP_IN:
            *(cpu->sp++) = getchar();
            break;
        case OP_OUT_CHAR:
        case OP_OUT_NUM:
            output = *(--cpu->sp);
            if (instr == OP_OUT_CHAR)
                printf("%c", (char)(output & 0xFF));
            else
                printf("%ld", output);
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
                mem_addr = *(--cpu->sp);

            cpu->ip = cpu->memory + mem_addr;
            break;
        case OP_JMPZ_ADDR:
        case OP_JMPNZ_ADDR:
        case OP_JMPZ:
        case OP_JMPNZ:
            if (instr == OP_JMPZ_ADDR || instr == OP_JMPNZ_ADDR)
                mem_addr = GET_IMMEDIATE_ARG();
            else
                /* Pop memory address off the stack */
                mem_addr = *(--cpu->sp);

            tos_val = *(--cpu->sp);
            if ((instr == OP_JMPZ || instr == OP_JMPZ_ADDR) && tos_val == 0)
                cpu->ip = cpu->memory + mem_addr;
            if ((instr == OP_JMPNZ || instr == OP_JMPNZ_ADDR) && tos_val != 0)
                cpu->ip = cpu->memory + mem_addr;
            break;

        /* Function instructions */
        case OP_CALL: {
            word_t func_struct_addr = GET_IMMEDIATE_ARG();

            /*
                Get the number of arguments the function requires.
                NOTE: Address to the value is `func_struct_addr`
            */
            word_t arg_num = bytes_to_word(cpu->memory + func_struct_addr);

            /*
                Pop the arguments off the argument stack and push them to the
                call stack.
            */
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
                NOTE: Address to the value is `func_struct_addr + W`
            */
            word_t lcl_var_seg_size = 
                bytes_to_word(cpu->memory + func_struct_addr + WORD_SIZE);
            cpu->fp += lcl_var_seg_size;

            /* Push the size of the local variable section to the call stack */
            memcpy(cpu->fp, cpu->memory + func_struct_addr + WORD_SIZE,
                   WORD_SIZE);
            cpu->fp += WORD_SIZE;

            /* Push the return address to the call stack. */
            temp_bytes.word = (cpu->ip - cpu->memory);
            memcpy(cpu->fp, temp_bytes.bytes, WORD_SIZE);
            cpu->fp += WORD_SIZE;

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
            cpu->fp -= WORD_SIZE;
            cpu->ip = cpu->memory + bytes_to_word(cpu->fp);

            /* Pop off the local variable section. */
            cpu->fp -= WORD_SIZE;
            word_t lcl_var_sect_size = bytes_to_word(cpu->fp);
            cpu->fp -= lcl_var_sect_size;

            /* Remove the function arguments from the OPERAND STACK */
            cpu->fp -= WORD_SIZE;
            word_t arg_num = bytes_to_word(cpu->fp);
            cpu->fp -= (arg_num * WORD_SIZE);
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
    if (cpu == NULL
        || cpu->memory == NULL
        || cpu->op_stack == NULL
        || cpu->call_stack == NULL
        || cpu->state == UNINITIALIZED)
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
    cpu->state = UNINITIALIZED;
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