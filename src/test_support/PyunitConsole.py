from cdc160a import Storage

class PyConsole:
    pass

    def before_instruction_fetch(self, storage: Storage) -> None:
        """
        Performs console-related tasks required to fetch an instruction.

        The run loop invokes this method just before it fetches an instruction.
        Implementations should set the jump and stop switch masks in the
        provided Storage.

        :param storage: memory and register file
        :return: None
        """
        pass

    def before_instruction_logic(self, storage: Storage) -> None:
        """
        Perform console-related tasks required to run instruction logic.

        The run loop invokes this method after it unpacks the instruction
        and determines its effective address. Implementations should halt
        the machine if the user has moved the run/stop switch to stop.

        :param storage: memory and register file
        :return: None
        """
        pass

    def before_advance(self, storage: Storage) -> bool:
        """
        Perform module-related tasks required to advance to the next
        instruction. Implementations should stop and display the console
        if the machine has been halted by HLT, ERR, or for any other reasons.

        To support testing, the run loop will halt when this method
        returns False. Production implementations must always return True.

        :param storage: memory and register file
        :return: True if the run loop should keep going, False if the run
                 loop should exit. This is to support PyUnit testing.
                 Production versions must return True.
        """
        return storage.run_stop_status

