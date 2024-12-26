from cdc160a.BufferPump import BufferPump, PumpStatus
from cdc160a.Device import Device
from cdc160a.Storage import Storage

class BufferedInputPump(BufferPump):

    def __init__(self, device: Device, storage: Storage):
        self.__device = device
        self.__storage = storage
        self.__cycles_remaining = self.__device.initial_read_delay()

    def device(self) -> Device:
        return self.__device

    def pump(self, elapsed_cycles: int) -> PumpStatus:
        self.__cycles_remaining -= elapsed_cycles
        buffer_status = PumpStatus.NO_DATA_MOVED
        if self.__cycles_remaining <= 0:
            self.__cycles_remaining = self.__device.read_delay()
            read_status, datum = self.__device.read()
            if read_status:
                self.__storage.buffer_data_register = datum
                buffer_status = (
                    PumpStatus.ONE_WORD_MOVED) if (
                    self.__storage.buffer_data_to_memory()) else \
                    PumpStatus.COMPLETED
            else:
                buffer_status = PumpStatus.FAILURE
        return buffer_status

    def cycles_remaining(self) -> int:
        return self.__cycles_remaining
