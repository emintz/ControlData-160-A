from cdc160a.BufferPump import BufferPump, PumpStatus
from cdc160a.Device import Device
from cdc160a.NullDevice import NullDevice
from typing import Final

class NullBufferPump(BufferPump):
    """
    A buffer pump that does nothing and never finishes.
    """
    __null_device: Final[Device] = NullDevice()

    def device(self) -> Device:
        return self.__null_device

    def pump(self, elapsed_cycles: int) -> PumpStatus:
        return PumpStatus.NO_DATA_MOVED
