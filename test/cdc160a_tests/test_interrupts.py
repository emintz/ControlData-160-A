import unittest

from cdc160a.RunLoop import RunLoop
from cdc160a.Storage import InterruptLock
from cdc160a.Storage import Storage
from test_support.Assembler import assembler_from_string
from test_support.PyunitConsole import PyConsole
from test_support import Programs

class TestInterrupts(unittest.TestCase):
    def setUp(self) -> None:
        self.__console = PyConsole()
        self.__storage = Storage()
        self.__run_loop = RunLoop(self.__console, self.__storage)
        self.__storage.set_direct_storage_bank(0o2)
        self.__storage.set_indirect_storage_bank(0o1)
        self.__storage.set_relative_storage_bank(0o3)
        self.__storage.set_program_counter(0o0100)
        self.__storage.run()

    def program_to_storage(self, source: str) -> None:
        assembler_from_string(source, self.__storage).run()

    def test_clear_interrupt(self) -> None:
        self.program_to_storage(Programs.CLEAR_INTERRUPT_LOCKOUT)
        self.__storage.interrupt_lock = InterruptLock.LOCKED
        assert self.__storage.run_stop_status
        assert self.__storage.interrupt_lock == InterruptLock.LOCKED
        self.__run_loop.single_step()
        assert self.__storage.interrupt_lock == InterruptLock.UNLOCK_PENDING
        assert self.__storage.run_stop_status
        self.__run_loop.single_step()
        assert self.__storage.interrupt_lock == InterruptLock.FREE
        assert self.__storage.run_stop_status
        self.__run_loop.single_step()
        assert self.__storage.interrupt_lock == InterruptLock.FREE
        assert not self.__storage.run_stop_status

if __name__ == '__main__':
    unittest.main()
