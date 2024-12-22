from Device import IOChannelSupport
from cdc160a.Device import Device

class HyperLoopQuantumGravityBiTape(Device):
    """
    A hypothetical I/O device that supports input and output using
    in-memory buffers that supports hermetic testing.

    This device supports the following external function codes:

    3700: Select
    3701: Reset, mount an empty output tape and rewind the input tape.
    3702: Change tape, mount the output take as input and mount an
          empty output tape.

    All external functions return one of the following status codes:

    0000: Operation successful, no input available
    0001: Operation successful, input is available
    4000: Device is off-line.
    7777: Illegal function code
    """

    def __init__(self, input_data: [int]):
        super().__init__(
        "HyperLoop Quantum Gravity BiTape",
            True,
            True,
            5,
            IOChannelSupport.NORMAL_AND_BUFFERED)
        self.__input_data: [int] = input_data
        self.__input_position: int = 0
        self.__output_data: [int] = []
        self.__online = False

    def __has_input(self) -> bool:
        return self.__input_position < len(self.__input_data)

    def external_function(self, external_function_code) -> (bool, int | None):
        status = self.accepts(external_function_code)
        value = 0o7777
        if status:
            if self.__online:
                match external_function_code:
                    case 0o3700:
                        value = 1 if self.__has_input() else 0
                    case 0o3701:
                        self.__input_position = 0
                        self.__output_data = []
                        value = 1 if self.__has_input() else 0
                    case 0o3702:
                        self.__input_data = self.__output_data
                        self.__input_position = 0
                        self.__output_data = []
                        value = 1 if self.__has_input() else 0
            else:
                value = 0o4000

        return status, value

    def accepts(self, function_code: int) -> bool:
        return 0o3700 <= function_code <= 0o3702

    def online_status(self) -> bool:
        return self.__online

    def output_data(self) -> [int]:
        return self.__output_data.copy()

    def read(self) -> (bool, int):
        read_value = 0
        status = self.__online and self.__has_input()
        if status:
            read_value = self.__input_data[self.__input_position]
            self.__input_position += 1
        return status, read_value

    def read_delay(self) -> int:
        return 3

    def set_online_status(self, status: bool) -> None:
        self.__online = status

    def write(self, value) -> bool:
        if self.__online:
            self.__output_data.append(value)
        return self.__online

    def write_delay(self) -> int:
        return 4
