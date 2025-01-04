"""
Tracks memory loaded, typically by the Assembler

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

from enum import Enum, unique
from typing import Optional

@unique
class MemoryBankStatus(Enum):
    EMPTY = 1,
    POPULATED = 2,

class MemoryUsedInBank:
    """
    Tracks the memory use within a single memory bank
    """
    def __init__(self):
        self.__first_word_address: Optional[int] = None
        self.__last_word_address_plus_one: Optional[int] = None
        self.__status: MemoryBankStatus = MemoryBankStatus.EMPTY

    def __str__(self):
        return "Empty" if self.is_empty() else (
            "fwa = {0:o}, lwa + 1 = {1:o}".format(
                self.__first_word_address,
                self.__last_word_address_plus_one))

    def is_empty(self) -> bool:
        """
        Memory use status: empty or populated

        :return: True if an only if nothing has been stored in the
                 tracked memory bank
        """
        return self.__status == MemoryBankStatus.EMPTY

    def mark_used(self, location: int) -> None:
        """
        Mark the specified location in the tracked memory bank
        as being in use

        :param location: memory location in [0o0000 .. 0o7777]
        :return:  None
        """
        assert 0o0000 <= location <= 0o7777
        match self.__status:
            case MemoryBankStatus.EMPTY:
                self.__first_word_address = location
                self.__last_word_address_plus_one = location + 1
                self.__status = MemoryBankStatus.POPULATED
            case MemoryBankStatus.POPULATED:
                if location < self.__first_word_address:
                    self.__first_word_address = location
                if self.__last_word_address_plus_one <= location:
                    self.__last_word_address_plus_one = location + 1

    def first_word_address(self) -> Optional[int]:
        """
        Return the first word address (FWA) used in the tracked memory bank

        :return: the first (i.e. lowest) memory address if the bank
                 contains values, None if the bank is empty
        """
        return self.__first_word_address

    def last_word_address_plus_one(self) -> Optional[int]:
        """
        Return the last word address used in the tracked memory bank
        plus one (LWA + 1)

        :return: the last (i.e. highest) memory address plus 1 if
                 the bank contains values, None if the bank is empty
        """
        return self.__last_word_address_plus_one

class MemoryUse:
    """
    Tracks the memory used by a program at load time. Note that the
    map might not reflect the working set size of a running program,
    as code can use memory that is not set at load time.

    This class specifies the memory to write to a bootable paper
    tape.
    """
    def __init__(self):
        self.__memory_map: [MemoryUsedInBank] = [
            MemoryUsedInBank(),
            MemoryUsedInBank(),
            MemoryUsedInBank(),
            MemoryUsedInBank(),
            MemoryUsedInBank(),
            MemoryUsedInBank(),
            MemoryUsedInBank(),
            MemoryUsedInBank(),
        ]

    def mark_used(self, bank: int, location: int) -> None:
        """
        Mark the specified location as used in the specified memory
        bank

        :param bank: the target memory bank in [0o0 .. 0o7]
        :param location: the location in the target memory bank in
                         [0o0000 .. 0o7777]
        :return: None
        """
        self.__memory_map[bank].mark_used(location)

    def memory_use(self, bank: int) -> MemoryUsedInBank:
        """
        Retrieve the memory use statistics for the specified
        memory bank

        :param bank: memory bank number in [0o0 .. 0o7]
        :return: the statistics, as specified above
        """
        return self.__memory_map[bank]
