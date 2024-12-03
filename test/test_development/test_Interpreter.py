from unittest import TestCase

from cdc160a.Storage import Storage
from development import CommandInterpreters
from development import Interpreter


class TestCommandReader:

    def __init__(self):
        self.command = [""]

    def read_command(self) -> [str]:
        return self.command


class TestInterpreter(TestCase):

    def setUp(self) -> None:
        self.__command_reader = TestCommandReader()
        self.__interpreter = Interpreter.Interpreter(CommandInterpreters.COMMANDS, self.__command_reader)
        self.__storage = Storage()

    def test_is_octal(self):
        assert not Interpreter.is_octal("")
        assert not Interpreter.is_octal("A")
        assert not Interpreter.is_octal("0A")
        assert not Interpreter.is_octal("8")
        assert not Interpreter.is_octal("!")
        assert Interpreter.is_octal("0")
        assert Interpreter.is_octal("1")
        assert Interpreter.is_octal("2")
        assert Interpreter.is_octal("3")
        assert Interpreter.is_octal("4")
        assert Interpreter.is_octal("5")
        assert Interpreter.is_octal("6")
        assert Interpreter.is_octal("7")
        assert Interpreter.is_octal("76543210")


    def test_halt(self) -> None:
        self.__storage.run()
        assert not self.__interpreter.run_command(self.__storage, "halt", "")
        assert not self.__storage.run_stop_status

    def test_run(self) -> None:
        self.__storage.stop()
        assert not self.__interpreter.run_command(self.__storage, "run", "")
        assert self.__storage.run_stop_status

    def test_jump_switch_1(self) -> None:
        switch_bit = 1
        assert self.__storage.get_jump_switch_mask() == 0
        assert self.__interpreter.jump_set_mask() == 0
        assert self.__interpreter.jump_down_mask() == 0
        assert self.__interpreter.run_command(self.__storage, "jump1", "sideways")
        assert self.__storage.get_jump_switch_mask() == 0
        assert self.__interpreter.jump_set_mask() == 0
        assert self.__interpreter.jump_down_mask() == 0
        assert self.__interpreter.run_command(self.__storage, "jump1", "up")
        assert self.__interpreter.jump_set_mask() == switch_bit
        assert self.__interpreter.jump_down_mask() == 0
        assert self.__storage.get_jump_switch_mask() == switch_bit
        assert self.__interpreter.run_command(self.__storage, "jump1", "center")
        assert self.__storage.get_jump_switch_mask() == 0
        assert self.__interpreter.jump_set_mask() == 0
        assert self.__interpreter.jump_down_mask() == 0
        assert self.__interpreter.run_command(self.__storage, "jump1", "down")
        assert self.__interpreter.jump_set_mask() == switch_bit
        assert self.__interpreter.jump_down_mask() == switch_bit
        assert self.__storage.get_jump_switch_mask() == switch_bit

    def test_unknown_command(self) -> None:
        assert self.__interpreter.run_command(
            self.__storage,"Unknown", "command")

    def test_jump_1_up(self) -> None:
        assert self.__storage.get_jump_switch_mask() == 0
        assert self.__interpreter.run_command(self.__storage, "jump1", "up")
        assert self.__storage.get_jump_switch_mask() == 1
        assert self.__interpreter.run_command(self.__storage, "jump1", "sideways")
        assert self.__storage.get_jump_switch_mask() == 1
        assert self.__interpreter.run_command(self.__storage, "jump1", "center")
        assert self.__storage.get_jump_switch_mask() == 0
        assert self.__interpreter.run_command(self.__storage, "jump1", "down")
        assert self.__storage.get_jump_switch_mask() == 1

    def test_jump_2_up(self) -> None:
        assert self.__storage.get_jump_switch_mask() == 0
        assert self.__interpreter.run_command(self.__storage, "jump2", "up")
        assert self.__storage.get_jump_switch_mask() == 2
        assert self.__interpreter.run_command(self.__storage, "jump2", "sideways")
        assert self.__storage.get_jump_switch_mask() == 2
        assert self.__interpreter.run_command(self.__storage, "jump2", "center")
        assert self.__storage.get_jump_switch_mask() == 0
        assert self.__interpreter.run_command(self.__storage, "jump2", "down")
        assert self.__storage.get_jump_switch_mask() == 2

    def test_jump_3_up(self) -> None:
        assert self.__storage.get_jump_switch_mask() == 0
        assert self.__interpreter.run_command(self.__storage, "jump3", "up")
        assert self.__storage.get_jump_switch_mask() == 4
        assert self.__interpreter.run_command(self.__storage, "jump3", "sideways")
        assert self.__storage.get_jump_switch_mask() == 4
        assert self.__interpreter.run_command(self.__storage, "jump3", "center")
        assert self.__storage.get_jump_switch_mask() == 0
        assert self.__interpreter.run_command(self.__storage, "jump3", "down")
        assert self.__storage.get_jump_switch_mask() == 4

    def test_stop_1_up(self) -> None:
        assert self.__storage.get_stop_switch_mask() == 0
        assert self.__interpreter.run_command(self.__storage, "stop1", "up")
        assert self.__storage.get_stop_switch_mask() == 1
        assert self.__interpreter.run_command(self.__storage, "stop1", "sideways")
        assert self.__storage.get_stop_switch_mask() == 1
        assert self.__interpreter.run_command(self.__storage, "stop1", "center")
        assert self.__storage.get_stop_switch_mask() == 0
        assert self.__interpreter.run_command(self.__storage, "stop1", "down")
        assert self.__storage.get_stop_switch_mask() == 1

    def test_stop_2_up(self) -> None:
        assert self.__storage.get_stop_switch_mask() == 0
        assert self.__interpreter.run_command(self.__storage, "stop2", "up")
        assert self.__storage.get_stop_switch_mask() == 2
        assert self.__interpreter.run_command(self.__storage, "stop2", "sideways")
        assert self.__storage.get_stop_switch_mask() == 2
        assert self.__interpreter.run_command(self.__storage, "stop2", "center")
        assert self.__storage.get_stop_switch_mask() == 0
        assert self.__interpreter.run_command(self.__storage, "stop2", "down")
        assert self.__storage.get_stop_switch_mask() == 2

    def test_stop_3_up(self) -> None:
        assert self.__storage.get_stop_switch_mask() == 0
        assert self.__interpreter.run_command(self.__storage, "stop3", "up")
        assert self.__storage.get_stop_switch_mask() == 4
        assert self.__interpreter.run_command(self.__storage, "stop3", "sideways")
        assert self.__storage.get_stop_switch_mask() == 4
        assert self.__interpreter.run_command(self.__storage, "stop3", "center")
        assert self.__storage.get_stop_switch_mask() == 0
        assert self.__interpreter.run_command(self.__storage, "stop3", "down")
        assert self.__storage.get_stop_switch_mask() == 4

    def test_halt(self) -> None:
        self.__storage.run()
        assert not self.__interpreter.run_command(self.__storage, "halt", "")
        assert not self.__storage.run_stop_status

    def test_run(self) -> None:
        self.__storage.stop()
        assert not self.__interpreter.run_command(self.__storage, "run", "")
        assert self.__storage.run_stop_status

    def test_seta(self) -> None:
        assert self.__storage.a_register == 0
        assert self.__interpreter.run_command(self.__storage, "seta", "1234")
        assert self.__storage.a_register == 0o1234

    def test_setb(self) -> None:
        assert self.__storage.buffer_storage_bank == 0
        assert self.__interpreter.run_command(self.__storage, "setb", "6")
        assert self.__storage.buffer_storage_bank == 0o06

    def test_setd(self) -> None:
        assert self.__storage.direct_storage_bank == 0
        assert self.__interpreter.run_command(self.__storage, "setd", "6")
        assert self.__storage.direct_storage_bank == 0o06

    def test_seti(self) -> None:
        assert self.__storage.indirect_storage_bank == 0
        assert self.__interpreter.run_command(self.__storage, "seti", "6")
        assert self.__storage.indirect_storage_bank == 0o06

    def test_setp(self) -> None:
        assert self.__storage.get_program_counter() == 0
        assert self.__interpreter.run_command(self.__storage, "setp", "4231")
        assert self.__storage.get_program_counter() == 0o4231

    def test_setr(self) -> None:
        assert self.__storage.relative_storage_bank == 0
        assert self.__interpreter.run_command(self.__storage, "setr", "6")
        assert self.__storage.relative_storage_bank == 0o06

    def test_step(self) -> None:
        self.__storage.run()
        assert not self.__interpreter.run_command(self.__storage, "step", "")
        assert not self.__storage.run_stop_status

    def test_read_step_command(self) -> None:
        self.__command_reader.command = ["step"]
        self.__storage.run()
        assert not self.__interpreter.read_and_run_command(self.__storage)
        assert not self.__storage.run_stop_status

    def test_read_run_command(self) -> None:
        self.__command_reader.command = ["run"]
        self.__storage.stop()
        assert not self.__interpreter.read_and_run_command(self.__storage)
        assert self.__storage.run_stop_status

    def test_run_seta_command(self) -> None:
        assert self.__storage.a_register == 0
        self.__command_reader.command = ["seta", "7654"]
        assert self.__interpreter.read_and_run_command(self.__storage)
        assert self.__storage.a_register == 0o7654

    def test_interpreter_exit_on_run(self) -> None:
        self.__command_reader.command = ["run"]
        self.__interpreter.run(self.__storage)
        # Test succeeds if it doesn't hang

    def test_interpreter_exit_on_step(self) -> None:
        self.__command_reader.command = ["step"]
        self.__interpreter.run(self.__storage)
        # Test succeeds if it doesn't hang
