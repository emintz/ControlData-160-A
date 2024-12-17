from cdc160a.InputOutput import InputOutput
from cdc160a.Storage import Storage

class Hardware:
    """
    Holds all hardware components so we can pass them around easily.
    """
    def __init__(self, input_output: InputOutput, storage: Storage):
        self.input_output = input_output
        self.storage = storage
