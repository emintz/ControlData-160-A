from cdc160a.BufferPump import BufferPump, PumpStatus
from cdc160a.Device import Device
from cdc160a.Storage import Storage

class BufferedOutputPump(BufferPump):
    """
    Buffers data from the emulator's buffer storage bank to an
    output device.
    """

    def __init__(self, device: Device, storage: Storage):
        self.__device = device
        self.__storage = storage
        self.__cycles_remaining = self.__device.initial_write_delay()

    def device(self) -> Device:
        return self.__device

    def pump(self, elapsed_cycles: int) -> PumpStatus:
        buffer_status = PumpStatus.NO_DATA_MOVED
        self.__cycles_remaining -= elapsed_cycles
        if self.__cycles_remaining <= 0:
            self.__cycles_remaining = self.__device.write_delay()
            data_remains = self.__storage.memory_to_buffer_data()
            write_status = self.__device.write(
                self.__storage.buffer_data_register)
            if write_status:
                buffer_status = PumpStatus.ONE_WORD_MOVED if data_remains \
                    else PumpStatus.COMPLETED
            else:
                buffer_status = PumpStatus.FAILURE
                # TODO(emintz): what should happen here?

        return buffer_status

    def cycles_remaining(self) -> int:
        return self.__cycles_remaining
