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
"""

from abc import ABC, abstractmethod

class BufferPump(ABC):
    """
    Base class for device-specific buffer pumps.
    """

    @abstractmethod
    def pump(self, elapsed_cycles: int) -> bool:
        """
        Pump one word into or out of memory if the buffer is not
        currently moving data. If the buffer is currently processing
        the previously pumped data word, do not move any data.

        :param elapsed_cycles: the number of cycles that have elapsed
               since the prior pump invocation. Pumps can use this
               to simulate I/O latency
        :return: True if data remains to be buffered, False otherwise.
        """
        return False
