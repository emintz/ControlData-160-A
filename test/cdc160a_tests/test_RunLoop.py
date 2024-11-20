from unittest import TestCase

from cdc160a.RunLoop import RunLoop
from cdc160a.Storage import  Storage
from test_support.Assembler import Assembler
from test_support import Programs

class TestRunLoop(TestCase):

    def setUp(self) -> None:
        self.__storage = Storage()
        self.__run_loop = RunLoop(self.__storage)
        self.__storage.set_direct_storage_bank(2)
        self.__storage.set_indirect_storage_bank(1)
        self.__storage.set_relative_storage_bank(0o3)
        self.__storage.set_program_counter(0o0100)

    def tearDown(self) -> None:
        self.__storage = None

    def load_test_program(self, source: str) -> None:
        Assembler(source, self.__storage).run()

    def test_run_hlt(self) -> None:
        self.load_test_program(Programs.HALT)
        self.__run_loop.run()
        assert not self.__storage.err_status
        assert not self.__storage.run_stop_status
        # Note: the run loop advances the P register AFTER checking for halt
        # so that the HLT instruction's address appears on the console.
        assert self.__storage.p_register == 0o0100

    def test_ldc_then_halt(self) -> None:
        self.load_test_program(Programs.LDC_THEN_HALT)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o4321
        assert self.__storage.p_register == 0o0102
        assert not self.__storage.err_status
        assert not self.__storage.run_stop_status

    def test_ldc_ls3_halt(self) -> None:
        self.load_test_program(Programs.LDC_SHIFT_HALT)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o3214
        assert self.__storage.p_register == 0o0103
        assert not self.__storage.err_status
        assert not self.__storage.run_stop_status

    def test_lpb(self) -> None:
        self.load_test_program(Programs.LOGICAL_PRODUCT_BACKWARD)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o21
        assert self.__storage.p_register == 0o103
        assert not self.__storage.err_status

    def test_lpc(self) -> None:
        self.load_test_program(Programs.LOGICAL_PRODUCT_CONSTANT)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o21
        assert self.__storage.p_register == 0o104
        assert not self.__storage.err_status

    def test_lpd(self) -> None:
        self.load_test_program(Programs.LOGICAL_PRODUCT_DIRECT)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o21
        assert self.__storage.p_register == 0o103
        assert not self.__storage.err_status

    def test_lpf(self) -> None:
        self.load_test_program(Programs.LOGICAL_PRODUCT_FORWARD)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o21
        assert self.__storage.p_register == 0o103
        assert not self.__storage.err_status

    def test_lpi(self) -> None:
        self.load_test_program(Programs.LOGICAL_PRODUCT_INDIRECT)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o21
        assert self.__storage.p_register == 0o103
        assert not self.__storage.err_status

    def test_lpm(self) -> None:
        self.load_test_program(Programs.LOGICAL_PRODUCT_MEMORY)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o21
        assert self.__storage.p_register == 0o104
        assert not self.__storage.err_status

    def test_lpn(self) -> None:
        self.load_test_program(Programs.LOGICAL_PRODUCT_NONE)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o21
        assert self.__storage.p_register == 0o103
        assert not self.__storage.err_status

    def test_lps(self) -> None:
        self.load_test_program(Programs.LOGICAL_PRODUCT_SPECIFIC)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o21
        assert self.__storage.p_register == 0o103
        assert not self.__storage.err_status

    def test_njb_a_minus_zero(self) -> None:
        self.load_test_program(Programs.NEGATIVE_JUMP_BACKWARD_MINUS_ZERO_A)
        self.__run_loop.run()
        assert not self.__storage.err_status
        assert self.__storage.p_register == 0o77

    def test_njb_a_zero(self) -> None:
        self.load_test_program(Programs.NEGATIVE_JUMP_BACKWARD_ZERO_A)
        self.__run_loop.run()
        assert not self.__storage.err_status
        assert self.__storage.p_register == 0o103

    def test_njf_a_minus_zero(self) -> None:
        self.load_test_program(Programs.NEGATIVE_JUMP_FORWARD_MINUS_ZERO_A)
        self.__run_loop.run()
        assert not self.__storage.err_status
        assert self.__storage.p_register == 0o0104

    def test_njf_a_zero(self) -> None:
        self.load_test_program(Programs.NEGATIVE_JUMP_FORWARD_ZERO_A)
        self.__run_loop.run()
        assert not self.__storage.err_status
        assert self.__storage.p_register == 0o0102

    def test_nzf_a_minus_zero(self) -> None:
        self.load_test_program(Programs.NONZERO_JUMP_FORWARD_MINUS_ZERO_A)
        self.__run_loop.run()
        assert not self.__storage.err_status
        assert self.__storage.p_register == 0o104

    def test_nzf_a_zero(self) -> None:
        self.load_test_program(Programs.NONZERO_JUMP_FORWARD_ZERO_A)
        self.__run_loop.run()
        assert not self.__storage.err_status
        assert self.__storage.p_register == 0o103

    def test_pjb_a_minus_zero(self) -> None:
        self.load_test_program(Programs.POSITIVE_JUMP_BACKWARD_MINUS_ZERO_A)
        self.__run_loop.run()
        assert not self.__storage.err_status
        assert self.__storage.p_register == 0o77

    def test_pjb_a_zero(self) -> None:
        self.load_test_program(Programs.POSITIVE_JUMP_BACKWARD_ZERO_A)
        self.__run_loop.run()
        assert not self.__storage.err_status
        assert self.__storage.p_register == 0o77

    def test_pjf_a_minus_zero(self) -> None:
        self.load_test_program(Programs.POSITIVE_JUMP_FORWARD_MINUS_ZERO_A)
        self.__run_loop.run()
        assert not self.__storage.err_status
        assert self.__storage.p_register ==  0o103

    def test_pjf_a_zero(self) -> None:
        self.load_test_program(Programs.POSITIVE_JUMP_FORWARD_ZERO_A)
        self.__run_loop.run()
        assert not self.__storage.err_status
        assert self.__storage.p_register ==  0o104

    def test_sbb(self) -> None:
        self.load_test_program(Programs.SUBTRACT_BACKWARD)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o1234
        assert self.__storage.get_program_counter() == 0o103
        assert not self.__storage.err_status

    def test_sbc(self) -> None:
        self.load_test_program(Programs.SUBTRACT_CONSTANT)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o1234
        assert self.__storage.get_program_counter() == 0o104
        assert not self.__storage.err_status

    def test_sbd(self) -> None:
        self.load_test_program(Programs.SUBTRACT_DIRECT)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o1234
        assert self.__storage.get_program_counter() == 0o103
        assert not self.__storage.err_status

    def test_sbf(self) -> None:
        self.load_test_program(Programs.SUBTRACT_FORWARD)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o1234
        assert self.__storage.get_program_counter() == 0o103
        assert not self.__storage.err_status

    def test_shi(self) -> None:
        self.load_test_program(Programs.SUBTRACT_INDIRECT)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o1234
        assert self.__storage.get_program_counter() == 0o103
        assert not self.__storage.err_status

    def test_sbm(self) -> None:
        self.load_test_program(Programs.SUBTRACT_MEMORY)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o1234
        assert self.__storage.get_program_counter() == 0o104
        assert not self.__storage.err_status

    def test_sbn(self) -> None:
        self.load_test_program(Programs.SUBTRACT_NO_ADDRESS)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o1234
        assert self.__storage.get_program_counter() == 0o103
        assert not self.__storage.err_status

    def test_sbs(self) -> None:
        self.load_test_program(Programs.SUBTRACT_SPECIFIC)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o1234
        assert self.__storage.get_program_counter() == 0o103
        assert not self.__storage.err_status

    def test_stb(self) -> None:
        self.load_test_program(Programs.STORE_BACKWARD)
        assert self.__storage.read_absolute(3, 0o77) == 0o7777
        self.__run_loop.run()
        assert self.__storage.read_absolute(3, 0o77) == 0o1234

    def test_stc(self) -> None:
        self.load_test_program(Programs.STORE_CONSTANT)
        assert self.__storage.read_absolute(3, 0o103) == 0o7777
        self.__run_loop.run()
        assert self.__storage.read_absolute(3, 0o103) == 0o1234

    def test_std(self) -> None:
        self.load_test_program(Programs.STORE_DIRECT)
        assert self.__storage.read_absolute(2, 0o0040) == 0o7777
        self.__run_loop.run()
        assert not self.__storage.err_status
        assert self.__storage.read_absolute(2, 0o0040) == 0o1234

    def test_stf(self) -> None:
        self.load_test_program(Programs.STORE_FORWARD)
        assert self.__storage.read_absolute(3, 0o104) == 0o7777
        self.__run_loop.run()
        assert self.__storage.read_absolute(3, 0o104) == 0o1234

    def test_sti(self) -> None:
        self.load_test_program(Programs.STORE_INDIRECT)
        assert self.__storage.read_absolute(1, 0o0040) == 0o7777
        self.__run_loop.run()
        assert not self.__storage.err_status
        assert self.__storage.read_absolute(1, 0o0040) == 0o1234

    def test_stm(self) -> None:
        self.load_test_program(Programs.STORE_MEMORY)
        assert self.__storage.read_absolute(3, 0o1000) == 0o7777
        self.__run_loop.run()
        assert not self.__storage.err_status
        assert self.__storage.read_absolute(3, 0o1000) == 0o1234

    def test_sts(self) -> None:
        self.load_test_program(Programs.STORE_SPECIFIC)
        assert self.__storage.read_absolute(0, 0o7777) == 0o7777
        self.__run_loop.run()
        assert self.__storage.read_absolute(0, 0o7777) == 0o1234

    def test_zjb_a_minus_zero(self) -> None:
        self.load_test_program(Programs.ZERO_JUMP_BACKWARD_MINUS_ZERO_A)
        self.__run_loop.run()
        assert not self.__storage.err_status
        assert self.__storage.p_register == 0o103

    def test_zjb_a_zero(self) -> None:
        self.load_test_program(Programs.ZERO_JUMP_BACKWARD_ZERO_A)
        self.__run_loop.run()
        assert not self.__storage.err_status
        assert self.__storage.p_register == 0o77

    def test_zjf_a_minus_zero(self) -> None:
        self.load_test_program(Programs.ZERO_JUMP_FORWARD_MINUS_ZERO_A)
        self.__run_loop.run()
        assert not self.__storage.err_status
        assert self.__storage.p_register == 0o104

    def test_zjf_a_zero(self) -> None:
        self.load_test_program(Programs.ZERO_JUMP_FORWARD_ZERO_A)
        self.__run_loop.run()
        assert not self.__storage.err_status
        assert self.__storage.p_register == 0o104
