from unittest import TestCase
from cdc160a.InputOutput import InputOutput
from cdc160a.Storage import InterruptLock
from cdc160a.NullDevice import NullDevice
from cdc160a.Storage import Storage
from test_support.HyperLoopQuantumGravityBiTape import HyperLoopQuantumGravityBiTape
from development import CommandInterpreters
from development.Interpreter import Interpreter

class TestCommandReader:
    def __init__(self):
        self.command = [""]

    def read_command(self) -> [str]:
        return self.command

class TestCommandInterpreters(TestCase):

    _INPUT_DATA = [0o0000, 0o0001, 0o0200, 0o0210, 0o1111,
                   0o4001, 0o4011, 0o4111, 0o4112, 0o4122]


    def setUp(self):
        self.__command_reader = TestCommandReader()
        self.__bi_tape = HyperLoopQuantumGravityBiTape(self._INPUT_DATA)
        self.__null_device = NullDevice()
        self.__input_output = InputOutput([
            self.__bi_tape,
            self.__null_device])
        self.__interpreter = Interpreter(
            [CommandInterpreters.COMMANDS], self.__command_reader)
        self.__storage = Storage()

    def test_clear(self) -> None:
        self.__storage.a_register = 0o5000
        self.__storage.z_register = 0o5400
        self.__storage.p_register = 0o100
        self.__storage.relative_storage_bank = 3
        self.__storage.f_instruction = 0o50
        self.__storage.f_e = 0o40
        self.__storage.run()
        self.__storage.set_interrupt_lock()
        self.__storage.machine_hung = True
        self.__input_output.external_function(0o3700)
        assert (self.__input_output.device_on_normal_channel() ==
                self.__bi_tape)
        assert self.__input_output.device_on_buffer_channel() is None

        assert CommandInterpreters.Clear().apply(self.__interpreter, self.__storage, self.__input_output, [])

        assert self.__storage.a_register == 0
        assert self.__storage.z_register == 0
        assert self.__storage.get_program_counter() == 0
        assert self.__storage.relative_storage_bank == 0
        assert self.__storage.f_instruction == 0
        assert self.__storage.f_e == 0
        assert not self.__storage.run_stop_status
        assert self.__storage.interrupt_lock == InterruptLock.FREE
        assert not self.__storage.machine_hung
        assert self.__input_output.device_on_normal_channel() is None
        assert self.__input_output.device_on_buffer_channel() is None

    def test_close(self) -> None:
        close_command = CommandInterpreters.Close()
        assert self.__input_output.device("nul") == self.__null_device
        assert not self.__null_device.is_open()
        assert close_command.apply(self.__interpreter, self.__storage, self.__input_output, ["nul"])
        assert not self.__null_device.is_open()
        self.__null_device.open("ipcress")
        assert self.__null_device.is_open()
        assert close_command.apply(self.__interpreter, self.__storage, self.__input_output, [])
        assert self.__null_device.is_open()
        assert close_command.apply(self.__interpreter, self.__storage, self.__input_output, ["bi_tape"])
        assert self.__null_device.is_open()
        assert close_command.apply(self.__interpreter, self.__storage, self.__input_output, ["nul"])
        assert not self.__null_device.is_open()

    def test_halt(self) -> None:
        halt_runner = CommandInterpreters.Step()
        self.__storage.run()
        assert not halt_runner.apply(self.__interpreter, self.__storage, self.__input_output, [])
        assert not self.__storage.run_stop_status

    def test_jump_switch(self) -> None:
        jump_switch_runner = CommandInterpreters.JumpSwitch(1)
        assert self.__interpreter.jump_set_mask() == 0
        assert self.__interpreter.jump_down_mask() == 0
        assert self.__storage.get_jump_switch_mask() == 0
        assert jump_switch_runner.apply(self.__interpreter, self.__storage, self.__input_output, ["sideways"])
        assert self.__interpreter.jump_set_mask() == 0
        assert self.__interpreter.jump_down_mask() == 0
        assert jump_switch_runner.apply(self.__interpreter, self.__storage, self.__input_output, ["down"])
        assert self.__interpreter.jump_down_mask() == 0o02
        assert self.__interpreter.jump_set_mask() == 0o02
        assert jump_switch_runner.apply(self.__interpreter, self.__storage, self.__input_output, ["center"])
        assert self.__interpreter.jump_set_mask() == 0
        assert self.__interpreter.jump_down_mask() == 0
        assert jump_switch_runner.apply(self.__interpreter, self.__storage, self.__input_output, ["up"])
        assert self.__interpreter.jump_down_mask() == 0o0
        assert self.__interpreter.jump_set_mask() == 0o02

    def test_open_device(self) -> None:
        device_opener = CommandInterpreters.OpenDevice()
        assert not self.__null_device.is_open()
        assert device_opener.apply(
            self.__interpreter, self.__storage, self.__input_output, ["nul", "double_cut.txt"])
        assert self.__null_device.is_open()
        assert self.__null_device.file_name() == "double_cut.txt"

    def test_resume(self) -> None:
        restarter = CommandInterpreters.Resume()
        self.__storage.stop()
        assert not restarter.apply(self.__interpreter, self.__storage, self.__input_output, [])
        assert self.__storage.run_stop_status

    def test_seta(self) -> None:
        setter = CommandInterpreters.SetA()
        assert self.__storage.a_register == 0
        assert setter.apply(self.__interpreter, self.__storage, self.__input_output, ["A"])
        assert self.__storage.a_register == 0
        assert setter.apply(self.__interpreter, self.__storage, self.__input_output, ["10000"])
        assert self.__storage.a_register == 0
        assert setter.apply(self.__interpreter, self.__storage, self.__input_output, ["1234"])
        assert self.__storage.a_register == 0o1234

    def test_setb(self) -> None:
        setter = CommandInterpreters.SetB()
        assert self.__storage.buffer_storage_bank == 0
        assert setter.apply(self.__interpreter, self.__storage, self.__input_output, ["UP"])
        assert self.__storage.buffer_storage_bank == 0
        assert setter.apply(self.__interpreter, self.__storage, self.__input_output, ["10"])
        assert self.__storage.buffer_storage_bank == 0
        assert setter.apply(self.__interpreter, self.__storage, self.__input_output, ["3"])
        assert self.__storage.buffer_storage_bank == 3

    def test_setd(self) -> None:
        setter = CommandInterpreters.SetD()
        assert self.__storage.direct_storage_bank == 0
        assert setter.apply(self.__interpreter, self.__storage, self.__input_output, ["UP"])
        assert self.__storage.direct_storage_bank == 0
        assert setter.apply(self.__interpreter, self.__storage, self.__input_output, ["10"])
        assert self.__storage.direct_storage_bank == 0
        assert setter.apply(self.__interpreter, self.__storage, self.__input_output, ["3"])
        assert self.__storage.direct_storage_bank == 3

    def test_seti(self) -> None:
        setter = CommandInterpreters.SetI()
        assert self.__storage.indirect_storage_bank == 0
        assert setter.apply(self.__interpreter, self.__storage, self.__input_output, ["UP"])
        assert self.__storage.indirect_storage_bank == 0
        assert (setter.apply(self.__interpreter, self.__storage, self.__input_output, ["10"]))
        assert self.__storage.indirect_storage_bank == 0
        assert setter.apply(self.__interpreter, self.__storage, self.__input_output, ["3"])
        assert self.__storage.indirect_storage_bank == 3

    def test_setr(self) -> None:
        setter = CommandInterpreters.SetR()
        assert self.__storage.relative_storage_bank == 0
        assert setter.apply(self.__interpreter, self.__storage, self.__input_output, ["UP"])
        assert self.__storage.relative_storage_bank == 0
        assert setter.apply(self.__interpreter, self.__storage, self.__input_output, ["10"])
        assert self.__storage.relative_storage_bank == 0
        assert setter.apply(self.__interpreter, self.__storage, self.__input_output, ["3"])
        assert self.__storage.relative_storage_bank == 3

    def test_step(self):
        step = CommandInterpreters.Step()
        self.__storage.stop()
        assert not step.apply(self.__interpreter, self.__storage, self.__input_output, [])
        assert not self.__storage.run_stop_status

    def test_stop_switch(self) -> None:
        stop_switch_runner = CommandInterpreters.StopSwitch(1)
        assert self.__interpreter.stop_set_mask() == 0
        assert self.__interpreter.stop_down_mask() == 0
        assert stop_switch_runner.apply(self.__interpreter, self.__storage, self.__input_output, ["sideways"])
        assert self.__interpreter.stop_set_mask() == 0
        assert self.__interpreter.stop_down_mask() == 0
        assert stop_switch_runner.apply(self.__interpreter, self.__storage, self.__input_output, ["down"])
        assert self.__interpreter.stop_down_mask() == 0o02
        assert self.__interpreter.stop_set_mask() == 0o02
        assert stop_switch_runner.apply(self.__interpreter, self.__storage, self.__input_output, ["center"])
        assert self.__interpreter.stop_set_mask() == 0
        assert self.__interpreter.stop_down_mask() == 0
        assert stop_switch_runner.apply(self.__interpreter, self.__storage, self.__input_output, ["up"])
        assert self.__interpreter.stop_down_mask() == 0o0
        assert self.__interpreter.stop_set_mask() == 0o02
