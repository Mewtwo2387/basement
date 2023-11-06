from data_size import WORD_SIZE
from dataclasses import dataclass


@dataclass
class Function:
    arg_num      : int
    var_sec_size : int
    address      : int

    @property
    def arg_sec_size(self):
        """
        Size of the argument section of the call frame.
        This also includes the field for the number of arguments.
        """
        return (self.arg_num + 1) * WORD_SIZE

    @property
    def call_frame_size(self):
        """
        Size of the function call frame in bytes. The call frame consists of the
        following elements:
            1. Argument section
            2. Local variable section
            3. Return address
        The argument section is always a multiple of WORD_SIZE, while the local
        variable section can have any size in bytes. The return address is
        always of has the size WORD_SIZE.
        """
        return ((self.arg_num + 1) * WORD_SIZE) + self.var_sec_size \
            + 2 * WORD_SIZE
    
    @property
    def func_data_list(self):
        return [self.arg_num, self.var_sec_size, self.address]