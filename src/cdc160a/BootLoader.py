from cdc160a.Device import Device
from cdc160a.Storage import Storage
from enum import Enum, unique

class BootLoader:
    """
    Loads a boot tape into memory. To use:

    1. Open a boot image on the paper tape reader.
    2. Master clear. This sets the A (accumulator), P (program counter),
       and Relative Bank registers to 0, halts any active I/O buffering,
       and disconnects all selected devices from the I/O bus.
    3. Enter the start address, the address to receive the first
       word in the boot record, into P.
    4. Run the boot load.

    When the loader finishes reading the boot image:

    * A will contain a check sum of the boot image module
      2^12 - 1 (note: NOT 2^12)
    * P will contain the LWA (note: NOT LWA + 1) where the loader
      stored data.

    For further detains, including the paper tape format, see page
    3-41 of the 160-A Computer Reference Manual, March 1965 edition.

    TODO(emintz): URL. Should we link to BitSavers or store a copy
                  of the manual in the project's GitHub repository?
    """

    @unique
    class __State(Enum):
        CREATED = 0,
        FEEDING_LEADER = 1,
        READ_MOST_SIGNIFICANT = 2,
        READ_LEAST_SIGNIFICANT = 3,
        BOOT_SUCCEEDED = 4,
        BOOT_FAILED = 5,

        def index(self) -> int:
            return self.value[0]

    @unique
    class __Event(Enum):
        LEAST_SIGNIFICANT_READ = 0,
        MOST_SIGNIFICANT_READ = 1,
        INVALID_VALUE_READ = 2,

        def index(self) -> int:
            return self.value[0]

    @unique
    class Status(Enum):
        IDLE = 0,        # Boot load not started
        LOADING = 1,     # Boot image being loaded
        SUCCEEDED = 2,   # Boot succeeded
        FAILED = 3,      # Boot failed

    # State transition table which enforces the boot format:
    #
    #   Successive words [successive pairs of 6 bit bytes, the first being
    #   the most significant having a 7th level punch, the second not
    #   having a 7th level punch] must follow each other on the tape.
    #   The automatic load will stop when a frame is read which should
    #   contain a 7th level punch and none exists. Tape may be placed in
    #   the reader at any place on the leader; the automatic will not
    #   begin will not begin until the first 7th level punch is sensed.
    #
    __STATE_TRANSITION_TABLE: list[list[__State]] = [
        [   # __State.CREATED, 0
            __State.FEEDING_LEADER,         # LEAST_SIGNIFICANT_READ
            __State.READ_MOST_SIGNIFICANT,  # MOST_SIGNIFICANT_READ
            __State.BOOT_FAILED,            # INVALID_VALUE_READ
        ],
        [  # __State.FEEDING_LEADER, 1
            __State.FEEDING_LEADER,         # LEAST_SIGNIFICANT_READ
            __State.READ_MOST_SIGNIFICANT,  # MOST_SIGNIFICANT_READ
            __State.BOOT_FAILED,            # INVALID_VALUE_READ
        ],
        [   # __State.READ_MOST_SIGNIFICANT, 2, least significant must follow
            __State.READ_LEAST_SIGNIFICANT, # LEAST_SIGNIFICANT_READ
            __State.BOOT_FAILED,            # MOST_SIGNIFICANT_READ,
            __State.BOOT_FAILED,            # INVALID_VALUE_READ
        ],
        [   # __State.READ_LEAST_SIGNIFICANT, 3
            __State.BOOT_SUCCEEDED,          # LEAST_SIGNIFICANT_READ
            __State.READ_MOST_SIGNIFICANT ,  # MOST_SIGNIFICANT_READ
            __State.BOOT_FAILED,             # INVALID_VALUE_READ

        ],
        [   # __State.BOOT_SUCCEEDED, 4 should never be referenced.
            __State.BOOT_FAILED,             # LEAST_SIGNIFICANT_READ
            __State.BOOT_FAILED,             # MOST_SIGNIFICANT_READ
            __State.BOOT_FAILED,             # INVALID_VALUE_READ
        ],
        [  # __State.BOOT_FAILED, 5 should never be referenced.
            __State.BOOT_FAILED,  # LEAST_SIGNIFICANT_READ
            __State.BOOT_FAILED,  # MOST_SIGNIFICANT_READ
            __State.BOOT_FAILED,  # INVALID_VALUE_READ
        ],
    ]

    def __init__(self, boot_device: Device, storage: Storage):
        """
        Constructor that creates a BootLoader that will read from the
        specified device to the memory contained in the specified
        storage.

        :param boot_device: reads the boot image. To ensure faithful
                            emulation, this must be a paper tape
                            reader. Since this is not checked, the
                            invoker must enforce this. A boot
                            image should be open on the device now,
                            and must be open before the boot runs.
        :param storage: provides the memory to receive the boot image.
        """
        self.__boot_device: Device = boot_device
        self.__storage: Storage = storage
        self.__state = self.__State.CREATED
        self.__status = self.Status.IDLE
        self.__address_pre_increment: int = 0

    def status(self) -> Status:
        return self.__status

    def load(self) -> Status:
        memory_value: int = 0

        while True:
            input_value, event = self.__read_and_classify_frame()
            new_state = self.__transition(event)

            match new_state:
                case BootLoader.__State.FEEDING_LEADER:
                    pass
                case BootLoader.__State.READ_MOST_SIGNIFICANT:
                    memory_value = (input_value & 0o77) << 6
                case BootLoader.__State.READ_LEAST_SIGNIFICANT:
                    memory_value |= input_value
                    self.__storage.p_register += self.__address_pre_increment
                    self.__storage.write_relative_bank(
                        self.__storage.p_register, memory_value)
                    self.__storage.a_register += memory_value
                    self.__storage.a_register %= 0o7777
                    memory_value = 0
                    self.__address_pre_increment = 1
                case BootLoader.__State.BOOT_SUCCEEDED:
                    self.__status = BootLoader.Status.SUCCEEDED
                    break
                case BootLoader.__State.BOOT_FAILED:
                    self.__status = BootLoader.Status.FAILED
                    break
            self.__state = new_state

        return self.__status

    def __read_and_classify_frame(self) -> (int, __Event):
        """
        Read one frame and classify it. Frames can contain the
        least significant 6 bits of a value (no 7th level punch),
        the most significant 6 bits of a value (7th level punch),
        or an erroneous value not in [0o00 .. 0o177]

        :return: the frame value and corresponding event type
        """
        read_status, input_value = self.__boot_device.read()
        event: BootLoader.__Event = self.__Event.INVALID_VALUE_READ
        if read_status:
            if 0o00 <= input_value <= 0o77:
                event = BootLoader.__Event.LEAST_SIGNIFICANT_READ
            elif 0o100 <= input_value <= 0o177:
                event = BootLoader.__Event.MOST_SIGNIFICANT_READ
        return input_value, event

    def __transition(self, event: __Event) -> __State:
        """
        Returns the state resulting from applying the specified event
        to the current state.

        :param event: triggers the transition
        :return: the new state as described above
        """
        current_state_index: int = self.__state.index()
        event_index: int = event.index()
        return self.__STATE_TRANSITION_TABLE[current_state_index][event_index]
