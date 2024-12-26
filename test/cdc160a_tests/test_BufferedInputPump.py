from unittest import TestCase
from cdc160a.BufferPump import PumpStatus
from cdc160a.BufferedInputPump import BufferedInputPump
from cdc160a.Storage import Storage
from test_support.HyperLoopQuantumGravityBiTape import HyperLoopQuantumGravityBiTape

class TestBufferedInputPump(TestCase):

    _INPUT_DATA = [0o7777, 0o0001, 0o0200, 0o0210, 0o1111,
                   0o4001, 0o4011, 0o4111, 0o4112, 0o4122]

    _BUFFER_FIRST_WORD_ADDRESS = 0o200
    _BUFFER_LAST_WORD_ADDRESS_PLUS_ONE = (
            _BUFFER_FIRST_WORD_ADDRESS + len(_INPUT_DATA))

    def setUp(self):
        self.__bi_tape: HyperLoopQuantumGravityBiTape =\
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
        self.__buffered_input_pump = BufferedInputPump(
            self.__bi_tape, self.__storage)

    def test_construction(self) -> None:
        assert (self.__buffered_input_pump.cycles_remaining() ==
                self.__bi_tape.initial_read_delay())

    def test_life_cycle(self) -> None:
        words_moved = 0
        cycles_consumed = 0
        self.__bi_tape.set_online_status(True)
        while True:
            cycles_consumed += 1
            match self.__buffered_input_pump.pump(1):
                case PumpStatus.NO_DATA_MOVED:
                    pass
                case PumpStatus.ONE_WORD_MOVED:
                    words_moved += 1
                case PumpStatus.COMPLETED:
                    words_moved += 1
                    break
                case PumpStatus.FAILURE:
                    self.fail("Unexpected device failure")
        assert words_moved == 10
        assert cycles_consumed == 33 # 1 initial delay + 9 read delays
        assert (self.__storage.buffer_entrance_register ==
                self._BUFFER_LAST_WORD_ADDRESS_PLUS_ONE)
        assert (self.__storage.buffer_exit_register ==
                self._BUFFER_LAST_WORD_ADDRESS_PLUS_ONE)
        data_location = self._BUFFER_FIRST_WORD_ADDRESS
        for value in self._INPUT_DATA:
            assert self.__storage.read_buffer_bank(data_location) == value
            data_location += 1
