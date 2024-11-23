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

    def test_token_to_bank_valid_input(self) -> None:
        assembler = self.assembler("          END\n")
        assert assembler.token_to_bank("3") == 3
        assert assembler.error_count() == 0

    def test_token_to_bank_input_too_long(self) -> None:
        assembler = self.assembler("          END\n")
        assert assembler.token_to_bank("10") == 0
        assert assembler.error_count() == 1

    def test_token_to_bank_not_octal(self) -> None:
        assembler = self.assembler("          END\n")
        assert assembler.token_to_bank("9") == 0
        assert assembler.error_count() == 1

    def test_token_to_e_valid_input(self) -> None:
        assembler = self.assembler("          END\n")
        assert assembler.token_to_e("1", 0) == 0o1
        assert assembler.error_count() == 0
        assert assembler.token_to_e("12", 0) == 0o12
        assert assembler.error_count() == 0

    def test_token_to_e_input_too_long(self) -> None:
        assembler = self.assembler("          END\n")
        assert assembler.token_to_e("123", 0) == 0
        assert assembler.error_count() == 1

    def test_token_to_e_not_octal(self) -> None:
        assembler = self.assembler("          END\n")
        assert assembler.token_to_e("##", 0) == 0
        assert assembler.error_count() == 1

    def test_token_to_g_valid_input(self) -> None:
        assembler = self.assembler("          END\n")
        assert assembler.token_to_g("1", 0) == 0o1
        assert assembler.error_count() == 0
        assert assembler.token_to_g("12", 0) == 0o12
        assert assembler.error_count() == 0
        assert assembler.token_to_g("123", 0) == 0o123
        assert assembler.error_count() == 0
        assert assembler.token_to_g("1234", 0) == 0o1234
        assert assembler.error_count() == 0

    def test_token_to_g_input_too_long(self) -> None:
        assembler = self.assembler("          END\n")
        assert assembler.token_to_g("12345", 0) == 0
        assert assembler.error_count() == 1

    def test_token_to_g_not_octal(self) -> None:
        assembler = self.assembler("          END\n")
        assert assembler.token_to_g("*", 0) == 0
        assert assembler.error_count() == 1

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

    def test_adb(self) -> None:
        self.__single_instruction_test("ADB 4", [0o3304])

    def test_adc(self) -> None:
        self.__single_instruction_test(
            "ADC 4321", [0o3200, 0o4321])

    def test_add(self) -> None:
        self.__single_instruction_test("ADD 40", [0o3040])

    def test_adf(self) -> None:
        self.__single_instruction_test("ADF 14", [0o3214])

    def test_adi(self) -> None:
        self.__single_instruction_test("ADI 20", [0O3120])

    def test_adm(self) -> None:
        self.__single_instruction_test(
            "ADM 1234", [0o3100, 0o1234])

    def test_adn(self) -> None:
        self.__single_instruction_test("ADN 40", [0o0640])

    def test_ads(self) -> None:
        self.__single_instruction_test("ADS", [0o3300])

    def test_aob(self) -> None:
        self.__single_instruction_test("AOB 6", [0o5706])

    def test_aoc(self) -> None:
        self.__single_instruction_test("AOC 4321", [0o5600, 0o4321])

    def test_aod(self) -> None:
        self.__single_instruction_test("AOD 20", [0o5420])

    def test_aof(self) -> None:
        self.__single_instruction_test("AOF 4", [0o5604])

    def test_aoi(self) -> None:
        self.__single_instruction_test("AOI 14", [0o5514])

    def test_aom(self) -> None:
        self.__single_instruction_test("AOM 1234", [0o5500, 0o1234])

    def test_aos(self) -> None:
        self.__single_instruction_test("AOS", [0o5700])

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
        assert assembler.line_count() == 9
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

    def test_lpb(self) -> None:
        self.__single_instruction_test("LPB 22", [0o1322])

    def test_lpc(self) -> None:
        self.__single_instruction_test("LPC 0000", [0o1200, 0o0000])
        self.__single_instruction_test("LPC 4321", [0o1200, 0o4321])

    def test_lpd(self) -> None:
        self.__single_instruction_test("LPD 00", [0o1000])
        self.__single_instruction_test("LPD 40", [0o1040])

    def test_lpi(self) -> None:
        self.__single_instruction_test("LPI 31", [0o1131])

    def test_lpm(self) -> None:
        self.__single_instruction_test("LPM 0", [0o1100, 0])
        self.__single_instruction_test("LPM 01400", [0o1100, 0o1400])

    def test_lpn(self) -> None:
        self.__single_instruction_test("LPN 00", [0o0200])
        self.__single_instruction_test("LPN 40", [0o0240])

    def test_lps(self) -> None:
        self.__single_instruction_test("LPS", [0o1300])

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

    def test_muh(self) -> None:
        self.__single_instruction_test("MUH", [0o0113])

    def test_mut(self) -> None:
        self.__single_instruction_test("MUT", [0o112])

    def test_oct(self) -> None:
        assembler = self.assembler(Programs.SET_LITERAL)
        assembler.run()
        assert assembler.address() == 0o0101
        assert assembler.bank() == 3
        assert self.__storage.read_absolute(3, 0o0100) == 0o1234

    def test_njb(self) -> None:
        self.__single_instruction_test("NJB 50", [0o6750])
        self.__single_instruction_test("NJB 0", [0o6700])

    def test_njf(self) -> None:
        self.__single_instruction_test(
            "NJF 40", [0o6340])

    def test_nop(self) -> None:
        self.__single_instruction_test("NOP", [0o0007])

    def test_nzb(self) -> None:
        self.__single_instruction_test("NZB 30", [0o6530])
        self.__single_instruction_test("NZB 0", [0o6500])

    def test_nzf(self) -> None:
        self.__single_instruction_test(
            "NZF 40", [0o6140])

    def test_pjb(self) -> None:
        self.__single_instruction_test("PJB 34", [0o6634])
        self.__single_instruction_test("PJB 0", [0o6600])

    def test_pjf(self) -> None:
        self.__single_instruction_test(
            "PJF 40",[0o6240])

    def test_ras(self) -> None:
        self.__single_instruction_test(
            "RAB 24", [0o5324])

    def test_rac(self) -> None:
        self.__single_instruction_test(
            "RAC 1234", [0o5200, 0o1234])

    def test_rad(self) -> None:
        self.__single_instruction_test(
            "RAD 10", [0o5010])

    def test_raf(self) -> None:
        self.__single_instruction_test(
            "RAF 20", [0o5220])

    def test_rai(self) -> None:
        self.__single_instruction_test(
            "RAI 30", [0o5130])

    def test_ram(self) -> None:
        self.__single_instruction_test(
            "RAM 2000", [0o5100, 0o2000])

    def test_ras(self) -> None:
        self.__single_instruction_test("RAS", [0o5300])

    def test_rs1(self) -> None:
        self.__single_instruction_test("RS1", [0o0114])

    def test_rs2(self) -> None:
        self.__single_instruction_test("RS2", [0o0115])

    def test_sbc(self) -> None:
        self.__single_instruction_test("SBC 4321", [0o3600, 0o4321])

    def test_sbb(self) -> None:
        self.__single_instruction_test("SBB 17", [0o3717])

    def test_sbd(self) -> None:
        self.__single_instruction_test("SBD 12", [0o3412])
        self.__single_instruction_test("SBD 0", [0o3400])

    def test_sbf(self) -> None:
        self.__single_instruction_test("SBF 77", [0o3677])

    def test_sbi(self) -> None:
        self.__single_instruction_test("SBI 34", [0o3534])

    def test_sbm(self) -> None:
        self.__single_instruction_test("SBM 1234", [0o03500, 0o1234])

    def test_sbn(self) -> None:
        self.__single_instruction_test("SBN 12", [0o0712])
        self.__single_instruction_test("SBN 00", [0O0700])

    def test_sbs(self) -> None:
        self.__single_instruction_test("SBS", [0o3700])

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

    def test_zjb(self) -> None:
        self.__single_instruction_test("ZJB 60", [0o6460])
        self.__single_instruction_test("ZJB 0", [0o6400])

    def test_zjf(self) -> None:
        self.__single_instruction_test(
            "ZJF 40", [0o6040])
        self.__single_instruction_test("ZJF 0", [0o6000])

    def __single_instruction_test(
            self, instruction: str, expected_output: [int]) -> None:
        assembler = self.assembler(
            SINGLE_INSTRUCTION_TEMPLATE.format(instruction))
        assembler.run()
        address = 0o77
        for expected in expected_output:
            address += 1
            assert self.__storage.read_absolute(3, address) == expected
        address += 1
        assert self.__storage.read_absolute(3, address) == 0o00