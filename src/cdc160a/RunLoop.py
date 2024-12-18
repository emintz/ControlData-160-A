"""
The emulator's run loop.

The run loop runs the computer, executing instructions until
the machine halts.

This is a temporary version to support testing, and needs a
lot of work before we can integrate it with the console and
I/O system.
"""
from Hardware import Hardware
from InputOutput import InputOutput
import InstructionDecoder
from Storage import Storage

class RunLoop:
    """
    Run loop for the CDC 160-A emulator.
    """

    def __init__(self, console, storage: Storage, input_output: InputOutput):
        """
        Constructor. Note that the computer configuration is injected.

        :param input_output:
        :param console: the CDC 160A console. May be a dummy for
               testing under PyUnit, a character-mode console for
               development, or a full-blown GUI.
        :param storage: CDC 160-A memory and register file
        """
        self.__console = console
        self.__input_output = input_output
        self.__storage = storage
        self.__hardware = Hardware(self.__input_output, self.__storage)

    def single_step(self) -> bool:
        """
        Run a single instruction.

        :return: True unless user halts the emulator.
        """
        self.__console.before_instruction_fetch(self.__storage)
        self.__storage.service_pending_interrupts()
        # TODO(emintz): service pending buffer requests
        self.__storage.unpack_instruction()
        decoder = InstructionDecoder.decoder_at(self.__storage.f_instruction)
        current_instruction = decoder.decode(self.__storage.f_e)
        current_instruction.determine_effective_address(self.__storage)
        self.__console.before_instruction_logic(self.__storage)
        current_instruction.perform_logic(self.__hardware)
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
