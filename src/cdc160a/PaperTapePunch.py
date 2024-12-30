
import os
from io import TextIOWrapper
from typing import Optional
from cdc160a.Device import Device, IOChannelSupport

class PaperTapePunch(Device):
    """
    An emulated paper tape punch that writes to files. Each character
    is emitted as a 3 digit octal string in the range [000 .. 377],
    meaning that the punch can emit 5, 7, and 8 level (i.e. row)
    paper tapes.
    """

    def __init__(self):
        """
        Constructor that sets all device characteristics. Note that the
        paper tape punch punches 110 characters/second.
        """
        super().__init__(
            "Paper Tape Punch",
            "pt_pun",
            False,
            True, IOChannelSupport.NORMAL_ONLY)
        self.__output_file: Optional[TextIOWrapper] = None
        self.__file_name: Optional[str] = None

    def accepts(self, function_code: int) -> bool:
        """
        Signal if the paper tape punch accepts the specified external
        function code. Note that the punch accepts exactly one: 4104,
        select paper tape punch.
        :param function_code: the function to evaluate
        :return: True if the punch accepts the code, False otherwise
        """
        return function_code == 0o4104

    def close(self) -> None:
        """
        Close the paper tape output file if one is open, otherwise do
        nothing
        :return: None
        """
        if self.__output_file is not None:
            self.__output_file.close()
            self.__output_file = None
            self.__file_name = None

    def external_function(self, external_function_code) -> (bool, int | None):
        return external_function_code == 0o4104, None

    def file_name(self) -> Optional[str]:
        return self.__file_name

    def initial_write_delay(self) -> int:
        return self.write_delay()

    def is_open(self) -> bool:
        return self.__output_file is not None

    def open(self, file_name: str) -> bool:
        if self.__output_file is not None:
            status = False
            print(
                "Cannot open {0} for paper tape output because "
                "{1} is already open.".format(
                    file_name,
                    self.__file_name))
        else:
            status: bool = not os.path.exists(file_name)
            if status:
                self.__output_file = open(file_name, "wt")
                self.__file_name = file_name
        return status

    def write(self, value: int) -> bool:
        status: bool = self.__output_file is not None
        if status:
            formatted_value = "{0:0>3o}\n".format(value & 0o377)
            self.__output_file.write(formatted_value)
        return status

    def write_delay(self) -> int:
        return 1420
