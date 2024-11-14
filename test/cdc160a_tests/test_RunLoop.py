from unittest import TestCase
from cdc160a.RunLoop import RunLoop
from cdc160a.Storage import  Storage
from test_support.Assembler import Assembler
from test_support import Programs

class TestRunLoop(TestCase):

    def setUp(self) -> None:
        self.__storage = Storage()
        self.__run_loop = RunLoop(self.__storage)
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
