"""
CDC 160A Instructions

Instructions contain three methods:

1. Determine the operand's effective address
2. Perform the instruction logic and determine the following
   instruction's address

The design supports the following run loop:

1. Determine the current instruction's operand address.
2. Check the Run/Step switch and stop if the operator moved it to Step.
   The register display will show the instruction and its operand's
   address.
3. Run the instruction.
4. Halt if the instruction halted the machine

"""
from abc import abstractmethod, ABCMeta
from cdc160a import EffectiveAddress
from cdc160a import Microinstructions
from cdc160a.Storage import Storage
from typing import Callable

def __no_advance(_) -> None:
    """
    A placeholder advance function used by instructions that
    either advance by a variable amount or change the flow of
    control.

    :return: None
    """
    pass

def __single_advance(storage: Storage) -> None:
    """
    P + 1 <- P, used by one-word instructions that do not change
    the flow of control.

    :param storage: computer storage, holds the P register
    :return: None
    """
    storage.next_after_one_word_instruction()

def __double_advance(storage: Storage) -> None:
    """
    P + 2 -> P, used by two-word instructions that do not change
    the flow of control

    :param storage: computer storage, holds the P register
    :return: None
    """
    storage.next_after_two_word_instruction()


class BaseInstruction(metaclass=ABCMeta):
    def __init__(self, name: str):
        self.__name = name

    @abstractmethod
    def determine_effective_address(self, storage):
        """
        Determine the instruction's effective address. The constructor
        sets the method.

        :param storage: the emulated 160A's memory and register file
        :return: Nothing
        """
        pass

    def name(self):
        """
        Instruction name accessor

        :return: the instruction name, the assembler's mnemonic for the instruction
        """
        return self.__name

    @abstractmethod
    def perform_logic(self, storage):
        """
        Performs the Instruction's logic

        :param storage: emulated 1650A memory and register file.
        :return: instruction execution type in cycles
        """
        pass


class Instruction(BaseInstruction):
    """
    Emulates a 160A Instruction with a fixed run time

    Provides effective address and logic for an emulated instruction.
    The effective address calculation determines the operand address
    and storage bank. Typically, it loads the operand into the S register.
    The logic performs the actual instruction, e.g. adding, jumping,
    or moving values.

    """
    def __init__(
            self,
            name: str,
            effective_address: Callable[[Storage], None],
            logic: Callable[[Storage], None],
            advance: Callable[[Storage], None],
            cycles: int):
        """
        Constructor

        :param name: instruction name as used in the assembler. Note that
               an instruction's name identifies it, so it must be unique.
        :param effective_address: a function that calculates the
               instruction's operand address, as described above.
        :param logic: the instruction's logic, what it does, as
               described above.
        :param advance: advances the P register upon completion
        :param cycles: the number of memory cycles required to
               execute the instruction, where it is a constant.
               Set this to 0 for instructions that must
               calculate their run time on the fly.
        """
        super().__init__(name)
        self.__cycles = cycles
        self.__effective_address = effective_address
        self.__advance = advance
        self.__logic = logic

    def determine_effective_address(self, storage: Storage) -> None:
        """
        Determine the instruction's effective address. The constructor
        sets the method.

        :param storage: the emulated 160A's memory and register file
        :return: Nothing
        """
        self.__effective_address(storage)

    def perform_logic(self, storage: Storage) -> int:
        """
        Performs the Instruction's logic

        :param storage: emulated 1650A memory and register file.
        :return: instruction execution type in cycles
        """
        self.__logic(storage)
        self.__advance(storage)
        return self.__cycles

class VariableTimingInstruction(BaseInstruction):

    def __init__(self,
                 name: str,
                 effective_address: Callable[[Storage], None],
                 logic: Callable[[Storage], int],
                 advance: Callable[[Storage], None]):
        """
        Constructor

        :param name: instruction name as used in the assembler. Note that
               an instruction's name identifies it, so it must be unique.
        :param effective_address: a function that calculates the
               instruction's operand address, as described above.
        :param logic: the instruction's logic, what it does, as
               described above. Must return the execution time in
               cycles.
        :param advance: advances the P register upon completion
        """
        super().__init__(name)
        self.__effective_address = effective_address
        self.__advance = advance
        self.__logic = logic
        self.__name = name

    def determine_effective_address(self, storage: Storage) -> None:
        """
        Determine the instruction's effective address. The constructor
        sets the method.

        :param storage: the emulated 160A's memory and register file
        :return: Nothing
        """
        self.__effective_address(storage)

    def perform_logic(self, storage: Storage) -> int:
        """
        Performs the Instruction's logic

        :param storage: emulated 1650A memory and register file.
        :return: instruction execution type in cycles
        """
        cycles = self.__logic(storage)
        self.__advance(storage)
        return cycles

def __no_advance_instruction(name, effective_address, logic, cycles: int) -> Instruction:
    """
    Convenience factory method that creates "no advance" instructions

    :param name: instruction name
    :param effective_address: function that calculates the instruction
           operand's effective address.
    :param logic: instruction logic, what the instruction does
    :param cycles: execution time in computer cycles
    :return: the newly minted instruction
    """
    return Instruction(name, effective_address, logic, __no_advance, cycles)

def __single_advance_instruction(
        name: str,
        effective_address: Callable[[Storage], None],
        logic: Callable[[Storage], None],
        cycles: int) -> Instruction:
    """
    Convenience factory method that creates one-word instructions that
    do not change the flow of control

    :param name: instruction name
    :param effective_address: function that calculates the instruction
           operand's effective address.
    :param logic: instruction logic, what the instruction does
    :param cycles: execution time in computer cycles
    :return: the newly minted instruction
    """
    return Instruction(name, effective_address, logic, __single_advance, cycles)

def __double_advance_instruction(
        name: str,
        effective_address: Callable[[Storage], None],
        logic: Callable[[Storage], None],
        cycles: int) -> Instruction:
    """
    Convenience factory method that creates two-word instructions that
    do not change the flow of control

    :param name: instruction name
    :param effective_address: function that calculates the instruction
           operand's effective address.
    :param logic: instruction logic, what the instruction does
    :param cycles: execution time in computer cycles
    :return: the newly minted instruction
    """
    return Instruction(name, effective_address, logic, __double_advance, cycles)

ACJ = __no_advance_instruction("ACJ", EffectiveAddress.no_address, Microinstructions.set_dir_ind_rel_bank_from_e_and_jump, 1)
ADB = __single_advance_instruction("ADB", EffectiveAddress.relative_backward, Microinstructions.add_relative_to_a, 2)
ADC = __double_advance_instruction("ADC", EffectiveAddress.constant, Microinstructions.add_relative_to_a, 2)
ADD = __single_advance_instruction("ADD", EffectiveAddress.direct, Microinstructions.add_direct_to_a, 2)
ADF = __single_advance_instruction("ADF", EffectiveAddress.relative_forward, Microinstructions.add_relative_to_a, 2)
ADI = __single_advance_instruction("ADI", EffectiveAddress.indirect, Microinstructions.add_indirect_to_a, 3)
ADM = __double_advance_instruction("ADM", EffectiveAddress.memory, Microinstructions.add_relative_to_a, 3)
ADN = __single_advance_instruction("ADN", EffectiveAddress.no_address, Microinstructions.add_e_to_a, 1)###
ADS = __single_advance_instruction("ADS", EffectiveAddress.specific, Microinstructions.add_specific_to_a, 2)
AOB = __single_advance_instruction("AOB", EffectiveAddress.relative_backward, Microinstructions.replace_add_one_relative, 3)
AOC = __double_advance_instruction("AOC", EffectiveAddress.constant, Microinstructions.replace_add_one_relative, 3)
AOD = __single_advance_instruction("AOD", EffectiveAddress.direct, Microinstructions.replace_add_one_direct, 3)
AOF = __single_advance_instruction("AOF", EffectiveAddress.relative_forward, Microinstructions.replace_add_one_relative, 3)
AOI = __single_advance_instruction("AOI", EffectiveAddress.indirect, Microinstructions.replace_add_one_indirect, 4)
AOM = __double_advance_instruction("AOM", EffectiveAddress.memory, Microinstructions.replace_add_one_relative, 4)
AOS = __single_advance_instruction("AOS", EffectiveAddress.specific, Microinstructions.replace_add_one_specific, 3)
ATE = VariableTimingInstruction("ATE", EffectiveAddress.no_address, Microinstructions.a_to_buffer_entrance, __no_advance)
ATX = VariableTimingInstruction("ATX", EffectiveAddress.no_address, Microinstructions.a_to_buffer_exit, __no_advance)
BLS = VariableTimingInstruction("BLS", EffectiveAddress.no_address, Microinstructions.block_store, __no_advance)
CIL = __single_advance_instruction("CIL", EffectiveAddress.no_address, Microinstructions.clear_interrupt_lock, 1)
CTA = __single_advance_instruction("CTA", EffectiveAddress.no_address, Microinstructions.bank_controls_to_a, 1)
DRJ = __no_advance_instruction("DRJ", EffectiveAddress.no_address, Microinstructions.set_dir_rel_bank_from_e_and_jump, 1)
ERR = __single_advance_instruction("ERR", EffectiveAddress.no_address, Microinstructions.error, 1)
ETA = __single_advance_instruction("ETA", EffectiveAddress.no_address, Microinstructions.buffer_entrance_to_a, 1)
ETX = __single_advance_instruction("ETX", EffectiveAddress.no_address, Microinstructions.buffer_exit_to_a, 1)
HLT = __single_advance_instruction("HLT", EffectiveAddress.no_address, Microinstructions.halt, 1)
HWI = __single_advance_instruction("HWI", EffectiveAddress.via_direct_at_e, Microinstructions.half_write_indirect, 4)
IRJ = __no_advance_instruction("IRJ", EffectiveAddress.no_address, Microinstructions.set_ind_rel_bank_from_e_and_jump, 1)
JFI = __no_advance_instruction("JFI", EffectiveAddress.relative_forward, Microinstructions.jump_forward_indirect, 2)
JPI = __no_advance_instruction("JPI", EffectiveAddress.no_address, Microinstructions.jump_indirect, 2)
JPR = __no_advance_instruction("JPR", EffectiveAddress.memory, Microinstructions.return_jump, 3)
LCB = __single_advance_instruction("LCB", EffectiveAddress.relative_backward, Microinstructions.s_relative_complement_to_a, 2)
LCC = __double_advance_instruction("LCC", EffectiveAddress.constant, Microinstructions.s_relative_complement_to_a, 2)
LCD = __single_advance_instruction("LCD", EffectiveAddress.direct, Microinstructions.s_direct_complement_to_a, 2)
LCF = __single_advance_instruction("LCF", EffectiveAddress.relative_forward, Microinstructions.s_relative_complement_to_a, 2)
LCI = __single_advance_instruction("LCI", EffectiveAddress.indirect, Microinstructions.s_indirect_complement_to_a, 3)
LCM = __double_advance_instruction("LCM", EffectiveAddress.memory, Microinstructions.s_indirect_complement_to_a, 3)
LCN = __single_advance_instruction("LCN", EffectiveAddress.no_address, Microinstructions.e_complement_to_a, 1)
LCS = __single_advance_instruction("LCS", EffectiveAddress.specific, Microinstructions.specific_complement_to_a, 2)
LDB = __single_advance_instruction("LDB", EffectiveAddress.relative_backward, Microinstructions.s_relative_to_a, 2)
LDC = __double_advance_instruction("LDC", EffectiveAddress.constant, Microinstructions.s_relative_to_a, 2)
LDD = __single_advance_instruction("LDD", EffectiveAddress.direct, Microinstructions.s_direct_to_a, 2)
LDF = __single_advance_instruction("LDF", EffectiveAddress.relative_forward, Microinstructions.s_relative_to_a, 2)
LDI = __single_advance_instruction("LDI", EffectiveAddress.indirect, Microinstructions.s_indirect_to_a, 3)
LDM = __double_advance_instruction("LDM", EffectiveAddress.memory, Microinstructions.s_indirect_to_a, 3)
LDN = __single_advance_instruction("LDN", EffectiveAddress.no_address, Microinstructions.e_to_a, 1)
LPB = __single_advance_instruction("LPB", EffectiveAddress.relative_backward, Microinstructions.and_relative_with_a, 2)
LPC = __double_advance_instruction("LPC", EffectiveAddress.constant, Microinstructions.and_relative_with_a, 2)
LPD = __single_advance_instruction("LPD", EffectiveAddress.direct, Microinstructions.and_direct_with_a, 2)
LPF = __single_advance_instruction("LPF", EffectiveAddress.relative_forward, Microinstructions.and_relative_with_a, 2)
LPI = __single_advance_instruction("LPI", EffectiveAddress.indirect, Microinstructions.and_indirect_with_a, 3)
LPM = __double_advance_instruction("LPM", EffectiveAddress.memory, Microinstructions.and_relative_with_a, 3)
LDS = __single_advance_instruction("LDS", EffectiveAddress.specific, Microinstructions.specific_to_a, 2)
LPN = __single_advance_instruction("LPN", EffectiveAddress.no_address, Microinstructions.and_e_with_a, 1)
LPS = __single_advance_instruction("LPS", EffectiveAddress.specific, Microinstructions.and_specific_with_a, 2)
LS1 = __single_advance_instruction("LS1", EffectiveAddress.no_address, Microinstructions.rotate_a_left_one, 1)
LS2 = __single_advance_instruction("LS2", EffectiveAddress.no_address, Microinstructions.rotate_a_left_two, 1)
LS3 = __single_advance_instruction("LS3", EffectiveAddress.no_address, Microinstructions.rotate_a_left_three, 1)
LS6 = __single_advance_instruction("LS6", EffectiveAddress.no_address, Microinstructions.rotate_a_left_six, 1)
MUH = __single_advance_instruction("MUH", EffectiveAddress.no_address, Microinstructions.multiply_a_by_100, 1)
MUT = __single_advance_instruction("MUT", EffectiveAddress.no_address, Microinstructions.multiply_a_by_10, 1)
NOP = __single_advance_instruction("NOP", EffectiveAddress.no_address, Microinstructions.do_nothing, 1)
NJB = __no_advance_instruction("NJB", EffectiveAddress.relative_backward, Microinstructions.jump_if_a_negative, 1)
NJF = __no_advance_instruction("NJF", EffectiveAddress.relative_forward, Microinstructions.jump_if_a_negative, 1)
NZB = __no_advance_instruction("NZB", EffectiveAddress.relative_backward, Microinstructions.jump_if_a_nonzero, 1)
NZF = __no_advance_instruction("NZF", EffectiveAddress.relative_forward, Microinstructions.jump_if_a_nonzero, 1)
PJB = __no_advance_instruction("PJB", EffectiveAddress.relative_backward, Microinstructions.jump_if_a_positive, 1)
PJF = __no_advance_instruction("PJF", EffectiveAddress.relative_forward, Microinstructions.jump_if_a_positive, 1)
PTA = __single_advance_instruction("PTA", EffectiveAddress.no_address, Microinstructions.p_to_a, 1)
RAB = __single_advance_instruction("RAB", EffectiveAddress.relative_backward, Microinstructions.replace_add_relative, 3)
RAC = __double_advance_instruction("RAC", EffectiveAddress.constant, Microinstructions.replace_add_relative, 3)
RAD = __single_advance_instruction("RAD", EffectiveAddress.direct, Microinstructions.replace_add_direct, 3)
RAF = __single_advance_instruction("RAF", EffectiveAddress.relative_forward, Microinstructions.replace_add_relative, 3)
RAI = __single_advance_instruction("RAI", EffectiveAddress.indirect, Microinstructions.replace_add_indirect, 4)
RAM = __double_advance_instruction("RAM", EffectiveAddress.memory, Microinstructions.replace_add_relative, 4)
RAS = __single_advance_instruction("RAS", EffectiveAddress.specific, Microinstructions.replace_add_specific, 3)
RS1 = __single_advance_instruction("RS1", EffectiveAddress.no_address, Microinstructions.shift_a_right_one, 1)
RS2 = __single_advance_instruction("RS2", EffectiveAddress.no_address, Microinstructions.shift_a_right_two, 1)
SBB = __single_advance_instruction("SBB", EffectiveAddress.relative_backward, Microinstructions.subtract_relative_from_a, 2)
SBC = __double_advance_instruction("SBC", EffectiveAddress.constant, Microinstructions.subtract_relative_from_a, 2)
SBD = __single_advance_instruction("SBD", EffectiveAddress.direct, Microinstructions.subtract_direct_from_a, 2)
SBF = __single_advance_instruction("SBF", EffectiveAddress.relative_forward, Microinstructions.subtract_relative_from_a, 2)
SBI = __single_advance_instruction("SBI", EffectiveAddress.indirect, Microinstructions.subtract_indirect_from_a, 3)
SBM = __double_advance_instruction("SBM", EffectiveAddress.memory, Microinstructions.subtract_relative_from_a, 3)
SBN = __single_advance_instruction("SBN", EffectiveAddress.no_address, Microinstructions.subtract_e_from_a, 1)
SBS = __single_advance_instruction("SBS", EffectiveAddress.specific, Microinstructions.subtract_specific_from_a, 2)
SBU = __single_advance_instruction("SBU", EffectiveAddress.no_address, Microinstructions.set_buf_bank_from_e, 1)
SCB = __single_advance_instruction("SCB", EffectiveAddress.relative_backward, Microinstructions.selective_complement_relative, 2)
SCC = __double_advance_instruction("SCC", EffectiveAddress.constant, Microinstructions.selective_complement_relative, 2)
SCD = __single_advance_instruction("SCD", EffectiveAddress.direct, Microinstructions.selective_complement_direct, 2)
SCF = __single_advance_instruction("SCF", EffectiveAddress.relative_forward, Microinstructions.selective_complement_relative, 2)
SCI = __single_advance_instruction("SCI", EffectiveAddress.indirect, Microinstructions.selective_complement_indirect, 3)
SCM = __double_advance_instruction("SCM", EffectiveAddress.memory, Microinstructions.selective_complement_relative, 3)
SDC = __single_advance_instruction("SDC", EffectiveAddress.no_address, Microinstructions.set_dir_bank_from_e, 1)
SCN = __single_advance_instruction("SCN", EffectiveAddress.no_address, Microinstructions.selective_complement_no_address, 1)
SCS = __single_advance_instruction("SCS", EffectiveAddress.specific, Microinstructions.selective_complement_specific, 2)
SIC = __single_advance_instruction("SIC", EffectiveAddress.no_address, Microinstructions.set_ind_bank_from_e, 1)
SID = __single_advance_instruction("SID", EffectiveAddress.no_address, Microinstructions.set_ind_dir_bank_from_e, 1)
SJS = VariableTimingInstruction("SJS", EffectiveAddress.constant, Microinstructions.selective_stop_and_jump, __no_advance)
SLJ = VariableTimingInstruction("SLJ", EffectiveAddress.constant, Microinstructions.selective_jump, __no_advance)
SLS = __single_advance_instruction("SLS", EffectiveAddress.no_address, Microinstructions.selective_stop, 1)
SRB = __single_advance_instruction("SRB", EffectiveAddress.relative_backward, Microinstructions.shift_replace_relative, 3)
SRC = __double_advance_instruction("SRC", EffectiveAddress.constant, Microinstructions.shift_replace_relative, 3)
SRD = __single_advance_instruction("SRD", EffectiveAddress.direct, Microinstructions.shift_replace_direct, 3)
SRF = __single_advance_instruction("SRF", EffectiveAddress.relative_forward, Microinstructions.shift_replace_relative, 3)
SRI = __single_advance_instruction("SRI", EffectiveAddress.indirect, Microinstructions.shift_replace_indirect, 4)
SRJ = __no_advance_instruction("SRJ", EffectiveAddress.no_address, Microinstructions.set_rel_bank_from_e_and_jump, 1)
SRM = __double_advance_instruction("SRM", EffectiveAddress.memory, Microinstructions.shift_replace_relative, 4)
SRS = __single_advance_instruction("SRS", EffectiveAddress.specific, Microinstructions.shift_replace_specific, 3)
STB = __single_advance_instruction("STB", EffectiveAddress.relative_backward, Microinstructions.a_to_s_relative, 3)
# TODO(emintz): verify STC behavior, which makes no sense to me.
STC = __double_advance_instruction("STC", EffectiveAddress.constant, Microinstructions.a_to_s_relative, 3)
STD = __single_advance_instruction("STD", EffectiveAddress.direct, Microinstructions.a_to_s_direct, 3)
STF = __single_advance_instruction("STF", EffectiveAddress.relative_forward, Microinstructions.a_to_s_relative, 3)
STE = __single_advance_instruction("STE", EffectiveAddress.no_address, Microinstructions.buffer_entrance_to_direct_and_set_from_a, 3)
STI = __single_advance_instruction("STI", EffectiveAddress.indirect, Microinstructions.a_to_s_indirect, 4)
STM = __double_advance_instruction("STM", EffectiveAddress.memory, Microinstructions.a_to_s_relative, 4)
STP = __single_advance_instruction("STP", EffectiveAddress.no_address, Microinstructions.p_to_e_direct, 3)
STS = __single_advance_instruction("STS", EffectiveAddress.specific, Microinstructions.a_to_specific, 3)
ZJB = __no_advance_instruction("ZJB", EffectiveAddress.relative_backward, Microinstructions.jump_if_a_zero, 1)
ZJF = __no_advance_instruction("ZJF", EffectiveAddress.relative_forward, Microinstructions.jump_if_a_zero, 1)
