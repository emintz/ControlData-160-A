"""
Validates EffectiveAddress.py

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
from unittest import TestCase
from cdc160a.Storage import MCS_MODE_BFR
from cdc160a.Storage import MCS_MODE_DIR
from cdc160a.Storage import MCS_MODE_IND
from cdc160a.Storage import MCS_MODE_REL
from cdc160a.Storage import Storage
from typing import Final
from cdc160a import EffectiveAddress

READ_AND_WRITE_ADDRESS: Final[int] = 0o1234
INSTRUCTION_ADDRESS: Final[int] = 0o1232
G_ADDRESS: Final[int] = INSTRUCTION_ADDRESS + 1


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
        self.storage.run()

    def tearDown(self) -> None:
        self.storage = None

    def test_constant(self) -> None:
        # LDC 1234 -- 2 words
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o2200)
        self.storage.write_relative_bank(G_ADDRESS, 0o1234)
        self.storage.unpack_instruction()
        EffectiveAddress.constant(self.storage)
        assert self.storage.s_register == G_ADDRESS
        assert self.storage.storage_cycle == MCS_MODE_REL

    def test_direct(self):
        # LDD 12
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o2012)
        self.storage.unpack_instruction()
        EffectiveAddress.direct(self.storage)
        assert self.storage.s_register == 0o12
        assert self.storage.storage_cycle == MCS_MODE_DIR

    def test_forward_indirect(self):
        # JFI 44
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o7144)
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS + 0o44, 0o137)
        self.storage.unpack_instruction()
        EffectiveAddress.forward_indirect(self.storage)
        assert self.storage.s_register == 0o137
        assert self.storage.storage_cycle == MCS_MODE_REL

    def test_indirect(self):
        # LDI 21
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o2121)
        self.storage.unpack_instruction()
        EffectiveAddress.direct(self.storage)
        assert self.storage.s_register == 0o21
        assert self.storage.storage_cycle == MCS_MODE_DIR

    def test_memory(self):
        # LDM 4321, two words. E == 00
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o2100)
        self.storage.write_relative_bank(G_ADDRESS, 0o5555)
        self.storage.unpack_instruction()
        EffectiveAddress.memory(self.storage)
        assert self.storage.s_register == 0o5555
        assert self.storage.storage_cycle == MCS_MODE_REL

    def test_no_address(self):
        # LDN 55
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0455)
        self.storage.unpack_instruction()
        EffectiveAddress.no_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS
        assert self.storage.storage_cycle == MCS_MODE_REL

    def test_relative_backward(self):
        # LDB 10
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o2310)
        self.storage.unpack_instruction()
        EffectiveAddress.relative_backward(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS - 0o10
        assert self.storage.storage_cycle == MCS_MODE_REL

    def test_relative_forward(self):
        # LDF 10
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o2210)
        self.storage.unpack_instruction()
        EffectiveAddress.relative_forward(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 0o10
        assert self.storage.storage_cycle == MCS_MODE_REL

    def test_specific(self):
        # LDS
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o2300)
        self.storage.unpack_instruction()
        EffectiveAddress.specific(self.storage)
        assert self.storage.s_register == 0o7777
        assert self.storage.storage_cycle == MCS_MODE_REL

    def test_via_direct_at_e(self) -> None:
        # NWI
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o7615)
        self.storage.unpack_instruction()
        self.storage.write_direct_bank(0o15, 0o2400)
        EffectiveAddress.via_direct_at_e(self.storage)
        assert self.storage.s_register == 0o2400

    def test_vacuous(self) -> None:
        # ITA
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o7600)
        self.storage.unpack_instruction()
        self.storage.s_register = 0o7654
        EffectiveAddress.vacuous(self.storage)
        assert self.storage.s_register == 0o7654

if __name__ == "__main__":
    unittest.main()
