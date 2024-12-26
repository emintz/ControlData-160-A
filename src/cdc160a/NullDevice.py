from cdc160a.Device import Device, IOChannelSupport

class NullDevice(Device):
    """
    Null (i.e. vacuous, do nothing) device that writes to the bit bucket
    and returns nonsense when read
    """

    def __init__(self):
        super().__init__(
            "Null Device",
            True,
            True,
            1,
            IOChannelSupport.NORMAL_AND_BUFFERED)
        pass

    def external_function(self, external_function_code) -> (bool, int | None):
        return True, 0

    def accepts(self, function_code: int) -> bool:
        return True

    def read(self) -> (bool, int):
        return True, 0

    def read_delay(self) -> int:
        return 1

    def write(self, value: int) -> bool:
        return True

    def write_delay(self) -> int:
        return 1
