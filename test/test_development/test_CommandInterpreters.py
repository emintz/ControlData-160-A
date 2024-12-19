from unittest import TestCase
from cdc160a.Storage import InterruptLock
from cdc160a.Storage import Storage
from development import CommandInterpreters
from development.Interpreter import Interpreter

class TestCommandReader:
    def __init__(self):
        self.command = [""]

    def read_command(self) -> [str]:
        return self.command

class TestCommandInterpreters(TestCase):

    def setUp(self):
        self.__command_reader = TestCommandReader()
        self.__interpreter = Interpreter(CommandInterpreters.COMMANDS, self.__command_reader)
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

        assert CommandInterpreters.Clear().apply(self.__interpreter, self.__storage, "")

        assert self.__storage.a_register == 0
        assert self.__storage.z_register == 0
        assert self.__storage.get_program_counter() == 0
        assert self.__storage.relative_storage_bank == 0
        assert self.__storage.f_instruction == 0
        assert self.__storage.f_e == 0
        assert not self.__storage.run_stop_status
        assert self.__storage.interrupt_lock == InterruptLock.FREE
        assert not self.__storage.machine_hung

    def test_halt(self) -> None:
        halt_runner = CommandInterpreters.Step()
        self.__storage.run()
        assert not halt_runner.apply(self.__interpreter, self.__storage, "")
        assert not self.__storage.run_stop_status

    def test_jump_switch(self) -> None:
        jump_switch_runner = CommandInterpreters.JumpSwitch(1)
        assert self.__interpreter.jump_set_mask() == 0
        assert self.__interpreter.jump_down_mask() == 0
        assert self.__storage.get_jump_switch_mask() == 0
        assert jump_switch_runner.apply(self.__interpreter, self.__storage, "sideways")
        assert self.__interpreter.jump_set_mask() == 0
        assert self.__interpreter.jump_down_mask() == 0
        assert jump_switch_runner.apply(self.__interpreter, self.__storage, "down")
        assert self.__interpreter.jump_down_mask() == 0o02
        assert self.__interpreter.jump_set_mask() == 0o02
        assert jump_switch_runner.apply(self.__interpreter, self.__storage, "center")
        assert self.__interpreter.jump_set_mask() == 0
        assert self.__interpreter.jump_down_mask() == 0
        assert jump_switch_runner.apply(self.__interpreter, self.__storage, "up")
        assert self.__interpreter.jump_down_mask() == 0o0
        assert self.__interpreter.jump_set_mask() == 0o02

    def test_resume(self) -> None:
        restarter = CommandInterpreters.Resume()
        self.__storage.stop()
        assert not restarter.apply(self.__interpreter, self.__storage, "")
        assert self.__storage.run_stop_status

    def test_seta(self) -> None:
        setter = CommandInterpreters.SetA()
        assert self.__storage.a_register == 0
        assert setter.apply(self.__interpreter, self.__storage, "A")
        assert self.__storage.a_register == 0
        assert setter.apply(self.__interpreter, self.__storage, "10000")
        assert self.__storage.a_register == 0
        assert setter.apply(self.__interpreter, self.__storage, "1234")
        assert self.__storage.a_register == 0o1234

    def test_setb(self) -> None:
        setter = CommandInterpreters.SetB()
        assert self.__storage.buffer_storage_bank == 0
        assert setter.apply(self.__interpreter, self.__storage, "UP")
        assert self.__storage.buffer_storage_bank == 0
        assert setter.apply(self.__interpreter, self.__storage, "10")
        assert self.__storage.buffer_storage_bank == 0
        assert setter.apply(self.__interpreter, self.__storage, "3")
        assert self.__storage.buffer_storage_bank == 3

    def test_setd(self) -> None:
        setter = CommandInterpreters.SetD()
        assert self.__storage.direct_storage_bank == 0
        assert setter.apply(self.__interpreter, self.__storage, "UP")
        assert self.__storage.direct_storage_bank == 0
        assert setter.apply(self.__interpreter, self.__storage, "10")
        assert self.__storage.direct_storage_bank == 0
        assert setter.apply(self.__interpreter, self.__storage, "3")
        assert self.__storage.direct_storage_bank == 3

    def test_seti(self) -> None:
        setter = CommandInterpreters.SetI()
        assert self.__storage.indirect_storage_bank == 0
        assert setter.apply(self.__interpreter, self.__storage, "UP")
        assert self.__storage.indirect_storage_bank == 0
        assert setter.apply(self.__interpreter, self.__storage, "10")
        assert self.__storage.indirect_storage_bank == 0
        assert setter.apply(self.__interpreter, self.__storage, "3")
        assert self.__storage.indirect_storage_bank == 3

    def test_setr(self) -> None:
        setter = CommandInterpreters.SetR()
        assert self.__storage.relative_storage_bank == 0
        assert setter.apply(self.__interpreter, self.__storage, "UP")
        assert self.__storage.relative_storage_bank == 0
        assert setter.apply(self.__interpreter, self.__storage, "10")
        assert self.__storage.relative_storage_bank == 0
        assert setter.apply(self.__interpreter, self.__storage, "3")
        assert self.__storage.relative_storage_bank == 3

    def test_step(self):
        step = CommandInterpreters.Step()
        self.__storage.stop()
        assert not step.apply(self.__interpreter, self.__storage, "")
        assert not self.__storage.run_stop_status

    def test_stop_switch(self) -> None:
        stop_switch_runner = CommandInterpreters.StopSwitch(1)
        assert self.__interpreter.stop_set_mask() == 0
        assert self.__interpreter.stop_down_mask() == 0
        assert stop_switch_runner.apply(self.__interpreter, self.__storage, "sideways")
        assert self.__interpreter.stop_set_mask() == 0
        assert self.__interpreter.stop_down_mask() == 0
        assert stop_switch_runner.apply(self.__interpreter, self.__storage, "down")
        assert self.__interpreter.stop_down_mask() == 0o02
        assert self.__interpreter.stop_set_mask() == 0o02
        assert stop_switch_runner.apply(self.__interpreter, self.__storage, "center")
        assert self.__interpreter.stop_set_mask() == 0
        assert self.__interpreter.stop_down_mask() == 0
        assert stop_switch_runner.apply(self.__interpreter, self.__storage, "up")
        assert self.__interpreter.stop_down_mask() == 0o0
        assert self.__interpreter.stop_set_mask() == 0o02
