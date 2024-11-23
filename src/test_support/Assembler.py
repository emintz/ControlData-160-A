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

   Note that well-formed E and G values will not exceed
   the maximum allowed value. Minimums are checked where
   required.
   """
from __future__ import annotations

from cdc160a import Storage
import re
import sys

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

class BankSetter:
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
    An instruction having a fixed E value
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

class TwoWordFixedE:
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

class Assembler:
    def __init__(self, source: str, storage: Storage):
        self.__address = 0
        self.__bank = 0
        self.__current_source_line = ""
        self.__line_count = 0
        self.__running = True
        self.__errors = 0
        self.__error_or_warning = None
        self.__formatted_instruction = None
        self.__source_lines = source.splitlines()
        self.__storage = storage
        self.__warnings = 0
        self.__words_written = 0

        self.__emitters = {
            "ADB": OneWordNonZeroE(self, "ADB", 0o33),
            "ADC": TwoWordFixedE(self, "ADC", 0o32),
            "ADD": OneWordAnyE(self, "ADD", 0o30),
            "ADF": OneWordNonZeroE(self, "ADC", 0o32),
            "ADI": OneWordNonZeroE(self, "ADI", 0o31),
            "ADM": TwoWordFixedE(self, "ADM", 0o31),
            "ADN": OneWordAnyE(self, "ADN", 0o06),
            "ADS": FixedEValue(self, "ADS", 0o3300),
            "AOB": OneWordNonZeroE(self, "AOB", 0o57),
            "AOC": TwoWordFixedE(self, "AOC", 0o56),
            "AOD": OneWordAnyE(self, "AOD", 0o54),
            "AOF": OneWordNonZeroE(self, "AOF", 0o56),
            "AOI": OneWordNonZeroE(self, "AOI", 0o55),
            "AOM": TwoWordFixedE(self, "AOM", 0o55),
            "AOS": FixedEValue(self, "AOS", 0o5700),
            "BNK": BankSetter(self, "BNK"),
            "END": StopAssembly(self, "ERR"),
            "ERR": FixedEValue(self, "ERR", 0o0000),
            "HLT": FixedEValue(self, "HLT", 0o7700),
            "LCB": OneWordNonZeroE(self, "LCB", 0o27),
            "LCC": TwoWordFixedE(self, "LCC", 0o26),
            "LCD": OneWordAnyE(self, "LCD", 0o24),
            "LCF": OneWordNonZeroE(self, "LCF", 0o26),
            "LCI": OneWordNonZeroE(self, "LCI", 0o25),
            "LCM": TwoWordFixedE(self, "LCM", 0o25),
            "LCN": OneWordAnyE(self, "LCN", 0o05),
            "LCS": FixedEValue(self, "LCS", 0o2700),
            "LDC": TwoWordFixedE(self, "LDC", 0o22),
            "LDB": OneWordNonZeroE(self,"LDB", 0o23),
            "LDD": OneWordAnyE(self, "LDD", 0o20),
            "LDF": OneWordNonZeroE(self, "LDF", 0o22),
            "LDI": OneWordNonZeroE(self, "LDI", 0o21),
            "LDM": TwoWordFixedE(self, "LDM", 0o21),
            "LDN": OneWordAnyE(self, "LDN", 0o04),
            "LDS": FixedEValue(self, "LDS", 0o2300),
            "LPB": OneWordNonZeroE(self, "LPM", 0o13),
            "LPC": TwoWordFixedE(self, "LPC", 0o12),
            "LPD": OneWordAnyE(self, "LPD", 0o10),
            "LPF": OneWordNonZeroE(self, "LPF", 0o12),
            "LPI": OneWordNonZeroE(self, "LPI",0o11),
            "LPM": TwoWordFixedE(self, "LPM", 0o11),
            "LPN": OneWordAnyE(self, "LPN", 0o02),
            "LPS": FixedEValue(self, "LPS", 0o1300),
            "LS1": FixedEValue(self, "LSI", 0o0102),
            "LS2": FixedEValue(self, "LS2", 0o0103),
            "LS3": FixedEValue(self, "LS3", 0o0110),
            "LS6": FixedEValue(self,"LS6", 0o0111),
            "NJB": OneWordAnyE(self, "NJB", 0o67),
            "NJF": OneWordAnyE(self, "NJF", 0o63),
            "NOP": FixedEValue(self, "NOP", 0o0007),
            "NZB": OneWordAnyE(self, "NZB", 0o65),
            "NZF": OneWordAnyE(self, "NZF", 0o61),
            "PJB": OneWordAnyE(self, "PJB", 0o66),
            "PJF": OneWordAnyE(self, "PJF", 0o62),
            "OCT": MemorySetter(self, "OCT"),
            "ORG": AddressSetter(self, "ORG"),
            "RAB": OneWordNonZeroE(self, "RAB", 0o53),
            "RAC": TwoWordFixedE(self, "RAC", 0o52),
            "RAD": OneWordAnyE(self, "RAD", 0o50),
            "RAF": OneWordNonZeroE(self, "RAF", 0o52),
            "RAI": OneWordNonZeroE(self, "RAI", 0o51),
            "RAS": FixedEValue(self, "RAS", 0o5300),
            "RAM": TwoWordFixedE(self, "RAM", 0o51),
            "REM": VacuousEmitter(self, "REM"),
            "RS1": FixedEValue(self, "RS1", 0o0114),
            "RS2": FixedEValue(self, "RS2", 0o0115),
            "SBB": OneWordNonZeroE(self, "SBB", 0o37),
            "SBC": TwoWordFixedE(self, "SBC", 0o36),
            "SBD": OneWordAnyE(self, "SBD", 0o34),
            "SBF": OneWordNonZeroE(self, "SBF", 0o36),
            "SBI": OneWordNonZeroE(self, "SBD", 0o35),
            "SBM": TwoWordFixedE(self, "SBM", 0o35),
            "SBN": OneWordAnyE(self, "SBN", 0o07),
            "SBS": FixedEValue(self, "SBS", 0o3700),
            "STB": OneWordNonZeroE(self, "STB", 0o43),
            "STC": TwoWordFixedE(self, "STC", 0o42),
            "STD": OneWordAnyE(self, "STD", 0o40),
            "STF": OneWordNonZeroE(self, "STF", 0o42),
            "STI": OneWordAnyE(self, "STI", 0o41),
            "STM": TwoWordFixedE(self, "STM", 0o41),
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

    def print_current_line(self, instr: str) -> None:
        print(
            "{0}> {1} {2} {3}".format(
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
        for self.__current_source_line in self.__source_lines:
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


