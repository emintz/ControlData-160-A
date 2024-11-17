"""
The emulator's run loop.

The run loop runs the computer, executing instructions until
the machine halts.

This is a temporary version to support testing, and needs a
lot of work before we can integrate it with the console and
I/O system.
"""
from Instructions import  Instruction
import InstructionDecoder
from Storage import Storage

class RunLoop:
    pass

    def __init__(self, storage: Storage):
        """
        Constructor. Note that the computer configuration is injected.

        :param storage: CDC 160-A memory and register file

        TODO(emintz): add console.
        """
        self.__storage = storage

    def run(self) -> None:
        self.__storage.run()
        # TODO(emintz): the following must become an endless loop when we have a
        #               working console.
        while self.__storage.run_stop_status:
            # TODO(emintz): query the console jump and stop switches
            # TODO(emintz): respond to pending interrupts
            # TODO(emintz): service pending buffer requests
            # TODO(emintz): refactor instruction decoding into the Storage class
            self.__storage.unpack_instruction()
            decoder = InstructionDecoder.decoder_at(self.__storage.f_instruction)
            current_instruction = decoder.decode(self.__storage.f_e)
            current_instruction.determine_effective_address(self.__storage)
            # TODO(emintz): invoke the console's run/stop handler. The handler should
            #               return immediately any of the following holds:
            #               1.  The computer is running
            #               2.  The user starts the computer (moves run/stop to run)
            #               3.  The user requests a single-instruction step.
            current_instruction.perform_logic(self.__storage)
            # TODO(emintz): invoke the console if the computer has halted
            # instead of exiting.
            if not self.__storage.run_stop_status:
                break
            self.__storage.advance_to_next_instruction()
