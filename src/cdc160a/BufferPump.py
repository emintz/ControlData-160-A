"""
Base class for buffered I/O implementations: provides an API for pumping data
from a source to memory, and pumping data from memory into a sink. The source
or sink is typically, but not necessarily, a peripheral device.

Buffer pumps come in two versions: input, and output. Input pumps take
data from their associated device and pump them into memory, while
output pumps take data from memory and pump them into their
associated device. Input-only or output-only devices card readers will have
a single input or output (respectfully) pump, while input and output-capable
devices like tape drives will have one of each.

Buffer pumps only move data. They do not manage other machine state.

Note that the BufferPump class does not reference the Storage class
to sidestep circular references in subclasses. If the BufferPump
bound a Storage instance, circular references would occur.

Buffer pumps are intended for single use, to be created at the start
of a buffered read or write and discarded when the operation has
completed.
"""

from abc import ABC, abstractmethod
from cdc160a.Device import Device
from enum import Enum, unique

@unique
class PumpStatus(Enum):
    NO_DATA_MOVED = 1,   # The device is not ready to consume or provide data.
    ONE_WORD_MOVED = 2,  # The device consumed or provided one word.
    COMPLETED = 3,       # Buffered input or output successfully completed.
                         # The last required word has been moved to or from
                         # memory.
    FAILURE = 4,         # Buffering has failed.

class BufferPump(ABC):
    """
    Base class for device-specific buffer pumps.
    """

    @abstractmethod
    def device(self) -> Device:
        pass

    @abstractmethod
    def pump(self, elapsed_cycles: int) -> PumpStatus:
        """
        Pump one word into or out of memory if the buffer is not
        currently moving data. If the buffer is currently processing
        the previously pumped data word, do not move any data.

        :param elapsed_cycles: the number of cycles that have elapsed
               since the prior pump invocation. Pumps can use this
               to simulate I/O latency
        :return: operation status as defined in the BufferStatus enumeration
                 above.
        """
        pass
