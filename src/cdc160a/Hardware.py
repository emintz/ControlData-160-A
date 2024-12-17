from cdc160a.Device import Device
from cdc160a.Storage import Storage

class Hardware:
    """
    Holds all hardware components so we can pass them around easily.
    """
    def __init__(self, device: Device, storage: Storage):
        self.device = device
        self.storage = storage
