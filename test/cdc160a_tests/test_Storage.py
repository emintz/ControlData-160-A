import unittest
from typing import Final
from unittest import TestCase

from cdc160a.Storage import Storage

READ_AND_WRITE_ADDRESS: Final[int] = 0o1234
INSTRUCTION_ADDRESS: Final[int] = 0o1232
G_ADDRESS: Final[int] = INSTRUCTION_ADDRESS + 1


class TestStorage(TestCase):

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
        self.storage.memory[3, INSTRUCTION_ADDRESS] = 0o0417  # LDN  17
        self.storage.memory[4, INSTRUCTION_ADDRESS] = 0x2100  # LDM 4321
        self.storage.memory[4, G_ADDRESS] = 0o4321
        self.storage.set_program_counter(INSTRUCTION_ADDRESS)

    def tearDown(self) -> None:
        self.storage = None

    def test_a_predicates(self) -> None:
        self.storage.a_register = 0
        assert not self.storage.a_negative()
        assert not self.storage.a_not_zero()
        assert self.storage.a_positive()
        assert self.storage.a_zero()
        self.storage.a_register = 1
        assert not self.storage.a_negative()
        assert self.storage.a_not_zero()
        assert self.storage.a_positive()
        assert not self.storage.a_zero()
        self.storage.a_register = 0o7777
        assert self.storage.a_negative()
        assert self.storage.a_not_zero()
        assert not self.storage.a_positive()
        assert not self.storage.a_zero()
        self.storage.a_register = 0o4000
        assert self.storage.a_negative()
        assert self.storage.a_not_zero()
        assert not self.storage.a_positive()
        assert self.storage.a_not_zero()

    def test_a_to_s_buffer(self) -> None:
        self.storage.a_register = 0o0770
        self.storage.s_register = READ_AND_WRITE_ADDRESS
        self.storage.set_buffer_storage_bank(1)
        self.storage.a_to_s_buffer()
        assert self.storage.z_register == 0o0770
        assert self.storage.read_buffer_bank(READ_AND_WRITE_ADDRESS) == 0o0770

    def test_a_to_s_direct(self) -> None:
        self.storage.a_register = 0o0770
        self.storage.s_register = READ_AND_WRITE_ADDRESS
        self.storage.set_direct_storage_bank(1)
        self.storage.a_to_s_direct()
        assert self.storage.z_register == 0o0770
        assert self.storage.read_direct_bank(READ_AND_WRITE_ADDRESS) == 0o0770

    def test_a_to_s_indirect(self) -> None:
        self.storage.a_register = 0o0770
        self.storage.s_register = READ_AND_WRITE_ADDRESS
        self.storage.set_indirect_storage_bank(1)
        self.storage.a_to_s_indirect()
        assert self.storage.z_register == 0o0770
        assert self.storage.read_indirect_bank(READ_AND_WRITE_ADDRESS) == 0o0770

    def test_a_to_s_relative(self) -> None:
        self.storage.a_register = 0o0770
        self.storage.s_register = READ_AND_WRITE_ADDRESS
        self.storage.set_relative_storage_bank(1)
        self.storage.a_to_s_relative()
        assert self.storage.z_register == 0o0770
        assert self.storage.read_relative_bank(READ_AND_WRITE_ADDRESS) == 0o0770

    def test_add_e_to_a(self) -> None:
        self.storage.a_register = 0o1211
        self.storage.f_e = 0o23
        self.storage.add_e_to_a()
        assert self.storage.a_register == 0o1234
        assert self.storage.z_register == 0o23

    def test_add_s_address_to_a(self) -> None:
        self.storage.a_register = 0o1211
        self.storage.s_register = 0o7777
        self.storage.write_absolute(0, 0o7777, 0o23)
        self.storage.add_s_address_to_a(0)
        assert self.storage.a_register == 0o1234
        assert self.storage.z_register == 0o23

    def test_and_a_with_a(self) -> None:
        self.storage.a_register = 0o4363
        self.storage.f_e = 0o31
        self.storage.and_e_with_a()
        assert self.storage.f_e == 0o31
        assert self.storage.a_register == 0o0021

    def test_and_s_address_with_a(self) -> None:
        self.storage.a_register = 0o5733
        self.storage.s_register = 0o240
        self.storage.write_absolute(5, self.storage.s_register, 0o6365)
        self.storage.and_s_address_with_a(5)
        assert self.storage.z_register == 0o6365
        assert self.storage.a_register == 0o4321

    def test_and_specific_with_a(self) -> None:
        self.storage.a_register = 0o5733
        self.storage.write_absolute(0, 0o7777, 0o6365)
        self.storage.and_specific_with_a()
        assert self.storage.z_register == 0o6365
        assert self.storage.a_register == 0o4321

    def test_complement_a(self) -> None:
        self.storage.a_register = 0o7777
        self.storage.complement_a()
        assert self.storage.a_register == 0o0000
        self.storage.a_register = 0o7070
        self.storage.complement_a()
        assert self.storage.a_register == 0o0707

    def test_decode_instruction(self) -> None:
        self.storage.relative_storage_bank = 3
        self.storage.unpack_instruction()
        assert self.storage.s_register == INSTRUCTION_ADDRESS
        assert self.storage.f_instruction == 0o04
        assert self.storage.f_e == 0o17

    def test_e_to_s(self) -> None:
        self.storage.relative_storage_bank = 3
        self.storage.unpack_instruction()
        self.storage.e_to_z()
        assert self.storage.z_register == 0o17

    def test_g_to_s(self) -> None:
        self.storage.relative_storage_bank = 4
        self.storage.unpack_instruction()
        self.storage.g_to_s()
        assert self.storage.s_register == 0o4321

    def test_g_to_z(self) -> None:
        self.storage.relative_storage_bank = 4
        self.storage.unpack_instruction()
        self.storage.g_to_z()
        assert self.storage.s_register == G_ADDRESS
        assert self.storage.z_register == 0o4321

    def test_next_after_one_instruction_normal(self) -> None:
        self.storage.set_program_counter(0o1234)
        self.storage.next_after_one_word_instruction()
        assert self.storage.get_program_counter() == 0o1234
        self.storage.advance_to_next_instruction()
        assert self.storage.get_program_counter() == 0o1235

    def test_next_after_one_instruction_0o7775(self) -> None:
        self.storage.set_program_counter(0o7775)
        self.storage.next_after_one_word_instruction()
        assert self.storage.get_program_counter() == 0o7775
        self.storage.advance_to_next_instruction()
        assert self.storage.get_program_counter() == 0o7776

    def test_next_after_one_instruction_0o7776(self):
        self.storage.set_program_counter(0o7776)
        self.storage.next_after_one_word_instruction()
        assert self.storage.get_program_counter() == 0o7776
        self.storage.advance_to_next_instruction()
        assert self.storage.get_program_counter() == 0o0000

    def test_next_after_one_instruction_0o7777(self) -> None:
        self.storage.set_program_counter(0o7777)
        self.storage.next_after_one_word_instruction()
        assert self.storage.get_program_counter() == 0o7777
        self.storage.advance_to_next_instruction()
        assert self.storage.get_program_counter() == 0o0001

    def test_next_after_two_instruction_normal(self) -> None:
        self.storage.set_program_counter(0o1234)
        self.storage.next_after_two_word_instruction()
        assert self.storage.get_program_counter() == 0o1234
        self.storage.advance_to_next_instruction()
        assert self.storage.get_program_counter() == 0o1236

    def test_next_after_two_instruction_0o7774(self) -> None:
        self.storage.set_program_counter(0o7774)
        self.storage.next_after_two_word_instruction()
        assert self.storage.get_program_counter() == 0o7774
        self.storage.advance_to_next_instruction()
        assert self.storage.get_program_counter() == 0o7776

    def test_next_after_two_instruction_0o7775(self) -> None:
        self.storage.set_program_counter(0o7775)
        self.storage.next_after_two_word_instruction()
        assert self.storage.get_program_counter() == 0o7775
        self.storage.advance_to_next_instruction()
        assert self.storage.get_program_counter() == 0o0000

    def test_next_after_two_instruction_0o7776(self) -> None:
        self.storage.set_program_counter(0o7776)
        self.storage.next_after_two_word_instruction()
        assert self.storage.get_program_counter() == 0o7776
        self.storage.advance_to_next_instruction()
        assert self.storage.get_program_counter() == 0o0001


    def test_relative_backward_address_to_s(self) -> None:
        self.storage.relative_storage_bank = 4
        # LDB 15
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o2315)
        self.storage.unpack_instruction()
        self.storage.relative_backward_to_s()
        assert self.storage.s_register == INSTRUCTION_ADDRESS - 0o15

    def test_relative_forward_address_to_s(self) -> None:
        self.storage.relative_storage_bank = 4
        # LDF 51
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o2251)
        self.storage.unpack_instruction()
        self.storage.relative_forward_to_s()
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 0o51

    def test_run(self) -> None:
        self.storage.run_stop_status = False
        self.storage.run()
        assert self.storage.run_stop_status

    def test_s_to_a(self) -> None:
        self.storage.s_register = 0o7007
        self.storage.s_to_p()
        assert self.storage.p_register == 0o7007

    def test_s_to_next_address(self) -> None:
        assert self.storage.next_address() == 0
        self.storage.s_register = 0o321
        self.storage.s_to_next_address()
        assert self.storage.next_address() == 0o321

    def test_set_buffer_storage_bank(self) -> None:
        assert self.storage.buffer_storage_bank == 0
        assert self.storage.read_buffer_bank(READ_AND_WRITE_ADDRESS) == 0o10
        self.storage.write_buffer_bank(READ_AND_WRITE_ADDRESS, 0o20)
        assert self.storage.read_buffer_bank(READ_AND_WRITE_ADDRESS) == 0o20
        self.storage.set_buffer_storage_bank(3)
        assert self.storage.buffer_storage_bank == 3
        assert self.storage.read_buffer_bank(READ_AND_WRITE_ADDRESS) == 0o13
        self.storage.write_buffer_bank(READ_AND_WRITE_ADDRESS, 0o23)
        assert self.storage.read_buffer_bank(READ_AND_WRITE_ADDRESS) == 0o23
        self.storage.set_buffer_storage_bank(0o15)
        assert self.storage.buffer_storage_bank == 5
        assert self.storage.read_buffer_bank(READ_AND_WRITE_ADDRESS) == 0o15
        self.storage.write_buffer_bank(READ_AND_WRITE_ADDRESS, 0o25)
        assert self.storage.read_buffer_bank(READ_AND_WRITE_ADDRESS) == 0o25

    def test_set_direct_storage_bank(self) -> None:
        assert self.storage.direct_storage_bank == 0
        assert self.storage.read_direct_bank(READ_AND_WRITE_ADDRESS) == 0o10
        self.storage.write_direct_bank(READ_AND_WRITE_ADDRESS, 0o20)
        assert self.storage.read_indirect_bank(READ_AND_WRITE_ADDRESS) == 0o20
        self.storage.set_direct_storage_bank(3)
        assert self.storage.direct_storage_bank == 3
        assert self.storage.read_direct_bank(READ_AND_WRITE_ADDRESS) == 0o13
        self.storage.write_indirect_bank(READ_AND_WRITE_ADDRESS, 0o23)
        assert self.storage.read_buffer_bank(READ_AND_WRITE_ADDRESS) == 0o23
        self.storage.set_direct_storage_bank(0o15)
        assert self.storage.direct_storage_bank == 5
        assert self.storage.read_direct_bank(READ_AND_WRITE_ADDRESS) == 0o15
        self.storage.write_direct_bank(READ_AND_WRITE_ADDRESS, 0o25)
        assert self.storage.read_direct_bank(READ_AND_WRITE_ADDRESS) == 0o25

    def test_set_indirect_storage_bank(self) -> None:
        assert self.storage.indirect_storage_bank == 0
        assert self.storage.read_indirect_bank(READ_AND_WRITE_ADDRESS) == 0o10
        self.storage.write_indirect_bank(READ_AND_WRITE_ADDRESS, 0o20)
        assert self.storage.read_indirect_bank(READ_AND_WRITE_ADDRESS) == 0o20
        self.storage.set_indirect_storage_bank(3)
        assert self.storage.indirect_storage_bank == 3
        assert self.storage.read_indirect_bank(READ_AND_WRITE_ADDRESS) == 0o13
        self.storage.write_indirect_bank(READ_AND_WRITE_ADDRESS, 0o23)
        assert self.storage.read_indirect_bank(READ_AND_WRITE_ADDRESS) == 0o23
        self.storage.set_indirect_storage_bank(0o15)
        assert self.storage.indirect_storage_bank == 5
        assert self.storage.read_indirect_bank(READ_AND_WRITE_ADDRESS) == 0o15
        self.storage.write_indirect_bank(READ_AND_WRITE_ADDRESS, 0o25)
        assert self.storage.read_indirect_bank(READ_AND_WRITE_ADDRESS) == 0o25

    def test_set_next_instruction_address(self) -> None:
        self.storage.set_program_counter(0o1234)
        self.storage.set_next_instruction_address(0o4321)
        assert self.storage.get_program_counter() == 0o1234
        self.storage.advance_to_next_instruction()
        assert self.storage.get_program_counter() == 0o4321

    def test_set_program_counter(self) -> None:
        self.storage.set_program_counter(0o1423)
        assert self.storage.get_program_counter() == 0o1423

    def test_set_relative_storage_bank(self) -> None:
        assert self.storage.relative_storage_bank == 0
        assert self.storage.read_relative_bank(READ_AND_WRITE_ADDRESS) == 0o10
        self.storage.write_relative_bank(READ_AND_WRITE_ADDRESS, 0o20)
        assert self.storage.read_relative_bank(READ_AND_WRITE_ADDRESS) == 0o20
        self.storage.set_relative_storage_bank(3)
        assert self.storage.relative_storage_bank == 3
        assert self.storage.read_relative_bank(READ_AND_WRITE_ADDRESS) == 0o13
        self.storage.write_relative_bank(READ_AND_WRITE_ADDRESS, 0o23)
        assert self.storage.read_relative_bank(READ_AND_WRITE_ADDRESS) == 0o23
        self.storage.set_relative_storage_bank(0o15)
        assert self.storage.relative_storage_bank == 5
        assert self.storage.read_relative_bank(READ_AND_WRITE_ADDRESS) == 0o15
        self.storage.write_relative_bank(READ_AND_WRITE_ADDRESS, 0o25)
        assert self.storage.read_relative_bank(READ_AND_WRITE_ADDRESS) == 0o25

    def test_stop(self) -> None:
        self.storage.run_stop_status = True
        self.storage.stop()
        assert not self.storage.run_stop_status

    def test_subtract_e_from_a(self) -> None:
        self.storage.a_register = 0o1255
        self.storage.f_e = 0o21
        self.storage.subtract_e_from_a()
        assert self.storage.z_register == 0o21
        assert self.storage.a_register == 0o1234

    def test_subtract_s_absolute_from_a_neg_neg_neg(self) -> None:
        self.storage.a_register = 0o7000
        self.storage.write_absolute(3, 0o40, 0o1000)
        self.storage.s_register = 0o40
        self.storage.subtract_s_address_from_a(3)
        assert self.storage.z_register == 0o1000
        assert self.storage.a_register == 0o6000

    def test_subtract_s_absolute_from_a_neg_neg_pos(self) -> None:
        self.storage.a_register = 0o7776
        self.storage.write_absolute(3, 0o40, 0o7775)
        self.storage.s_register = 0o40
        self.storage.subtract_s_address_from_a(3)
        assert self.storage.z_register == 0o7775
        assert self.storage.a_register == 0o0001

    def test_subtract_s_absolute_from_a_pos_mzro_pos(self) -> None:
        self.storage.a_register = 0o1234
        self.storage.write_absolute(3, 0o40, 0o7777)
        self.storage.s_register = 0o40
        self.storage.subtract_s_address_from_a(3)
        assert self.storage.z_register == 0o7777
        assert self.storage.a_register == 0o1234

    def test_subtract_s_absolute_pos_pos_neg(self) -> None:
        self.storage.a_register = 0o300
        self.storage.write_absolute(3, 0o40, 0o0700)
        self.storage.s_register = 0o40
        self.storage.subtract_s_address_from_a(3)
        assert self.storage.z_register == 0o700
        assert self.storage.a_register == 0o7377

    def test_subtract_s_absolute_from_a_pos_pos_pos(self) -> None:
        self.storage.a_register = 0o2234
        self.storage.write_absolute(3, 0o40, 0o1000)
        self.storage.s_register = 0o40
        self.storage.subtract_s_address_from_a(3)
        assert self.storage.z_register == 0o1000
        assert self.storage.a_register == 0o1234

    def test_subtract_s_absolute_from_a_pos_zero_pos(self) -> None:
        self.storage.a_register = 0o1234
        self.storage.write_absolute(3, 0o40, 0)
        self.storage.s_register = 0o40
        self.storage.subtract_s_address_from_a(3)
        assert self.storage.z_register == 0
        assert self.storage.a_register == 0o1234

    def test_subtract_specific_from_a(self) -> None:
        self.storage.a_register = 0o2234
        self.storage.write_absolute(0, 0o7777, 0o1000)
        self.storage.subtract_specific_from_a()
        assert self.storage.z_register == 0o1000
        assert self.storage.a_register == 0o1234

    def test_read_absolute(self) -> None:
        assert self.storage.read_absolute(0, 0o1000) == 0
        self.storage.memory[0, 0o1000] = 0o3777
        assert self.storage.read_absolute(0, 0o1000) == 0o3777

    def test_read_write_specific(self) -> None:
        assert self.storage.read_specific() == 0o77
        self.storage.write_specific(0o777)
        assert self.storage.read_specific() == 0o777

    def test_write_absolute(self) -> None:
        assert self.storage.memory[0, 0o1000] == 0
        self.storage.write_absolute(0, 0o1000, 0o3777)
        assert self.storage.memory[0, 0o1000] == 0o3777

if __name__ == "__main__":
    unittest.main()
