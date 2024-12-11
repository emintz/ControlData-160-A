"""
The emulator's run loop.

The run loop runs the computer, executing instructions until
the machine halts.

This is a temporary version to support testing, and needs a
lot of work before we can integrate it with the console and
I/O system.
"""
import InstructionDecoder
from Storage import Storage

class RunLoop:
    """
    Run loop for the CDC 160-A emulator.
    """

    def __init__(self, console, storage: Storage):
        """
        Constructor. Note that the computer configuration is injected.

        :param console: the CDC 160A console. May be a dummy for
               testing under PyUnit, a character-mode console for
               development, or a full-blown GUI.
        :param storage: CDC 160-A memory and register file
        """
        self.__console = console
        self.__storage = storage

    def single_step(self) -> bool:
        """
        Run a single instruction.

        :return: True unless an ERR or HLT instruction is run.
        """
        self.__console.before_instruction_fetch(self.__storage)
        self.__storage.service_pending_interrupts()
        # TODO(emintz): service pending buffer requests
        self.__storage.unpack_instruction()
        decoder = InstructionDecoder.decoder_at(self.__storage.f_instruction)
        current_instruction = decoder.decode(self.__storage.f_e)
        current_instruction.determine_effective_address(self.__storage)
        self.__console.before_instruction_logic(self.__storage)
        current_instruction.perform_logic(self.__storage)
        if not self.__console.before_advance(self.__storage):
            return False
        self.__storage.advance_to_next_instruction()
        return True

    def run(self) -> None:
        """
        Runs the emulator, returning when the emulator performs an
        ERR or HLT instruction.

        :return: None
        """
        while self.single_step():
            pass
