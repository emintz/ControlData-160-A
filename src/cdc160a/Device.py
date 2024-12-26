from abc import ABC, abstractmethod
from enum import Enum, unique

class IllegalInvocation(Exception):
    """
    Raised when the device receives an invalid external request
    code.
    """
    pass

class IOChannelSupport(Enum):
    """
    I/O channels supported.

    Note: from the Reference Manual, page 3-32:

        A device on the normal channel may be read or written on only the
        normal channel, but a device on the buffer channel may be read
        and written on either the normal or the buffer channel.
    """
    NORMAL_ONLY = 1
    NORMAL_AND_BUFFERED = 2

@unique
class ExternalFunctionAction(Enum):
    """
    Responses to an external function a request emanating
    from an EXC or EXF instruction.
    """
    ERROR = 1           # Handle an invalid operation.
    BUFFER_SELECT = 2   # Select on the buffer and normal channels.
    NORMAL_SELECT = 3   # Select on the normal channel.
    STATUS_CHECK = 4    # Return a status code.
    NONE = 5            # No action required.

class Device(ABC):
    """
    Base class for all I/O devices.

    """
    def __init__(
            self,
            name: str,
            can_read: bool,
            can_write: bool,
            cycles_per_transfer: int,
            io_channel_support: IOChannelSupport) -> None:
        """
        Constructor. Note that a device must be able to read, write, or
        both.

        :param name: device name, e.g. "Paper Tape Reader"; for display only.
        :param can_read: True if the device can read, False otherwise
        :param can_write: True if the device can write, False otherwise.
        :param cycles_per_transfer: number of machine cycles required to
                                    transfer one word to or from the device
        :param io_channel_support: I/O channels to which the device connects.
                                   Some devices only connect to the normal
                                   channel and can only perform synchronous,
                                   blocking I/O. The rest can connect to
                                   either the normal or the buffered channels
                                   support both synchronous and buffered
                                   asynchronous I/O.
        """
        assert can_read or can_write
        self.__name = name
        self.__can_read = can_read
        self.__can_write = can_write
        self.__cycles_per_transfer = cycles_per_transfer
        self.__io_channel_support = io_channel_support

    @abstractmethod
    def accepts(self, function_code: int) -> bool:
        """
        Returns True if and only if this Device can respond to the specified
        function code.

        :param function_code: device-specific function code. See Appendix
                              II of the Reference Manual for details.
        :return: True if and only if this device can respond to the
                 provided function code. For example, only the paper
                 tape reader can respond to 4102, select reader.
        """
        return False

    @abstractmethod
    def external_function(
            self,
            external_function_code) -> (bool, int | None):
        """
        Performs the requested external function, a request emanating
        from an EXC or EXF instruction. All subclasses must override
        this method.

        :param external_function_code:
        :return: a pair (2 item tuple) containing True if the device
                 supports the requested function and False otherwise,
                 and an optional status code. If the function does not
                 generate a status code, the second element will be None.
        """
        raise NotImplemented

    def can_read(self) -> bool:
        return self.__can_read

    def can_write(self) -> bool:
        return self.__can_write

    def initial_read_delay(self) -> int:
        """
        Provides the initial delay, the number of cycles required for
        the first word to become readable after the device is selected
        for reading.

        :return: the number of cycles, an integer >= 0. May be 0
                 if the device becomes ready immediately upon
                 selection.
        :raises: NotImplemented if the device does not support
                 reading. It is an error to invoke this method
                 on devices that do not support input (i.e. output-only
                 devices).
        """
        raise NotImplemented

    def io_channel_support(self) -> IOChannelSupport:
        return self.__io_channel_support

    def initial_write_delay(self) -> int:
        """
        Provides the initial delay, the number of cycles required for
        the first word to become writable after the device is selected
        for reading.

        :return: the number of cycles, an integer >= 0. May be 0
                 if the device becomes ready immediately upon
                 selection.
        :raises: NotImplemented if the device does not support
                 writing. It is an error to invoke this method on
                 devices that do not support output (i.e. input-only devices).
        """
        raise NotImplemented

    def name(self) -> str:
        return self.__name

    def read(self) -> (bool, int):
        """
        Reads and returns one 12-bit word from the device. If the device
        returns partial words, the value is 0-padded on the left. Devices
        that can read must override this method.

        :return: a status code that is True if the read succeeds and False
                 if it failed along with the input, as described above.
        """
        return False, 0

    def read_delay(self) -> int:
        """
        Provides the number of cycles used by a single read. It is an
        error to invoke this on devices that cannot read (i.e. on
        write-only devices). Devices that can read must override
        this method.

        :return: the delay, as described above.
        :raises: NotImplemented if the device cannot read. It is
                 an error to invoke this method on devices that
                 do not support input (i.e. on write-only devices).
        """
        raise NotImplemented

    def write(self, value: int) -> bool:
        """
        Write a single word to the device.

        :param value: the word to write. If the device writes partial
                      words, the least significant bits are written.
        :return: True if output succeeded, False otherwise
        """
        return False

    def write_delay(self) -> int:
        """
        Provides the number of cycles used by a single write. It is an
        error to invoke this on devices that cannot read (i.e. on
        write-only devices). Devices that can write must override
        this method.

        :return: the delay, as described above.
        :raises: NotImplemented if the device cannot read. It is
                 an error to invoke this method on devices that
                 do not support input (i.e. on write-only devices).
        """
        raise NotImplemented
