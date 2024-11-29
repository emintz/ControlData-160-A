import unittest
from typing import Final
from unittest import TestCase

from numpy.compat import open_latin1

from Storage import MCS_MODE_BFR
from Storage import MCS_MODE_DIR
from Storage import MCS_MODE_IND
from Storage import MCS_MODE_REL
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

    def test_a_times_10(self) -> None:
        self.storage.a_register = 1
        self.storage.a_times_10()
        assert self.storage.a_register == 10

    def test_a_times_100(self) -> None:
        self.storage.a_register = 1
        self.storage.a_times_100()
        assert self.storage.a_register == 100

    def test_a_to_absolute(self) -> None:
        self.storage.a_register = 0o1234
        self.storage.a_to_absolute(1, 0o100)
        assert self.storage.z_register == 0o1234
        assert self.storage.memory[1, 0o100] == 0o1234

    def test_a_to_buffer(self) -> None:
        self.storage.a_register = 0o1234
        self.storage.buffer_storage_bank = 1
        self.storage.s_register = 0o100
        self.storage.a_to_s_buffer()
        assert self.storage.z_register == 0o1234
        assert self.storage.memory[1, 0o100] == 0o1234
        assert self.storage.storage_cycle == MCS_MODE_BFR

    def test_a_to_s_direct(self) -> None:
        self.storage.a_register = 0o1234
        self.storage.direct_storage_bank = 1
        self.storage.s_register = 0o100
        self.storage.a_to_s_direct()
        assert self.storage.z_register == 0o1234
        assert self.storage.memory[1, 0o100] == 0o1234
        assert self.storage.storage_cycle == MCS_MODE_DIR

    def test_a_to_s_indirect(self) -> None:
        self.storage.a_register = 0o1234
        self.storage.indirect_storage_bank = 1
        self.storage.s_register = 0o100
        self.storage.a_to_s_indirect()
        assert self.storage.z_register == 0o1234
        assert self.storage.memory[1, 0o100] == 0o1234
        assert self.storage.storage_cycle == MCS_MODE_IND

    def test_a_to_s_relative(self) -> None:
        self.storage.a_register = 0o1234
        self.storage.relative_storage_bank = 1
        self.storage.s_register = 0o100
        self.storage.a_to_s_relative()
        assert self.storage.z_register == 0o1234
        assert self.storage.memory[1, 0o100] == 0o1234
        assert self.storage.storage_cycle == MCS_MODE_REL

    def test_a_to_s_buffer(self) -> None:
        self.storage.a_register = 0o0770
        self.storage.s_register = READ_AND_WRITE_ADDRESS
        self.storage.set_buffer_storage_bank(1)
        self.storage.a_to_s_buffer()
        assert self.storage.z_register == 0o0770
        assert self.storage.read_buffer_bank(READ_AND_WRITE_ADDRESS) == 0o0770

    def test_a_to_direct(self) -> None:
        self.storage.a_register = 0o0770
        self.storage.s_register = READ_AND_WRITE_ADDRESS
        self.storage.set_direct_storage_bank(1)
        self.storage.a_to_s_direct()
        assert self.storage.z_register == 0o0770
        assert self.storage.read_direct_bank(READ_AND_WRITE_ADDRESS) == 0o0770

    def test_a_to_indirect(self) -> None:
        self.storage.a_register = 0o0770
        self.storage.s_register = READ_AND_WRITE_ADDRESS
        self.storage.set_indirect_storage_bank(1)
        self.storage.a_to_s_indirect()
        assert self.storage.z_register == 0o0770
        assert self.storage.read_indirect_bank(READ_AND_WRITE_ADDRESS) == 0o0770

    def test_a_to_relative(self) -> None:
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

    def test_add_to_a(self) -> None:
        self.storage.a_register = 0o1200
        self.storage.add_to_a(0o34)
        assert not self.storage.err_status
        assert self.storage.a_register == 0o1234

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

    def test_bank_controls_to_a(self) -> None:
        self.storage.set_buffer_storage_bank(0o1)
        self.storage.set_direct_storage_bank(0o2)
        self.storage.set_indirect_storage_bank(0o3)
        self.storage.set_relative_storage_bank(0o4)
        self.storage.bank_controls_to_a()
        assert self.storage.a_register == 0o1234

    def test_complement_a(self) -> None:
        self.storage.a_register = 0o7777
        self.storage.complement_a()
        assert self.storage.a_register == 0o0000
        self.storage.a_register = 0o7070
        self.storage.complement_a()
        assert self.storage.a_register == 0o0707

    def test_unpack_instruction(self) -> None:
        self.storage.relative_storage_bank = 3
        self.storage.unpack_instruction()
        assert self.storage.s_register == INSTRUCTION_ADDRESS
        assert self.storage.f_instruction == 0o04
        assert self.storage.f_e == 0o17

    def test_e_direct_to_s(self) -> None:
        self.storage.set_direct_storage_bank(1)
        self.storage.set_indirect_storage_bank(2)
        self.storage.set_relative_storage_bank(3)
        self.storage.f_e = 0o23
        self.storage.write_direct_bank(0o23, 0o2000)
        self.storage.e_direct_to_s()
        assert self.storage.s_register == 0o2000

    def test_e_to_s(self) -> None:
        self.storage.relative_storage_bank = 3
        self.storage.unpack_instruction()
        self.storage.e_to_z()
        assert self.storage.z_register == 0o17
        assert self.storage.storage_cycle == MCS_MODE_REL

    def test_g_to_next_address(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o7710)
        self.storage.write_relative_bank(G_ADDRESS, 0o1000)
        self.storage.unpack_instruction()
        self.storage.g_to_next_address()
        assert self.storage.get_next_execution_address() == 0o1000
        assert self.storage.z_register == 0o1000

    def test_g_to_s(self) -> None:
        self.storage.relative_storage_bank = 4
        self.storage.unpack_instruction()
        self.storage.g_to_s()
        assert self.storage.s_register == 0o4321
        assert self.storage.z_register == 0o4321

    def test_half_write_to_s_indirect(self) -> None:
        self.storage.relative_storage_bank = 0o03
        self.storage.indirect_storage_bank = 0o01
        self.storage.a_register = 0o7621
        self.storage.s_register = 0o200
        self.storage.write_indirect_bank(self.storage.s_register, 0o4367)
        self.storage.half_write_to_s_indirect()
        assert self.storage.read_indirect_bank(0o200) == 0o4321

    def test_jump_switches(self) -> None:
        self.storage.set_jump_switch_mask(0)
        assert self.storage.and_with_jump_switches(0o7) == 0o0
        self.storage.set_jump_switch_mask(0o1)
        assert self.storage.and_with_jump_switches(0o7) == 0o1
        self.storage.set_jump_switch_mask(0o6)
        assert self.storage.and_with_jump_switches(0o4) == 0o04

    def test_stop_switches(self) -> None:
        self.storage.set_stop_switch_mask(0)
        assert self.storage.and_with_stop_switches(0o7) == 0o0
        self.storage.set_stop_switch_mask(0o1)
        assert self.storage.and_with_stop_switches(0o7) == 0o1
        self.storage.set_stop_switch_mask(0o6)
        assert self.storage.and_with_stop_switches(0o4) == 0o04

    def test_load_a(self) -> None:
        self.storage.write_absolute(1, 0o100, 0o1234)
        self.storage.load_a(1, 0o100)
        assert self.storage.a_register == 0o1234
        assert self.storage.z_register == 0o1234

    def test_load_a_from_s(self) -> None:
        self.storage.write_absolute(1, 0o100, 0o1234)
        self.storage.s_register = 0o100
        self.storage.load_a_from_s(1)
        assert self.storage.a_register == 0o1234
        assert self.storage.z_register == 0o1234

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

    def test_p_to_a(self) -> None:
        self.storage.p_register = 0o3241
        self.storage.p_to_a()
        assert self.storage.p_register == 0o3241

    def test_p_to_s_direct(self) -> None:
        self.storage.p_register = 0o1324
        self.storage.f_e = 0o54
        self.storage.f_instruction = 0o01
        self.storage.p_to_s_direct()
        assert self.storage.read_direct_bank(0o54) == 0o1324

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

    def test_s_absolute_to_a(self) -> None:
        self.storage.memory[1, 0o100] = 0o1234
        self.storage.s_register = 0o100
        self.storage.s_absolute_to_a(1)
        assert self.storage.a_register == 0o1234
        assert self.storage.z_register == 0o1234

    def test_absolute_to_z(self) -> None:
        self.storage.memory[1, 0o100] = 0o1234
        self.storage.s_register = 0o100
        self.storage.s_absolute_to_z(1)
        assert self.storage.a_register == 0
        assert self.storage.z_register == 0o1234

    def test_direct_to_a(self) -> None:
        self.storage.direct_storage_bank = 1
        self.storage.s_register = 0o40
        self.storage.write_direct_bank(0o40, 0o1234)
        self.storage.s_direct_to_a()
        assert self.storage.a_register == 0o1234
        assert self.storage.z_register == 0o1234
        assert self.storage.storage_cycle == MCS_MODE_DIR

    def test_direct_to_z(self) -> None:
        self.storage.direct_storage_bank = 1
        self.storage.s_register = 0o40
        self.storage.write_direct_bank(0o40, 0o1234)
        self.storage.s_direct_to_z()
        assert self.storage.a_register == 0
        assert self.storage.z_register == 0o1234
        assert self.storage.storage_cycle == MCS_MODE_DIR

    def test_indirect_to_a(self) -> None:
        self.storage.indirect_storage_bank = 1
        self.storage.s_register = 0o40
        self.storage.write_indirect_bank(0o40, 0o1234)
        self.storage.s_indirect_to_a()
        assert self.storage.a_register == 0o1234
        assert self.storage.z_register == 0o1234
        assert self.storage.storage_cycle == MCS_MODE_IND

    def test_indirect_to_z(self) -> None:
        self.storage.indirect_storage_bank = 1
        self.storage.s_register = 0o40
        self.storage.write_indirect_bank(0o40, 0o1234)
        self.storage.s_indirect_to_z()
        assert self.storage.a_register == 0
        assert self.storage.z_register == 0o1234
        assert self.storage.storage_cycle == MCS_MODE_IND

    def test_relative_indirect_to_next_address(self) -> None:
        self.storage.s_register = 0o200
        self.storage.write_relative_bank(0o200, 0o300)
        self.storage.write_relative_bank(0o300, 0o4132)
        self.storage.s_relative_indirect_to_next_address()
        assert self.storage.get_next_execution_address() == 0o4132

    def test_relative_to_a(self) -> None:
        self.storage.relative_storage_bank = 1
        self.storage.s_register = 0o40
        self.storage.write_relative_bank(0o40, 0o1234)
        self.storage.s_relative_to_a()
        assert self.storage.a_register == 0o1234
        assert self.storage.z_register == 0o1234
        assert self.storage.storage_cycle == MCS_MODE_REL

    def test_relative_to_z(self) -> None:
        self.storage.relative_storage_bank = 1
        self.storage.s_register = 0o40
        self.storage.write_relative_bank(0o40, 0o1234)
        self.storage.s_relative_to_z()
        assert self.storage.a_register == 0
        assert self.storage.z_register == 0o1234
        assert self.storage.storage_cycle == MCS_MODE_REL

    def test_s_to_p(self) -> None:
        self.storage.s_register = 0o7007
        self.storage.s_to_p()
        assert self.storage.p_register == 0o7007

    def test_s_to_next_address(self) -> None:
        assert self.storage.next_address() == 0
        self.storage.s_register = 0o321
        self.storage.s_to_next_address()
        assert self.storage.next_address() == 0o321

    def test_set_buffer_bank_from_e(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0146)
        self.storage.unpack_instruction()
        self.storage.set_buffer_bank_from_e()
        assert self.storage.buffer_storage_bank == 0o06

    def test_set_direct_bank_from_e(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0046)
        self.storage.unpack_instruction()
        self.storage.set_direct_bank_from_e()
        assert self.storage.direct_storage_bank == 0o06

    def test_set_indirect_bank_from_e(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0026)
        self.storage.unpack_instruction()
        self.storage.set_indirect_bank_from_e()
        assert self.storage.indirect_storage_bank == 0o06

    def test_set_relative_bank_from_e_and_jump(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0016)
        self.storage.unpack_instruction()
        self.storage.a_register = 0o200
        self.storage.set_relative_bank_from_e_and_jump()
        assert self.storage.relative_storage_bank == 0o06
        self.storage.advance_to_next_instruction()
        assert self.storage.get_program_counter() == 0o200

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

    def test_specific_to_a(self) -> None:
        self.storage.write_absolute(0, 0o7777, 0o1234)
        self.storage.specific_to_a()
        assert self.storage.z_register == 0o1234
        assert self.storage.a_register == 0o1234

    def test_specific_to_z(self) -> None:
        self.storage.write_absolute(0, 0o7777, 0o1234)
        self.storage.specific_to_z()
        assert self.storage.z_register == 0o1234
        assert self.storage.a_register == 0

    def test_stop(self) -> None:
        self.storage.run_stop_status = True
        self.storage.stop()
        assert not self.storage.run_stop_status

    def test_store_a(self) -> None:
        self.storage.run_stop_status = True
        self.storage.s_register = 0o777
        self.storage.a_register = 0o123
        assert self.storage.memory[3, 0o777] == 0
        self.storage.store_a(3)
        assert self.storage.memory[3, 0o777] == 0o123
        assert self.storage.run_stop_status
        assert self.storage.s_register == 0o777
        assert self.storage.s_register == 0o777

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

    def test_value_to_s_address_relative(self) -> None:
        self.storage.s_register = 0o300
        self.storage.value_to_s_address_relative(0o1234)
        assert self.storage.read_relative_bank(0o300) == 0o1234

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

    def test_xor_with_z(self) -> None:
        self.storage.z_register = 0o14
        self.storage.a_register = 0o12
        self.storage.xor_a_with_z()
        assert self.storage.z_register == 0o14
        assert self.storage.a_register == 0o06

    def test_z_to_a(self) -> None:
        self.storage.z_register = 0o4321
        self.storage.z_to_a()
        assert self.storage.a_register == 0o4321

    def test_z_to_p(self) -> None:
        self.storage.z_register = 0o4321
        self.storage.z_to_p()
        assert self.storage.p_register == 0o4321

    def test_z_to_s_indirect(self) -> None:
        self.storage.s_register = 0o4400
        self.storage.z_register = 0o1234
        self.storage.set_indirect_storage_bank(0o6)
        self.storage.z_to_s_indirect()
        assert self.storage.read_indirect_bank(0o4400) == 0o1234
        assert self.storage.storage_cycle == MCS_MODE_IND

if __name__ == "__main__":
    unittest.main()
