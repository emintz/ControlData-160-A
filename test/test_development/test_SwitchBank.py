"""
Validates SwitchBank.py

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

from unittest import TestCase
from development.ConsoleSwitch import SwitchState
from development.SwitchBank import SwitchBank

class TestSwitchBank(TestCase):

    def setUp(self) -> None:
        self.__switch_bank = SwitchBank()

    def test_unset(self) -> None:
        assert not self.__switch_bank.any_down()
        assert self.__switch_bank.down_mask() == 0
        assert self.__switch_bank.mask() == 0
        assert self.__switch_bank.switch_state(0) == SwitchState.CENTER
        assert self.__switch_bank.switch_state_name(0) == "center"

    def test_0_up(self) -> None:
        self.__switch_bank.set_up(0)
        assert not self.__switch_bank.any_down()
        assert self.__switch_bank.down_mask() == 0
        assert self.__switch_bank.mask() == 1
        assert self.__switch_bank.switch_state(0) == SwitchState.UP
        assert self.__switch_bank.switch_state_name(0) == "up"

    def test_0_down(self) -> None:
        self.__switch_bank.set_down(0)
        assert self.__switch_bank.any_down()
        assert self.__switch_bank.down_mask() == 1
        assert self.__switch_bank.mask() == 1
        assert self.__switch_bank.switch_state(0) == SwitchState.DOWN
        assert self.__switch_bank.switch_state_name(0) == "down"

    def test_1_up(self) -> None:
        self.__switch_bank.set_up(1)
        assert not self.__switch_bank.any_down()
        assert self.__switch_bank.down_mask() == 0
        assert self.__switch_bank.mask() == 2

    def test_1_down(self) -> None:
        self.__switch_bank.set_down(1)
        assert self.__switch_bank.any_down()
        assert self.__switch_bank.down_mask() == 2
        assert self.__switch_bank.mask() == 2

    def test_2_up(self) -> None:
        self.__switch_bank.set_up(2)
        assert not self.__switch_bank.any_down()
        assert self.__switch_bank.down_mask() == 0
        assert self.__switch_bank.mask() == 4

    def test_2_down(self) -> None:
        self.__switch_bank.set_down(2)
        assert self.__switch_bank.any_down()
        assert self.__switch_bank.down_mask() == 4
        assert self.__switch_bank.mask() == 4

    def test_release_down_switches(self) -> None:
        self.set_0_up_2_down()
        self.__switch_bank.release_down_switches()
        assert self.__switch_bank.down_mask() == 0
        assert self.__switch_bank.mask() == 0o1

    def set_0_and_2_up(self) -> None:
        self.__switch_bank.set_up(0)
        self.__switch_bank.set_up(2)
        assert not self.__switch_bank.any_down()
        assert self.__switch_bank.down_mask() == 0
        assert self.__switch_bank.mask() == 5

    def set_0_up_2_down(self) -> None:
        self.__switch_bank.set_up(0)
        self.__switch_bank.set_down(2)
        assert self.__switch_bank.any_down()
        assert self.__switch_bank.down_mask() == 4
        assert self.__switch_bank.mask() == 5

    def set_0_and_2_down(self) -> None:
        self.__switch_bank.set_down(0)
        self.__switch_bank.set_down(2)
        assert self.__switch_bank.any_down()
        assert self.__switch_bank.down_mask() == 5
        assert self.__switch_bank.mask() == 5
