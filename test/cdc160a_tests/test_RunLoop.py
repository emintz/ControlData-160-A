import unittest
from unittest import TestCase

from cdc160a.InputOutput import InputOutput
from cdc160a.RunLoop import RunLoop
from cdc160a.Storage import  Storage
from test_support.Assembler import assembler_from_string
from test_support.PyunitConsole import PyConsole
from test_support import Programs

class TestRunLoop(TestCase):

    def setUp(self) -> None:
        self.__storage = Storage()
        self.__console = PyConsole()
        self.__run_loop = RunLoop(
            self.__console, self.__storage, InputOutput([]))
        self.__storage.set_direct_storage_bank(0o2)
        self.__storage.set_indirect_storage_bank(0o1)
        self.__storage.set_relative_storage_bank(0o3)
        self.__storage.set_program_counter(0o0100)
        self.__storage.run()

    def tearDown(self) -> None:
        self.__storage = None

    def load_test_program(self, source: str) -> None:
        assembler_from_string(source, self.__storage).run()

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

    def test_acj(self) -> None:
        self.load_test_program(
            Programs.SET_DIRECT_INDIRECT_AND_RELATIVE_BANK_CONTROL_AND_JUMP)
        self.__run_loop.run()
        assert self.__storage.direct_storage_bank == 0o06
        assert self.__storage.indirect_storage_bank == 0o06
        assert self.__storage.relative_storage_bank == 0o06
        assert self.__storage.get_program_counter() == 0o200

    def test_adb(self) -> None:
        self.load_test_program(Programs.ADD_BACKWARD)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o1234
        assert self.__storage.p_register == 0o103
        assert not self.__storage.err_status

    def test_adc(self) -> None:
        self.load_test_program(Programs.ADD_CONSTANT)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o1234
        assert self.__storage.p_register == 0o104
        assert not self.__storage.err_status

    def test_add(self) -> None:
        self.load_test_program(Programs.ADD_DIRECT)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o1234
        assert self.__storage.p_register == 0o103
        assert not self.__storage.err_status

    def test_adf(self) -> None:
        self.load_test_program(Programs.ADD_FORWARD)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o1234
        assert self.__storage.p_register == 0o103
        assert not self.__storage.err_status

    def test_adi(self) -> None:
        self.load_test_program(Programs.ADD_INDIRECT)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o1234
        assert self.__storage.p_register == 0o103
        assert not self.__storage.err_status

    def test_adm(self) -> None:
        self.load_test_program(Programs.ADD_MEMORY)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o1234
        assert self.__storage.p_register == 0o104
        assert not self.__storage.err_status

    def test_adn(self) -> None:
        self.load_test_program(Programs.ADD_NO_ADDRESS)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o1234
        assert self.__storage.p_register == 0o103
        assert not self.__storage.err_status

    def test_ads(self) -> None:
        self.load_test_program(Programs.ADD_SPECIFIC)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o1234
        assert self.__storage.p_register == 0o103
        assert not self.__storage.err_status

    def test_aob(self) -> None:
        self.load_test_program(Programs.REPLACE_ADD_ONE_BACKWARD)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o1234
        assert self.__storage.read_relative_bank(0o77) == 0o1234
        assert not self.__storage.err_status

    def test_aoc(self) -> None:
        self.load_test_program(Programs.REPLACE_ADD_ONE_CONSTANT)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o1234
        assert self.__storage.read_relative_bank(0o101) == 0o1234
        assert not self.__storage.err_status

    def test_aod(self) -> None:
        self.load_test_program(Programs.REPLACE_ADD_ONE_DIRECT)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o1234
        assert self.__storage.p_register == 0o101
        assert self.__storage.read_direct_bank(0o40) == 0o1234

    def test_aof(self) -> None:
        self.load_test_program(Programs.REPLACE_ADD_ONE_FORWARD)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o1234
        assert self.__storage.read_relative_bank(0o102) == 0o1234

    def test_aoi(self) -> None:
        self.load_test_program(Programs.REPLACE_ADD_ONE_INDIRECT)
        self.__run_loop.run()
        assert self.__storage.read_indirect_bank(0o40) == 0o1234
        assert self.__storage.a_register == 0o1234
        assert not self.__storage.err_status

    def test_aom(self) -> None:
        self.load_test_program(Programs.REPLACE_ADD_ONE_MEMORY)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o1234
        assert self.__storage.read_relative_bank(0o200) == 0o1234
        assert not self.__storage.err_status

    def test_aos(self) -> None:
        self.load_test_program(Programs.REPLACE_ADD_ONE_SPECIFIC)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o1234
        assert self.__storage.read_specific() == 0o1234
        assert not self.__storage.err_status

    def test_ats(self) -> None:
        self.load_test_program(Programs.A_TO_BUFFER_ENTRANCE)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o3000
        assert self.__storage.buffer_entrance_register == 0o3000
        assert not self.__storage.buffering
        assert self.__storage.get_program_counter() == 0o104

    def test_atx(self) -> None:
        self.load_test_program(Programs.A_TO_BUFFER_EXIT)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o3000
        assert self.__storage.buffer_exit_register == 0o3000
        assert not self.__storage.buffering
        assert self.__storage.get_program_counter() == 0o104

    def test_bls(self) -> None:
        self.load_test_program(Programs.BLOCK_STORE)
        self.__run_loop.run()
        assert self.__storage.buffer_entrance_register == 0o4001
        assert self.__storage.buffer_exit_register == 0o4001
        assert self.__storage.a_register == 0o6000
        for loc in range(0o0000, 0o1000):
            assert self.__storage.read_buffer_bank(loc) == 0o0000
        for loc in range(0o1000, 0o4001):
            value = self.__storage.read_buffer_bank(loc)
            if value != 0o6000:
                print("At {0} ({1:o} octal), value is {2} ({3:o} octal).".format(
                    loc, loc, value, value))
            assert self.__storage.read_buffer_bank(loc) == 0o6000
        for loc in range(0o4001, 0o10000):
            assert self.__storage.read_buffer_bank(loc) == 0o0000
        assert self.__storage.get_program_counter() == 0o114
        assert not self.__storage.buffering

    def test_cta(self) -> None:
        self.load_test_program(Programs.BANK_CONTROLS_TO_A)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o1234
        assert not self.__storage.err_status
        assert self.__storage.relative_storage_bank == 0o04
        assert self.__storage.get_program_counter() == 0o201

    def test_drj(self) -> None:
        self.load_test_program(
            Programs.SET_DIRECT_AND_RELATIVE_BANK_CONTROL_AND_JUMP)
        self.__run_loop.run()
        assert self.__storage.direct_storage_bank == 0o06
        assert self.__storage.relative_storage_bank == 0o06
        assert self.__storage.get_program_counter() == 0o200

    def test_err(self) -> None:
        self.load_test_program(Programs.ERROR_HALT)
        self.__run_loop.run()
        assert self.__storage.err_status

    def test_eta(self) -> None:
        self.load_test_program(
            Programs.BUFFER_ENTRANCE_TO_A)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o3000
        assert self.__storage.buffer_entrance_register == 0o3000
        assert self.__storage.get_program_counter() == 0o106
        assert not self.__storage.buffering

    def test_hwi(self) -> None:
        self.load_test_program(Programs.HALF_WRITE_INDIRECT)
        self.__run_loop.run()
        assert self.__storage.read_indirect_bank(0o2100) == 0o4321

    def test_irj(self) -> None:
        self.load_test_program(Programs.SET_INDIRECT_AND_RELATIVE_BANK_CONTROL_AND_JUMP)
        self.__run_loop.run()
        assert self.__storage.indirect_storage_bank == 0o06
        assert self.__storage.relative_storage_bank == 0o06
        assert self.__storage.get_program_counter() == 0o200

    def test_jfi(self) -> None:
        self.load_test_program(Programs.JUMP_FORWARD_INDIRECT)
        self.__run_loop.run()
        assert self.__storage.get_program_counter() == 0o200

    def test_jpi(self) -> None:
        self.load_test_program(Programs.JUMP_INDIRECT)
        self.__run_loop.run()
        assert not self.__storage.err_status
        assert self.__storage.get_program_counter() == 0o200

    def test_jpr(self) -> None:
        self.load_test_program(Programs.RETURN_JUMP)
        self.__run_loop.run()
        assert self.__storage.get_program_counter() == 0o201
        assert self.__storage.read_relative_bank(0o200) == 0o102
        assert not self.__storage.err_status

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

    def test_muh(self) -> None:
        self.load_test_program(Programs.MULTIPLY_BY_100)
        self.__run_loop.run()
        assert self.__storage.a_register == 100
        assert not self.__storage.err_status

    def test_mut(self) -> None:
        self.load_test_program(Programs.MULTIPLY_BY_10)
        self.__run_loop.run()
        assert self.__storage.a_register == 10
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

    def test_pta(self) -> None:
        self.load_test_program(Programs.P_TO_A)
        self.__run_loop.run()
        assert not self.__storage.err_status
        assert self.__storage.a_register == 0o100
        assert self.__storage.p_register == 0o101

    def test_pjf_a_zero(self) -> None:
        self.load_test_program(Programs.POSITIVE_JUMP_FORWARD_ZERO_A)
        self.__run_loop.run()
        assert not self.__storage.err_status
        assert self.__storage.p_register ==  0o104

    def test_rab(self) -> None:
        self.load_test_program(Programs.REPLACE_ADD_BACKWARD)
        self.__run_loop.run()
        assert not self.__storage.err_status
        assert self.__storage.a_register == 0o1234
        assert self.__storage.read_absolute(0o3, 0o77) == 0o1234

    def test_rac(self) -> None:
        self.load_test_program(Programs.REPLACE_ADD_CONSTANT)
        self.__run_loop.run()
        assert not self.__storage.err_status
        assert self.__storage.a_register == 0o1234
        assert self.__storage.read_absolute(0o3, 0o103) == 0o1234

    def test_rad(self) -> None:
        self.load_test_program(Programs.REPLACE_ADD_DIRECT)
        self.__run_loop.run()
        assert not self.__storage.err_status
        assert self.__storage.a_register == 0o1234
        assert self.__storage.read_absolute(0o2, 0o20) == 0o1234

    def test_raf(self) -> None:
        self.load_test_program(Programs.REPLACE_ADD_FORWARD)
        self.__run_loop.run()
        assert not self.__storage.err_status
        assert self.__storage.a_register == 0o1234
        assert self.__storage.read_absolute(0o3, 0o104) == 0o1234

    def test_rai(self) -> None:
        self.load_test_program(Programs.REPLACE_ADD_INDIRECT)
        self.__run_loop.run()
        assert not self.__storage.err_status
        assert self.__storage.a_register == 0o1234
        assert self.__storage.read_absolute(0o1, 0o14) == 0o1234

    def test_ram(self) -> None:
        self.load_test_program(Programs.REPLACE_ADD_MEMORY)
        self.__run_loop.run()
        assert not self.__storage.err_status
        assert self.__storage.a_register == 0o1234
        assert self.__storage.read_absolute(0o3, 0o200)

    def test_ras(self) -> None:
        self.load_test_program(Programs.REPLACE_ADD_SPECIFIC)
        self.__run_loop.run()
        assert not self.__storage.err_status
        assert self.__storage.a_register == 0o1234
        assert self.__storage.read_absolute(0, 0o7777) == 0o1234

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

    def test_sbu(self) -> None:
        self.load_test_program(Programs.SET_BUFFER_STORAGE_BANK)
        self.__run_loop.run()
        assert self.__storage.buffer_storage_bank == 0o06
        assert self.__storage.get_program_counter() == 0o101

    def test_scb(self) -> None:
        self.load_test_program(Programs.SELECTIVE_COMPLEMENT_BACKWARD)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o06

    def test_scc(self) -> None:
        self.load_test_program(Programs.SELECTIVE_COMPLEMENT_MEMORY)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o06

    def test_scd(self) -> None:
        self.load_test_program(Programs.SELECTIVE_COMPLEMENT_DIRECT)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o06

    def test_sci(self) -> None:
        self.load_test_program(Programs.SELECTIVE_COMPLEMENT_INDIRECT)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o06

    def test_scm(self) -> None:
        self.load_test_program(Programs.SELECTIVE_COMPLEMENT_MEMORY)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o06

    def test_scn(self) -> None:
        self.load_test_program(Programs.SELECTIVE_COMPLEMENT_NO_ADDRESS)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o06

    def test_sid(self) -> None:
        self.load_test_program(Programs.SET_INDIRECT_AND_DIRECT_BANK_CONTROL)
        self.__run_loop.run()
        assert self.__storage.direct_storage_bank == 0o06
        assert self.__storage.indirect_storage_bank == 0o06
        assert self.__storage.get_program_counter() == 0o101

    def test_scs(self) -> None:
        self.load_test_program(Programs.SELECTIVE_COMPLEMENT_SPECIFIC)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o06

    def test_sdc(self) -> None:
        self.load_test_program(Programs.SET_DIRECT_BANK_CONTROL)
        self.__run_loop.run()
        assert self.__storage.direct_storage_bank == 0o06
        assert self.__storage.relative_storage_bank == 0o03
        assert self.__storage.s_register == 0o101

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

    def test_sic(self) -> None:
        self.load_test_program(Programs.SET_INDIRECT_BANK_CONTROL)
        self.__run_loop.run()
        assert self.__storage.indirect_storage_bank == 0o06
        assert self.__storage.get_program_counter() == 0o101

    def test_sjs_stop_and_branch(self) -> None:
        self.__storage.set_jump_switch_mask(0o6)
        self.__storage.set_stop_switch_mask(0o6)
        self.load_test_program(Programs.SELECTIVE_STOP_AND_JUMP)
        self.__run_loop.run()
        assert self.__storage.get_program_counter() == 0o100
        # Note: cannot restart loop after a halt instruction
        # because, when running a test, it run loop would restart
        # from the SLS address and simply rerun the instruction.
        # The best we can do is  check the next address.
        assert self.__storage.get_next_execution_address() == 0o200

    def test_sjs_stop_and_no_branch(self) -> None:
        self.__storage.set_jump_switch_mask(0o2)
        self.__storage.set_stop_switch_mask(0o6)
        self.load_test_program(Programs.SELECTIVE_STOP_AND_JUMP)
        self.__run_loop.run()
        assert self.__storage.get_program_counter() == 0o100
        # Note: cannot restart loop after a halt instruction
        # because, when running a test, it run loop would restart
        # from the SLS address and simply rerun the instruction.
        # The best we can do is  check the next address.
        assert self.__storage.get_next_execution_address() == 0o102

    def test_sjs_no_stop_and_branch(self) -> None:
        self.__storage.set_jump_switch_mask(0o6)
        self.__storage.set_stop_switch_mask(0o5)
        self.load_test_program(Programs.SELECTIVE_STOP_AND_JUMP)
        self.__run_loop.run()
        assert self.__storage.get_program_counter() == 0o200

    def test_sjs_no_stop_and_no_branch(self) -> None:
        self.__storage.set_jump_switch_mask(0o2)
        self.__storage.set_stop_switch_mask(0o5)
        self.load_test_program(Programs.SELECTIVE_STOP_AND_JUMP)
        self.__run_loop.run()
        assert self.__storage.get_program_counter() == 0o102

    def test_slj_branch(self) -> None:
        self.__storage.set_jump_switch_mask(0o6)
        self.load_test_program(Programs.SELECTIVE_JUMP)
        self.__run_loop.run()
        assert self.__storage.get_program_counter() == 0o200
        assert not self.__storage.err_status

    def test_slj_no_branch(self) -> None:
        self.__storage.set_jump_switch_mask(0o5)
        self.load_test_program(Programs.SELECTIVE_JUMP)
        self.__run_loop.run()
        assert self.__storage.get_program_counter() == 0o102
        assert not self.__storage.err_status

    def test_sls_no_stop(self) -> None:
        self.__storage.set_stop_switch_mask(0o05)
        self.load_test_program(Programs.SELECTIVE_STOP)
        self.__run_loop.run()
        assert self.__storage.get_program_counter() == 0o101
        assert not self.__storage.run_stop_status

    def test_sls_stop(self) -> None:
        self.__storage.set_stop_switch_mask(0o06)
        self.load_test_program(Programs.SELECTIVE_STOP)
        self.__run_loop.run()
        assert self.__storage.get_program_counter() == 0o100
        assert not self.__storage.run_stop_status

    def test_srb(self) -> None:
        self.load_test_program(Programs.SHIFT_REPLACE_BACKWARD)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o0003
        assert self.__storage.read_relative_bank(0o76) == 0o0003
        assert self.__storage.get_program_counter() == 0o101
        assert not self.__storage.err_status

    def test_src(self) -> None:
        self.load_test_program(Programs.SHIFT_REPLACE_CONSTANT)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o0003
        assert self.__storage.read_relative_bank(0o0101) == 0o0003
        assert self.__storage.get_program_counter() == 0o102
        assert not self.__storage.err_status

    def test_srd(self) -> None:
        self.load_test_program(Programs.SHIFT_REPLACE_DIRECT)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o0003
        assert self.__storage.read_direct_bank(0o14) == 0o0003
        assert self.__storage.get_program_counter() == 0o101
        assert not self.__storage.err_status

    def test_srf(self) -> None:
        self.load_test_program(Programs.SHIFT_REPLACE_FORWARD)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o0003
        assert self.__storage.read_relative_bank(0o102) == 0o0003
        assert self.__storage.get_program_counter() == 0o101
        assert not self.__storage.err_status

    def test_sri(self) -> None:
        self.load_test_program(Programs.SHIFT_REPLACE_INDIRECT)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o0003
        assert self.__storage.read_indirect_bank(0o24) == 0o0003
        assert self.__storage.get_program_counter() == 0o101
        assert not self.__storage.err_status

    def test_srj(self) -> None:
        self.load_test_program(Programs.SET_RELATIVE_BANK_CONTROL_AND_JUMP)
        self.__run_loop.run()
        assert self.__storage.relative_storage_bank == 0o06
        assert self.__storage.get_program_counter() == 0o200

    def test_srm(self) -> None:
        self.load_test_program(Programs.SHIFT_REPLACE_MEMORY)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o0003
        assert self.__storage.read_relative_bank(0o200) == 0o0003
        assert self.__storage.get_program_counter() == 0o102
        assert not self.__storage.err_status

    def test_srs(self) -> None:
        self.load_test_program(Programs.SHIFT_REPLACE_SPECIFIC)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o0003
        assert self.__storage.read_specific() == 0o0003
        assert self.__storage.get_program_counter() == 0o101
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

    def test_ste(self) -> None:
        self.load_test_program(
            Programs.STORE_BUFFER_ENTRANCE_DIRECT_AND_A_TO_BUFFER_ENTRANCE)
        self.__run_loop.run()
        assert self.__storage.read_direct_bank(0o67) == 0o5000
        assert self.__storage.buffer_entrance_register == 0o3000
        assert self.__storage.get_program_counter() == 0o107

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

    def test_stp(self) -> None:
        self.load_test_program(Programs.STORE_P_REGISTER)
        self.__run_loop.run()
        assert not self.__storage.err_status
        assert self.__storage.read_direct_bank(0o56) == 0o100

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

    def test_call_and_return(self) -> None:
        self.load_test_program(Programs.CALL_AND_RETURN)
        self.__run_loop.run()
        assert self.__storage.read_relative_bank(0o200) == 0o102
        assert self.__storage.get_program_counter() == 0o102

if __name__ == "__main__":
    unittest.main()
