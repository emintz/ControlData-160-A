"""
Emulated paper tape reader

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

from cdc160a.Device import Device, ExternalFunctionAction, IOChannelSupport
from typing import Optional
import re

class PaperTapeReader(Device):
    """
    Emulates the CDC 350 Paper Tape Reader, which can read 5, 7, and 8 level
    paper tape at 350 characters per second, which makes the read delay
    approximately 446 6.4 microsecond cycles.

    Paper tape read is restricted to the normal I/O channel. The reader
    cannot buffer.

    The reader emulator takes input from text files having a single octal
    input value per line. Input values are constrained input format:

    Level       Values
    -----       ------------
        5       0 .. 2^5 - 1, i.e. [0 .. 0o37]
        7       0 .. 2^7 - 1, i.e. [0 .. 0o177]
        8       0 .. 2^8 - 1, i.e. [0 .. 0o377]

    The file format does not distinguish between physical tape formats.
    The reader reads, validates, converts, and returns the values in the
    file.

    It is recommended that paper tape data files have the extension ptape,
    papertape, paper-tape, or something similar to distinguish them from
    other text files.
    """

    __octal_pattern = re.compile("^[0-7]+$")

    def __init__(self):
        super().__init__("Paper Tape Reader", "pt_rdr", True, False, IOChannelSupport.NORMAL_ONLY)
        self.__input_file = None
        self.__input_path_name = None

    def accepts(self, function_code: int) -> bool:
        return function_code == 0o4102

    def close(self) -> bool:
        result = False
        if self.__input_file is None:
            print("Cannot close paper tape input because no file is open.")
        else:
            self.__input_file.close()
            self.__input_file = None
            self.__input_path_name = None
        return result

    def external_function(self, external_function_code: int) -> (
            (bool, Optional[int])):
        return (
            self.__input_file is not None and external_function_code == 0o4102,
            None)

    def file_name(self) -> Optional[str]:
        return self.__input_path_name

    def is_open(self) -> bool:
        return self.__input_file is not None

    def open(self, path_name: str) -> bool:
        result = False
        if self.__input_file is not None:
            print(
                "Cannot open {0} for paper tape input because "
                "{1}} is already open".format(
                    path_name,
                    self.__input_path_name))
        else:
            try:
                self.__input_file = open(path_name, 'r')
                self.__input_path_name = path_name
                result = True
            except FileNotFoundError:
                print("File {0} does not exist.".format(path_name))
        return result

    def read(self) -> (bool, int):
        read_data = 0
        status = self.__input_file is not None
        raw_input = self.__input_file.readline()
        if status:
            if re.match("^[0-7]+$", raw_input) is not None:
                read_data = int(raw_input, 8)
            else:
                print("Illegal input: '{0}', using 0.".format(raw_input.strip()))
        return status, read_data

    def read_delay(self) -> int:
        return 446
