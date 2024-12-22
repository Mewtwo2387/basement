from dataclasses import dataclass
from .token import Token


@dataclass
class MemoryBlock(Token):
    """
    A special token to mark a block of memory
    """

    def __str__(self) -> str:
        return f"  [Memory block. ID={hex(id(self))}, size={self.size}B]"
    
    def update(self, expr_size: int) -> None:
        # Increase the size of the memory block
        self.size += expr_size


@dataclass
class MemoryBlockOffset(Token):
    block:  MemoryBlock
    offset: int

    def __str__(self) -> str:
        block_id = hex(id(self.block))
        return f"    [{self.offset}B from block {block_id}]"