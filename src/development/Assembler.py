"""
An extremely basic assembler used for testing. Please see the Assembler
class documentation below for details.

Copyright © 2025 The System Source Museum, the authors and maintainers,
and others

This file is part of the System Source Museum Control Data 160-A Emulator.

The System Source Museum Control Data 160-A Emulator is free software: you
can redistribute it and/or modify it under the terms of the GNU General
Public License as published by the Free Software Foundation, either version
3 of the License, or (at your option) any later version.

The System Source Museum Control Data 160-A Emulator is distributed in the
hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with the System Source Museum Control Data 160-A Emulator. If not, see
<https://www.gnu.org/licenses/.
"""

from __future__ import annotations
from cdc160a import Storage
from development.MemoryUse import MemoryUse
from os import path
import re
import sys
from typing import Callable, Optional

BANK_PATTERN = re.compile("[0-7]")
E_PATTERN = re.compile("[0-7]{1,2}")
G_PATTERN = re.compile("[0-7]{1,4}")
OCTAL_DIGITS = ['0', '1', '2', '3', '4', '5', '6', '7']

def one_digit_octal(value: int) -> str:
    value_in_octal = oct(value)
    assert \
           0o0 <= value <= 0o7, \
            f"Value must be in [0o0 .. 0o7], is {value_in_octal}."
    return OCTAL_DIGITS[value]

def two_digit_octal(value: int) -> str:
    value_in_octal = oct(value)
    assert \
           0 <= value <= 0o77, \
           f"Value must be in [0o00 .. 0o77], is {0}".format(
            value_in_octal)
    return ''.join([
       OCTAL_DIGITS[((value >> 3) & 0o7)],
       OCTAL_DIGITS[value & 0o7]
    ])

def four_digit_octal(value: int) -> str:
    value_in_octal = oct(value)
    assert \
        0 <= value <= 0o7777, \
        f"Value must be in [0o0000 .. 0o7777], is {0}.".format(value_in_octal)

    return ''.join( [
        OCTAL_DIGITS[(value >> 9) & 0o7],
        OCTAL_DIGITS[(value >> 6) & 0o7],
        OCTAL_DIGITS[(value >> 3) & 0o7],
        OCTAL_DIGITS[value & 0o7]
    ])

class AddressSetter:
    def __init__(self, assembler: Assembler, name: str) -> None:
        self.__assembler = assembler
        self.__name = name


    def emit(self, tokens: [str]) -> None:
        if (len(tokens)) < 2:
            self.__assembler.error("Address value missing, using 0x0000")
        else:
            address = self.__assembler.token_to_g(tokens[1], 0)
            self.__assembler.set_address(address)

    def name(self) -> str:
        return self.__name

class AssemblerBankSetter:
    """
    Implements BNK, which sets the bank to receive assembler output. Leaves
    the Storage bank registers unchanged.
    """
    def __init__(self, assembler: Assembler, name: str):
        self.__assembler = assembler
        self.__name = name

    def emit(self, tokens: [str]) -> None:
        bank_number = 0
        if (len(tokens)) < 2:
            self.__assembler.error("Bank number required, using 0.")
        else:
            bank_number = self.__assembler.token_to_bank(tokens[1])
        self.__assembler.set_bank(bank_number)

    def name(self) -> str:
        return self.__name

class MemorySetter:
    def __init__(self, assembler: Assembler, name: str):
        self.__assembler = assembler
        self.__name = name

    def emit(self, tokens: [str]) -> None:
        if len(tokens) < 2:
            self.__assembler.warning("Literal value missing, using 0o0000")
        self.__assembler.emit_word(int(tokens[1], 8))

class AbstractStorageRegisterSetter:
    """
    Base class for commands that set storage registers in the
    emulator register bank.
    """
    def __init__(self, assembler: Assembler, name: str, max: int):
        """
        Constructor

        :param max:
        :param assembler: Assembler containing the storage whose bank
               registers will be set.
        :param max maximum allowed value
        :param name: instruction name, e.g. SETB to set the buffer
               bank register
        """
        self._assembler = assembler
        self.__name = name
        self.__max = max

    def string_to_setting(self, tokens : [str]) ->(bool, int):
        """
        Check that the token list contains a valid register setting and, if
        valid, convert it to an integer

        :param tokens: parsed instructions token
        :return: (status, value), where status is True if an only if the
                 token list contains a valid value, and value contains
                 the bank value if status is True.
        """
        status = False
        value = -1
        if len(tokens) >= 2:
            try:
                maybe_bank_no = int(tokens[1], 8)
                if 0 <= maybe_bank_no <= self.__max:
                    value = maybe_bank_no
                    status = True
                else:
                    self._assembler.error(
                        "Bank number must be between 0 and 7, found {0}."
                        .format(maybe_bank_no))
            except ValueError:
                self._assembler.error("Invalid value: {0}".format(tokens[1]))
        else:
            self._assembler.error( "Bank number required.")
        return status, value

    def name(self) -> str:
        return self.__name

class BufferRegisterSetter(AbstractStorageRegisterSetter):
    """
    Sets the buffer bank register in the interpreter's register file
    """

    def __init__(self, assembler: Assembler,  name: str):
        """
        Constructor

        :param assembler: Assembler containing the storage whose bank
               registers will be set.
        :param name: instruction name
        """
        super(BufferRegisterSetter, self).__init__(assembler, name, 7)

    def emit(self, tokens: [str]) -> None:
        status, bank_no = self.string_to_setting(tokens)
        if status:
            self._assembler.set_buffer_bank(bank_no)
        self._assembler.print_current_line_without_instruction()


class DirectRegisterSetter(AbstractStorageRegisterSetter):
    """
    Sets the direct bank register in the interpreter's register file
    """

    def __init__(self, assembler: Assembler, name: str):
        """
        Constructor

        :param assembler: Assembler containing the storage whose bank
               registers will be set.
        :param name: instruction name
        """
        super(DirectRegisterSetter, self).__init__(assembler, name, 7)

    def emit(self, tokens: [str]) -> None:
        status, bank_no = self.string_to_setting(tokens)
        if status:
            self._assembler.set_direct_bank(bank_no)
        self._assembler.print_current_line_without_instruction()


class IndirectRegisterSetter(AbstractStorageRegisterSetter):
    """
    Sets the indirect bank register in the interpreter's register file
    """

    def __init__(self, assembler: Assembler, name: str):
        """
        Constructor

        :param assembler: Assembler containing the storage whose bank
               registers will be set.
        :param name: instruction name
        """
        super(IndirectRegisterSetter, self).__init__(assembler, name, 7)

    def emit(self, tokens: [str]) -> None:
        status, bank_no = self.string_to_setting(tokens)
        if status:
            self._assembler.set_indirect_bank(bank_no)
        self._assembler.print_current_line_without_instruction()


class ProgramAddressSetter(AbstractStorageRegisterSetter):
    """
    Sets the relative bank register in the interpreter's register file
    """

    def __init__(self, assembler: Assembler, name: str):
        """
        Constructor

        :param assembler: Assembler containing the storage whose bank
               registers will be set.
        :param name: instruction name
        """
        super(ProgramAddressSetter, self).__init__(assembler, name, 0o7777)

    def emit(self, tokens: [str]) -> None:
        status, address = self.string_to_setting(tokens)
        if status:
            self._assembler.set_program_counter(address)
        self._assembler.print_current_line_without_instruction()


class RelativeRegisterSetter(AbstractStorageRegisterSetter):
    """
    Sets the relative bank register in the interpreter's register file
    """

    def __init__(self, assembler: Assembler, name: str):
        """
        Constructor

        :param assembler: Assembler containing the storage whose bank
               registers will be set.
        :param name: instruction name
        """
        super(RelativeRegisterSetter, self).__init__(assembler, name, 7)

    def emit(self, tokens: [str]) -> None:
        status, bank_no = self.string_to_setting(tokens)
        if status:
            self._assembler.set_relative_bank(bank_no)
        self._assembler.print_current_line_without_instruction()


class VacuousEmitter:
    def __init__(self, assembler: Assembler, name: str):
        self.__assembler = assembler
        self.__name = name

    def emit(self, _) -> None:
        self.__assembler.emit_nothing()

    def name(self) -> str:
        return self.__name

class FixedEValue:
    """
    A one word instruction having a fixed E value
    """
    def __init__(self, assembler: Assembler, name: str, output: int):
        """
        Constructor

        :param assembler: receives the assembled instruction
        :param name: three character instruction name
        :param output: output in the range [0o0000, 0o7777]
        """
        self.__assembler = assembler
        self.__name = name
        self.__output = output

    def emit(self, _: [str]) -> None:
        self.__assembler.emit_word(self.__output)

    def name(self) -> str:
        return self.__name

class StopAssembly:
    """
    Stops assembly
    """
    def __init__(self, assembler: Assembler, name: str):
        """
        Construction

        :param assembler: receives the assembled instruction
        :param name: three character instruction name
        """
        self.__assembler = assembler
        self.__name = name

    def emit(self, _: [str]) -> None:
        self.__assembler.stop()

    def name(self) -> str:
        return self.__name

class OneWordAnyE:
    """
    A single word instruction whose E can assume any possible value
    in [0o00 .. 0o77]
    """

    def __init__(self, assembler: Assembler, name: str, instruction: int):
        """
        Construction

        :param assembler: the target assembler
        :param name: instruction name
        :param instruction: op-code in [0o00 .. 0o77]
        """
        self.__assembler = assembler
        self.__name = name
        self.__instruction = (instruction << 6) & 0o7700

    def emit(self, tokens: [str]) -> None:
        e_value = 0o77
        if len(tokens) < 2:
            self.__assembler.error(
                "E value missing, using 77")
        else:
            e_value = self.__assembler.token_to_e(tokens[1], 0o77)
        self.__assembler.emit_word(self.__instruction | e_value)

    def name(self) -> str:
        """
        Returns the instruction name

        :return: the instruction name as documented in the CDC-160-A
                 reference manual
        """
        return self.__name

class OneWordLowE:

    def __init__(
            self, assembler: Assembler,  name: str, opcode: int, high_e: int):
        self.__assembler = assembler
        self.__name = name
        self.__opcode = opcode << 6
        self.__high_e = (high_e << 3) & 0o70

    def emit(self, tokens: [str]) -> None:
        low_e = 0o07
        if len(tokens) < 2:
            self.__assembler.error(
                "Bank number missing, using 7")
        else:
            low_e = self.__assembler.token_to_bank(tokens[1])
        self.__assembler.emit_word(self.__opcode | self.__high_e | low_e)

    def name(self) -> str:
        return self.__name

class OneWordNonZeroE:
    """
    An instruction with n E in [0o01 .. 0o77]
    """
    def __init__(self, assembler: Assembler, name: str, instruction: int):
        """
        Constructor

        :param assembler: receives the assembled instruction
        :param name: three character instruction name
        :param instruction: instruction code in the range [0o00 .. 0o77]
        """
        self.__assembler = assembler
        self.__instruction = (instruction << 6) & 0o7700
        self.__name = name

    def emit(self, tokens: [str]) -> None:
        e_value = 0o77
        if len(tokens) < 2:
            self.__assembler.error(
                "E value is required; using 0077")
        else:
            maybe_e_value = self.__assembler.token_to_e(tokens[1], 0o77)
            if maybe_e_value == 0:
                self.__assembler.error(
                    "E cannot be zero, using 77")
            else:
                e_value = maybe_e_value
        self.__assembler.emit_word(self.__instruction | e_value)

    def name(self) -> str:
        return self.__name

class OneWordRangeE:
    """
    Emitter for an instruction whose E value must be in a fixed range.
    The range is set at construction.
    """
    def __init__(
            self,
            assembler: Assembler,
            name: str,
            instruction: int,
            e_lower_bound: int,
            e_upper_bound: int):
        """
        Constructor

        :param assembler: emits the instruction
        :param name: instruction name
        :param instruction: op-code in [0o00 .. 0o77]
        :param e_lower_bound: lowest permissible E
        :param e_upper_bound: highest permissible E
        """
        self.__assembler = assembler
        self.__name = name
        self.__instruction = (instruction << 6) & 0o7700
        self.__e_lower_bound = e_lower_bound
        self.__e_upper_bound = e_upper_bound

    def emit(self, tokens: [str]):
        e_value = self.__e_upper_bound
        if len(tokens) < 2:
            self.__assembler.error(
                "E not provided, using {0}.".format(e_value))
        else:
            maybe_e_value = self.__assembler.token_to_e(tokens[1], e_value)
            if (maybe_e_value < self.__e_lower_bound
                or self.__e_upper_bound < maybe_e_value):
                self.__assembler.error(
                    "E must be between {0} and {1} inclusive, {2} provided. Using {3}."
                        .format(
                        oct(self.__e_lower_bound),
                              oct(self.__e_upper_bound),
                              oct(maybe_e_value),
                              oct(e_value)))
            else:
                e_value = maybe_e_value

        self.__assembler.emit_word(self.__instruction | e_value)


    def name(self):
        return self.__name

class TwoWordZeroE:
    """
    A two word instruction whose E is fixed at 00
    """
    def __init__(self, assembler: Assembler, name: str, instruction: int):
        """
          Constructor

          :param assembler: receives the assembled instruction
          :param name: three character instruction name
          :param instruction: instruction code in the range [0o00 .. 0o77]
          """
        self.__assembler = assembler
        self.__name = name
        self.__output = (instruction << 6) & 0o7700

    def emit(self, tokens: [str]) -> None:
        g_value = 0
        if len(tokens) < 2:
            self.__assembler.error(
                "G value (second token) is missing, using 0")
        else:
            g_value = int(tokens[1], 8)
        self.__assembler.emit_two_words(self.__output, g_value)


    def name(self) -> str:
        return self.__name

class TwoWordFixedE:
    """
    A two word instruction having a fixed E value.
    """
    def __init__(
            self,
            assembler: Assembler,
            name: str,
            instruction: int,
            e_value: int):
        self.__assembler = assembler
        self.__name = name
        self.__output = instruction << 6 | e_value

    def emit(self, tokens: [str]) -> None:
        g_value = 0
        match len(tokens):
            case 0:
                raise "Internal error, instruction name missing"
            case 1:
                self.__assembler.error("G value missing, using 7777")
            case _:
                g_value =self.__assembler.token_to_g(tokens[1], 0o7777)
        self.__assembler.emit_two_words(self.__output, g_value)

    def name(self) -> str:
        return self.__name


class TwoWordVariableE:
    """
    A two word instruction whose E value varies. A transform is made between
    the provided E and the generated E. The transform is provided at
    construction, and can be trivial if desired.
    """
    def __init__(
            self,
            assembler: Assembler,
            name: str,
            instruction: int,
            e_validator: Callable[[int], bool],
            e_transform: Callable[[int], int]):
        """
        Constructor

        :param assembler: emits assembled instructions
        :param name: instruction mnemonic
        :param instruction: op-code in [0o00 .. 0o77
        :param e_validator: predicate that validates the provided E value
        :param e_transform: applied to the provided E before emission.
        """
        self.__assembler = assembler
        self.__name = name
        self.__instruction = (instruction << 6) & 0o7700
        self.__e_validator = e_validator
        self.__e_transform = e_transform

    def emit(self, tokens: [str]) -> None:
        raw_e = 7
        g = 0o7777

        match len(tokens):
            case 0:
                raise "Internal error: no instruction name."
            case 1:
                    self.__assembler.error(
                        "E and G are required, using 7 and 7777 respectively")
            case 2:
                self.__assembler.error(
                    "G is required, using 7777")
                raw_e = self.__extract_e(tokens[1])
            case _:
                raw_e = self.__extract_e(tokens[1])
                g = self.__assembler.token_to_g(tokens[2], 0o7777)

        instruction = self.__e_transform(raw_e) | self.__instruction
        self.__assembler.emit_two_words(instruction, g)

    def name(self) -> str:
        return self.__name

    def __extract_e(self, token: str):
        e = 7
        maybe_raw_e = self.__assembler.token_to_e(token, e)
        if self.__e_validator(maybe_raw_e):
            e = maybe_raw_e
        else:
            self.__assembler.error("Invalid E value, using 7.Please find "
                                   "valid values in the  reference manual.")
        return e

class Assembler:
    """
    A primitive assembler that loads Storage with the assembled code.

    A primitive proto-assembler that translates source into binary
    and loads the binary into a Storage instance. Instruction names
    are taken from the CDC 160-A assembler, programming, and
    reference manuals. The assembler supports a few pseudo-instructions
    defined in the assembler manual and some implementation-specific
    additions. It does not support symbols of any sort, and the
    output is absolute, i.e. not relocatable.

    Input format:

    Each line contains a single instruction which is formed of one
    or two tokens. Unlike the official assembler, input has no set
    form.

    Numbers are unsigned octal and only contain digits in ['0' .. '7'].
    Numbers MUST NOT have a prefix (e.g. no "0o" prefix).

    Output format:

    The assembler writes a listing to the termai. Each line contains:

      A line number, starting from 0

      The target address and bank in the form AAAA(b) where AAAA is a
      four digit octal memory address and b is a one octal digit
      bank number. This is printed even if the assembler emits no
      code.

      The emitted code, one or two four-digit octal numbers depending
      on the instruction.

    Instructions have three possible semantics, each of which
    has its own format.

    1. One word instructions having a set E value, e.g. LS1 (0o0102),
       which are represented by one token, the instruction name. All
       following tokens (if any) are ignored except that the
       assembler issues a warning if the second token, if present,
       is an octal number.

    2. One word instructions having a variable E value, e.g. LDF OO,
       where OO is an octal number in the range [0, 0o77] inclusive.
       The first token contains the instruction name and the second
       contains the E value. The assembler issues an error if the
       second token is missing or malformed.

    3. Two word instructions having a fixed E value and a G value
       in the range of [0, 0o7777]. The first token contains
       the instruction name and the second contains the G value.
       The assembler issues an error if the G value is missing,
       malformed, or out of range.

    4. Two word instructions having a variable and possibly restricted
       E value. The first token is the instruction, the second is the E
       value, and the third is the G value.

    5. Pseudo-instructions, instructions that affect assembly and
       generate no code.

    Note that well-formed E and G values will not exceed
    the maximum allowed value. Bounds are checked where
    required.

    The assembler supports the following pseudo instruction types:

    Formatting, pseudo instructions that are written to the listing and
    do nothing else:

        A blank line, which produces a blank like in the listing and is
        otherwise ignored.

        REM, remarks to appear in the listing and otherwise ignored.

    Code generation control:

        BNK sets the memory bank to receive emitted code. Note that BNK
        does not alter the target memory address, nor does it set bank
        registers to be used when the emitted program runs.

        ORG sets the target memory address for the next emitted
        instruction. Note that ORG does not change any memory bank
        settings.

    Runtime configuration, instructions that configure the emulator's
    runtime settings.

        SETB: sets the buffer bank register to its starting value,
        the value it will have when the assembled program starts.

        SETD: sets the direct bank register to its starting value

        SETI: sets the indirect bank register to its starting value

        SETP: sets the program address, a.k.a. P Register, to its
        starting value

        SETR: sets the relative storage bank register to its starting value

    Note that s runtime configuration pseudo instruction overwrites
    any previous settings. If two SETB instructions occur in a program,
    the second one prevails.
    """

    def __init__(self, source, storage: Storage):
        """
        Constructor

        :param source: iterator that provides source, one line at a time.
        :param storage: emulator's memory and register file.
        """
        self.__address = 0
        self.__bank = 0
        self.__current_source_line = ""
        self.__line_count = 0
        self.__errors = 0
        self.__error_or_warning = None
        self.__formatted_instruction = None
        self.__memory_use = MemoryUse()
        self.__running = True
        self.__source_lines = source
        self.__storage = storage
        self.__warnings = 0
        self.__words_written = 0

        self.__emitters = {
            "ACJ": OneWordLowE(self, "ACJ", 0o00, 0o07),
            "ADB": OneWordNonZeroE(self, "ADB", 0o33),
            "ADC": TwoWordZeroE(self, "ADC", 0o32),
            "ADD": OneWordAnyE(self, "ADD", 0o30),
            "ADF": OneWordNonZeroE(self, "ADC", 0o32),
            "ADI": OneWordNonZeroE(self, "ADI", 0o31),
            "ADM": TwoWordZeroE(self, "ADM", 0o31),
            "ADN": OneWordAnyE(self, "ADN", 0o06),
            "ADS": FixedEValue(self, "ADS", 0o3300),
            "AOB": OneWordNonZeroE(self, "AOB", 0o57),
            "AOC": TwoWordZeroE(self, "AOC", 0o56),
            "AOD": OneWordAnyE(self, "AOD", 0o54),
            "AOF": OneWordNonZeroE(self, "AOF", 0o56),
            "AOI": OneWordNonZeroE(self, "AOI", 0o55),
            "AOM": TwoWordZeroE(self, "AOM", 0o55),
            "AOS": FixedEValue(self, "AOS", 0o5700),
            "ATE": TwoWordFixedE(self, "ATE", 0o01, 0o05),
            "ATX": TwoWordFixedE(self, "ATX", 0o01, 0x06),
            "BLS": TwoWordZeroE(self, "BLS", 0o01),
            "BNK": AssemblerBankSetter(self, "BNK"),
            "CBC": FixedEValue(self, "CBC", 0o0104),
            "CIL": FixedEValue(self, "CIL", 0o0120),
            "CTA": FixedEValue(self, "CTA", 0o0130),
            "DRJ": OneWordLowE(self, "DRJ", 0o00, 0o05),
            "END": StopAssembly(self, "ERR"),
            "ERR": FixedEValue(self, "ERR", 0o0000),
            "ETA": FixedEValue(self, "ETA", 0o0107),
            "EXC": TwoWordZeroE(self, "EXC", 0o75),
            "EXF": OneWordNonZeroE(self, "EXF", 0o75),
            "HLT": FixedEValue(self, "HLT", 0o7700),
            "IBI": TwoWordZeroE(self, "IBI", 0o72),
            "IBO": TwoWordZeroE(self, "IBO", 0o73),
            "INA": FixedEValue(self, "INA", 0o7600),
            "INP": TwoWordVariableE(self, "INP", 0o72, lambda e: True, lambda e:  e),
            "HWI": OneWordRangeE(self, "HWI", 0o76, 0o01, 0o76),
            "IRJ": OneWordLowE(self, "IRJ", 0o00, 0o03),
            "JFI": OneWordNonZeroE(self, "JFI", 0o71),
            "JPI": OneWordAnyE(self, "JPI", 0o70),
            "JPR": TwoWordZeroE(self, "JPR", 0o71),
            "LCB": OneWordNonZeroE(self, "LCB", 0o27),
            "LCC": TwoWordZeroE(self, "LCC", 0o26),
            "LCD": OneWordAnyE(self, "LCD", 0o24),
            "LCF": OneWordNonZeroE(self, "LCF", 0o26),
            "LCI": OneWordNonZeroE(self, "LCI", 0o25),
            "LCM": TwoWordZeroE(self, "LCM", 0o25),
            "LCN": OneWordAnyE(self, "LCN", 0o05),
            "LCS": FixedEValue(self, "LCS", 0o2700),
            "LDC": TwoWordZeroE(self, "LDC", 0o22),
            "LDB": OneWordNonZeroE(self,"LDB", 0o23),
            "LDD": OneWordAnyE(self, "LDD", 0o20),
            "LDF": OneWordNonZeroE(self, "LDF", 0o22),
            "LDI": OneWordNonZeroE(self, "LDI", 0o21),
            "LDM": TwoWordZeroE(self, "LDM", 0o21),
            "LDN": OneWordAnyE(self, "LDN", 0o04),
            "LDS": FixedEValue(self, "LDS", 0o2300),
            "LPB": OneWordNonZeroE(self, "LPM", 0o13),
            "LPC": TwoWordZeroE(self, "LPC", 0o12),
            "LPD": OneWordAnyE(self, "LPD", 0o10),
            "LPF": OneWordNonZeroE(self, "LPF", 0o12),
            "LPI": OneWordNonZeroE(self, "LPI",0o11),
            "LPM": TwoWordZeroE(self, "LPM", 0o11),
            "LPN": OneWordAnyE(self, "LPN", 0o02),
            "LPS": FixedEValue(self, "LPS", 0o1300),
            "LS1": FixedEValue(self, "LSI", 0o0102),
            "LS2": FixedEValue(self, "LS2", 0o0103),
            "LS3": FixedEValue(self, "LS3", 0o0110),
            "LS6": FixedEValue(self,"LS6", 0o0111),
            "MUH": FixedEValue(self, "MUH", 0o0113),
            "MUT": FixedEValue(self, "MUT", 0o0112),
            "NJB": OneWordAnyE(self, "NJB", 0o67),
            "NJF": OneWordAnyE(self, "NJF", 0o63),
            "NOP": FixedEValue(self, "NOP", 0o0007),
            "NZB": OneWordAnyE(self, "NZB", 0o65),
            "NZF": OneWordAnyE(self, "NZF", 0o61),
            "OCT": MemorySetter(self, "OCT"),
            "ORG": AddressSetter(self, "ORG"),
            "OTA": FixedEValue(self, "OTA", 0o7677),
            "OTN": OneWordAnyE(self, "OTN", 0o74),
            "OUT": TwoWordVariableE(self, "INP", 0o73, lambda e: True, lambda e:  e),
            "PJB": OneWordAnyE(self, "PJB", 0o66),
            "PJF": OneWordAnyE(self, "PJF", 0o62),
            "PTA": FixedEValue(self, "PTA", 0o0101),
            "RAB": OneWordNonZeroE(self, "RAB", 0o53),
            "RAC": TwoWordZeroE(self, "RAC", 0o52),
            "RAD": OneWordAnyE(self, "RAD", 0o50),
            "RAF": OneWordNonZeroE(self, "RAF", 0o52),
            "RAI": OneWordNonZeroE(self, "RAI", 0o51),
            "RAS": FixedEValue(self, "RAS", 0o5300),
            "RAM": TwoWordZeroE(self, "RAM", 0o51),
            "REM": VacuousEmitter(self, "REM"),
            "RS1": FixedEValue(self, "RS1", 0o0114),
            "RS2": FixedEValue(self, "RS2", 0o0115),
            "SBB": OneWordNonZeroE(self, "SBB", 0o37),
            "SBC": TwoWordZeroE(self, "SBC", 0o36),
            "SBD": OneWordAnyE(self, "SBD", 0o34),
            "SBF": OneWordNonZeroE(self, "SBF", 0o36),
            "SBI": OneWordNonZeroE(self, "SBD", 0o35),
            "SBM": TwoWordZeroE(self, "SBM", 0o35),
            "SBN": OneWordAnyE(self, "SBN", 0o07),
            "SBS": FixedEValue(self, "SBS", 0o3700),
            "SBU": OneWordLowE(self, "SBU", 0o01, 0o04),
            "SCB": OneWordNonZeroE(self, "SCB", 0o17),
            "SCC": TwoWordZeroE(self, "SCC", 0o16),
            "SCD": OneWordAnyE(self, "SCD", 0o14),
            "SCF": OneWordNonZeroE(self, "SCF", 0o16),
            "SCI": OneWordNonZeroE(self, "SCI", 0o15),
            "SETB": BufferRegisterSetter(self, "SETB"),
            "SETD": DirectRegisterSetter(self, "SETD"),
            "SETI": IndirectRegisterSetter(self, "SETI"),
            "SETP": ProgramAddressSetter(self, "SETP"),
            "SETR": RelativeRegisterSetter(self, "SETR"),
            "SIC": OneWordLowE(self, "SIC", 0o00, 0o02),
            "SID": OneWordLowE(self, "SID", 0o00, 0o06),
            "SCM": TwoWordZeroE(self, "SCM", 0o15),
            "SCN": OneWordAnyE(self, "SCN", 0o03),
            "SCS": FixedEValue(self, "SCS", 0o1700),
            "SDC": OneWordLowE(self, "SDC", 0o00, 0o04),
            "SJS": TwoWordVariableE(self, "SJS", 0o77, lambda e: 0 < e < 0o77, lambda e: e),
            "SLJ": TwoWordVariableE(self,"SLJ", 0o77, lambda e: 0 < e <= 7, lambda e: (e << 3) & 0o70),
            "SLS": OneWordRangeE(self, "SLS", 0o77, 0o1,0o7),
            "SRB": OneWordNonZeroE(self, "SRB", 0o47),
            "SRC": TwoWordZeroE(self, "SRC", 0o46),
            "SRD": OneWordAnyE(self, "SRD", 0o44),
            "SRF": OneWordNonZeroE(self, "SRF", 0o46),
            "SRI": OneWordNonZeroE(self, "SRI", 0o45),
            "SRJ": OneWordLowE(self, "SRJ", 0o00, 0o01),
            "SRS": FixedEValue(self, "SRS", 0o4700),
            "SRM": TwoWordZeroE(self, "SRM", 0o45),
            "STB": OneWordNonZeroE(self, "STB", 0o43),
            "STC": TwoWordZeroE(self, "STC", 0o42),
            "STD": OneWordAnyE(self, "STD", 0o40),
            "STE": OneWordRangeE(self, "STE", 0o01, 0o60, 0o67),
            "STF": OneWordNonZeroE(self, "STF", 0o42),
            "STI": OneWordAnyE(self, "STI", 0o41),
            "STM": TwoWordZeroE(self, "STM", 0o41),
            "STP": OneWordRangeE(self, "STP", 0o01, 0o50, 0o57),
            "STS": FixedEValue(self, "STS", 0o4300),
            "ZJB": OneWordAnyE(self, "ZJB", 0o64),
            "ZJF": OneWordAnyE(self, "ZJF", 0o60),
        }

    def __crack_and_emit(self) -> None:
        tokens = self.__current_source_line.split()
        if (len(tokens)) < 1:
            self.emit_nothing()
        elif tokens[0] in self.__emitters:
            emitter = self.__emitters[tokens[0]]
            emitter.emit(tokens)
        else:
            self.error(
                "Illegal operation name: {0}.".format(
                    tokens[0]
                )
            )
            self.print_current_line("         ")
        self.__line_count += 1

    def __store_and_advance(self, value: int) -> None:
        self.__storage.write_absolute(self.__bank, self.__address, value)
        self.__memory_use.mark_used(self.__bank, self.__address)
        self.__address = (self.__address + 1) & 0o7777
        self.__words_written += 1

    def address(self) -> int:
        return self.__address

    def bank(self) -> int:
        return self.__bank

    def error(self, description: str) -> None:
        self.__error_or_warning = "Error: {0}".format(description)
        self.__errors += 1

    def emit_nothing(self) -> None:
        self.print_current_line_without_instruction()

    def emit_two_words(self, first: int, second: int) -> None:
        self.print_current_line("{0} {1}".format(
            four_digit_octal(first),
            four_digit_octal(second)
        ))
        self.__store_and_advance(first)
        self.__store_and_advance(second)

    def emit_word(self, value: int) -> None:
        self.print_current_line("{0}     ".format(four_digit_octal(value)))
        self.__store_and_advance(value)

    def emitter(self, name: str):
        return self.__emitters[name]

    def error_count(self) -> int:
        return self.__errors

    def fatal(self, description: str) -> None:
        self.__error_or_warning ="Fatal error: {0}".format(description)
        self.__errors += 1
        self.__running = False

    def format_address(self) -> str:
        return "{0}({1}):".format(
            four_digit_octal(self.__address),
            one_digit_octal(self.__bank)
        )

    def line_count(self) -> int:
        return self.__line_count

    def memory_use(self) -> MemoryUse:
        return self.__memory_use

    def print_current_line(self, instr: str) -> None:
        print(
            "{0:5}> {1} {2} {3}".format(
                self.__line_count,
                self.format_address(),
                instr,
                self.__current_source_line),
            flush=True)
        if self.__error_or_warning:
            print(self.__error_or_warning, file=sys.stderr)

    def print_current_line_without_instruction(self) -> None:
        self.print_current_line("         ")

    def run(self) -> bool:
        with self.__source_lines as source:
            for self.__current_source_line in source:
                self.__error_or_warning = None
                self.__formatted_instruction = "                  "
                self.__crack_and_emit()
                if not self.__running:
                    break

        print(
            "End of program, {0} errors, {1} warnings".format(
                self.__errors,
                self.__warnings
            )
        )
        return self.__errors == 0

    def set_address(self, value: int) -> None:
        self.__address = value
        self.print_current_line_without_instruction()

    def set_bank(self, value: int) -> None:
        self.__bank = value
        self.print_current_line_without_instruction()

    def set_buffer_bank(self, value: int) -> None:
        """
        Sets the buffer bank register in the Storage bound
        to self. This value will apply if the3 assembled program
        runs. Does not alter the Assembler bank.

        :param value: bank number in [0 .. 0o7] Range not checked.
        :return: None
        """
        self.__storage.buffer_storage_bank = value

    def set_direct_bank(self, value: int) -> None:
        """
        Sets the direct bank register in the Storage bound
        to self. This value will apply if the3 assembled program
        runs. Does not alter the Assembler bank.

        :param value: bank number in [0 .. 0o7] Range not checked.
        :return: None
        """
        self.__storage.direct_storage_bank = value

    def set_indirect_bank(self, value: int) -> None:
        """
        Sets the indirect bank register in the Storage bound
        to self. This value will apply if the3 assembled program
        runs. Does not alter the Assembler bank.

        :param value: bank number in [0 .. 0o7] Range not checked.
        :return: None
        """
        self.__storage.indirect_storage_bank = value

    def set_relative_bank(self, value: int) -> None:
        """
        Sets the direct bank register in the Storage bound
        to self. This value will apply if the3 assembled program
        runs. Does not alter the Assembler bank.

        :param value: bank number in [0 .. 0o7] Range not checked.
        :return: None
        """
        self.__storage.relative_storage_bank = value

    def set_program_counter(self, value: int) -> None:
        """
        Sets the P register in the Storage bound
        to self. This value will apply if the3 assembled program
        runs. Does not alter the Assembler address.

        :param value: bank number in [0 .. 0o7777] Range not checked.
        :return: None
        """
        self.__storage.p_register = value

    def stop(self) -> None:
        self.__running = False
        self.print_current_line("         ")

    def token_to_bank(self, token: str) -> int:
        bank = 0
        if 0 < len(token) < 2 and BANK_PATTERN.match(token):
            bank = int(token, 8)
        else:
            self.error(
                "Bank must be a single octal digit in [0 .. ], was '{0}', using 0"
                    .format(token))
        return bank

    def token_to_e(self, token: str, default: int) -> int:
        e = default
        if 0 < len(token) < 3 and E_PATTERN.match(token):
            e = int(token, 8)
        else:
            self.error(
                "E must be one or two octal digits, was {0}, using {1}"
                    .format(token, default))
        return e

    def token_to_g(self, token: str, default: int) -> int:
        g = default
        if 0 < len(token) < 5 and G_PATTERN.match(token):
            g = int(token, 8)
        else:
            self.error(
                "E must be one through four octal digits, was {0} using {1}."
                    .format(token, default))
        return g

    def warning(self, description: str) -> None:
        sys.stderr.print("Warning: {0}", description)
        self.__warnings += 1

    def warning_count(self) -> int:
        return self.__warnings

    def words_written(self) -> int:
        return self.__words_written


def assembler_from_file(pathname: str, storage: Storage) -> Optional[Assembler]:
    """
    Create an Assembler that takes its input from the provided path name

    :param pathname of the file containing the assembler source. Supports
          full paths.
    :param storage interpreter's memory and register file
    :return: an Assembler if creation is successful, None otherwise.
    """
    result = None
    if path.exists(pathname):
        input_file = open(pathname)
        result = Assembler(input_file, storage)
    return result


class ClosableString:
    """
    Wrapper class that makes a string iterable by breaking it into
    lines and usable with 'with'.
    """
    def __init__(self, source: str):
        self.__source = source

    def __enter__(self):
        return self.__source.splitlines()

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

def assembler_from_string(source: str, storage: Storage) -> Optional[Assembler]:
    """
    Creates an assembler that takes a string as input.

    :param source: contains the program to assemble
    :param storage: emulator memory and register file
    :return: the newly minted Assembler
    """
    return Assembler(ClosableString(source), storage)
