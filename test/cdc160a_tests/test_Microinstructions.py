import unittest
from unittest import TestCase

from cdc160a import Microinstructions
from cdc160a.Storage import Storage
from typing import Final

from cdc160a_tests.test_Instructions import AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

READ_AND_WRITE_ADDRESS: Final[int] = 0o1234
INSTRUCTION_ADDRESS: Final[int] = 0o1232
G_ADDRESS: Final[int] = INSTRUCTION_ADDRESS + 1
JUMP_ADDRESS: Final[int] = 0o2000

class Test(TestCase):

    def setUp(self) -> None:
        self.storage = Storage()
        self.storage.memory[0, READ_AND_WRITE_ADDRESS] = 0o10
        self.storage.memory[1, READ_AND_WRITE_ADDRESS] = 0o11
        self.storage.memory[2, READ_AND_WRITE_ADDRESS] = 0o12
        self.storage.memory[3, READ_AND_WRITE_ADDRESS] = 0o13
        self.storage.memory[4, READ_AND_WRITE_ADDRESS] = 0o14
        self.storage.memory[5, READ_AND_WRITE_ADDRESS] = 0o15
        self.storage.memory[6, READ_AND_WRITE_ADDRESS] = 0o16
        self.storage.memory[7, READ_AND_WRITE_ADDRESS] = 0o17
        self.storage.memory[0, 0o7777] = 0o77
        self.storage.p_register = INSTRUCTION_ADDRESS
        self.storage.s_register = INSTRUCTION_ADDRESS
        self.storage.relative_storage_bank = 3
        self.storage.run()

    def tearDown(self) -> None:
        self.storage = None

    def test_a_to_buffer(self) -> None:
        self.storage.set_buffer_storage_bank(1)
        self.storage.a_register = 0o0330
        self.storage.s_register = READ_AND_WRITE_ADDRESS
        Microinstructions.a_to_buffer(self.storage)
        assert self.storage.z_register == 0o0330
        assert self.storage.read_buffer_bank(READ_AND_WRITE_ADDRESS) == 0o0330

    def test_a_to_direct_buffer(self) -> None:
        self.storage.set_direct_storage_bank(1)
        self.storage.a_register = 0o0330
        self.storage.s_register = READ_AND_WRITE_ADDRESS
        Microinstructions.a_to_direct(self.storage)
        assert self.storage.z_register == 0o0330
        assert self.storage.read_direct_bank(READ_AND_WRITE_ADDRESS) == 0o0330

    def test_a_to_indirect_buffer(self) -> None:
        self.storage.set_indirect_storage_bank(1)
        self.storage.a_register = 0o0330
        self.storage.s_register = READ_AND_WRITE_ADDRESS
        Microinstructions.a_to_indirect(self.storage)
        assert self.storage.z_register == 0o0330
        assert self.storage.read_indirect_bank(READ_AND_WRITE_ADDRESS) == 0o0330

    def test_a_to_relative_buffer(self) -> None:
        self.storage.set_relative_storage_bank(1)
        self.storage.a_register = 0o0330
        self.storage.s_register = READ_AND_WRITE_ADDRESS
        Microinstructions.a_to_relative(self.storage)
        assert self.storage.z_register == 0o0330
        assert self.storage.read_relative_bank(READ_AND_WRITE_ADDRESS) == 0o0330

    def test_complement_a(self) -> None:
        self.storage.a_register = 0o7070
        self.storage.complement_a()
        assert self.storage.a_register == 0o0707

    def test_e_complement_to_a(self) -> None:
        # LDN 33
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0433)
        self.storage.unpack_instruction()
        Microinstructions.e_complement_to_a(self.storage)
        assert self.storage.run_stop_status
        assert self.storage.z_register == 0o33
        assert self.storage.a_register == 0o7744

    def test_e_to_a(self) -> None:
        # LDN 33
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0433)
        self.storage.unpack_instruction()
        Microinstructions.e_to_a(self.storage)
        assert self.storage.run_stop_status
        assert self.storage.z_register == 0o33
        assert self.storage.a_register == 0o33

    def test_s_to_a(self) -> None:
        # LDN 37
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0437)
        self.storage.unpack_instruction()
        Microinstructions.e_to_a(self.storage)
        assert self.storage.run_stop_status
        assert self.storage.z_register == 0o37
        assert self.storage.a_register == 0o37

    def test_direct_complement_to_a(self) -> None:
        self.storage.write_direct_bank(READ_AND_WRITE_ADDRESS, 0o7654)
        self.storage.s_register = READ_AND_WRITE_ADDRESS
        Microinstructions.s_direct_complement_to_a(self.storage)
        assert self.storage.run_stop_status
        assert self.storage.z_register == 0o7654
        assert self.storage.a_register == 0o7654 ^ 0o7777

    def test_s_direct_to_a(self) -> None:
        self.storage.write_direct_bank(READ_AND_WRITE_ADDRESS, 0o7654)
        self.storage.s_register = READ_AND_WRITE_ADDRESS
        Microinstructions.s_direct_to_a(self.storage)
        assert self.storage.run_stop_status
        assert self.storage.z_register == 0o7654
        assert self.storage.a_register == 0o7654

    def test_indirect_complement_to_a(self) -> None:
        self.storage.write_indirect_bank(READ_AND_WRITE_ADDRESS, 0o7654)
        self.storage.s_register = READ_AND_WRITE_ADDRESS
        Microinstructions.s_indirect_complement_to_a(self.storage)
        assert self.storage.run_stop_status
        assert self.storage.z_register == 0o7654
        assert self.storage.a_register == 0o7654 ^ 0o7777

    def test_jump_if_a_negative(self) -> None:
        self.__prepare_for_jump()
        self.storage.a_register = 0
        Microinstructions.jump_if_a_negative(self.storage)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        self.__prepare_for_jump()
        self.storage.a_register = 0o0001
        Microinstructions.jump_if_a_negative(self.storage)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        self.__prepare_for_jump()
        self.storage.a_register = 0o7777
        Microinstructions.jump_if_a_negative(self.storage)
        assert self.storage.next_address() == JUMP_ADDRESS
        self.__prepare_for_jump()
        self.storage.a_register = 0o7776
        Microinstructions.jump_if_a_negative(self.storage)
        assert self.storage.next_address() == JUMP_ADDRESS

    def test_jump_if_a_nonzero(self) -> None:
        self.__prepare_for_jump()
        self.storage.a_register = 0
        Microinstructions.jump_if_a_nonzero(self.storage)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        self.__prepare_for_jump()
        self.storage.a_register = 0o0001
        Microinstructions.jump_if_a_nonzero(self.storage)
        assert self.storage.next_address() == JUMP_ADDRESS
        self.__prepare_for_jump()
        self.storage.a_register = 0o7777
        Microinstructions.jump_if_a_nonzero(self.storage)
        assert self.storage.next_address() == JUMP_ADDRESS
        self.__prepare_for_jump()
        self.storage.nex = 0o7776
        Microinstructions.jump_if_a_nonzero(self.storage)
        assert self.storage.next_address() == JUMP_ADDRESS

    def test_jump_if_a_positive(self) -> None:
        self.__prepare_for_jump()
        self.storage.a_register = 0
        Microinstructions.jump_if_a_positive(self.storage)
        assert self.storage.next_address() == JUMP_ADDRESS
        self.__prepare_for_jump()
        self.storage.a_register = 0o0001
        Microinstructions.jump_if_a_positive(self.storage)
        assert self.storage.next_address() == JUMP_ADDRESS
        self.__prepare_for_jump()
        self.storage.a_register = 0o7777
        Microinstructions.jump_if_a_positive(self.storage)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        self.__prepare_for_jump()
        self.storage.a_register = 0o7776
        Microinstructions.jump_if_a_positive(self.storage)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_jump_if_a_zero(self) -> None:
        self.__prepare_for_jump()
        self.storage.a_register = 0
        Microinstructions.jump_if_a_zero(self.storage)
        assert self.storage.next_address() == JUMP_ADDRESS
        self.__prepare_for_jump()
        self.storage.a_register = 0o0001
        Microinstructions.jump_if_a_zero(self.storage)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        self.__prepare_for_jump()
        self.storage.a_register = 0o7777
        Microinstructions.jump_if_a_zero(self.storage)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        self.__prepare_for_jump()
        self.storage.a_register = 0o7776
        Microinstructions.jump_if_a_zero(self.storage)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_s_indirect_to_a(self) -> None:
        self.storage.write_indirect_bank(READ_AND_WRITE_ADDRESS, 0o7654)
        self.storage.s_register = READ_AND_WRITE_ADDRESS
        Microinstructions.s_indirect_to_a(self.storage)
        assert self.storage.run_stop_status
        assert self.storage.z_register == 0o7654
        assert self.storage.a_register == 0o7654

    def test_s_relative_complement_to_a(self) -> None:
        self.storage.s_register = READ_AND_WRITE_ADDRESS
        Microinstructions.s_relative_complement_to_a(self.storage)
        assert self.storage.run_stop_status
        assert self.storage.z_register == 0o13
        assert self.storage.a_register == 0o7764

    def test_rotate_a_left_one(self) -> None:
        self.storage.a_register = 0o0001
        Microinstructions.rotate_a_left_one(self.storage)
        assert self.storage.a_register == 0x0002
        self.storage.a_register = 0o4001
        Microinstructions.rotate_a_left_one(self.storage)
        assert self.storage.a_register == 0x0003

    def test_rotate_a_left_two(self) -> None:
        self.storage.a_register = 0o6000
        Microinstructions.rotate_a_left_two(self.storage)
        assert self.storage.a_register == 0o0003
        self.storage.a_register = 0o4001
        Microinstructions.rotate_a_left_two(self.storage)
        assert self.storage.a_register == 0o0006

    def test_rotate_a_left_three(self) -> None:
        self.storage.a_register = 0o7000
        Microinstructions.rotate_a_left_three(self.storage)
        assert self.storage.a_register == 0o0007

    def test_rotate_a_left_six(self) -> None:
        self.storage.z_register = 0o2143
        self.storage.z_to_a()
        Microinstructions.rotate_a_left_six(self.storage)
        assert self.storage.z_register == 0o2143
        assert self.storage.a_register == 0o4321

    def test_shift_a_right_one(self) -> None:
        self.storage.a_register = 0o4000
        Microinstructions.shift_a_right_one(self.storage)
        assert self.storage.a_register == 0o6000
        self.storage.a_register = 0o6000
        Microinstructions.shift_a_right_one(self.storage)
        assert self.storage.a_register == 0o7000
        self.storage.a_register = 0o2000
        Microinstructions.shift_a_right_one(self.storage)
        assert self.storage.a_register == 0o1000
        self.storage.a_register = 0o2002
        Microinstructions.shift_a_right_one(self.storage)
        assert self.storage.a_register == 0o1001

    def test_shift_a_right_two(self) -> None:
        self.storage.a_register = 0o4000
        Microinstructions.shift_a_right_two(self.storage)
        assert self.storage.a_register == 0o7000
        self.storage.a_register = 0x2000
        Microinstructions.shift_a_right_one(self.storage)
        assert self.storage.a_register -- 0o0400
        self.storage.a_register = 0o0014
        Microinstructions.shift_a_right_two(self.storage)
        assert self.storage.a_register == 0o0003
        self.storage.a_register = 0o4014
        Microinstructions.shift_a_right_two(self.storage)
        assert self.storage.a_register == 0o7003

    def test_s_relative_to_a(self) -> None:
        self.storage.s_register = READ_AND_WRITE_ADDRESS
        Microinstructions.s_relative_to_a(self.storage)
        assert self.storage.run_stop_status
        assert self.storage.z_register == 0o13
        assert self.storage.a_register == 0o13

    def test_specific_complement_to_a(self) -> None:
        Microinstructions.specific_complement_to_a(self.storage)
        assert self.storage.run_stop_status
        assert self.storage.z_register == 0o77
        assert self.storage.a_register == 0o7700

    def test_specific_to_a(self) -> None:
        Microinstructions.specific_to_a(self.storage)
        assert self.storage.run_stop_status
        assert self.storage.z_register == 0o77
        assert self.storage.a_register == 0o77

    def __prepare_for_jump(self) -> None:
        self.storage.p_register = INSTRUCTION_ADDRESS
        self.storage.s_register = JUMP_ADDRESS

if __name__ == "__main__":
    unittest.main()
