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
from cdc160a import EffectiveAddress
from cdc160a import Microinstructions
from cdc160a.Storage import Storage

def __no_advance(storage: Storage) -> None:
    """
    A placeholder advance function used by instructions that
    either advance by a variable amount or change the flow of
    control.
    :param storage: placeholder, not referenced
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

class Instruction:
    """
    Emulates a 160A Instruction

    Provides effective address and logic for an emulated instruction.
    The effective address calculation determines the operand address
    and storage bank. Typically, it loads the operand into the S register.
    The logic performs the actual instruction, e.g. adding, jumping,
    or moving values.

    """
    def __init__(self, name, effective_address, logic, advance, cycles: int):
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
        self.__cycles = cycles
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

    def name(self):
        """
        Instruction name accessor

        :return: the instruction name, the assembler's mnemonic for the instruction
        """
        return self.__name

    def perform_logic(self, storage: Storage) -> int:
        """
        Performs the Instruction's logic

        :param storage: emulated 1650A memory and register file.
        :return: instruction execution type in cycles
        """
        self.__logic(storage)
        self.__advance(storage)
        return self.__cycles

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

def __single_advance_instruction(name, effective_address, logic, cycles: int) -> Instruction:
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

def __double_advance_instruction(name, effective_address: object, logic: object, cycles: int) -> Instruction:
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

ERR = __single_advance_instruction("ERR", EffectiveAddress.no_address, Microinstructions.error, 1)
HLT = __single_advance_instruction("HLT", EffectiveAddress.no_address, Microinstructions.halt, 1)
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
LDS = __single_advance_instruction("LDS", EffectiveAddress.specific, Microinstructions.specific_to_a, 2)
LS1 = __single_advance_instruction("LS1", EffectiveAddress.no_address, Microinstructions.rotate_a_left_one, 1)
LS2 = __single_advance_instruction("LS2", EffectiveAddress.no_address, Microinstructions.rotate_a_left_two, 1)
LS3 = __single_advance_instruction("LS3", EffectiveAddress.no_address, Microinstructions.rotate_a_left_three, 1)
LS6 = __single_advance_instruction("LS6", EffectiveAddress.no_address, Microinstructions.rotate_a_left_six, 1)
NOP = __single_advance_instruction("NOP", EffectiveAddress.no_address, Microinstructions.do_nothing, 1)
NJF = __no_advance_instruction("NJF", EffectiveAddress.relative_forward, Microinstructions.jump_if_a_negative, 1)
NZF = __no_advance_instruction("NZF", EffectiveAddress.relative_forward, Microinstructions.jump_if_a_nonzero, 1)
PJF = __no_advance_instruction("PJF", EffectiveAddress.relative_forward, Microinstructions.jump_if_a_positive, 1)
RS1 = __single_advance_instruction("RS1", EffectiveAddress.no_address, Microinstructions.shift_a_right_one, 1)
RS2 = __single_advance_instruction("RS2", EffectiveAddress.no_address, Microinstructions.shift_a_right_two, 1)
STB = __single_advance_instruction("STB", EffectiveAddress.relative_backward, Microinstructions.a_to_relative, 3)
# TODO(emintz): verify STC behavior, which makes no sense to me.
STC = __double_advance_instruction("STC", EffectiveAddress.constant, Microinstructions.a_to_relative, 3)
STD = __single_advance_instruction("STD", EffectiveAddress.direct, Microinstructions.a_to_direct, 3)
STF = __single_advance_instruction("STF", EffectiveAddress.relative_forward, Microinstructions.a_to_relative, 3)
STI = __single_advance_instruction("STI", EffectiveAddress.indirect, Microinstructions.a_to_indirect, 4)
STM = __double_advance_instruction("STM", EffectiveAddress.memory, Microinstructions.a_to_indirect, 4)
STS = __single_advance_instruction("STS", EffectiveAddress.specific, Microinstructions.a_to_specific, 3)
ZJF = __no_advance_instruction("ZJF", EffectiveAddress.relative_forward, Microinstructions.jump_if_a_zero, 1)