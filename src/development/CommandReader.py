class CommandReader:
    """
    Reads commands from the keyboard
    """
    def read_command(self) -> [str]:
        command = input("> ")
        return command.split()
