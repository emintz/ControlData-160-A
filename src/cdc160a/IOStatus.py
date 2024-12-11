from enum import Enum


class IOStatus(Enum):
    """
    I/O Status Values
    """
    IDLE = 0,     # I/O is inactive, no I/O in progress
    INPUT = 1,    # CPU is reading from an input device
    OUTPUT = 2,   # CPU is writing to an output device
