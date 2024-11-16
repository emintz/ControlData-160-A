from unittest import TestCase
from test_support import Programs
from cdc160a.Storage import Storage
from test_support.Assembler import Assembler, two_digit_octal, four_digit_octal
from test_support.Assembler import one_digit_octal

SINGLE_INSTRUCTION_TEMPLATE = """
          BNK 3
          ORG 100
          {0}
          END
"""

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

    def test_ldc_shift_halt(self) -> None:
        assembler = self.assembler(Programs.LDC_SHIFT_HALT)
        assembler.run()
        assert assembler.address() == 0o0104
        assert assembler.bank() == 3
        assert assembler.line_count() == 8
        assert assembler.error_count() == 0
        assert assembler.warning_count() == 0
        assert assembler.words_written() == 4
        assert self.__storage.read_absolute(3, 0o0100) == 0o2200
        assert self.__storage.read_absolute(3, 0o0101) == 0o4321
        assert self.__storage.read_absolute(3, 0o0102) == 0o0110
        assert self.__storage.read_absolute(3, 0o0103) == 0o7700
        assert self.__storage.read_absolute(3, 0o0104) == 0o0000

    def test_lcb(self) -> None:
        self.__single_instruction_test("LCB 12", [0o2712])

    def test_lcc(self) -> None:
        self.__single_instruction_test("LCC 6543", [0o2600, 0o6543])

    def test_lcd(self) -> None:
        self.__single_instruction_test("LCD 10", [0o2410])
        self.__single_instruction_test("LCD 0", [0o2400])

    def test_lcf(self) -> None:
        self.__single_instruction_test("LCF 40", [0o2640])

    def test_lci(self) -> None:
        self.__single_instruction_test("LCI 32", [0o2532])

    def test_lcm(self) -> None:
        self.__single_instruction_test("LCM 7654", [0o2500, 0o7654])

    def test_lcn(self) -> None:
        self.__single_instruction_test("LCN 0", [0o0500])
        self.__single_instruction_test("LCN 30", [0o0530])

    def test_lcs(self) -> None:
        self.__single_instruction_test("LCS", [0o2700])

    def test_err(self) -> None:
        self.__single_instruction_test("ERR", [0o0000])

    def test_hlt(self) -> None:
        self.__single_instruction_test("HLT", [0o7700])

    def test_ldb(self) -> None:
        self.__single_instruction_test("LDB 30", [0o2330])

    def test_ldc(self) -> None:
        self.__single_instruction_test(
            "LDC 2143", [0o2200, 0o2143])

    def test_ldd(self) -> None:
        self.__single_instruction_test("LDD 10", [0o2010])

    def test_ldf(self) -> None:
        self.__single_instruction_test("LDF 14", [0o2214])

    def test_ldi(self) -> None:
        self.__single_instruction_test("LDI 20", [0o2120])

    def test_ldm(self) -> None:
        self.__single_instruction_test(
            "LDM 4321", [0o2100, 0o4321])

    def test_ldn(self) -> None:
        self.__single_instruction_test("LDN 20", [0o0420])
        self.__single_instruction_test("LDN 0", [0o0400])

    def test_lds(self) -> None:
        self.__single_instruction_test("LDS", [0o2300])

    def test_ls1(self) -> None:
        self.__single_instruction_test("LS1", [0o0102])

    def test_ls2(self) -> None:
        self.__single_instruction_test("LS2", [0o0103])

    def test_ls3(self) -> None:
        self.__single_instruction_test("LS3", [0o00110])

    def test_ls6(self) -> None:
        self.__single_instruction_test("LS6", [0o0111])

    def test_oct(self) -> None:
        assembler = self.assembler(Programs.SET_LITERAL)
        assembler.run()
        assert assembler.address() == 0o0101
        assert assembler.bank() == 3
        assert self.__storage.read_absolute(3, 0o0100) == 0o1234

    def test_njf(self) -> None:
        self.__single_instruction_test(
            "NJF 40", [0o6340])

    def test_nop(self) -> None:
        self.__single_instruction_test("NOP", [0o0007])

    def test_nzf(self) -> None:
        self.__single_instruction_test(
            "NZF 40", [0o6140])

    def test_pjf(self) -> None:
        self.__single_instruction_test(
            "PJF 40",[0o6240])

    def test_rs1(self) -> None:
        self.__single_instruction_test("RS1", [0o0114])

    def test_rs2(self) -> None:
        self.__single_instruction_test("RS2", [0o0115])

    def test_stb(self) -> None:
        self.__single_instruction_test("STB 24", [0o4324])

    def test_stc(self) -> None:
        self.__single_instruction_test(
            "STC 5432", [0o4200, 0o5432])

    def test_std(self) -> None:
        self.__single_instruction_test(
            "STD 10", [0o4010])
        self.__single_instruction_test("STD 0", [0o4000])

    def test_stf(self) -> None:
        self.__single_instruction_test("STF 5", [0o4205])

    def test_sdi(self) -> None:
        self.__single_instruction_test("STI 50", [0o4150])
        self.__single_instruction_test("STI 0", [0o4100])

    def test_stm(self) -> None:
        self.__single_instruction_test(
            "STM 5432", [0o4100, 0o5432])

    def test_sts(self) -> None:
        self.__single_instruction_test("STS", [0o4300])

    def test_zdf(self) -> None:
        self.__single_instruction_test(
            "ZJF 40", [0o6040])

    def __single_instruction_test(
            self, instruction: str, expected_output: [int]) -> None:
        assembler = self.assembler(
            SINGLE_INSTRUCTION_TEMPLATE.format(instruction))
        assembler.run()
        address = 0o77
        for expected in expected_output:
            address += 1
            assert self.__storage.read_absolute(3, address) == expected