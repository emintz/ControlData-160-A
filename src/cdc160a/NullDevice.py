from typing import Optional

from cdc160a.Device import Device, IOChannelSupport

class NullDevice(Device):
    """
    Null (i.e. vacuous, do nothing) device that writes to the bit bucket
    and returns nonsense when read
    """

    def __init__(self):
        super().__init__(
            "Null Device",
            "nul",
            True,
            True,
            IOChannelSupport.NORMAL_AND_BUFFERED)
        self.__file_name = None

    def accepts(self, function_code: int) -> bool:
        return function_code == 0o7777

    def close(self) -> None:
        self.__file_name = None

    def external_function(self, external_function_code) -> (bool, Optional[int]):
        return external_function_code == 0o7777, 0

    def file_name(self) -> Optional[str]:
        return self.__file_name

    def initial_read_delay(self) -> int:
        return self.read_delay()

    def initial_write_delay(self) -> int:
        return self.write_delay()

    def is_open(self) -> bool:
        return self.__file_name is not None

    def open(self, file_name: str) -> bool:
        self.__file_name = file_name
        return self.__file_name is not None

    def read(self) -> (bool, int):
        return True, 0

    def read_delay(self) -> int:
        return 1

    def write(self, value: int) -> bool:
        return True

    def write_delay(self) -> int:
        return 1
