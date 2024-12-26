from unittest import TestCase
from cdc160a.BufferPump import PumpStatus
from cdc160a.BufferedOutputPump import BufferedOutputPump
from cdc160a.Storage import Storage
from test_support.HyperLoopQuantumGravityBiTape import HyperLoopQuantumGravityBiTape

class TestBufferedOutputPump(TestCase):
    _INPUT_DATA = [0o7777, 0o0001, 0o0200, 0o0210, 0o1111, 0o4001, 0o4011, 0o4111, 0o4112, 0o4122]
    _OUTPUT_DATA = [0o10, 0o06, 0o04, 0o02, 0o00, 0o01, 0o03, 0o05, 0o07]
    _BUFFER_FIRST_WORD_ADDRESS = 0o200
    _BUFFER_LAST_WORD_ADDRESS_PLUS_ONE = (
            _BUFFER_FIRST_WORD_ADDRESS + len(_OUTPUT_DATA))

    def setUp(self):
        self.__bi_tape: HyperLoopQuantumGravityBiTape = \
            HyperLoopQuantumGravityBiTape(self._INPUT_DATA.copy())
        self.__storage: Storage = Storage()
        self.__storage.buffer_storage_bank = 0
        self.__storage.direct_storage_bank = 1
        self.__storage.indirect_storage_bank = 2
        self.__storage.relative_storage_bank = 3
        self.__storage.buffer_entrance_register = (
            self._BUFFER_FIRST_WORD_ADDRESS)
        self.__storage.buffer_exit_register = (
            self._BUFFER_LAST_WORD_ADDRESS_PLUS_ONE)
        self.__buffered_output_pump = BufferedOutputPump(
            self.__bi_tape, self.__storage)
        data_location = self._BUFFER_FIRST_WORD_ADDRESS
        for value in self._OUTPUT_DATA:
            self.__storage.write_buffer_bank(data_location, value)
            data_location += 1

    def test_construction(self) -> None:
        assert (self.__buffered_output_pump.cycles_remaining() ==
                self.__bi_tape.initial_write_delay())

    def test_life_cycle(self) -> None:
        words_moved = 0
        elapsed_cycles = 0
        self.__bi_tape.set_online_status(True)
        self.__storage.buffer_entrance_register = (
            self._BUFFER_FIRST_WORD_ADDRESS)
        self.__storage.buffer_exit_register = (
            self._BUFFER_LAST_WORD_ADDRESS_PLUS_ONE)
        while True:
            elapsed_cycles += 1
            match self.__buffered_output_pump.pump(1):
                case PumpStatus.NO_DATA_MOVED:
                    pass
                case PumpStatus.ONE_WORD_MOVED:
                    words_moved += 1
                case PumpStatus.COMPLETED:
                    words_moved += 1
                    break
                case PumpStatus.FAILURE:
                    self.fail("Unexpected device failure")
        assert words_moved == len(self._OUTPUT_DATA)
        assert (self.__storage.buffer_entrance_register ==
                self._BUFFER_LAST_WORD_ADDRESS_PLUS_ONE)
        assert (self.__storage.buffer_exit_register ==
                self._BUFFER_LAST_WORD_ADDRESS_PLUS_ONE)
        assert self.__bi_tape.output_data() == self._OUTPUT_DATA
