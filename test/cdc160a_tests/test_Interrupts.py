"""
Validates Interrupts.py

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

import unittest

from cdc160a.InputOutput import InputOutput
from cdc160a.Storage import InterruptLock
from cdc160a.RunLoop import RunLoop
from cdc160a.Storage import Storage
from development.Assembler import assembler_from_string
from test_support.PyunitConsole import PyConsole
from test_support import Programs

class TestInterrupts(unittest.TestCase):
    def setUp(self) -> None:
        self.__console = PyConsole()
        self.__storage = Storage()
        self.__run_loop = RunLoop(self.__console, self.__storage, InputOutput([]))
        self.__storage.set_buffer_storage_bank(0o0)
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

    def test_interrupt_10_simplest_scenario(self) -> None:
        self.program_to_storage(Programs.INTERRUPT_10_SIMPLE)
        self.__run_loop.single_step()
        self.__storage.request_interrupt(0o10)
        self.__run_loop.run()
        assert self.__storage.a_register == 0o01
        assert self.__storage.interrupt_lock == InterruptLock.FREE
        assert self.__storage.get_program_counter() == 0o101

if __name__ == '__main__':
    unittest.main()
