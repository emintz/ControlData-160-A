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
from enum import Enum, unique
import numpy as np
from typing import Final
from cdc160a import Arithmetic
from cdc160a.IOStatus import IOStatus

# MCS modes and corresponding codes
MCS_MODE: Final[list[str]] = ["BFR", "DIR", "IND", "REL"]
# TODO(emintz): use an Enum class.
MCS_MODE_BFR: Final[int] = 0
MCS_MODE_DIR: Final[int] = 1
MCS_MODE_IND: Final[int] = 2
MCS_MODE_REL: Final[int] = 3

@unique
class InterruptLock(Enum):
    FREE = 0
    LOCKED = 1
    UNLOCK_PENDING = 2

class Storage:
    def __init__(self):
        """
        Constructor

        """
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
        self.buffer_exit_register = 0
        # The following field must be True when the computer is buffering
        # and False when it is not. The buffering device is responsible
        # for maintaining its state. A master clear will set it to
        # false.
        self.buffering = False
        # The following two members comprise the F register, which holds
        # the decoded instruction being executed. In the hardware, it
        # contains 12 bits; the most significant 6 bits contain the
        # effective instruction, while the least significant bits
        # contain the instruction's effective E component.
        self.f_instruction = 1
        self.f_e = 0
        # Interrupt lock. The machine can service an interrupt if and only if
        # the interrupt lock value is InterruptLock.FREE. Otherwise,
        # the machine cannot honor an interrupt request.
        #
        # The CLI instruction sets the interrupt lock to
        # InterruptLock.UNLOCK_PENDING. The interrupt handler will set
        # the lock to InterruptLock.FREE after the next instruction
        # runs.
        self.interrupt_lock = InterruptLock.FREE
        # Normal I/O Status.
        self.normal_io_status = IOStatus.IDLE
        """
        Pending interrupt requests. Interrupt numbers 10, 20, 30, and 40
        are mapped to array index 0, 1, 2, and 3 respectively.
        """
        self.interrupt_requests = [False, False, False, False]
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
        # Machine hung status. Some errors, e.g. illegal external function,
        # delay the machine indefinitely. If machine_hung is True, such
        # an error has occurred and the machine will hang.
        self.machine_hung = False
        # TODO(emintz): Storage Cycle, A, B, C, or D, with D being Relative
        # See MODES above. It's unclear what should happen with a direct access
        self.storage_cycle = MCS_MODE_REL
        # The address of the next instruction. The 160-A has no corresponding
        # register. This is a hack that supports deferring the move
        # to the next instruction until we determine that the machine
        # has not halted itself.
        self.__next_address = 0
        # Jump switch settings. The console is responsible for
        # keeping its value current.
        self.__jump_switch_mask = 0
        # Stop switch mask. The console is responsible for
        # keeping its value current.
        self.__stop_switch_mask = 0

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

    def a_times_10(self) -> None:
        self.a_register = Arithmetic.times_ten(self.a_register)

    def a_times_100(self) -> None:
        self.a_register = Arithmetic.times_hundred(self.a_register)

    def a_to_absolute(self, bank: int, address: int) -> None:
        """
        A -> Z and [address(bank)]

        :param bank: memory bank
        :param address: target address
        :return: None
        """
        self.z_register = self.a_register
        self.memory[bank, address] = self.z_register

    def a_to_s_absolute(self, bank: int):
        self.a_to_absolute(bank, self.s_register)

    def a_to_s_buffer(self) -> None:
        self.a_to_s_absolute(self.buffer_storage_bank)
        self.mode_buffer()

    def a_to_buffer_data_register(self) -> None:
        self.buffer_data_register = self.a_register

    def a_to_buffer_entrance_register(self) -> None:
        self.buffer_entrance_register = self.a_register

    def a_to_buffer_exit_register(self) -> None:
        self.buffer_exit_register = self.a_register

    def a_to_s_direct(self) -> None:
        self.a_to_s_absolute(self.direct_storage_bank)
        self.mode_direct()

    def a_to_s_indirect(self) -> None:
        self.a_to_s_absolute(self.indirect_storage_bank)
        self.mode_indirect()

    def a_to_s_relative(self) -> None:
        self.a_to_s_absolute(self.relative_storage_bank)
        self.mode_relative()

    def a_to_specific(self) -> None:
        self.a_to_absolute(0, 0o7777)
        self.mode_specific()

    def a_to_z(self) -> None:
        self.z_register = self.a_register

    def add_e_to_a(self) -> None:
        self.add_to_a(self.f_e)

    def add_s_address_to_a(self, bank: int) -> None:
        from_memory = int(self.memory[bank, self.s_register])
        self.add_to_a(from_memory)

    def add_to_a(self, increment: int) -> None:
        self.__sum_to_a(self.a_register, increment)

    def buffer_data_to_memory(self) -> bool:
        """
        Move the contents of the buffer data register to the memory
        location in the buffer entrance register in the buffer memory
        bank, then increment the buffer entrance register. Successive
        calls move store data in adjacent memory locations in the buffer
        storage bank.

        Note that the buffer entrance register contents must be strictly
        less than the buffer exit contents when this method is invoked.
        The computer must be buffering when this method is entered.

        :return: True if the buffer is not full (i.e. more data can be
                 transferred into the buffer); False if  the invocation
                 filled the buffer.
        """
        assert self.buffer_entrance_register < self.buffer_exit_register
        self.memory[self.buffer_storage_bank, self.buffer_entrance_register] =\
            self.buffer_data_register
        self.buffer_entrance_register += 1
        return self.buffer_entrance_register < self.buffer_exit_register

    def clear(self) -> None:
        self.buffering = False
        self.a_register = 0
        self.p_register = 0
        self.f_e = 0
        self.f_instruction = 0
        self.z_register = 0
        self.relative_storage_bank = 0
        self.run_stop_status = False
        self.interrupt_lock = InterruptLock.FREE
        self.machine_hung = False

    def complement_a(self) -> None:
        self.a_register = self.a_register ^ 0o7777

    def and_e_with_a(self) -> None:
        self.z_register = self.f_e & 0o0077
        self.a_register &= self.z_register

    def and_s_address_with_a(self, bank: int) -> None:
        self.z_register = self.memory[bank, self.s_register]
        self.a_register &= self.z_register

    def and_specific_with_a(self) -> None:
        self.z_register = self.memory[0, 0o7777]
        self.a_register &= self.z_register

    def and_with_jump_switches(self, mask: int) -> int:
        """
        Conjoin the provided mask with the jump switch setting

        :param mask: value to be conjoined. Must be in [0o0 .. 0o7]
        :return: the conjunction
        """
        return mask & self.__jump_switch_mask

    def and_with_stop_switches(self, mask: int) -> int:
        """
        Conjoin the provided mask with the stop switch setting.

        :param mask: value to conjoin
        :return: the conjunction
        """
        return self.__stop_switch_mask & mask

    def bank_controls_to_a(self) -> None:
        self.a_register = self.buffer_storage_bank
        self.a_register <<= 3
        self.a_register |= self.direct_storage_bank
        self.a_register <<= 3
        self.a_register |= self.indirect_storage_bank
        self.a_register <<= 3
        self.a_register |= self.relative_storage_bank

    def buffer_entrance_to_a(self) -> None:
        self.a_register = self.buffer_entrance_register

    def buffer_entrance_register_to_direct_storage(self) -> None:
        """
        Move the contents of the buffer entrance register to E(d)

        :return: None
        """
        self.z_register = self.buffer_entrance_register
        self.memory[self.direct_storage_bank, self.f_e] = self.z_register

    def buffer_exit_to_a(self) -> None:
        self.a_register = self.buffer_exit_register

    def clear_interrupt_lock(self) -> None:
        """
        Clear the interrupt lock if it is currently locked and unlock
        is not pending.

        :return: None
        """
        lock_setting = self.interrupt_lock
        # TODO(emintz): Find out why a simple if statement doesn't work here.
        match lock_setting:
            case InterruptLock.FREE:
                pass
            case InterruptLock.LOCKED:
                self.interrupt_lock = InterruptLock.UNLOCK_PENDING
            case InterruptLock.UNLOCK_PENDING:
                pass
            case _:
                print("Unknown lock setting {0}.".format(lock_setting))

    def direct_to_z(self, address: int) -> None:
        """
        [address(d)] -> Z, set memory access mode to direct

        :param address: location in the direct memory bank
        :return: None
        """
        self.z_register = self.memory[self.direct_storage_bank, address]
        self.mode_direct()

    def e_direct_to_s(self) -> None:
        self.s_register = self.read_direct_bank(self.f_e)

    def half_write_to_s_indirect(self) -> None:
        self.s_indirect_to_z()
        self.z_register &= 0o7700
        self.z_register |= self.a_register & 0o77
        self.z_to_s_indirect()

    def indefinite_delay(self) -> None:
        print("Machine hung.")
        self.machine_hung = True

    def load_a(self, bank: int, address: int)-> None:
        """
        Move [address(bank)] -> Z and A

        :param bank: storage bank
        :param address: memory address
        :return: None
        """
        self.z_register = self.memory[bank, address]
        self.a_register = self.z_register

    def load_a_from_s(self, bank: int) -> None:
        """
        Move the value at [S](bank) to the Z and A registers

        :param bank: memory bank containing the desired value
        :return: None
        """
        self.load_a(bank, self.s_register)

    def memory_to_buffer_data(self) -> bool:
        """
        Move one word of data from the memory address in the buffer entrance
        register to the buffer data register and increment the buffer
        entrance register. Return True if the buffer contains more data
        to be transferred and False if the last word has been transferred.

        Note: Successive calls read data from successive memory locations
        in the buffer storage bank. Data must be available to be transferred
        (i.e., the buffer entrance register contents must be strictly less
        than the buffer exit register contents on entry). This is checked.
        The computer must be buffering when this method is called. This is
        also checked.

        :return: True if the buffer contains more data to be read; False
                 if the call read the last word in the buffer.
        """
        assert self.buffer_entrance_register < self.buffer_exit_register
        self.buffer_data_register =self.memory[
            self.buffer_storage_bank, self.buffer_entrance_register]
        self.buffer_entrance_register += 1
        return  self.buffer_entrance_register < self.buffer_exit_register

    def mode_buffer(self) -> None:
        """
        Declares that data was retrieved from the buffer bank.

        :return: None
        """
        self.storage_cycle = MCS_MODE_BFR

    def mode_direct(self):
        """
        Declares that data was retrieved from the direct storage bank

        :return: None
        """
        self.storage_cycle = MCS_MODE_DIR

    # Declares that the next memory access will be in the indirect bank.
    def mode_indirect(self) -> None:
        """
        Declares that data was retrieved from the indirect storage bank

        :return: None
        """
        self.storage_cycle = MCS_MODE_IND

    # Declares that the next memory access will be in the relative bank.
    def mode_relative(self) -> None:
        """
        Declares that data was retrieved from the relative bank.

        :return: None
        """
        self.storage_cycle = MCS_MODE_REL

    def mode_specific(self) -> None:
        """
        Declares that data was retrieved from the specific memory
        location 0o7777(0). This is a placeholder

        TODO(emintz): discover what this method should do and do it.

        :return: None
        """
        self.storage_cycle = MCS_MODE_REL

    def normal_input_active(self) -> None:
        self.in_status = True

    def normal_input_inactive(self) -> None:
        self.in_status = False

    def normal_output_active(self) -> None:
        self.out_status = True

    def normal_output_inactive(self) -> None:
        self.out_status = False

    def p_to_s(self) -> None:
        """
        Move the contents of the P (program counter) register to the
        S (storage address to reference) register.

        :return: None
        """
        self.s_register = self.p_register

    def p_to_e_direct(self) -> None:
        """
        Write [P] to E(d). The range of E contents depends on the op-code.

        :return: None
        """
        self.z_register = self.p_register
        self.write_direct_bank(self.f_e, self.z_register)

    def read_from_s_indirect_and_increment_s(self) -> int:
        self.storage_cycle = MCS_MODE_IND
        retrieved_value = self.memory[
            self.indirect_storage_bank, self.s_register]
        self.s_register += 1
        return int(retrieved_value)

    def request_interrupt(self, interrupt_no: int) -> None:
        """
        Request the machine to perform the specified interrupt.
        :param interrupt_no:
        :return:
        """
        assert interrupt_no & 0o07 == 0
        assert 0o10 <= interrupt_no <= 0o40
        self.interrupt_requests[(interrupt_no >> 3) - 1] = True

    def retrieve_s_indirect_and_increment_s(self) -> int:
        """
        Retrieve [S(i)] and increment S

        :return: the retrieved value.
        """
        self.storage_cycle = MCS_MODE_IND
        retrieved_value = self.memory[self.indirect_storage_bank, self.s_register]
        self.s_register += 1
        return int(retrieved_value)

    def s_address_contents(self, bank: int) -> int:
        self.z_register = self.memory[bank, self.s_register]
        return int(self.z_register)

    def s_relative_address_contents(self) -> int:
        self.storage_cycle = MCS_MODE_REL
        return self.s_address_contents(self.relative_storage_bank)

    def service_pending_interrupts(self) -> None:
        match self.interrupt_lock:
            case InterruptLock.FREE:
                # Can do. Has anyone asked?
                interrupt_no = 0
                index = 0
                for request in self.interrupt_requests:
                    interrupt_no += 0o10
                    if request:
                        self.interrupt_requests[index] = False
                        self.memory[self.direct_storage_bank, interrupt_no] = (
                            self.p_register)
                        self.p_register = interrupt_no + 1
                        self.interrupt_lock = InterruptLock.LOCKED
                        break
                    index += 1

            case InterruptLock.LOCKED:
                # No can do.
                pass
            case InterruptLock.UNLOCK_PENDING:
                # Ask me next time
                self.interrupt_lock = InterruptLock.FREE

    def set_interrupt_lock(self) -> None:
        self.interrupt_lock = InterruptLock.LOCKED

    def start_buffering(self) -> None:
        assert not self.buffering
        assert self.buffer_entrance_register < self.buffer_exit_register
        self.buffering = True

    def stop_buffering(self) -> None:
        assert self.buffering
        self.buffering = False

    def store_a(self, bank: int) -> None:
        """
        Store the contents of the A register in address S(bank) via
        the Z register

        :param bank: receiving memory bank
        :return: None
        """
        self.z_register = self.a_register
        self.memory[bank, self.s_register] = self.z_register

    def store_at_s_indirect_and_increment_s(self, value: int) -> None:
        self.storage_cycle = MCS_MODE_IND
        self.memory[self.indirect_storage_bank, self.s_register] = value
        self.s_register += 1

    def subtract_e_from_a(self) -> None:
        """
        A -> A - E

        Subtract E from A

        :return: None
        """
        self.__difference_to_a(self.a_register, self.f_e)

    def subtract_s_address_from_a(self, bank: int) -> None:
        """
        A -> A - [S](bank)

        Take the value located at the S register's value in bank
        'bank' and subtract it from A. Leave the result in A

        :param bank: memory bank containing the subtrahend Note
               that S contains the subtrahend's address.
        :return: None
        """
        self.__difference_to_a(self.a_register, int(self.memory[bank, self.s_register]))

    def subtract_specific_from_a(self) -> None:
        """
        Subtract the contents of the specific memory address, 7777(0) from
        the accumulator (i.e., the A register)

        :return: None
        """
        minuend = self.a_register
        subtrahend = int(self.memory[0, 0o7777])
        self.z_register = subtrahend
        self.a_register = Arithmetic.subtract(minuend, subtrahend)

    def unpack_instruction(self) -> None:
        """
        Split a 12-bit machine instruction into F, the most significant 6 bits
        a.k.a., the opcode into the F register and the least significant 6
        bits, the effective address, into the E register. Note that the
        E register has no counterpart in the real computer.

        :return: None
        """
        self.p_to_s()
        self.z_register = self.memory[
            self.relative_storage_bank, self.s_register]
        self.f_e = self.z_register & 0o77
        self.f_instruction = (self.z_register >> 6) & 0o77

    def e_to_s(self) -> None:
        self.s_register = self.f_e

    def e_to_z(self) -> None:
        """
        Copy the contents of the E register to Z. This is used by No Address
        instructions

        :return: None
        """
        self.z_register = self.f_e
        self.storage_cycle = MCS_MODE_REL

    def forward_indirect_to_s(self) -> None:
        """
        Calculate the forward indirect address and store the result
        in S. The address is [(P + YY)(r)]

        :return: None
        """
        self.z_register = self.read_relative_bank(self.p_register + self.f_e)
        self.s_register = self.z_register

    def get_program_counter(self) -> int:
        return self.p_register

    def get_next_execution_address(self) -> int:
        return self.__next_address

    def g_address_to_s(self) -> None:
        """
        Sets S, the effective address register, to G

        :return: None
        """
        self.s_register = self.p_register + 1

    def g_contents(self) -> int:
        """
        [G](r) -> return value

        :return: the contents of the relative bank location given
                 in G.
        """
        self.z_register = self.read_relative_bank(self.p_register + 1)
        self.storage_cycle = MCS_MODE_REL
        return int(self.z_register)

    def g_to_s(self) -> None:
        """
        Sets S, the effective address register, to [G(r)]

        :return: None
        """
        self.z_register = self.g_contents()
        self.s_register = self.z_register

    def g_to_next_address(self) -> None:
        """
        Sets S, the effective address register, to [G(r)]

        :return: None
        """
        self.g_address_to_s()
        self.z_register = self.read_relative_bank(self.s_register)
        self.__next_address = self.z_register

    def get_jump_switch_mask(self) -> int:
        return self.__jump_switch_mask

    def get_stop_switch_mask(self) -> int:
        return self.__stop_switch_mask

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

    def p_to_a(self) -> None:
        self.a_register = self.p_register

    def relative_backward_to_s(self) -> None:
        """
        Calculate the relative backward address, the contents of P
        minus the contents of E, and place the result in S. Relative
        backward instructions invoke this to move their operand
        address to S.

        :return: None
        """
        self.s_register = self.p_register - self.f_e

    def relative_forward_to_s(self) -> None:
        """
        Calculate the relative forward address, the contents of P plus
        the contents of E, and place the result in S. Relative forward
        instructions invoke this to move their operand addresses to S

        :return: None
        """
        self.s_register = self.p_register + self.f_e

    def s_to_p(self) -> None:
        """
        Move the contents of the S (i.e. effective address) register
        to the P (program address) register

        :return: None
        """
        self.p_register = self.s_register

    def set_buffer_storage_bank(self, value: int) -> None:
        """
        Set the buffer storage bank to the least significant bits in
        the specified value.

        :param value: the bank number for the buffer storage bank
        :return:
        """
        self.buffer_storage_bank = value & 0o7

    def set_direct_storage_bank(self, value: int) -> None:
        """
        Set the direct storage bank to the least significant bits in
        the specified value.

        :param value: the bank number for the direct storage bank
        :return: None
        """
        self.direct_storage_bank = value & 0o7

    def set_indirect_storage_bank(self, value: int) -> None:
        """
        Set the indirect storage bank to the least significant bits in
        the specified value.

        :param value: the bank number for the indirect storage bank
        :return: None
        """
        self.indirect_storage_bank = value & 0o7

    def set_jump_switch_mask(self, mask: int) -> None:
        """
        Sets the jump mask to the specified value.

        :param mask: new jump switch settings. Must be in [0o0 .. 0o7]
        :return: None
        """
        self.__jump_switch_mask = mask

    def set_next_instruction_address(self, next_address: int) -> None:
        """
        Set the address of the next instruction. Note that the current
        address does not change. The program actually advance when the
        user invokes self.advance_to_next_instruction().

        :param next_address: address of next instruction.
        :return:
        """
        self.__next_address = next_address

    def set_program_counter(self, address: int) -> None:
        """
        Set the program counter to the specified address, branching the
        program to address.

        :param address: branch address
        :return: None
        """
        self.p_register = address

    def set_relative_storage_bank(self, value: int) -> None:
        """
        Set the relative storage bank to the least significant bits
        the specified value.

        :param value: memory bank number in [0 .. 7]
        :return: None
        """
        self.relative_storage_bank = value & 0o7

    def set_stop_switch_mask(self, mask: int) -> None:
        """
        Set the stop switch mask to the specified value

        :param mask: value to set, must be in range [0o0, 0o7]
        :return: None
        """
        self.__stop_switch_mask = mask

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

    def read_buffer_bank(self, address: int):
        """
        Read and return the value from a specified address in the
        buffer storage bank. The least significant 12 bits in the
        provided address argument specifies the address to be read.

        :param address: address in the buffer bank
        :return: the contents of the specified memory location
        """
        return self.memory[self.buffer_storage_bank, address & 0o7777]

    def read_direct_bank(self, address: int):
        """
        Read and return the value from a specified address in the
        direct storage bank. The least significant 12 bits in the
        provided address argument specifies the address to be read.

        :param address: the address in the direct memory bank
        :return: the contents of the specified memory location
        """
        return self.memory[self.direct_storage_bank, address & 0o7777]

    def read_indirect_bank(self, address: int):
        """
        Read and return the value from a specified address in the
        indirect storage bank. The least significant 12 bits in the
        provided address argument specifies the address to be read.

        :param address: the address in the indirect memory bank
        :return: the contents of the specified memory location
        """
        return self.memory[self.indirect_storage_bank, address & 0o7777]

    def read_relative_bank(self, address: int):
        """
        Read and return the value from a specified address in the
        relative storage bank. The least significant 12 bits in the
        provided address argument specifies the address to be read.

        :param address: the memory address in the relative storage bank
        :return: the contents of the specified memory location
        """
        return self.memory[self.relative_storage_bank, address & 0o7777]

    def read_specific(self):
        """
        Read the contents of the specific address: bank 0, location
        0o7777

        :return: the contents of 0o7777(0)
        """
        return self.memory[0, 0o7777]

    def run(self) -> None:
        self.run_stop_status = True

    def specific_to_a(self) -> None:
        self.specific_to_z()
        self.z_to_a()

    def specific_to_z(self) -> None:
        self.z_register = self.memory[0o0, 0o7777]
        self.mode_specific()

    def specific_to_s(self) -> None:
        self.s_register = 0o7777

    def stop(self) -> None:
        self.run_stop_status = False

    def s_absolute_to_a(self, bank: int) -> None:
        """
        [S(bank)] -> Z, A

        :param bank: memory bank
        :return: None
        """
        self.z_register = self.memory[bank, self.s_register]
        self.a_register = self.z_register

    def s_absolute_to_z(self, bank: int) -> None:
        """
        [S(bank)] -> Z

        :param bank: memory bank
        :return: None
        """
        self.z_register = self.memory[bank, self.s_register]

    def s_direct_to_a(self):
        """
        [S(d)] -> Z, A
        Memory mode -> Direct

        :return: None
        """
        self.s_direct_to_z()
        self.z_to_a()

    def s_direct_to_z(self) -> None:
        """
        [S(d)] -> Z
        Memory mode -> Direct

        :return: None
        """
        self.s_absolute_to_z(self.direct_storage_bank)
        self.mode_direct()

    def s_indirect_to_a(self) -> None:
        self.s_indirect_to_z()
        self.z_to_a()

    def s_indirect_to_z(self) -> None:
        self.s_absolute_to_z(self.indirect_storage_bank)
        self.mode_indirect()

    def s_relative_to_a(self) -> None:
        self.s_relative_to_z()
        self.z_to_a()

    def s_relative_to_next_address(self) -> None:
        """
        [S(r)] -> next address

        if S contains 200 and 200(r) contains 3400, the next
        address will contain 3400 on exit.

        :return: None
        """
        self.s_relative_to_z()
        self.z_to_next_address()

    def s_relative_to_p(self) -> None:
        """
        [S(r)] -> P

        if S contains 200 and 200(r) contains 3400, P
        will contain 3400 on exit.

        :return: None
        """
        self.s_relative_to_z()
        self.z_to_p()

    def s_relative_indirect_to_next_address(self) -> None:
        """
        [[S(r)]] -> next address

        If S contains 0o200 and 0o200(r) contains 0o1400, the next
        address will be set to 0o1400

        :return: None
        """
        self.s_relative_to_z()
        self.z_to_s()
        self.s_relative_to_z()
        self.__next_address = self.z_register

    def s_relative_to_z(self) -> None:
        """
        [S](r) -> Z

        Move the contents of the relative location in S to Z. Often
        used in instruction logic where the S value is set on entry.

        :return: None
        """
        self.s_absolute_to_z(self.relative_storage_bank)
        self.mode_relative()

    def s_to_next_address(self) -> None:
        self.__next_address = self.s_register

    def set_buffer_bank_from_e(self) -> None:
        self.buffer_storage_bank = self.f_e & 0o7

    def set_direct_bank_from_e(self) -> None:
        self.direct_storage_bank = self.f_e & 0o7

    def set_indirect_bank_from_e(self) -> None:
        self.indirect_storage_bank = self.f_e & 0o7

    def set_relative_bank_from_e_and_jump(self) -> None:
        self.relative_storage_bank = self.f_e & 0o07
        self.__next_address = self.a_register

    def value_to_s_address_relative(self, value: int) -> None:
        """
        value -> S(r)

        :param value: value to store
        :return: None
        """
        self.memory[self.relative_storage_bank, self.s_register] = value

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

    def write_buffer_bank(self, address: int, value: int) -> None:
        """
        Write the specified value to the specified address in the
        buffer storage bank. The least significant 12 bits in the
        provided address argument specifies the address to be written.

        :param address: the destination address in the buffer memory bank
        :param value: the value to write
        :return: None
        """
        self.memory[self.buffer_storage_bank, address & 0o7777] = (
                value & 0o7777)

    def write_direct_bank(self, address: int, value: int) -> None:
        """
        Write the specified value to the specified address in the
        direct storage bank. The least significant 12 bits in the
        provided address argument specifies the address to be written.

        :param address: the destination address in the direct memory bank
        :param value: the value to write
        :return: None
        """
        self.memory[self.direct_storage_bank, address & 0o7777] = (
                value & 0o7777)

    def write_indirect_bank(self, address: int, value: int) -> None:
        """
        Write the specified value to the specified address in the
        indirect storage bank. The least significant 12 bits in the
        provided address argument specifies the address to be written.

        :param address: the destination address in the indirect memory bank
        :param value: the value to write
        :return: None
        """
        self.memory[self.indirect_storage_bank, address & 0o7777] = (
                value & 0o7777)

    def write_relative_bank(self, address: int, value: int) -> None:
        """
        Write the specified value to the specified address in the
        relative storage bank. The least significant 12 bits in the
        provided address argument specifies the address to be written.

        :param address: destination address in the relative storage bank
        :param value: value to write
        :return: None
        """
        self.memory[self.relative_storage_bank, address & 0o7777] =  value & 0o7777

    def write_specific(self, value: int):
        """
        Write the specified value to the specific address, bank 0,
        location 0o7777.

        :param value: value to write
        :return: None
        """
        self.memory[0, 0o7777] = value

    def xor_a_with_z(self) -> None:
        """
        [Z] xor [A] -> A

        :return: None
        """
        self.a_register ^= self.z_register

    def z_to_a(self) -> None:
        self.a_register = self.z_register

    def z_to_next_address(self) -> None:
        self.__next_address = self.z_register

    def z_to_p(self) -> None:
        self.p_register = self.z_register

    def z_to_s(self) -> None:
        self.s_register = self.z_register

    def z_to_s_indirect(self) -> None:
        self.write_indirect_bank(self.s_register, self.z_register)
        self.storage_cycle = MCS_MODE_IND

    def __difference_to_a(self, minuend: int, subtrahend: int) -> None:
        """
        Move subtrahend to the Z register and minuend - subtrahend to the
        A register. Note that it is assumed that the subtrahend was
        just retrieved from memory.

        :param minuend: the value to subtract from
        :param subtrahend: the value to subtract
        :return: None
        """
        self.z_register = subtrahend
        self.a_register = Arithmetic.subtract(minuend, subtrahend)

    def __sum_to_a(self, existing_value: int, value_from_memory: int):
        """
        Move value_from_memory to Z and existing_value + value_from_memory
        to A. It assumed that value_from_memory was just retrieved from
        storage.

        :param existing_value: current value, probably from A
        :param value_from_memory: value just retrieved from storage
        :return: None
        """
        self.z_register = value_from_memory
        self.a_register = Arithmetic.add(existing_value, value_from_memory)

if __name__ == "__main__":
    print('Running storage in stand-alone mode.\n')
    storage = Storage()
    print('Program completed.\n')
