from unittest import TestCase
from test_support import Programs
from cdc160a.Storage import Storage
from test_support.Assembler import Assembler, two_digit_octal, four_digit_octal
from test_support.Assembler import one_digit_octal

class TestAssembler(TestCase):

    def setUp(self) -> None:
        self.__storage = Storage()

    def dearDown(self):
        self.__storage = None

    def assembler(self, source: str = '') -> Assembler:
        return Assembler(source, self.__storage)

    def test_one_digit_octal(self) -> None:
        assert one_digit_octal(0o0) == "0"
        assert one_digit_octal(0o1) == "1"
        assert one_digit_octal(0o2) == "2"
        assert one_digit_octal(0o3) == "3"
        assert one_digit_octal(0o4) == "4"
        assert one_digit_octal(0o4) == "4"
        assert one_digit_octal(0o5) == "5"
        assert one_digit_octal(0o6) == "6"
        assert one_digit_octal(0o7) == "7"
        try:
            one_digit_octal(0o10)
            self.fail("Expected failure on 0o10")
        except AssertionError:
            pass
        try:
            one_digit_octal(-1)
            self.fail("Expected failure on -1")
        except AssertionError:
            pass

    def test_two_digit_octal(self) -> None:
        assert two_digit_octal(0o0) == "00"
        assert two_digit_octal(0o12) == "12"
        try:
            two_digit_octal(-1)
            self.fail("Exception expected for -1")
        except AssertionError:
            pass
        try:
            two_digit_octal(0o100)
            self.fail("Expected exception on 0o100")
        except AssertionError:
            pass

    def test_four_digit_octal(self) -> None:
        assert four_digit_octal(0o0000) == "0000"
        assert four_digit_octal(0o1234) == "1234"
        try:
            four_digit_octal(-1)
            self.fail("Exception expected for -1")
        except AssertionError:
            pass
        try:
            four_digit_octal(0o10000)
            self.fail("Expected exception on 0o10000")
        except AssertionError:
            pass

    def test_empty_one_statement_program(self) -> None:
        source = "          END\n"
        assembler = self.assembler(source)
        assert assembler.run()
        assert assembler.address() == 0
        assert assembler.bank() == 0
        assert assembler.line_count() == 1
        assert assembler.error_count() == 0
        assert assembler.warning_count() == 0
        assert assembler.words_written() == 0

    def test_empty_three_statement_program(self) -> None:
        assembler = self.assembler(
            Programs.VACUOUS_THREE_LINE_PROGRAM_WITH_BLANK_LINE)
        assert assembler.run()
        assert assembler.address() == 0
        assert assembler.bank() == 0
        assert assembler.line_count() == 3
        assert assembler.error_count() == 0
        assert assembler.warning_count() == 0
        assert assembler.words_written() == 0

    def test_set_bank(self) -> None:
        assembler = self.assembler(Programs.SET_STORAGE_BANK)
        assembler.run()
        assert assembler.address() == 0
        assert assembler.bank() == 3
        assert assembler.line_count() == 4
        assert assembler.error_count() == 0
        assert assembler.warning_count() == 0
        assert assembler.words_written() == 0

    def test_set_address(self) -> None:
        assembler = self.assembler(Programs.SET_ADDRESS)
        assert assembler.run()
        assert assembler.address() == 0o1234
        assert assembler.bank() == 0
        assert assembler.line_count() == 4
        assert assembler.error_count() == 0
        assert assembler.warning_count() == 0
        assert assembler.words_written() == 0

    def test_halt(self) -> None:
        assembler = self.assembler(Programs.HALT)
        assert assembler.run()
        assert assembler.address() == 0o0101
        assert assembler.bank() == 3
        assert assembler.line_count() == 6
        assert assembler.error_count() == 0
        assert assembler.warning_count() == 0
        assert assembler.words_written() == 1
        assert self.__storage.read_absolute(0o3, 0o0100) == 0o7700

    def test_nop_then_halt(self) -> None:
        assembler = self.assembler(Programs.NOOP_THEN_HALT)
        assert assembler.run()
        assert assembler.address() == 0o0102
        assert assembler.bank() == 3
        assert assembler.line_count() == 7
        assert assembler.error_count() == 0
        assert assembler.warning_count() == 0
        assert assembler.words_written() == 2
        assert self.__storage.read_absolute(0o3, 0o0100) == 0o0007
        assert self.__storage.read_absolute(0o3, 0o0101) == 0o7700

    def test_ldc_then_halt(self) -> None:
        assembler = self.assembler(Programs.LDC_THEN_HALT)
        assert assembler.run()
        assert assembler.address() == 0o0103
        assert assembler.bank() == 3
        assert assembler.line_count() == 7
        assert assembler.error_count() == 0
        assert assembler.warning_count() == 0
        assert assembler.words_written() == 3
        assert self.__storage.read_absolute(0o3, 0o0100) == 0o2200
        assert self.__storage.read_absolute(0o3, 0o0101) == 0o4321
        assert self.__storage.read_absolute(0o3, 0o0102) == 0o7700
