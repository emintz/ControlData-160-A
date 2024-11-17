import unittest
from unittest import TestCase

from Instructions import Instruction
from cdc160a import Instructions
from cdc160a.Storage import Storage
from typing import Final

READ_AND_WRITE_ADDRESS: Final[int] = 0o1234
INSTRUCTION_ADDRESS: Final[int] = 0o1232
G_ADDRESS: Final[int] = INSTRUCTION_ADDRESS + 1
AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS: Final[int] = INSTRUCTION_ADDRESS + 1
AFTER_DOUBLE_WORD_INSTRUCTION_ADDRESS: Final[int] = INSTRUCTION_ADDRESS + 2

class Test(TestCase):

    def setUp(self) -> None:
        self.storage = Storage()
        self.storage.memory[0, READ_AND_WRITE_ADDRESS] = 0o10
        self.storage.memory[1, READ_AND_WRITE_ADDRESS] = 0o11
        self.storage.memory[2, READ_AND_WRITE_ADDRESS] = 0o12
        self.storage.memory[3, READ_AND_WRITE_ADDRESS] = 0o13
        self.storage.memory[4, READ_AND_WRITE_ADDRESS] = 0o14
        self.storage.memory[5, READ_AND_WRITE_ADDRESS] = 0o15
        self.storage.memory[6, READ_AND_WRITE_ADDRESS] = 0o16
        self.storage.memory[7, READ_AND_WRITE_ADDRESS] = 0o17
        self.storage.memory[0, 0o7777] = 0o77
        self.storage.p_register = INSTRUCTION_ADDRESS
        self.storage.s_register = INSTRUCTION_ADDRESS
        self.storage.buffer_storage_bank = 1
        self.storage.direct_storage_bank = 2
        self.storage.indirect_storage_bank = 3
        self.storage.relative_storage_bank = 4
        self.storage.run()

    def tearDown(self) -> None:
        self.storage = None

    def test_err(self) -> None:
        # err
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0000)
        self.storage.z_register = 0o3333
        self.storage.a_register = 0o3333
        self.storage.unpack_instruction()
        Instructions.ERR.determine_effective_address(self.storage)
        assert Instructions.ERR.perform_logic(self.storage) == 1
        assert not self.storage.run_stop_status
        assert self.storage.err_status
        assert self.storage.a_register == 0o3333
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_hlt(self) -> None:
        # hlt
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o7700)
        self.storage.z_register = 0o3333
        self.storage.a_register = 0o3333
        self.storage.unpack_instruction()
        Instructions.ERR.determine_effective_address(self.storage)
        assert Instructions.HLT.perform_logic(self.storage) == 1
        assert not self.storage.run_stop_status
        assert not self.storage.err_status
        assert self.storage.a_register == 0o3333
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_lcb(self) -> None:
        # LCB 10
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o2710)
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS - 0o10, 0o5555)
        self.storage.unpack_instruction()
        Instructions.LCB.determine_effective_address(self.storage)
        Instructions.LCB.perform_logic(self.storage)
        assert self.storage.z_register == 0O5555
        assert self.storage.a_register == 0o5555 ^ 0o7777
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        assert self.storage.run_stop_status

    def test_lcc(self) -> None:
        # LCC 6666
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o2600)
        self.storage.write_relative_bank(G_ADDRESS, 0o6666)
        self.storage.p_register = INSTRUCTION_ADDRESS
        self.storage.unpack_instruction()
        Instructions.LCC.determine_effective_address(self.storage)
        assert Instructions.LCC.perform_logic(self.storage) == 2
        assert self.storage.z_register == 0o6666
        assert self.storage.a_register == 0o6666 ^ 0o7777
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_DOUBLE_WORD_INSTRUCTION_ADDRESS
        assert self.storage.run_stop_status

    def test_lcd(self) -> None:
        # LCD 45
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o2445)
        self.storage.write_direct_bank(INSTRUCTION_ADDRESS, 0o7654)
        self.storage.unpack_instruction()
        assert Instructions.LCD.perform_logic(self.storage) == 2
        assert self.storage.s_register == INSTRUCTION_ADDRESS
        assert self.storage.z_register == 0o7654
        assert self.storage.a_register == 0o7654 ^ 0o7777
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        assert self.storage.run_stop_status

    def test_lcf(self) -> None:
        # LCF 20
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o2620)
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS + 0o20, 0o2222)
        self.storage.unpack_instruction()
        Instructions.LCF.determine_effective_address(self.storage)
        Instructions.LCF.perform_logic(self.storage)
        assert self.storage.z_register == 0o2222
        assert self.storage.a_register ==0o2222 ^ 0o7777
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        assert self.storage.run_stop_status

    def test_lci(self) -> None:
        # LCI 45
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o2545)
        self.storage.write_indirect_bank(0o45, 0o7654)
        self.storage.unpack_instruction()
        Instructions.LCI.determine_effective_address(self.storage)
        assert Instructions.LCI.perform_logic(self.storage) == 3
        assert self.storage.s_register == 0o45
        assert self.storage.z_register == 0o7654
        assert self.storage.a_register == 0o7654 ^ 0o7777
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        assert self.storage.run_stop_status

    def test_lcm(self) -> None:
        # LCM 137
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o2500)
        self.storage.write_relative_bank(G_ADDRESS, 0o137)
        self.storage.write_indirect_bank(0o137, 0o1370)
        self.storage.unpack_instruction()
        Instructions.LCM.determine_effective_address(self.storage)
        assert Instructions.LCM.perform_logic(self.storage) ==3
        assert self.storage.s_register == 0o137
        assert self.storage.z_register == 0o1370
        assert self.storage.a_register == 0o1370 ^ 0o7777
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_DOUBLE_WORD_INSTRUCTION_ADDRESS
        assert self.storage.run_stop_status

    def test_lcn(self) -> None:
        # LCN 37
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0537)
        self.storage.unpack_instruction()
        Instructions.LCN.determine_effective_address(self.storage)
        assert Instructions.LCN.perform_logic(self.storage) == 1
        self.storage.advance_to_next_instruction()
        assert self.storage.s_register == INSTRUCTION_ADDRESS
        assert self.storage.z_register == 0o37
        assert self.storage.a_register == 0o37 ^ 0o7777

    def test_lcs(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o2700)
        self.storage.unpack_instruction()
        Instructions.LCS.determine_effective_address(self.storage)
        assert Instructions.LCS.perform_logic(self.storage) == 2
        assert self.storage.z_register == 0o77
        assert self.storage.a_register == 0o77 ^ 0o7777
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_ldb(self) -> None:
        # LDB 10
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o2310)
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS - 0o10, 0o5555)
        self.storage.unpack_instruction()
        Instructions.LDB.determine_effective_address(self.storage)
        Instructions.LDB.perform_logic(self.storage)
        assert self.storage.z_register == 0O5555
        assert self.storage.a_register == 0o5555
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        assert self.storage.run_stop_status

    def test_ldc(self) -> None:
        # LDC 6666
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o2200)
        self.storage.write_relative_bank(G_ADDRESS, 0o6666)
        self.storage.p_register = INSTRUCTION_ADDRESS
        self.storage.unpack_instruction()
        Instructions.LDC.determine_effective_address(self.storage)
        assert Instructions.LDC.perform_logic(self.storage) == 2
        assert self.storage.z_register == 0o6666
        assert self.storage.a_register == 0o6666
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_DOUBLE_WORD_INSTRUCTION_ADDRESS
        assert self.storage.run_stop_status

    def test_ldd(self) -> None:
        # LDD 45
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o2045)
        self.storage.write_direct_bank(INSTRUCTION_ADDRESS, 0o7654)
        self.storage.unpack_instruction()
        assert Instructions.LDD.perform_logic(self.storage) == 2
        assert self.storage.s_register == INSTRUCTION_ADDRESS
        assert self.storage.z_register == 0o7654
        assert self.storage.a_register == 0o7654
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        assert self.storage.run_stop_status

    def test_ldf(self) -> None:
        # LDF 20
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o2220)
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS + 0o20, 0o2222)
        self.storage.unpack_instruction()
        Instructions.LDF.determine_effective_address(self.storage)
        Instructions.LDF.perform_logic(self.storage)
        assert self.storage.z_register == 0o2222
        assert self.storage.a_register ==0o2222
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        assert self.storage.run_stop_status

    def test_ldi(self) -> None:
        # LDI 45
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o2145)
        self.storage.write_indirect_bank(0o45, 0o7654)
        self.storage.unpack_instruction()
        Instructions.LDI.determine_effective_address(self.storage)
        assert Instructions.LDI.perform_logic(self.storage) == 3
        assert self.storage.s_register == 0o45
        assert self.storage.z_register == 0o7654
        assert self.storage.a_register == 0o7654
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        assert self.storage.run_stop_status

    def test_ldm(self) -> None:
        # LDM 137
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o2100)
        self.storage.write_relative_bank(G_ADDRESS, 0o137)
        self.storage.write_indirect_bank(0o137, 0o1370)
        self.storage.unpack_instruction()
        Instructions.LDM.determine_effective_address(self.storage)
        assert Instructions.LDM.perform_logic(self.storage) ==3
        assert self.storage.s_register == 0o137
        assert self.storage.z_register == 0o1370
        assert self.storage.a_register == 0o1370
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_DOUBLE_WORD_INSTRUCTION_ADDRESS
        assert self.storage.run_stop_status

    def test_ldn(self) -> None:
        # LDN 37
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0437)
        self.storage.unpack_instruction()
        Instructions.LDN.determine_effective_address(self.storage)
        assert Instructions.LDN.perform_logic(self.storage) == 1
        self.storage.advance_to_next_instruction()
        assert self.storage.s_register == INSTRUCTION_ADDRESS
        assert self.storage.z_register == 0o37
        assert self.storage.a_register == 0o37

    def test_lds(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o3200)
        self.storage.unpack_instruction()
        Instructions.LDS.determine_effective_address(self.storage)
        assert Instructions.LDS.perform_logic(self.storage) == 2
        assert self.storage.z_register == 0o77
        assert self.storage.a_register == 0o77
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_ls1(self)-> None:
        # LS1
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0x0102)
        self.storage.unpack_instruction()
        self.storage.z_register = 0o4001
        self.storage.a_register = 0o4001
        Instructions.LS1.determine_effective_address(self.storage)
        assert Instructions.LS1.perform_logic(self.storage) == 1
        assert self.storage.run_stop_status
        assert self.storage.z_register == 0o4001
        assert self.storage.a_register == 0o0003
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_ls2(self) -> None:
        # LS2
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0103)
        self.storage.unpack_instruction()
        self.storage.z_register = 0o6001
        self.storage.a_register = 0o6001
        Instructions.LS2.determine_effective_address(self.storage)
        assert Instructions.LS2.perform_logic(self.storage) == 1
        assert self.storage.run_stop_status
        assert self.storage.z_register == 0o6001
        assert self.storage.a_register == 0o0007
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_ls3(self) -> None:
        # LS3
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0110)
        self.storage.unpack_instruction()
        self.storage.z_register = 0o7000
        self.storage.a_register = 0o7000
        Instructions.LS3.determine_effective_address(self.storage)
        assert Instructions.LS3.perform_logic(self.storage) == 1
        assert self.storage.run_stop_status
        assert self.storage.z_register == 0o7000
        assert self.storage.a_register == 0o0007
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_ls6(self) -> None:
        # LS6
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0111)
        self.storage.unpack_instruction()
        self.storage.z_register = 0o3412
        self.storage.z_to_a()
        Instructions.LS6.determine_effective_address(self.storage)
        assert Instructions.LS6.perform_logic(self.storage) == 1
        assert self.storage.run_stop_status
        assert self.storage.z_register == 0o3412
        assert self.storage.a_register == 0o1234
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_njb_a_minus_zero(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6402)
        self.storage.a_register = 0o7777
        self.storage.unpack_instruction()
        Instructions.NJB.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS - 2
        Instructions.NJB.perform_logic(self.storage)
        assert (self.storage.next_address() ==
                INSTRUCTION_ADDRESS - 2)
        self.storage.advance_to_next_instruction()
        assert (self.storage.p_register ==
                INSTRUCTION_ADDRESS - 2)

    def test_njb_a_negative(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6402)
        self.storage.a_register = 0o7777
        self.storage.unpack_instruction()
        Instructions.NJB.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS - 2
        Instructions.NJB.perform_logic(self.storage)
        assert (self.storage.next_address() ==
                INSTRUCTION_ADDRESS - 2)
        self.storage.advance_to_next_instruction()
        assert (self.storage.p_register ==
                INSTRUCTION_ADDRESS - 2)

    def test_njb_a_positive(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6402)
        self.storage.a_register = 1
        self.storage.unpack_instruction()
        Instructions.NJB.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS - 2
        Instructions.NJB.perform_logic(self.storage)
        assert (self.storage.next_address() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)
        self.storage.advance_to_next_instruction()
        assert (self.storage.p_register ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_njb_a_zero(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6402)
        self.storage.a_register = 0
        self.storage.unpack_instruction()
        Instructions.NJB.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS - 2
        Instructions.NJB.perform_logic(self.storage)
        assert (self.storage.next_address() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)
        self.storage.advance_to_next_instruction()
        assert (self.storage.p_register ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_njf_a_minus_zero(self) -> None:
        # NJF
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6340)
        self.storage.a_register = 0o7777
        self.storage.unpack_instruction()
        Instructions.NJF.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 0o0040
        Instructions.NJF.perform_logic(self.storage)
        assert self.storage.next_address() == INSTRUCTION_ADDRESS + 0o0040
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == INSTRUCTION_ADDRESS + 0o0040

    def test_njf_a_negative(self) -> None:
        # NJF
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6340)
        self.storage.a_register = 0o7776
        self.storage.unpack_instruction()
        Instructions.NJF.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 0o0040
        Instructions.NJF.perform_logic(self.storage)
        assert self.storage.next_address() == INSTRUCTION_ADDRESS + 0o0040
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == INSTRUCTION_ADDRESS + 0o0040

    def test_njf_a_positive(self) -> None:
        # NJF
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6340)
        self.storage.a_register = 0o3777
        self.storage.unpack_instruction()
        Instructions.NJF.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 0o0040
        Instructions.NJF.perform_logic(self.storage)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_njf_a_zero(self) -> None:
        # NJF
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6340)
        self.storage.a_register = 0
        self.storage.unpack_instruction()
        Instructions.NJF.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 0o0040
        Instructions.NJF.perform_logic(self.storage)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_nzb_a_minus_zero(self) -> None:
        # NZB
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6540)
        self.storage.a_register = 0o7777
        self.storage.unpack_instruction()
        Instructions.NZB.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS - 0o0040
        Instructions.NZB.perform_logic(self.storage)
        assert self.storage.next_address() == INSTRUCTION_ADDRESS - 0o0040
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == INSTRUCTION_ADDRESS - 0o0040

    def test_nzb_a_negative(self) -> None:
        # NZB
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6540)
        self.storage.a_register = 0o4000
        self.storage.unpack_instruction()
        Instructions.NZB.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS - 0o0040
        Instructions.NZB.perform_logic(self.storage)
        assert self.storage.next_address() == INSTRUCTION_ADDRESS - 0o0040
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == INSTRUCTION_ADDRESS - 0o0040

    def test_nzb_a_positive(self) -> None:
        # NZB
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6540)
        self.storage.a_register = 0o3777
        self.storage.unpack_instruction()
        Instructions.NZB.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS - 0o0040
        Instructions.NZB.perform_logic(self.storage)
        assert self.storage.next_address() == INSTRUCTION_ADDRESS - 0o0040
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == INSTRUCTION_ADDRESS - 0o0040

    def test_nzb_a_zero(self) -> None:
        # NZB
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6540)
        self.storage.a_register = 0
        self.storage.unpack_instruction()
        Instructions.NZB.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS - 0o0040
        Instructions.NZB.perform_logic(self.storage)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_nzf_a_minus_zero(self) -> None:
        # NZF
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6140)
        self.storage.a_register = 0o7777
        self.storage.unpack_instruction()
        Instructions.NZF.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 0o0040
        Instructions.NZF.perform_logic(self.storage)
        assert self.storage.next_address() == INSTRUCTION_ADDRESS + 0o0040
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == INSTRUCTION_ADDRESS + 0o0040

    def test_nzf_a_negative(self) -> None:
        # NZF
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6140)
        self.storage.a_register = 0o4000
        self.storage.unpack_instruction()
        Instructions.NZF.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 0o0040
        Instructions.NZF.perform_logic(self.storage)
        assert self.storage.next_address() == INSTRUCTION_ADDRESS + 0o0040
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == INSTRUCTION_ADDRESS + 0o0040

    def test_nzf_a_positive(self) -> None:
        # NZF
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6140)
        self.storage.a_register = 0o3777
        self.storage.unpack_instruction()
        Instructions.NZF.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 0o0040
        Instructions.NZF.perform_logic(self.storage)
        assert self.storage.next_address() == INSTRUCTION_ADDRESS + 0o0040
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == INSTRUCTION_ADDRESS + 0o0040

    def test_nzf_a_zero(self) -> None:
        # NZF
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6140)
        self.storage.a_register = 0
        self.storage.unpack_instruction()
        Instructions.NZF.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 0o0040
        Instructions.NZF.perform_logic(self.storage)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_nop(self) -> None:
        # NOP 1
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0001)
        self.storage.z_register = 0o3333
        self.storage.a_register = 0o3333
        Instructions.NOP.determine_effective_address(self.storage)
        assert Instructions.NOP.perform_logic(self.storage) == 1
        assert self.storage.a_register == 0o3333
        assert self.storage.z_register == 0o3333
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_pjf_a_minus_zero(self) -> None:
        # PJF
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6240)
        self.storage.a_register = 0o7777
        self.storage.unpack_instruction()
        Instructions.PJF.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 0o0040
        Instructions.PJF.perform_logic(self.storage)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_pjb_a_minus_zero(self) -> None:
        # PJB
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6240)
        self.storage.a_register = 0o7777
        self.storage.unpack_instruction()
        Instructions.PJB.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS - 0o0040
        Instructions.PJB.perform_logic(self.storage)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_pjb_a_negative(self) -> None:
        # PJB
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6240)
        self.storage.a_register = 0o7776
        self.storage.unpack_instruction()
        Instructions.PJB.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS - 0o0040
        Instructions.PJB.perform_logic(self.storage)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_pjb_a_positive(self) -> None:
        # PJB
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6240)
        self.storage.a_register = 1
        self.storage.unpack_instruction()
        Instructions.PJB.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS - 0o0040
        Instructions.PJB.perform_logic(self.storage)
        assert self.storage.next_address() == INSTRUCTION_ADDRESS - 0o0040
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == INSTRUCTION_ADDRESS - 0o0040

    def test_pjb_a_zero(self) -> None:
        # PJB
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6240)
        self.storage.a_register = 0
        self.storage.unpack_instruction()
        Instructions.PJB.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS - 0o0040
        Instructions.PJB.perform_logic(self.storage)
        assert self.storage.next_address() == INSTRUCTION_ADDRESS - 0o0040
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == INSTRUCTION_ADDRESS - 0o0040

    def test_pjf_a_negative(self) -> None:
        # PJF
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6240)
        self.storage.a_register = 0o7776
        self.storage.unpack_instruction()
        Instructions.PJF.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 0o0040
        Instructions.PJF.perform_logic(self.storage)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_pjf_a_positive(self) -> None:
        # PJF
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6240)
        self.storage.a_register = 1
        self.storage.unpack_instruction()
        Instructions.PJF.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 0o0040
        Instructions.PJF.perform_logic(self.storage)
        assert self.storage.next_address() == INSTRUCTION_ADDRESS + 0o0040
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == INSTRUCTION_ADDRESS + 0o0040

    def test_pjf_a_zero(self) -> None:
        # PJF
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6240)
        self.storage.a_register = 0
        self.storage.unpack_instruction()
        Instructions.PJF.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 0o0040
        Instructions.PJF.perform_logic(self.storage)
        assert self.storage.next_address() == INSTRUCTION_ADDRESS + 0o0040
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == INSTRUCTION_ADDRESS + 0o0040

    def test_rs1(self) -> None:
        # RS1
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0114)
        self.storage.unpack_instruction()
        self.storage.z_register = 0o4020
        self.storage.a_register = 0o4020
        Instructions.RS1.determine_effective_address(self.storage)
        assert Instructions.RS1.perform_logic(self.storage) == 1
        assert self.storage.run_stop_status
        assert self.storage.z_register == 0o4020
        assert self.storage.a_register == 0o6010
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_rs2(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0115)
        self.storage.unpack_instruction()
        self.storage.z_register = 0o0007
        self.storage.z_to_a()
        Instructions.RS2.determine_effective_address(self.storage)
        assert Instructions.RS2.perform_logic(self.storage) == 1
        assert self.storage.run_stop_status
        assert self.storage.z_register == 0o0007
        assert self.storage.a_register == 0o0001
        self.storage.z_register = 0o4007
        self.storage.z_to_a()
        assert Instructions.RS2.perform_logic(self.storage) == 1
        assert self.storage.run_stop_status
        assert self.storage.z_register == 0o4007
        assert self.storage.a_register == 0o7001


    def test_sdb(self) -> None:
        # STB 15
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o4315)
        self.storage.a_register = 0o0210
        self.storage.unpack_instruction()
        Instructions.STB.determine_effective_address(self.storage)
        assert Instructions.STB.perform_logic(self.storage) == 3
        assert self.storage.z_register == 0o0210
        assert self.storage.read_relative_bank(
            INSTRUCTION_ADDRESS - 0o15) == 0o0210
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    # TODO(emintz): verify STC behavior, which makes no sense to me.
    def test_stc(self) -> None:
        # STC 1234
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o4200)
        self.storage.write_relative_bank(G_ADDRESS, 0o1234)
        self.storage.a_register = 0o4321
        self.storage.unpack_instruction()
        Instructions.STC.determine_effective_address(self.storage)
        assert self.storage.s_register == G_ADDRESS
        assert Instructions.STC.perform_logic(self.storage) == 3
        self.storage.advance_to_next_instruction()
        assert self.storage.z_register == 0o4321
        assert self.storage.read_relative_bank(G_ADDRESS) == 0o4321
        assert (self.storage.get_program_counter() ==
                AFTER_DOUBLE_WORD_INSTRUCTION_ADDRESS)

    def test_sdd(self) -> None:
        # STD 15
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o4015)
        self.storage.a_register = 0o0210
        self.storage.unpack_instruction()
        Instructions.STD.determine_effective_address(self.storage)
        assert Instructions.STD.perform_logic(self.storage) == 3
        assert self.storage.z_register == 0o0210
        assert self.storage.read_direct_bank(0o15) == 0o0210
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_sdf(self) -> None:
        # STF 10
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o4210)
        self.storage.a_register = 0o0210
        self.storage.unpack_instruction()
        Instructions.STF.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 0o10
        Instructions.STF.perform_logic(self.storage)
        self.storage.advance_to_next_instruction()
        assert self.storage.z_register == 0o0210
        assert (self.storage.read_relative_bank(INSTRUCTION_ADDRESS + 0o10) ==
                0o0210)
        assert self.storage.get_program_counter() == INSTRUCTION_ADDRESS + 1

    def test_sdi(self) -> None:
        # SDI 14
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o4114)
        self.storage.a_register = 0o0210
        self.storage.unpack_instruction()
        Instructions.STI.determine_effective_address(self.storage)
        assert Instructions.STI.perform_logic(self.storage) == 4
        assert self.storage.z_register == 0o0210
        assert self.storage.read_indirect_bank(0o14) == 0o0210
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_stm(self) -> None:
        # STM 1234
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o4100)
        self.storage.write_relative_bank(G_ADDRESS, READ_AND_WRITE_ADDRESS)
        self.storage.a_register = 0o1234
        self.storage.unpack_instruction()
        Instructions.STM.determine_effective_address(self.storage)
        assert self.storage.s_register == READ_AND_WRITE_ADDRESS
        assert Instructions.STM.perform_logic(self.storage) == 4
        assert self.storage.z_register == 0o1234
        assert self.storage.read_relative_bank(READ_AND_WRITE_ADDRESS) == 0o1234
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_DOUBLE_WORD_INSTRUCTION_ADDRESS)

    def test_sts(self) -> None:
        # STS
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o4300)
        self.storage.a_register = 0o1234
        self.storage.unpack_instruction()
        Instructions.STS.determine_effective_address(self.storage)
        assert self.storage.s_register == 0o7777
        assert Instructions.STS.perform_logic(self.storage)
        assert self.storage.z_register == 0o1234
        assert self.storage.read_specific() == 0o1234
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_zjb_a_minus_zero(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6440)
        self.storage.a_register = 0o7777
        self.storage.unpack_instruction()
        Instructions.ZJB.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS - 0o0040
        Instructions.ZJB.perform_logic(self.storage)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_zjb_a_negative(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6440)
        self.storage.a_register = 0o7777
        self.storage.unpack_instruction()
        Instructions.ZJB.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS - 0o0040
        Instructions.ZJB.perform_logic(self.storage)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_zjb_a_positive(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6440)
        self.storage.a_register = 1
        self.storage.unpack_instruction()
        Instructions.ZJB.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS - 0o0040
        Instructions.ZJB.perform_logic(self.storage)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_zjb_a_zero(self) -> None:
        # ZJF
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6440)
        self.storage.a_register = 0
        self.storage.unpack_instruction()
        Instructions.ZJB.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS - 0o0040
        Instructions.ZJB.perform_logic(self.storage)
        assert self.storage.next_address() == INSTRUCTION_ADDRESS - 0o0040
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == INSTRUCTION_ADDRESS - 0o0040

    def test_zjf_a_minus_zero(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6040)
        self.storage.a_register = 0o7777
        self.storage.unpack_instruction()
        Instructions.ZJF.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 0o0040
        Instructions.ZJF.perform_logic(self.storage)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_zjf_a_negative(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6040)
        self.storage.a_register = 0o7777
        self.storage.unpack_instruction()
        Instructions.ZJF.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 0o0040
        Instructions.ZJF.perform_logic(self.storage)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_zjf_a_positive(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6040)
        self.storage.a_register = 1
        self.storage.unpack_instruction()
        Instructions.ZJF.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 0o0040
        Instructions.ZJF.perform_logic(self.storage)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_zjf_a_zero(self) -> None:
        # ZJF
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6040)
        self.storage.a_register = 0
        self.storage.unpack_instruction()
        Instructions.ZJF.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 0o0040
        Instructions.ZJF.perform_logic(self.storage)
        assert self.storage.next_address() == INSTRUCTION_ADDRESS + 0o0040
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == INSTRUCTION_ADDRESS + 0o0040

if __name__ == "__main__":
    unittest.main()
