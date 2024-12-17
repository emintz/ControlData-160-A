from abc import ABC, abstractmethod
from cdc160a.IOStatus import IOStatus
from cdc160a.Storage import Storage


class BaseConsole(ABC):
    """
    Base class for all console implementations. Maintains I/O status
    """

    def __init__(self):
        self.__buffering = False
        self.__normal_io_status = IOStatus.IDLE

    @abstractmethod
    def before_instruction_fetch(self, storage: Storage) -> None:
        pass

    @abstractmethod
    def before_instruction_logic(self, storage: Storage) -> None:
        pass

    @abstractmethod
    def before_advance(self, storage: Storage) -> bool:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass

    def buffering(self) -> bool:
        return self.__buffering

    def normal_io_status(self) -> IOStatus:
        return self.__normal_io_status

    def _cancel_io(self) -> None:
        self.__buffering = False
        self.__normal_io_status = IOStatus.IDLE

    def _set_buffering(self, buffering: bool) -> None:
        self.__buffering = buffering

    def _set_io_status(self, normal_io_status: IOStatus):
        self.__normal_io_status = normal_io_status
