"""
Stopgap CDC 160-A emulation used for development.

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

from cdc160a.InputOutput import InputOutput
from cdc160a.PaperTapePunch import PaperTapePunch
from cdc160a.PaperTapeReader import PaperTapeReader
from cdc160a.RunLoop import RunLoop
from cdc160a.Storage import Storage
from development.Console import create_console

def main() -> None:
    """
    Creates and runs a CDC 160-A emulator that uses the
    development, command line-driven console.

    :return: None
    """
    console = create_console()
    storage = Storage()
    run_loop = RunLoop(console, storage, InputOutput([
        PaperTapePunch(),
        PaperTapeReader(),]))
    run_loop.run()


if __name__ == "__main__":
    main()
