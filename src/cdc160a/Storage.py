"""
    CDC 160A Storage

    Provides registers and memory for the CDC 160A emulator. All values are
    stored in signed, 16-bit integers. Since the 160A is a 12-bit machine,
    the most significant 4 bits are not used, and must be 0.

    Storage includes all registers and the largest supported memory, 8 banks
    of 4096 words.

    The design is motivated by, though differs from, the CDC 160A Programming
    Manual, which can be found at
    https://archive.org/details/bitsavers_cdc160023aingManual1960_4826291

    TODO(emintz): move method descriptions to doc strings.
"""
import numpy as np
from typing import Final
from cdc160a import Arithmetic

# MCS modes and corresponding codes
MCS_MODE: Final[list[str]] = ["BFR", "DIR", "IND", "REL"]
MCS_MODE_BFR: Final[int] = 0
MCS_MODE_DIR: Final[int] = 1
MCS_MODE_IND: Final[int] = 2
MCS_MODE_REL: Final[int] = 3

class Storage:
    def __init__(self):
        # Core memory, 8 banks of 4096 12-bit words
        self.memory = np.zeros((8, 4096), dtype=np.int16)

        # Registers that support instruction execution, including arithmetic,
        # program flow, and I/O.

        # Accumulator
        self.a_register = 0
        # Auxiliary accumulator, called A' in the programming manual. It
        # acts as an auxiliary transmission register for information moving
        # between other registers. This is the output register of the
        # adder (a.k.a. borrow pyramid).
        self.aprime_register = 0
        # Buffer data register, which contains the word of information being
        # transferred to or from storage during a buffered I/O operation.
        self.buffer_data_register = 0
        # Buffer entrance register, which holds the address to or from which
        # information flows during buffered I/O. Its contents may be
        # transferred to storage or the A register.
        self.buffer_entrance_register = 0
        # Buffer exit register, which holds the last word address + 1 to or
        # from which information should flow during buffered operation.
        self.buffered_exit_register = 0
        # The following two members comprise the F register, which holds
        # the decoded instruction being executed. In the hardware, it
        # contains 12 bits; the most significant 6 bits contain the
        # effective instruction, while the least significant bits
        # contain the instruction's effective E component.
        self.f_instruction = 1
        self.f_e = 0
        # An 8-bit register that holds data being written to the paper
        # tape punch, thereby releasing the Z register for use by
        # high speed I/O.
        self.punch_storage_register = 0
        # Contains the address of the current instruction
        self.p_register = 0
        # Contains the storage address currently being referenced either
        # for an instruction or for an operand.
        self.s_register = 0
        # A transient register that holds information between storage and
        # peripheral equipment on the normal (that is, unbuffered) I/O
        # channel.
        self.z_register = 0

        # Storage bank control registers. These reside in the storage bank
        # control and specify the memory bank used by the supported addressing
        # modes. Bank control registers are named after the mode they support.
        # Note that the address contained in the P register always resides
        # in the relative storage bank.
        self.buffer_storage_bank = 0
        self.direct_storage_bank = 0
        self.indirect_storage_bank = 0
        self.relative_storage_bank = 0

        # Status registers, not guaranteed to correspond to the
        # hardware. These govern status display
        self.z_contains_instruction_address = False
        # Run/Stop, True if and only if the computer is running.
        self.run_stop_status = False
        # Error, True if and only if an ERR instruction caused
        # the computer to halt.
        self.err_status = False
        # SEL, True when an EXF or EXC instruction is executed and
        # False when the instruction has completed (i.e. the selection
        # is completed).
        self.sel_status = False
        # OUT, true only during normal output operations, False
        # otherwise
        self.out_status = False
        # IN, True only during normal output operations, False otherwise
        self.in_status = False
        # IBA, True during all buffer input operations, False otherwise
        self.iba_status = False
        # OBA, True during all buffer output operations, False otherwise
        self.oba_status = False
        # TODO(emintz): Storage Cycle, A, B, C, or D, with D being Relative
        # See MODES above. It's unclear what should happen with a direct access
        self.storage_cycle = MCS_MODE_REL
        # The address of the next instruction. The 160-A has no corresponding
        # register. This is a hack that supports deferring the move
        # to the next instruction until we determine that the machine
        # has not halted itself.
        self.__next_address = 0

    def a_negative(self) -> bool:
        return self.a_register & 0o4000 != 0

    def a_not_zero(self) -> bool:
        return self.a_register != 0

    def a_positive(self) -> bool:
        return self.a_register & 0o4000 == 0

    def a_zero(self) -> bool:
        return self.a_register == 0o0000

    def advance_to_next_instruction(self) -> None:
        self.p_register = self.__next_address

    def a_to_s_buffer(self) -> None:
        self.a_to_z()
        self.write_buffer_bank(self.s_register, self.a_register)

    def a_to_s_direct(self) -> None:
        self.a_to_z()
        self.write_direct_bank(self.s_register, self.a_register)

    def a_to_s_indirect(self) -> None:
        self.a_to_z()
        self.write_indirect_bank(self.s_register, self.z_register)

    def a_to_s_relative(self) -> None:
        self.a_to_z()
        self.write_relative_bank(self.s_register, self.z_register)

    def a_to_z(self) -> None:
        self.z_register = self.a_register

    def complement_a(self) -> None:
        self.a_register = self.a_register ^ 0o7777

    # Declares that the next memory access will be in the buffer bank.
    def mode_buffer(self) -> None:
        self.storage_cycle = MCS_MODE_BFR

    # Declares that the next memory access will be in the direct bank.
    def mode_direct(self):
        self.storage_cycle = MCS_MODE_DIR

    # Declares that the next memory access will be in the indirect bank.
    def mode_indirect(self) -> None:
        self.storage_cycle = MCS_MODE_IND

    # Declares that the next memory access will be in the relative bank.
    def mode_relative(self) -> None:
        self.storage_cycle = MCS_MODE_REL

    # Storage mode for specific memory mode. This is a placeholder,
    # as the documentation is unclear what should happen.
    def mode_specific(self) -> None:
        self.storage_cycle = MCS_MODE_REL

    # Move the contents of the P (program counter) register to the
    # S (storage address to reference) register.
    def p_to_s(self) -> None:
        self.s_register = self.p_register

    # Take the contents in the direct bank and the address contained
    # in the S register to the Z (transient) register.
    def s_direct_to_z(self) -> None:
        self.z_register = self.read_direct_from_s()

    def s_indirect_to_z(self) -> None:
        self.z_register = self.read_indirect_from_s()

    # Take the contents in the relative bank and the address contained
    # in the S register to the Z (transient) register.
    def s_address_relative_to_z(self)-> None:
        self.z_register = self.read_relative_bank(self.s_register)

    def unpack_instruction(self) -> None:
        self.p_to_s()
        self.s_address_relative_to_z()
        self.f_e = self.z_register & 0o77
        self.f_instruction = (self.z_register >> 6) & 0o77

    def e_to_s(self) -> None:
        self.s_register = self.f_e

    # Copy the contents of the E register to Z. This is used by No Address
    # instructions
    def e_to_z(self) -> None:
        self.z_register = self.f_e

    def forward_indirect_to_s(self) -> None:
        self.s_register = self.read_relative_bank(self.p_register + self.f_e)

    def get_program_counter(self) -> int:
        return self.p_register

    # Take the memory address from the G address, the current instruction
    # location plus 1.
    def g_address_to_s(self) -> None:
        self.s_register = self.p_register + 1

    # Take the memory address from a two word instruction's G (second word)
    def g_to_s(self) -> None:
        self.s_register = self.read_relative_bank(self.p_register + 1)

    def g_to_z(self) -> None:
        self.s_register = self.p_register + 1
        self.z_register = self.read_relative_bank(self.s_register)

    def next_address(self) -> int:
        """
        Returns the address of the next instruction. Used for testing

        :return: the address of the next instruction that will be
                 performed.
        """
        return self.__next_address

    def next_after_one_word_instruction(self) -> None:
        self.__next_address = Arithmetic.add(self.p_register, 1)

    def next_after_two_word_instruction(self) -> None:
        self.__next_address = Arithmetic.add(self.p_register, 2)

    # Calculate the relative backward address, the contents of P
    # minus the contents of E, and place the result in S. Relative
    # backward instructions invoke this to move their operand
    # address to S.
    def relative_backward_to_s(self) -> None:
        self.s_register = self.p_register - self.f_e

    # Calculate the relative forward address, the contents of P plus
    # the contents of E, and place the result in S. Relative forward
    # instructions invoke this to move their operand addresses to S
    def relative_forward_to_s(self) -> None:
        self.s_register = self.p_register + self.f_e

    def s_to_p(self) -> None:
        """
        Move the contents of the S (i.e. effective address) register
        to the P (program address) register

        :return: None
        """
        self.p_register = self.s_register

    # Set the buffer storage bank to the least significant bits in
    # the specified value.
    def set_buffer_storage_bank(self, value: int) -> None:
        self.buffer_storage_bank = value & 0o7

    # Set the direct storage bank to the least significant bits in
    # the specified value.
    def set_direct_storage_bank(self, value: int) -> None:
        self.direct_storage_bank = value & 0o7

    # Set the indirect storage bank to the least significant bits in
    # the specified value.
    def set_indirect_storage_bank(self, value: int) -> None:
        self.indirect_storage_bank = value & 0o7

    def set_next_instruction_address(self, next_address: int) -> None:
        self.__next_address = next_address

    def set_program_counter(self, address: int) -> None:
        self.p_register = address

    # Set the relative storage bank to the least significant bits in
    # the specified value.
    def set_relative_storage_bank(self, value: int) -> None:
        self.relative_storage_bank = value & 0o7

    def read_absolute(self, bank: int, address: int):
        """
        Read and return the 12-bit value stored at the specified
        address in the specified memory bank.

        :param bank: memory bank. Must be in [0 .. 7] inclusive
        :param address: address within the memory bank. Must be in
               [0 .. 0x7777] inclusive
        :return: the contents of the specified memory location
        """
        return self.memory[bank, address]

    # Read and return the value from a specified address in the
    # buffer storage bank. The least significant 12 bits in the
    # provided address argument specifies the address to be read.
    def read_buffer_bank(self, address: int):
        return self.memory[self.buffer_storage_bank, address & 0o7777]

    # Read and return the value from a specified address in the
    # direct storage bank. The least significant 12 bits in the
    # provided address argument specifies the address to be read.
    def read_direct_bank(self, address: int):
        return self.memory[self.direct_storage_bank, address & 0o7777]

    def read_direct_from_s(self):
        return self.read_direct_bank(self.s_register)

    # Read and return the value from a specified address in the
    # indirect storage bank. The least significant 12 bits in the
    # provided address argument specifies the address to be read.
    def read_indirect_bank(self, address: int):
        return self.memory[self.indirect_storage_bank, address & 0o7777]

    def read_indirect_from_s(self):
        return self.read_indirect_bank(self.s_register)

    # Read and return the value from a specified address in the
    # relative storage bank. The least significant 12 bits in the
    # provided address argument specifies the address to be read.
    def read_relative_bank(self, address: int):
        return self.memory[self.relative_storage_bank, address & 0o7777]

    # Read the contents of the specific address: bank 0, location
    # 0o7777
    def read_specific(self):
        return self.memory[0, 0o7777]

    def set_s_and_read_indirect(self, address: int):
        self.s_register = address
        return self.read_indirect_bank(self.s_register)

    def p_plus_one_to_s(self):
        self.s_register = self.p_register + 1

    def run(self) -> None:
        self.run_stop_status = True

    def specific_to_s(self) -> None:
        self.s_register = 0o7777

    def stop(self) -> None:
        self.run_stop_status = False

    def s_direct_to_a(self):
        self.z_register = self.read_direct_from_s()

    def s_indirect_to_a(self):
        self.a_register = self.read_indirect_bank(self.s_register)

    def s_relative_to_a(self) -> None:
        self.a_register = self.read_relative_bank(self.s_register)

    def s_to_next_address(self) -> None:
        self.__next_address = self.s_register

    def write_absolute(self, bank: int, address: int, value: int) -> None:
        """
        Write the specified value to the specified address in the specified
        memory bank.

        :param bank: the target memory bank. Holds the destination
               of the write operation. Must be in [0 .. 7] inclusive
        :param address: the cell to which to write
        :param value: the value to write. Must be in [0 .. 0o0000]
               inclusive.
        :return: None
        """
        self.memory[bank, address] = value

    # Write the specified value to the specified address in the
    # buffer storage bank. The least significant 12 bits in the
    # provided address argument specifies the address to be written.
    def write_buffer_bank(self, address: int, value: int) -> None:
        self.memory[self.buffer_storage_bank, address & 0o7777] = (
                value & 0o7777)

    # Write the specified value to the specified address in the
    # direct storage bank. The least significant 12 bits in the
    # provided address argument specifies the address to be written.
    def write_direct_bank(self, address: int, value: int) -> None:
        self.memory[self.direct_storage_bank, address & 0o7777] = (
                value & 0o7777)

    # Write the specified value to the specified address in the
    # indirect storage bank. The least significant 12 bits in the
    # provided address argument specifies the address to be written.
    def write_indirect_bank(self, address: int, value: int) -> None:
        self.memory[self.indirect_storage_bank, address & 0o7777] = (
                value & 0o7777)

    # Write the specified value to the specified address in the
    # relative storage bank. The least significant 12 bits in the
    # provided address argument specifies the address to be written.
    def write_relative_bank(self, address: int, value: int) -> None:
        self.memory[self.relative_storage_bank, address & 0o7777] = (
                value & 0o7777)

    # Write the specified value to the specific address, bank 0,
    # location 0o7777.
    def write_specific(self, value: int):
        self.memory[0, 0o7777] = value


    def z_to_a(self) -> None:
        self.a_register = self.z_register

if __name__ == "__main__":
    print('Running storage in stand-alone mode.\n')
    storage = Storage()
    print('Program completed.\n')

