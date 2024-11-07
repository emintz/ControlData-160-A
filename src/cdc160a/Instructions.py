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
    pass

def __single_advance(storage: Storage) -> None:
    storage.next_after_one_word_instruction()

def __double_advance(storage: Storage) -> None:
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
    def __init__(self, effective_address, logic, advance, cycles: int):
        """
        Constructor

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

def __no_advance_instruction(
        effective_address, logic, cycles: int) -> Instruction:
    return Instruction(effective_address, logic, __no_advance, cycles)

def __single_advance_instruction(
        effective_address, logic, cycles: int) -> Instruction:
    return Instruction(
        effective_address, logic, __single_advance, cycles)

def __double_advance_instruction(
        effective_address: object, logic: object, cycles: int) -> Instruction:
    return Instruction(
        effective_address, logic, __double_advance, cycles)

ERR = __single_advance_instruction(
    EffectiveAddress.no_address, Microinstructions.error, 1)
HLT = __single_advance_instruction(
    EffectiveAddress.no_address, Microinstructions.halt, 1)
LDB = __single_advance_instruction(
    EffectiveAddress.relative_backward,
    Microinstructions.s_relative_to_a,
    2)
LDC = __double_advance_instruction(
    EffectiveAddress.constant, Microinstructions.s_relative_to_a, 2)
LDD = __single_advance_instruction(
    EffectiveAddress.direct, Microinstructions.s_direct_to_a, 2)
LDF = __single_advance_instruction(
    EffectiveAddress.relative_forward, Microinstructions.s_relative_to_a,2)
LDI = __single_advance_instruction(
    EffectiveAddress.indirect, Microinstructions.s_indirect_to_a, 3)
LDM = __double_advance_instruction(
    EffectiveAddress.memory, Microinstructions.s_indirect_to_a, 3)
LDN = __single_advance_instruction(
    EffectiveAddress.no_address, Microinstructions.e_to_a, 1)
LDS = __single_advance_instruction(
    EffectiveAddress.specific, Microinstructions.specific_to_a, 2)
NOP = __single_advance_instruction(
    EffectiveAddress.no_address, Microinstructions.do_nothing, 1)
STB = __single_advance_instruction(
    EffectiveAddress.relative_backward, Microinstructions.a_to_relative, 3)
# TODO(emintz): verify STC behavior, which makes no sense to me.
STC = __double_advance_instruction(
    EffectiveAddress.constant, Microinstructions.a_to_relative, 3)
STD = __single_advance_instruction(
    EffectiveAddress.direct, Microinstructions.a_to_direct, 3)
STF = __single_advance_instruction(
    EffectiveAddress.relative_forward, Microinstructions.a_to_relative, 3)
STI = __single_advance_instruction(
    EffectiveAddress.indirect, Microinstructions.a_to_indirect, 4)
STM = __double_advance_instruction(
    EffectiveAddress.memory, Microinstructions.a_to_indirect, 4)
STS = __single_advance_instruction(
    EffectiveAddress.specific, Microinstructions.a_to_specific, 3)