from operator import ifloordiv

from cdc160a import Device

class InputOutput:
    def __init__(self, devices: [Device]):
        """
        Constructor

        :param devices: a list of I/O devices attached to this
                        160-A
        """
        self.__devices = devices
        self.__device_on_buffer_channel = None
        self.__device_on_normal_channel = None

    def clear(self) -> None:
        """
        Stop normal and buffered I/O and clear all selected devices
        :return: None
        """
        self.__device_on_buffer_channel = None
        self.__device_on_normal_channel = None

    def device_on_buffer_channel(self) -> Device:
        return self.__device_on_buffer_channel

    def device_on_normal_channel(self) -> Device:
        return self.__device_on_normal_channel

    def external_function(self, operand: int) -> (int | None, bool):
        """
        Perform an external function, select or query a device.

        :param operand:
        :return: a tuple whose first member is the device response, an
                 integer if the device response or None if it does not,
                 the second a boolean that is True if the request was
                 legal and False if it was illegal. Illegal requests can
                 be a request that an attached device cannot perform (e.g.
                 selecting a powered down device) or a device that does not
                 exist.
        """
        status = False
        response = None
        self.__device_on_normal_channel = None  # Deselect any active device.

        device = None
        for current_device in self.__devices:
            if current_device.accepts(operand):
                device = current_device
                break

        if device is not None:
            status, response = device.external_function(operand)
            if status:
                self.__device_on_normal_channel = device

        return response, status

    def read_delay(self) -> int:
        """
        :return: the selected normal I/O device's read delay or
                 0 if no device selected for normal I.O
        """
        return self.__device_on_normal_channel.read_delay() \
            if self.__device_on_normal_channel is not None \
            else 0

    def read_normal(self) -> (bool, int):
        """
        If a device has been selected on the normal channel, read one
        word; otherwise fail.

        :return: read status, True if successful and False otherwise,
                 and the value read. The value will be 0 on failure.
        """
        status = False
        data = 0
        if self.__device_on_normal_channel is not None:
            status, data = self.__device_on_normal_channel.read()
        return status, data

    def write_delay(self) -> int:
        """
        :return: the selected normal I/O device's read delay or
                 0 if no device selected for normal I.O
        """
        return self.__device_on_normal_channel.write_delay() \
            if self.__device_on_normal_channel is not None \
            else 0

    def write_normal(self, value: int) -> bool:
        """
        Write one word to the device on the normal I/O channel if
        a devices has been selected for normal I/O
        :param value: word to write
        :return: True if a device was selected for normal I/O and
                 output succeeded, False otherwise.
        """
        return self.__device_on_normal_channel.write(value) \
            if self.__device_on_normal_channel is not None \
            else False
