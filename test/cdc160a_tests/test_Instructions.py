import unittest
from unittest import TestCase
import os
from tempfile import NamedTemporaryFile

from cdc160a.Hardware import Hardware
from cdc160a.InputOutput import InputOutput
from cdc160a import Instructions
from cdc160a.PaperTapeReader import PaperTapeReader
from cdc160a.Storage import InterruptLock
from cdc160a.Storage import MCS_MODE_DIR
from cdc160a.Storage import MCS_MODE_IND
from cdc160a.Storage import MCS_MODE_REL
from cdc160a.Storage import Storage
from typing import Final

READ_AND_WRITE_ADDRESS: Final[int] = 0o1234
INSTRUCTION_ADDRESS: Final[int] = 0o1232
G_ADDRESS: Final[int] = INSTRUCTION_ADDRESS + 1
AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS: Final[int] = INSTRUCTION_ADDRESS + 1
AFTER_DOUBLE_WORD_INSTRUCTION_ADDRESS: Final[int] = INSTRUCTION_ADDRESS + 2

class Test(TestCase):

    def setUp(self) -> None:
        self.paper_tape_reader = PaperTapeReader()
        self.input_output = InputOutput([self.paper_tape_reader])
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
        self.storage.buffer_storage_bank = 1
        self.storage.direct_storage_bank = 2
        self.storage.indirect_storage_bank = 3
        self.storage.relative_storage_bank = 4
        self.storage.run()
        self.hardware = Hardware(self.input_output, self.storage)

    def tearDown(self) -> None:
        self.storage = None
        self.input_output = None
        self.hardware = None

    def test_acj(self) -> None:
        assert Instructions.ACJ.name() == "ACJ"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0076)
        self.storage.unpack_instruction()
        self.storage.a_register = 0o200
        Instructions.ACJ.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS
        assert Instructions.ACJ.perform_logic(self.hardware) == 1
        assert self.storage.direct_storage_bank == 0o06
        assert self.storage.indirect_storage_bank == 0o06
        assert self.storage.relative_storage_bank == 0o06
        self.storage.advance_to_next_instruction()
        assert self.storage.get_next_execution_address() == 0o200

    def test_adb(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o3301)
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS - 1, 0o21)
        self.storage.a_register = 0o1213
        self.storage.unpack_instruction()
        Instructions.ADB.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS - 1
        assert Instructions.ADB.perform_logic(self.hardware) == 2
        assert self.storage.run_stop_status
        assert not self.storage.err_status
        assert self.storage.a_register == 0o1234
        assert self.storage.z_register == 0o21
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_adc(self) -> None:
        # adc
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o3200)
        self.storage.write_relative_bank(G_ADDRESS, 0o21)
        self.storage.a_register = 0o1213
        self.storage.unpack_instruction()
        Instructions.ADC.determine_effective_address(self.storage)
        assert self.storage.s_register == G_ADDRESS
        assert Instructions.ADC.perform_logic(self.hardware) == 2
        assert self.storage.run_stop_status
        assert not self.storage.err_status
        assert self.storage.a_register == 0o1234
        assert self.storage.z_register == 0o21
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_DOUBLE_WORD_INSTRUCTION_ADDRESS)

    def test_add(self) -> None:
        # add
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o3040)
        self.storage.write_direct_bank(0o40, 0o21)
        self.storage.a_register = 0o1213
        self.storage.unpack_instruction()
        Instructions.ADD.determine_effective_address(self.storage)
        assert self.storage.s_register == 0o40
        assert Instructions.ADD.perform_logic(self.hardware) == 2
        assert self.storage.run_stop_status
        assert not self.storage.err_status
        assert self.storage.a_register == 0o1234
        assert self.storage.z_register == 0o21
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_adf(self) -> None:
        # adf
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o3202)
        self.storage.a_register = 0o1213
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS + 2, 0o21)
        self.storage.unpack_instruction()
        Instructions.ADF.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 2
        assert Instructions.ADF.perform_logic(self.hardware) == 2
        assert self.storage.run_stop_status
        assert not self.storage.err_status
        assert self.storage.a_register == 0o1234
        assert self.storage.z_register == 0o21
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_adi(self) -> None:
        # adi
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o3140)
        self.storage.a_register = 0o1213
        self.storage.write_indirect_bank(0o40, 0o21)
        self.storage.unpack_instruction()
        Instructions.ADI.determine_effective_address(self.storage)
        assert self.storage.s_register == 0o40
        assert Instructions.ADI.perform_logic(self.hardware) == 3
        assert self.storage.run_stop_status
        assert not self.storage.err_status
        assert self.storage.a_register == 0o1234
        assert self.storage.z_register == 0o21
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_adm(self) -> None:
        # adm
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o3100)
        self.storage.write_relative_bank(G_ADDRESS, READ_AND_WRITE_ADDRESS)
        self.storage.write_relative_bank(READ_AND_WRITE_ADDRESS, 0o21)
        self.storage.a_register = 0o1213
        Instructions.ADM.determine_effective_address(self.storage)
        assert self.storage.s_register == READ_AND_WRITE_ADDRESS
        assert Instructions.ADM.perform_logic(self.hardware) == 3
        assert self.storage.run_stop_status
        assert not self.storage.err_status
        assert self.storage.a_register == 0o1234
        assert self.storage.z_register == 0o21
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_DOUBLE_WORD_INSTRUCTION_ADDRESS)

    def test_adn(self) -> None:
        # adn
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0621)
        self.storage.a_register = 0o1213
        self.storage.unpack_instruction()
        Instructions.ADN.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS
        assert Instructions.ADN.perform_logic(self.hardware) == 1
        assert self.storage.run_stop_status
        assert not self.storage.err_status
        assert self.storage.a_register == 0o1234
        assert self.storage.z_register == 0o21
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_ads(self) -> None:
        # ads
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o3300)
        self.storage.write_absolute(0, 0o7777, 0o21)
        self.storage.a_register = 0o1213
        self.storage.unpack_instruction()
        Instructions.ADS.determine_effective_address(self.storage)
        assert self.storage.s_register == 0o7777
        assert Instructions.ADS.perform_logic(self.hardware) == 2
        assert self.storage.run_stop_status
        assert not self.storage.err_status
        assert self.storage.a_register == 0o1234
        assert self.storage.z_register == 0o21
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_aob(self) -> None:
        # aob
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o5701)
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS - 1, 0o1233)
        self.storage.unpack_instruction()
        Instructions.AOB.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS - 1
        assert self.storage.run_stop_status
        assert not self.storage.err_status
        assert Instructions.AOB.perform_logic(self.hardware) == 3
        assert self.storage.a_register == 0o1234
        assert self.storage.read_relative_bank(INSTRUCTION_ADDRESS - 1) == 0o1234
        assert self.storage.run_stop_status
        assert not self.storage.err_status

    def test_aoc(self) -> None:
        # aoc
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o5600)
        self.storage.write_relative_bank(G_ADDRESS, 0o1233)
        self.storage.unpack_instruction()
        Instructions.AOC.determine_effective_address(self.storage)
        assert self.storage.s_register == G_ADDRESS
        assert not self.storage.err_status
        assert self.storage.run_stop_status
        assert Instructions.AOC.perform_logic(self.hardware) == 3
        assert self.storage.read_relative_bank(G_ADDRESS) == 0o1234
        assert not self.storage.err_status
        assert self.storage.run_stop_status
        self.storage.advance_to_next_instruction()
        assert self.storage.get_program_counter() == AFTER_DOUBLE_WORD_INSTRUCTION_ADDRESS

    def test_aod(self) -> None:
        # aod
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o5410)
        self.storage.write_direct_bank(0o10, 0o1233)
        self.storage.unpack_instruction()
        Instructions.AOD.determine_effective_address(self.storage)
        assert self.storage.s_register == 0o10
        assert self.storage.run_stop_status
        assert not self.storage.err_status
        assert Instructions.AOD.perform_logic(self.hardware) == 3
        assert not self.storage.err_status
        assert self.storage.run_stop_status
        assert self.storage.a_register == 0o1234
        assert self.storage.read_direct_bank(0o10) == 0o1234
        assert not self.storage.err_status
        assert self.storage.run_stop_status
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_aof(self) -> None:
        # aof
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o5610)
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS + 0o10, 0o1233)
        self.storage.unpack_instruction()
        Instructions.AOF.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 0o10
        assert Instructions.AOF.perform_logic(self.hardware) == 3
        assert self.storage.a_register == 0o1234
        assert self.storage.read_relative_bank(INSTRUCTION_ADDRESS + 0o10) == 0o1234
        assert not self.storage.err_status
        assert self.storage.run_stop_status
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_aoi(self) -> None:
        # aoi
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o5514)
        self.storage.write_indirect_bank(0o14, 0o1233)
        self.storage.unpack_instruction()
        Instructions.AOI.determine_effective_address(self.storage)
        assert self.storage.s_register == 0o14
        assert not self.storage.err_status
        assert self.storage.run_stop_status
        assert Instructions.AOI.perform_logic(self.hardware) == 4
        assert self.storage.a_register == 0o1234
        assert self.storage.read_indirect_bank(0o14) == 0o1234
        assert not self.storage.err_status
        assert self.storage.run_stop_status
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_aom(self) -> None:
        assert Instructions.AOM.name() == "AOM"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o5500)
        self.storage.write_relative_bank(G_ADDRESS, 0o200)
        self.storage.write_relative_bank(0o200, 0o1233)
        self.storage.unpack_instruction()
        Instructions.AOM.determine_effective_address(self.storage)
        assert self.storage.s_register == 0o200
        assert not self.storage.err_status
        assert self.storage.run_stop_status
        assert Instructions.AOM.perform_logic(self.hardware) == 4
        assert self.storage.a_register == 0o1234
        assert self.storage.read_relative_bank(0o200) == 0o1234
        assert not self.storage.err_status
        assert self.storage.run_stop_status
        self.storage.advance_to_next_instruction()

    def test_ate_buffering(self) -> None:
        assert Instructions.ATE.name() == "ATE"
        self.storage.buffer_entrance_register = 0
        self.storage.buffer_exit_register = 0o7777
        self.storage.a_register = 0o200
        self.storage.p_register = 0o100
        self.storage.write_relative_bank(0o100, 0o0105)
        self.storage.write_relative_bank(0o101, 0o1000)
        self.storage.unpack_instruction()
        self.storage.start_buffering()
        Instructions.ATE.determine_effective_address(self.storage)
        assert self.storage.s_register == 0o100
        assert Instructions.ATE.perform_logic(self.hardware) == 2
        assert self.storage.buffer_entrance_register == 0
        assert self.storage.buffer_exit_register == 0o7777
        assert self.storage.buffering
        self.storage.advance_to_next_instruction()
        assert self.storage.get_program_counter() == 0o1000

    def test_ate_not_buffering(self) -> None:
        self.storage.buffer_entrance_register = 0
        self.storage.buffer_exit_register = 0
        self.storage.a_register = 0o200
        self.storage.p_register = 0o100
        self.storage.write_relative_bank(0o100, 0o0105)
        self.storage.write_relative_bank(0o101, 0o1000)
        self.storage.unpack_instruction()
        Instructions.ATE.determine_effective_address(self.storage)
        assert self.storage.s_register == 0o100
        assert Instructions.ATE.perform_logic(self.hardware) == 1
        assert self.storage.buffer_entrance_register == 0o200
        assert self.storage.buffer_exit_register == 0
        assert not self.storage.buffering
        self.storage.advance_to_next_instruction()
        assert self.storage.get_program_counter() == 0o102

    def test_atx_buffering(self) -> None:
        assert Instructions.ATX.name() == "ATX"
        self.storage.set_buffer_storage_bank(0o1)
        self.storage.set_direct_storage_bank(0o2)
        self.storage.set_indirect_storage_bank(0o3)
        self.storage.set_relative_storage_bank(0o4)
        self.storage.buffer_entrance_register = 0
        self.storage.buffer_exit_register = 0o7777
        self.storage.a_register = 0o200
        self.storage.p_register = 0o100
        self.storage.write_relative_bank(0o100, 0o0105)
        self.storage.write_relative_bank(0o101, 0o1000)
        self.storage.unpack_instruction()
        self.storage.start_buffering()
        Instructions.ATX.determine_effective_address(self.storage)
        assert self.storage.s_register == 0o100
        assert Instructions.ATX.perform_logic(self.hardware) == 2
        assert self.storage.buffer_entrance_register == 0
        assert self.storage.buffer_exit_register == 0o7777
        assert self.storage.buffering
        self.storage.advance_to_next_instruction()
        assert self.storage.get_program_counter() == 0o1000

    def test_atx_not_buffering(self) -> None:
        assert Instructions.ATX.name() == "ATX"
        self.storage.buffer_entrance_register = 0
        self.storage.buffer_exit_register = 0
        self.storage.a_register = 0o200
        self.storage.p_register = 0o100
        self.storage.write_relative_bank(0o100, 0o0106)
        self.storage.write_relative_bank(0o101, 0o1000)
        self.storage.unpack_instruction()
        Instructions.ATX.determine_effective_address(self.storage)
        assert self.storage.get_program_counter() == 0o100
        assert Instructions.ATX.perform_logic(self.hardware) == 1
        assert self.storage.buffer_exit_register == 0o200
        assert self.storage.buffer_entrance_register == 0
        assert not self.storage.buffering
        self.storage.advance_to_next_instruction()
        assert self.storage.get_program_counter() == 0o102

    def test_bls_buffering(self) -> None:
        assert Instructions.BLS.name() == "BLS"
        self.storage.buffer_entrance_register = 0o200
        self.storage.buffer_exit_register = 0o401
        self.storage.a_register = 0o7654
        self.storage.p_register = 0o100
        self.storage.write_relative_bank(0o100, 0o0100)
        self.storage.write_relative_bank(0o101, 0o1000)
        self.storage.unpack_instruction()
        self.storage.start_buffering()
        Instructions.BLS.determine_effective_address(self.storage)
        assert self.storage.get_program_counter() == 0o100
        assert Instructions.BLS.perform_logic(self.hardware) == 2
        assert self.storage.buffer_entrance_register == 0o200
        assert self.storage.buffer_exit_register == 0o401
        assert self.storage.buffering
        self.storage.advance_to_next_instruction()
        assert self.storage.buffer_entrance_register == 0o200

    def test_bls_not_buffering(self) -> None:
        assert Instructions.BLS.name() == "BLS"
        self.storage.buffer_entrance_register = 0o200
        self.storage.buffer_exit_register = 0o401
        self.storage.a_register = 0o7654
        self.storage.p_register = 0o100
        self.storage.write_relative_bank(0o100, 0o0100)
        self.storage.write_relative_bank(0o101, 0o1000)
        self.storage.unpack_instruction()
        Instructions.BLS.determine_effective_address(self.storage)
        assert self.storage.get_program_counter() == 0o100
        assert not self.storage.buffering
        assert Instructions.BLS.perform_logic(self.hardware) == 0o201
        assert self.storage.buffer_entrance_register == 0o401
        assert self.storage.buffer_exit_register == 0o401
        assert self.storage.read_buffer_bank(0o177) == 0
        assert self.storage.read_buffer_bank(0o401) == 0
        for address in range(0o200, 0o401):
            assert self.storage.read_buffer_bank(address) == 0o7654
        self.storage.advance_to_next_instruction()
        assert self.storage.get_program_counter() == 0o102

    def test_cil(self) -> None:
        assert Instructions.CIL.name() == "CIL"
        self.storage.interrupt_lock = InterruptLock.LOCKED
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0120)
        self.storage.unpack_instruction()
        Instructions.CTA.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS
        assert Instructions.CIL.perform_logic(self.hardware) == 1
        assert self.storage.interrupt_lock == InterruptLock.UNLOCK_PENDING
        self.storage.advance_to_next_instruction()
        assert self.storage.get_program_counter() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_cta(self) -> None:
        assert Instructions.CTA.name() == "CTA"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0130)
        self.storage.set_buffer_storage_bank(0o1)
        self.storage.set_direct_storage_bank(0o2)
        self.storage.set_indirect_storage_bank(0o3)
        self.storage.set_relative_storage_bank(0o4)
        Instructions.CTA.determine_effective_address(self.storage)
        assert self.storage.get_program_counter() == INSTRUCTION_ADDRESS
        Instructions.CTA.perform_logic(self.hardware)
        assert self.storage.a_register == 0o1234
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)


    def test_drj(self) -> None:
        assert Instructions.DRJ.name() == "DRJ"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0056)
        self.storage.unpack_instruction()
        self.storage.a_register = 0o200
        assert self.storage.s_register == INSTRUCTION_ADDRESS
        assert Instructions.DRJ.perform_logic(self.hardware) == 1
        assert self.storage.direct_storage_bank == 0o06
        assert self.storage.relative_storage_bank == 0o06
        self.storage.advance_to_next_instruction()
        assert self.storage.get_program_counter() == 0o200

    def test_err(self) -> None:
        # err
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0000)
        self.storage.z_register = 0o3333
        self.storage.a_register = 0o3333
        self.storage.unpack_instruction()
        Instructions.ERR.determine_effective_address(self.storage)
        assert Instructions.ERR.perform_logic(self.hardware) == 1
        assert not self.storage.run_stop_status
        assert self.storage.err_status
        assert self.storage.a_register == 0o3333
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_exc(self) -> None:
        temp_file = NamedTemporaryFile("w+", delete=False)
        print("Temporary file: {0},".format(temp_file.name))
        temp_file.write("456\n")
        temp_file.close()

        self.paper_tape_reader.open(temp_file.name)

        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o7500)
        self.storage.write_relative_bank(G_ADDRESS, 0o4102)
        self.storage.a_register = 0o5000
        self.storage.unpack_instruction()
        Instructions.EXC.determine_effective_address(self.storage)
        assert self.storage.s_register == G_ADDRESS
        assert Instructions.EXC.perform_logic(self.hardware) == 2
        assert self.storage.a_register == 0o5000
        assert not self.storage.machine_hung
        assert self.storage.interrupt_lock == InterruptLock.LOCKED
        assert (self.input_output.device_on_normal_channel() ==
                self.paper_tape_reader)
        assert self.input_output.device_on_buffer_channel() is None
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_DOUBLE_WORD_INSTRUCTION_ADDRESS)

        self.paper_tape_reader.close()
        os.unlink(temp_file.name)

    def test_exf(self) -> None:
        temp_file = NamedTemporaryFile("w+", delete=False)
        print("Temporary file: {0},".format(temp_file.name))
        temp_file.write("456\n")
        temp_file.close()

        self.paper_tape_reader.open(temp_file.name)

        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o7540)
        self.storage.a_register = 0o5000
        self.storage.write_relative_bank(
            INSTRUCTION_ADDRESS + 0o40, 0o4102)
        self.storage.unpack_instruction()
        Instructions.EXF.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 0o40
        assert Instructions.EXF.perform_logic(self.hardware) == 2
        assert self.storage.a_register == 0o5000
        assert self.storage.interrupt_lock == InterruptLock.LOCKED
        assert not self.storage.machine_hung
        assert (self.input_output.device_on_normal_channel() ==
                self.paper_tape_reader)
        assert self.input_output.device_on_buffer_channel() is None
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

        self.paper_tape_reader.close()
        os.unlink(temp_file.name)

    def test_hlt(self) -> None:
        # hlt
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o7700)
        self.storage.z_register = 0o3333
        self.storage.a_register = 0o3333
        self.storage.unpack_instruction()
        Instructions.ERR.determine_effective_address(self.storage)
        assert Instructions.HLT.perform_logic(self.hardware) == 1
        assert not self.storage.run_stop_status
        assert not self.storage.err_status
        assert self.storage.a_register == 0o3333
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_hwi(self) -> None:
        assert Instructions.HWI.name() == "HWI"
        # hwi 54
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o7654)
        self.storage.unpack_instruction()
        self.storage.write_direct_bank(0o54, 0o3200)
        self.storage.write_indirect_bank(0o3200, 0o4356)
        self.storage.a_register = 0o6521
        Instructions.HWI.determine_effective_address(self.storage)
        assert self.storage.s_register == 0o3200
        assert Instructions.HWI.perform_logic(self.hardware) == 4
        assert self.storage.read_indirect_bank(0o3200) == 0o4321
        assert self.storage.storage_cycle == MCS_MODE_IND
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_irj(self) -> None:
        assert Instructions.IRJ.name() == "IRJ"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0036)
        self.storage.unpack_instruction()
        self.storage.a_register = 0o200
        Instructions.IRJ.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS
        assert Instructions.IRJ.perform_logic(self.hardware) == 1
        assert self.storage.indirect_storage_bank == 0o06
        assert self.storage.relative_storage_bank == 0o06
        self.storage.advance_to_next_instruction()
        assert self.storage.get_program_counter() == 0o200

    def test_jfi(self) -> None:
        assert Instructions.JFI.name() == "JFI"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o7110)
        self.storage.unpack_instruction()
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS + 0o10, 0o400)
        self.storage.write_relative_bank(0o400, 0o1400)
        Instructions.JFI.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 0o10
        assert Instructions.JFI.perform_logic(self.hardware) == 2
        assert not self.storage.err_status
        assert self.storage.run_stop_status
        self.storage.advance_to_next_instruction()
        assert self.storage.get_program_counter() == 0o0400

    def test_jpi(self) -> None:
        assert Instructions.JPI.name() == "JPI"
        self.storage.write_direct_bank(0o20, 0o200)
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o7020)
        self.storage.unpack_instruction()
        assert Instructions.JPI.perform_logic(self.hardware) == 2
        assert self.storage.get_next_execution_address() == 0o200

    def test_jpr(self) -> None:
        assert Instructions.JPR.name() == "JPR"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o7100)
        self.storage.unpack_instruction()
        self.storage.write_relative_bank(G_ADDRESS, 0o1000)
        Instructions.JPR.determine_effective_address(self.storage)
        assert self.storage.s_register == 0o1000
        assert Instructions.JPR.perform_logic(self.hardware) == 3
        assert (self.storage.read_relative_bank(0o1000) ==
                INSTRUCTION_ADDRESS + 2)
        self.storage.advance_to_next_instruction()
        assert self.storage.get_program_counter() == 0o1001

    def test_lcb(self) -> None:
        # LCB 10
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o2710)
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS - 0o10, 0o5555)
        self.storage.unpack_instruction()
        Instructions.LCB.determine_effective_address(self.storage)
        Instructions.LCB.perform_logic(self.hardware)
        assert self.storage.z_register == 0O5555
        assert self.storage.a_register == 0o5555 ^ 0o7777
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        assert self.storage.run_stop_status

    def test_lcc(self) -> None:
        # LCC 6666
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o2600)
        self.storage.write_relative_bank(G_ADDRESS, 0o6666)
        self.storage.p_register = INSTRUCTION_ADDRESS
        self.storage.unpack_instruction()
        Instructions.LCC.determine_effective_address(self.storage)
        assert Instructions.LCC.perform_logic(self.hardware) == 2
        assert self.storage.z_register == 0o6666
        assert self.storage.a_register == 0o6666 ^ 0o7777
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_DOUBLE_WORD_INSTRUCTION_ADDRESS
        assert self.storage.run_stop_status

    def test_lcd(self) -> None:
        # LCD 45
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o2445)
        self.storage.write_direct_bank(INSTRUCTION_ADDRESS, 0o7654)
        self.storage.unpack_instruction()
        assert Instructions.LCD.perform_logic(self.hardware) == 2
        assert self.storage.s_register == INSTRUCTION_ADDRESS
        assert self.storage.z_register == 0o7654
        assert self.storage.a_register == 0o7654 ^ 0o7777
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        assert self.storage.run_stop_status

    def test_lcf(self) -> None:
        # LCF 20
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o2620)
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS + 0o20, 0o2222)
        self.storage.unpack_instruction()
        Instructions.LCF.determine_effective_address(self.storage)
        Instructions.LCF.perform_logic(self.hardware)
        assert self.storage.z_register == 0o2222
        assert self.storage.a_register ==0o2222 ^ 0o7777
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        assert self.storage.run_stop_status

    def test_lci(self) -> None:
        # LCI 45
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o2545)
        self.storage.write_indirect_bank(0o45, 0o7654)
        self.storage.unpack_instruction()
        Instructions.LCI.determine_effective_address(self.storage)
        assert Instructions.LCI.perform_logic(self.hardware) == 3
        assert self.storage.s_register == 0o45
        assert self.storage.z_register == 0o7654
        assert self.storage.a_register == 0o7654 ^ 0o7777
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        assert self.storage.run_stop_status

    def test_lcm(self) -> None:
        # LCM 137
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o2500)
        self.storage.write_relative_bank(G_ADDRESS, 0o137)
        self.storage.write_indirect_bank(0o137, 0o1370)
        self.storage.unpack_instruction()
        Instructions.LCM.determine_effective_address(self.storage)
        assert Instructions.LCM.perform_logic(self.hardware) ==3
        assert self.storage.s_register == 0o137
        assert self.storage.z_register == 0o1370
        assert self.storage.a_register == 0o1370 ^ 0o7777
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_DOUBLE_WORD_INSTRUCTION_ADDRESS
        assert self.storage.run_stop_status

    def test_lcn(self) -> None:
        # LCN 37
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0537)
        self.storage.unpack_instruction()
        Instructions.LCN.determine_effective_address(self.storage)
        assert Instructions.LCN.perform_logic(self.hardware) == 1
        self.storage.advance_to_next_instruction()
        assert self.storage.s_register == INSTRUCTION_ADDRESS
        assert self.storage.z_register == 0o37
        assert self.storage.a_register == 0o37 ^ 0o7777

    def test_lcs(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o2700)
        self.storage.unpack_instruction()
        Instructions.LCS.determine_effective_address(self.storage)
        assert Instructions.LCS.perform_logic(self.hardware) == 2
        assert self.storage.z_register == 0o77
        assert self.storage.a_register == 0o77 ^ 0o7777
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_ldb(self) -> None:
        # LDB 10
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o2310)
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS - 0o10, 0o5555)
        self.storage.unpack_instruction()
        Instructions.LDB.determine_effective_address(self.storage)
        Instructions.LDB.perform_logic(self.hardware)
        assert self.storage.z_register == 0O5555
        assert self.storage.a_register == 0o5555
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        assert self.storage.run_stop_status

    def test_ldc(self) -> None:
        # LDC 6666
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o2200)
        self.storage.write_relative_bank(G_ADDRESS, 0o6666)
        self.storage.p_register = INSTRUCTION_ADDRESS
        self.storage.unpack_instruction()
        Instructions.LDC.determine_effective_address(self.storage)
        assert Instructions.LDC.perform_logic(self.hardware) == 2
        assert self.storage.z_register == 0o6666
        assert self.storage.a_register == 0o6666
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_DOUBLE_WORD_INSTRUCTION_ADDRESS
        assert self.storage.run_stop_status

    def test_ldd(self) -> None:
        # LDD 45
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o2045)
        self.storage.write_direct_bank(INSTRUCTION_ADDRESS, 0o7654)
        self.storage.unpack_instruction()
        assert Instructions.LDD.perform_logic(self.hardware) == 2
        assert self.storage.s_register == INSTRUCTION_ADDRESS
        assert self.storage.z_register == 0o7654
        assert self.storage.a_register == 0o7654
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        assert self.storage.run_stop_status

    def test_ldf(self) -> None:
        # LDF 20
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o2220)
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS + 0o20, 0o2222)
        self.storage.unpack_instruction()
        Instructions.LDF.determine_effective_address(self.storage)
        Instructions.LDF.perform_logic(self.hardware)
        assert self.storage.z_register == 0o2222
        assert self.storage.a_register ==0o2222
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        assert self.storage.run_stop_status

    def test_ldi(self) -> None:
        # LDI 45
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o2145)
        self.storage.write_indirect_bank(0o45, 0o7654)
        self.storage.unpack_instruction()
        Instructions.LDI.determine_effective_address(self.storage)
        assert Instructions.LDI.perform_logic(self.hardware) == 3
        assert self.storage.s_register == 0o45
        assert self.storage.z_register == 0o7654
        assert self.storage.a_register == 0o7654
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        assert self.storage.run_stop_status

    def test_ldm(self) -> None:
        # LDM 137
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o2100)
        self.storage.write_relative_bank(G_ADDRESS, 0o137)
        self.storage.write_indirect_bank(0o137, 0o1370)
        self.storage.unpack_instruction()
        Instructions.LDM.determine_effective_address(self.storage)
        assert Instructions.LDM.perform_logic(self.hardware) ==3
        assert self.storage.s_register == 0o137
        assert self.storage.z_register == 0o1370
        assert self.storage.a_register == 0o1370
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_DOUBLE_WORD_INSTRUCTION_ADDRESS
        assert self.storage.run_stop_status

    def test_ldn(self) -> None:
        # LDN 37
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0437)
        self.storage.unpack_instruction()
        Instructions.LDN.determine_effective_address(self.storage)
        assert Instructions.LDN.perform_logic(self.hardware) == 1
        self.storage.advance_to_next_instruction()
        assert self.storage.s_register == INSTRUCTION_ADDRESS
        assert self.storage.z_register == 0o37
        assert self.storage.a_register == 0o37

    def test_lds(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o3200)
        self.storage.unpack_instruction()
        Instructions.LDS.determine_effective_address(self.storage)
        assert Instructions.LDS.perform_logic(self.hardware) == 2
        assert self.storage.z_register == 0o77
        assert self.storage.a_register == 0o77
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_lpc(self) -> None:
        assert Instructions.LPC.name() == "LPC"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o1200)
        self.storage.write_relative_bank(G_ADDRESS, 0o77)
        self.storage.a_register = 0o4321
        self.storage.unpack_instruction()
        Instructions.LPC.determine_effective_address(self.storage)
        assert self.storage.s_register == G_ADDRESS
        assert Instructions.LPC.perform_logic(self.hardware) == 2
        assert self.storage.z_register == 0o77
        assert self.storage.a_register == 0o21
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_DOUBLE_WORD_INSTRUCTION_ADDRESS

    def test_lpd(self) -> None:
        assert Instructions.LPD.name() == "LPD"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o1040)
        self.storage.write_direct_bank(0o40, 0o77)
        self.storage.a_register = 0o4321
        self.storage.unpack_instruction()
        assert self.storage.s_register == INSTRUCTION_ADDRESS
        Instructions.LPD.determine_effective_address(self.storage)
        assert self.storage.s_register == 0o40
        assert Instructions.LPD.perform_logic(self.hardware) == 2
        assert self.storage.z_register == 0o77
        assert self.storage.a_register == 0o21
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_lpf(self) -> None:
        assert Instructions.LPF.name() == "LPF"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o1201)
        self.storage.write_relative_bank(G_ADDRESS, 0o77)
        self.storage.a_register = 0o4321
        self.storage.unpack_instruction()
        Instructions.LPF.determine_effective_address(self.storage)
        assert self.storage.s_register == G_ADDRESS
        assert Instructions.LPF.perform_logic(self.hardware) == 2
        assert self.storage.z_register == 0o77
        assert self.storage.a_register == 0o21
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_lpi(self) -> None:
        assert Instructions.LPI.name() == "LPI"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o1140)
        self.storage.write_indirect_bank(0o40, 0o77)
        self.storage.a_register = 0o4321
        self.storage.unpack_instruction()
        assert self.storage.s_register == INSTRUCTION_ADDRESS
        Instructions.LPI.determine_effective_address(self.storage)
        assert self.storage.s_register == 0o40
        assert Instructions.LPI.perform_logic(self.hardware) == 3
        assert self.storage.z_register == 0o77
        assert self.storage.a_register == 0o21
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_lpm(self) -> None:
        assert Instructions.LPM.name() == "LPM"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o1100)
        self.storage.write_relative_bank(G_ADDRESS, 0o140)
        self.storage.write_relative_bank(0o140, 0o77)
        self.storage.a_register = 0o4321
        self.storage.unpack_instruction()
        assert self.storage.s_register == INSTRUCTION_ADDRESS
        Instructions.LPM.determine_effective_address(self.storage)
        assert self.storage.s_register == 0o140
        assert Instructions.LPM.perform_logic(self.hardware) == 3
        assert self.storage.z_register == 0o77
        assert self.storage.a_register == 0o21
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_DOUBLE_WORD_INSTRUCTION_ADDRESS

    def test_lpn(self) -> None:
        assert Instructions.LPN.name() == "LPN"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0277)
        self.storage.a_register = 0o4321
        self.storage.unpack_instruction()
        assert self.storage.s_register == INSTRUCTION_ADDRESS
        Instructions.LPN.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS
        assert Instructions.LPN.perform_logic(self.hardware) == 1
        assert self.storage.z_register == 0o77
        assert self.storage.a_register == 0o21
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_lps(self) -> None:
        assert Instructions.LPS.name() == "LPS"
        self.storage.write_specific(0o77)
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o1300)
        self.storage.a_register = 0o4321
        self.storage.unpack_instruction()
        Instructions.LPS.determine_effective_address(self.storage)
        assert self.storage.s_register == 0o7777
        assert Instructions.LPS.perform_logic(self.hardware) == 2
        assert self.storage.z_register == 0o77
        assert self.storage.a_register == 0o21
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_ls1(self)-> None:
        # LS1
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0x0102)
        self.storage.unpack_instruction()
        self.storage.z_register = 0o4001
        self.storage.a_register = 0o4001
        Instructions.LS1.determine_effective_address(self.storage)
        assert Instructions.LS1.perform_logic(self.hardware) == 1
        assert self.storage.run_stop_status
        assert self.storage.z_register == 0o4001
        assert self.storage.a_register == 0o0003
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_ls2(self) -> None:
        # LS2
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0103)
        self.storage.unpack_instruction()
        self.storage.z_register = 0o6001
        self.storage.a_register = 0o6001
        Instructions.LS2.determine_effective_address(self.storage)
        assert Instructions.LS2.perform_logic(self.hardware) == 1
        assert self.storage.run_stop_status
        assert self.storage.z_register == 0o6001
        assert self.storage.a_register == 0o0007
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_ls3(self) -> None:
        # LS3
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0110)
        self.storage.unpack_instruction()
        self.storage.z_register = 0o7000
        self.storage.a_register = 0o7000
        Instructions.LS3.determine_effective_address(self.storage)
        assert Instructions.LS3.perform_logic(self.hardware) == 1
        assert self.storage.run_stop_status
        assert self.storage.z_register == 0o7000
        assert self.storage.a_register == 0o0007
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_ls6(self) -> None:
        # LS6
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0111)
        self.storage.unpack_instruction()
        self.storage.z_register = 0o3412
        self.storage.z_to_a()
        Instructions.LS6.determine_effective_address(self.storage)
        assert Instructions.LS6.perform_logic(self.hardware) == 1
        assert self.storage.run_stop_status
        assert self.storage.z_register == 0o3412
        assert self.storage.a_register == 0o1234
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_muh(self) -> None:
        # MUH
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0113)
        self.storage.unpack_instruction()
        self.storage.a_register = 1
        Instructions.MUH.determine_effective_address(self.storage) # Does nothing.
        assert Instructions.MUH.perform_logic(self.hardware) == 1
        assert self.storage.run_stop_status
        assert self.storage.a_register == 100
        assert not self.storage.err_status
        self.storage.advance_to_next_instruction()
        assert (self.storage.p_register ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_mut(self) -> None:
        # MUT
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0112)
        self.storage.unpack_instruction()
        self.storage.a_register = 1
        Instructions.MUT.determine_effective_address(self.storage) # Does nothing.
        assert Instructions.MUT.perform_logic(self.hardware) == 1
        assert self.storage.run_stop_status
        assert self.storage.a_register == 10
        assert not self.storage.err_status
        self.storage.advance_to_next_instruction()
        assert (self.storage.p_register ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_njb_a_minus_zero(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6402)
        self.storage.a_register = 0o7777
        self.storage.unpack_instruction()
        Instructions.NJB.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS - 2
        Instructions.NJB.perform_logic(self.hardware)
        assert (self.storage.next_address() ==
                INSTRUCTION_ADDRESS - 2)
        self.storage.advance_to_next_instruction()
        assert (self.storage.p_register ==
                INSTRUCTION_ADDRESS - 2)

    def test_njb_a_negative(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6402)
        self.storage.a_register = 0o7777
        self.storage.unpack_instruction()
        Instructions.NJB.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS - 2
        Instructions.NJB.perform_logic(self.hardware)
        assert (self.storage.next_address() ==
                INSTRUCTION_ADDRESS - 2)
        self.storage.advance_to_next_instruction()
        assert (self.storage.p_register ==
                INSTRUCTION_ADDRESS - 2)

    def test_njb_a_positive(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6402)
        self.storage.a_register = 1
        self.storage.unpack_instruction()
        Instructions.NJB.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS - 2
        Instructions.NJB.perform_logic(self.hardware)
        assert (self.storage.next_address() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)
        self.storage.advance_to_next_instruction()
        assert (self.storage.p_register ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_njb_a_zero(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6402)
        self.storage.a_register = 0
        self.storage.unpack_instruction()
        Instructions.NJB.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS - 2
        Instructions.NJB.perform_logic(self.hardware)
        assert (self.storage.next_address() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)
        self.storage.advance_to_next_instruction()
        assert (self.storage.p_register ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_njf_a_minus_zero(self) -> None:
        # NJF
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6340)
        self.storage.a_register = 0o7777
        self.storage.unpack_instruction()
        Instructions.NJF.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 0o0040
        Instructions.NJF.perform_logic(self.hardware)
        assert self.storage.next_address() == INSTRUCTION_ADDRESS + 0o0040
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == INSTRUCTION_ADDRESS + 0o0040

    def test_njf_a_negative(self) -> None:
        # NJF
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6340)
        self.storage.a_register = 0o7776
        self.storage.unpack_instruction()
        Instructions.NJF.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 0o0040
        Instructions.NJF.perform_logic(self.hardware)
        assert self.storage.next_address() == INSTRUCTION_ADDRESS + 0o0040
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == INSTRUCTION_ADDRESS + 0o0040

    def test_njf_a_positive(self) -> None:
        # NJF
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6340)
        self.storage.a_register = 0o3777
        self.storage.unpack_instruction()
        Instructions.NJF.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 0o0040
        Instructions.NJF.perform_logic(self.hardware)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_njf_a_zero(self) -> None:
        # NJF
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6340)
        self.storage.a_register = 0
        self.storage.unpack_instruction()
        Instructions.NJF.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 0o0040
        Instructions.NJF.perform_logic(self.hardware)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_nzb_a_minus_zero(self) -> None:
        # NZB
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6540)
        self.storage.a_register = 0o7777
        self.storage.unpack_instruction()
        Instructions.NZB.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS - 0o0040
        Instructions.NZB.perform_logic(self.hardware)
        assert self.storage.next_address() == INSTRUCTION_ADDRESS - 0o0040
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == INSTRUCTION_ADDRESS - 0o0040

    def test_nzb_a_negative(self) -> None:
        # NZB
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6540)
        self.storage.a_register = 0o4000
        self.storage.unpack_instruction()
        Instructions.NZB.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS - 0o0040
        Instructions.NZB.perform_logic(self.hardware)
        assert self.storage.next_address() == INSTRUCTION_ADDRESS - 0o0040
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == INSTRUCTION_ADDRESS - 0o0040

    def test_nzb_a_positive(self) -> None:
        # NZB
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6540)
        self.storage.a_register = 0o3777
        self.storage.unpack_instruction()
        Instructions.NZB.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS - 0o0040
        Instructions.NZB.perform_logic(self.hardware)
        assert self.storage.next_address() == INSTRUCTION_ADDRESS - 0o0040
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == INSTRUCTION_ADDRESS - 0o0040

    def test_nzb_a_zero(self) -> None:
        # NZB
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6540)
        self.storage.a_register = 0
        self.storage.unpack_instruction()
        Instructions.NZB.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS - 0o0040
        Instructions.NZB.perform_logic(self.hardware)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_nzf_a_minus_zero(self) -> None:
        # NZF
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6140)
        self.storage.a_register = 0o7777
        self.storage.unpack_instruction()
        Instructions.NZF.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 0o0040
        Instructions.NZF.perform_logic(self.hardware)
        assert self.storage.next_address() == INSTRUCTION_ADDRESS + 0o0040
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == INSTRUCTION_ADDRESS + 0o0040

    def test_nzf_a_negative(self) -> None:
        # NZF
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6140)
        self.storage.a_register = 0o4000
        self.storage.unpack_instruction()
        Instructions.NZF.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 0o0040
        Instructions.NZF.perform_logic(self.hardware)
        assert self.storage.next_address() == INSTRUCTION_ADDRESS + 0o0040
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == INSTRUCTION_ADDRESS + 0o0040

    def test_nzf_a_positive(self) -> None:
        # NZF
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6140)
        self.storage.a_register = 0o3777
        self.storage.unpack_instruction()
        Instructions.NZF.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 0o0040
        Instructions.NZF.perform_logic(self.hardware)
        assert self.storage.next_address() == INSTRUCTION_ADDRESS + 0o0040
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == INSTRUCTION_ADDRESS + 0o0040

    def test_nzf_a_zero(self) -> None:
        # NZF
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6140)
        self.storage.a_register = 0
        self.storage.unpack_instruction()
        Instructions.NZF.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 0o0040
        Instructions.NZF.perform_logic(self.hardware)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_nop(self) -> None:
        # NOP 1
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0001)
        self.storage.z_register = 0o3333
        self.storage.a_register = 0o3333
        Instructions.NOP.determine_effective_address(self.storage)
        assert Instructions.NOP.perform_logic(self.hardware) == 1
        assert self.storage.a_register == 0o3333
        assert self.storage.z_register == 0o3333
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_pjf_a_minus_zero(self) -> None:
        # PJF
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6240)
        self.storage.a_register = 0o7777
        self.storage.unpack_instruction()
        Instructions.PJF.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 0o0040
        Instructions.PJF.perform_logic(self.hardware)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_pjb_a_minus_zero(self) -> None:
        # PJB
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6240)
        self.storage.a_register = 0o7777
        self.storage.unpack_instruction()
        Instructions.PJB.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS - 0o0040
        Instructions.PJB.perform_logic(self.hardware)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_pjb_a_negative(self) -> None:
        # PJB
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6240)
        self.storage.a_register = 0o7776
        self.storage.unpack_instruction()
        Instructions.PJB.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS - 0o0040
        Instructions.PJB.perform_logic(self.hardware)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_pjb_a_positive(self) -> None:
        # PJB
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6240)
        self.storage.a_register = 1
        self.storage.unpack_instruction()
        Instructions.PJB.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS - 0o0040
        Instructions.PJB.perform_logic(self.hardware)
        assert self.storage.next_address() == INSTRUCTION_ADDRESS - 0o0040
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == INSTRUCTION_ADDRESS - 0o0040

    def test_pjb_a_zero(self) -> None:
        # PJB
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6240)
        self.storage.a_register = 0
        self.storage.unpack_instruction()
        Instructions.PJB.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS - 0o0040
        Instructions.PJB.perform_logic(self.hardware)
        assert self.storage.next_address() == INSTRUCTION_ADDRESS - 0o0040
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == INSTRUCTION_ADDRESS - 0o0040

    def test_pjf_a_negative(self) -> None:
        # PJF
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6240)
        self.storage.a_register = 0o7776
        self.storage.unpack_instruction()
        Instructions.PJF.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 0o0040
        Instructions.PJF.perform_logic(self.hardware)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_pjf_a_positive(self) -> None:
        # PJF
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6240)
        self.storage.a_register = 1
        self.storage.unpack_instruction()
        Instructions.PJF.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 0o0040
        Instructions.PJF.perform_logic(self.hardware)
        assert self.storage.next_address() == INSTRUCTION_ADDRESS + 0o0040
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == INSTRUCTION_ADDRESS + 0o0040

    def test_pjf_a_zero(self) -> None:
        assert Instructions.PJF.name() == "PJF"
        # PJF
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6240)
        self.storage.a_register = 0
        self.storage.unpack_instruction()
        Instructions.PJF.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 0o0040
        Instructions.PJF.perform_logic(self.hardware)
        assert self.storage.next_address() == INSTRUCTION_ADDRESS + 0o0040
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == INSTRUCTION_ADDRESS + 0o0040

    def test_pta(self) -> None:
        assert Instructions.PTA.name() == "PTA"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0101)
        self.storage.unpack_instruction()
        Instructions.PTA.perform_logic(self.hardware)
        assert self.storage.a_register == INSTRUCTION_ADDRESS
        self.storage.advance_to_next_instruction()
        assert (self.storage.p_register ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_rab(self) -> None:
        address = INSTRUCTION_ADDRESS - 2
        self.storage.write_relative_bank(address, 0o777)
        self.storage.a_register = 0o1
        self.storage.run_stop_status = True
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o5302)
        self.storage.unpack_instruction()
        Instructions.RAB.determine_effective_address(self.storage)
        assert self.storage.s_register == address
        assert Instructions.RAB.perform_logic(self.hardware) == 3
        assert self.storage.run_stop_status
        assert not self.storage.err_status
        assert self.storage.s_register == address
        assert self.storage.read_relative_bank(self.storage.s_register) == 0o1000
        assert self.storage.a_register == 0o1000
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_rac(self) -> None:
        address = G_ADDRESS
        self.storage.a_register = 0o1
        self.storage.run_stop_status = True
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o5200)
        self.storage.write_relative_bank(address, 0o777)
        self.storage.unpack_instruction()
        Instructions.RAC.determine_effective_address(self.storage)
        assert self.storage.s_register == address
        assert Instructions.RAC.perform_logic(self.hardware) == 3
        assert self.storage.run_stop_status
        assert not self.storage.err_status
        assert self.storage.s_register == address
        assert self.storage.read_relative_bank(self.storage.s_register) == 0o1000
        assert self.storage.a_register == 0o1000
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_DOUBLE_WORD_INSTRUCTION_ADDRESS)

    def test_rad(self) -> None:
        address = 0o20
        self.storage.s_register = address
        self.storage.write_direct_bank(self.storage.s_register, 0o777)
        self.storage.a_register = 0o1
        self.storage.run_stop_status = True
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o5020)
        self.storage.unpack_instruction()
        Instructions.RAD.determine_effective_address(self.storage)
        assert self.storage.s_register == address
        assert Instructions.RAD.perform_logic(self.hardware) == 3
        assert self.storage.run_stop_status
        assert not self.storage.err_status
        assert self.storage.s_register == address
        assert self.storage.read_direct_bank(self.storage.s_register) == 0o1000
        assert self.storage.a_register == 0o1000
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_raf(self) -> None:
        address = INSTRUCTION_ADDRESS + 0o10
        self.storage.write_relative_bank(address, 0o777)
        self.storage.a_register = 0o1
        self.storage.run_stop_status = True
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o5210)
        self.storage.unpack_instruction()
        Instructions.RAF.determine_effective_address(self.storage)
        assert self.storage.s_register == address
        assert Instructions.RAF.perform_logic(self.hardware) == 3
        assert self.storage.run_stop_status
        assert not self.storage.err_status
        assert self.storage.s_register == address
        assert self.storage.read_relative_bank(self.storage.s_register) == 0o1000
        assert self.storage.a_register == 0o1000
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_ras(self) -> None:
        address = 0o7777
        self.storage.write_specific(0o777)
        self.storage.a_register = 0o1
        self.storage.run_stop_status = True
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o5300)
        self.storage.unpack_instruction()
        Instructions.RAS.determine_effective_address(self.storage)
        assert self.storage.s_register == address
        assert Instructions.RAS.perform_logic(self.hardware) == 3
        assert self.storage.run_stop_status
        assert not self.storage.err_status
        assert self.storage.s_register == address
        assert self.storage.read_specific() == 0o1000
        assert self.storage.a_register == 0o1000
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_rai(self) -> None:
        address = 0o20
        self.storage.s_register = address
        self.storage.write_indirect_bank(self.storage.s_register, 0o777)
        self.storage.a_register = 0o1
        self.storage.run_stop_status = True
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o5020)
        self.storage.unpack_instruction()
        Instructions.RAI.determine_effective_address(self.storage)
        assert self.storage.s_register == 0o20
        assert Instructions.RAI.perform_logic(self.hardware) == 4
        assert self.storage.run_stop_status
        assert not self.storage.err_status
        assert self.storage.s_register == address
        assert self.storage.read_indirect_bank(self.storage.s_register) == 0o1000
        assert self.storage.a_register == 0o1000
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_ram(self) -> None:
        address = 0o200
        self.storage.a_register = 0o1
        self.storage.run_stop_status = True
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o5100)
        self.storage.write_relative_bank(G_ADDRESS, address)
        self.storage.write_relative_bank(address, 0o777)
        self.storage.unpack_instruction()
        Instructions.RAM.determine_effective_address(self.storage)
        assert self.storage.s_register == address
        assert Instructions.RAM.perform_logic(self.hardware) == 4
        assert self.storage.run_stop_status
        assert not self.storage.err_status
        assert self.storage.s_register == address
        assert self.storage.read_relative_bank(self.storage.s_register) == 0o1000
        assert self.storage.a_register == 0o1000
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_DOUBLE_WORD_INSTRUCTION_ADDRESS)

    def test_rs1(self) -> None:
        # RS1
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0114)
        self.storage.unpack_instruction()
        self.storage.z_register = 0o4020
        self.storage.a_register = 0o4020
        Instructions.RS1.determine_effective_address(self.storage)
        assert Instructions.RS1.perform_logic(self.hardware) == 1
        assert self.storage.run_stop_status
        assert self.storage.z_register == 0o4020
        assert self.storage.a_register == 0o6010
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_rs2(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0115)
        self.storage.unpack_instruction()
        self.storage.z_register = 0o0007
        self.storage.z_to_a()
        Instructions.RS2.determine_effective_address(self.storage)
        assert Instructions.RS2.perform_logic(self.hardware) == 1
        assert self.storage.run_stop_status
        assert self.storage.z_register == 0o0007
        assert self.storage.a_register == 0o0001
        self.storage.z_register = 0o4007
        self.storage.z_to_a()
        assert Instructions.RS2.perform_logic(self.hardware) == 1
        assert self.storage.run_stop_status
        assert self.storage.z_register == 0o4007
        assert self.storage.a_register == 0o7001

    def test_sbu(self) -> None:
        assert Instructions.SBU.name() == "SBU"
        self.storage.a_register = 0o200
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0146)
        self.storage.unpack_instruction()
        Instructions.SBU.determine_effective_address(self.storage)
        assert self.storage.get_program_counter() == INSTRUCTION_ADDRESS
        assert Instructions.SBU.perform_logic(self.hardware) == 1
        assert self.storage.buffer_storage_bank == 0o06
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_scb(self) -> None:
        assert Instructions.SCB.name() == "SCB"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o1702)
        self.storage.unpack_instruction()
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS - 0o02, 0o14)
        self.storage.a_register = 0o12
        Instructions.SCB.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS - 0o02
        assert Instructions.SCB.perform_logic(self.hardware) == 2
        assert self.storage.z_register == 0o14
        assert self.storage.a_register == 0o06
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_scc(self) -> None:
        assert Instructions.SCC.name() == "SCC"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o1600)
        self.storage.write_relative_bank(G_ADDRESS, 0o14)
        self.storage.unpack_instruction()
        self.storage.a_register = 0o12
        Instructions.SCC.determine_effective_address(self.storage)
        assert self.storage.s_register == G_ADDRESS
        assert Instructions.SCC.perform_logic(self.hardware) == 2
        assert self.storage.z_register == 0o14
        assert self.storage.a_register == 0o06
        assert not self.storage.err_status
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_DOUBLE_WORD_INSTRUCTION_ADDRESS)

    def test_scd(self) -> None:
        assert Instructions.SCD.name() == "SCD"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o1424)
        self.storage.unpack_instruction()
        self.storage.write_direct_bank(0o24, 0o14)
        self.storage.a_register = 0o12
        Instructions.SCD.determine_effective_address(self.storage)
        assert self.storage.s_register == 0o24
        assert Instructions.SCD.perform_logic(self.hardware) == 2
        assert self.storage.z_register == 0o14
        assert self.storage.a_register == 0o06
        assert not self.storage.err_status
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_scf(self) -> None:
        assert Instructions.SCF.name() == "SCF"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o1624)
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS + 0o24, 0o14)
        self.storage.a_register = 0o12
        self.storage.unpack_instruction()
        Instructions.SCF.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 0o24
        assert Instructions.SCF.perform_logic(self.hardware) == 2
        assert self.storage.z_register == 0o14
        assert self.storage.a_register == 0o006
        assert not self.storage.err_status
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_sci(self) -> None:
        assert Instructions.SCI.name() == "SCI"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o1524)
        self.storage.unpack_instruction()
        self.storage.write_indirect_bank(0o24, 0o14)
        self.storage.a_register = 0o12
        Instructions.SCI.determine_effective_address(self.storage)
        assert self.storage.s_register == 0o24
        assert Instructions.SCI.perform_logic(self.hardware) == 3
        assert self.storage.z_register == 0o14
        assert self.storage.a_register == 0o06
        assert not self.storage.err_status
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_scm(self) -> None:
        assert Instructions.SCM.name() == "SCM"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o1500)
        self.storage.write_relative_bank(G_ADDRESS, READ_AND_WRITE_ADDRESS)
        self.storage.unpack_instruction()
        self.storage.write_relative_bank(READ_AND_WRITE_ADDRESS, 0o14)
        self.storage.a_register = 0o12
        Instructions.SCM.determine_effective_address(self.storage)
        assert self.storage.s_register == READ_AND_WRITE_ADDRESS
        Instructions.SCM.perform_logic(self.hardware)
        assert self.storage.z_register == 0o14
        assert self.storage.a_register == 0o06
        assert not self.storage.err_status
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_DOUBLE_WORD_INSTRUCTION_ADDRESS)

    def test_scn(self) -> None:
        assert Instructions.SCN.name() == "SCN"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0314)
        self.storage.unpack_instruction()
        self.storage.a_register = 0o12
        Instructions.SCN.determine_effective_address(self.storage)
        assert self.storage.get_program_counter() == INSTRUCTION_ADDRESS
        assert Instructions.SCN.perform_logic(self.hardware) == 1
        assert not self.storage.err_status
        assert self.storage.a_register == 0o6
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_scs(self) -> None:
        assert Instructions.SCS.name() == "SCS"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o14)
        self.storage.write_specific(0o14)
        self.storage.a_register = 0o12
        Instructions.SCS.determine_effective_address(self.storage)
        assert self.storage.get_program_counter() == INSTRUCTION_ADDRESS
        assert Instructions.SCS.perform_logic(self.hardware) == 2
        assert self.storage.z_register == 0o14
        assert self.storage.a_register == 0o06
        assert not self.storage.err_status
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_sdb(self) -> None:
        # STB 15
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o4315)
        self.storage.a_register = 0o0210
        self.storage.unpack_instruction()
        Instructions.STB.determine_effective_address(self.storage)
        assert Instructions.STB.perform_logic(self.hardware) == 3
        assert self.storage.z_register == 0o0210
        assert self.storage.read_relative_bank(
            INSTRUCTION_ADDRESS - 0o15) == 0o0210
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_sdc(self) -> None:
        assert Instructions.SDC.name() == "SDC"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0046)
        self.storage.unpack_instruction()
        Instructions.SDC.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS
        assert Instructions.SDC.perform_logic(self.hardware) == 1
        assert self.storage.direct_storage_bank == 0o06
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_sic(self) -> None:
        assert Instructions.SIC.name() == "SIC"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o26)
        self.storage.unpack_instruction()
        Instructions.SIC.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS
        assert Instructions.SIC.perform_logic(self.hardware) == 1
        assert self.storage.indirect_storage_bank == 0o06
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_sid(self) -> None:
        assert Instructions.SID.name() == "SID"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o66)
        self.storage.unpack_instruction()
        Instructions.SID.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS
        assert Instructions.SID.perform_logic(self.hardware) == 1
        assert self.storage.direct_storage_bank == 0o06
        assert self.storage.indirect_storage_bank == 0o06
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_sjs_halt_and_branch(self) -> None:
        assert Instructions.SJS.name() == "SJS"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o7712)
        self.storage.unpack_instruction()
        self.storage.write_relative_bank(G_ADDRESS, 0o200)
        self.storage.set_jump_switch_mask(0o3)
        self.storage.set_stop_switch_mask(0o6)
        Instructions.SJS.determine_effective_address(self.storage)
        assert self.storage.s_register == G_ADDRESS
        assert Instructions.SJS.perform_logic(self.hardware) == 2
        assert not self.storage.run_stop_status
        self.storage.advance_to_next_instruction()
        assert self.storage.get_program_counter() == 0o200

    def test_sls_halt_and_no_branch(self) -> None:
        assert Instructions.SJS.name() == "SJS"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o7712)
        self.storage.unpack_instruction()
        self.storage.write_relative_bank(G_ADDRESS, 0o200)
        self.storage.set_jump_switch_mask(0o6)
        self.storage.set_stop_switch_mask(0o6)
        Instructions.SJS.determine_effective_address(self.storage)
        assert self.storage.s_register == G_ADDRESS
        assert Instructions.SJS.perform_logic(self.hardware) == 1
        assert not self.storage.run_stop_status
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_DOUBLE_WORD_INSTRUCTION_ADDRESS)

    def test_sls_no_halt_and_branch(self):
        assert Instructions.SJS.name() == "SJS"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o7712)
        self.storage.unpack_instruction()
        self.storage.write_relative_bank(G_ADDRESS, 0o200)
        self.storage.set_jump_switch_mask(0o3)
        self.storage.set_stop_switch_mask(0o5)
        Instructions.SJS.determine_effective_address(self.storage)
        assert self.storage.s_register == G_ADDRESS
        assert Instructions.SJS.perform_logic(self.hardware) == 2
        assert self.storage.run_stop_status
        self.storage.advance_to_next_instruction()
        assert self.storage.get_program_counter() == 0o200

    def test_sls_no_halt_no_branch(self) -> None:
        assert Instructions.SJS.name() == "SJS"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o7712)
        self.storage.unpack_instruction()
        self.storage.write_relative_bank(G_ADDRESS, 0o200)
        self.storage.set_jump_switch_mask(0o6)
        self.storage.set_stop_switch_mask(0o5)
        Instructions.SJS.determine_effective_address(self.storage)
        assert self.storage.s_register == G_ADDRESS
        assert Instructions.SJS.perform_logic(self.hardware) == 1
        assert self.storage.run_stop_status
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_DOUBLE_WORD_INSTRUCTION_ADDRESS)

    def test_slj_branch(self) -> None:
        assert Instructions.SLJ.name() == "SLJ"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o7760)
        self.storage.unpack_instruction()
        self.storage.write_relative_bank(G_ADDRESS, 0o200)
        self.storage.set_jump_switch_mask(0o5)
        Instructions.SLJ.determine_effective_address(self.storage)
        assert self.storage.s_register == G_ADDRESS
        assert Instructions.SLJ.perform_logic(self.hardware) == 2
        self.storage.advance_to_next_instruction()
        assert self.storage.get_program_counter() == 0o200

    def test_slj_no_branch(self) -> None:
        assert Instructions.SLJ.name() == "SLJ"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o7760)
        self.storage.unpack_instruction()
        self.storage.write_relative_bank(G_ADDRESS, 0o200)
        self.storage.set_jump_switch_mask(0o1)
        Instructions.SLJ.determine_effective_address(self.storage)
        assert self.storage.s_register == G_ADDRESS
        assert Instructions.SLJ.perform_logic(self.hardware) == 1
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_DOUBLE_WORD_INSTRUCTION_ADDRESS)

    def test_sls_halt(self) -> None:
        assert Instructions.SLS.name() == "SLS"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o7702)
        self.storage.unpack_instruction()
        self.storage.set_stop_switch_mask(0o6)
        Instructions.SLJ.determine_effective_address(self.storage)
        assert self.storage.s_register == G_ADDRESS
        assert Instructions.SLS.perform_logic(self.hardware) == 1
        assert not self.storage.run_stop_status
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_sls_no_halt(self) -> None:
        assert Instructions.SLS.name() == "SLS"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o7702)
        self.storage.unpack_instruction()
        self.storage.set_stop_switch_mask(0o5)
        Instructions.SLJ.determine_effective_address(self.storage)
        assert self.storage.s_register == G_ADDRESS
        assert Instructions.SLS.perform_logic(self.hardware) == 1
        assert self.storage.run_stop_status
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_srj(self) -> None:
        assert Instructions.SRJ.name() == "SRJ"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0016)
        self.storage.unpack_instruction()
        self.storage.a_register = 0o200
        Instructions.SRJ.determine_effective_address(self.storage)
        assert self.storage.get_program_counter() == INSTRUCTION_ADDRESS
        assert Instructions.SRJ.perform_logic(self.hardware) == 1
        assert self.storage.relative_storage_bank == 0o06
        self.storage.advance_to_next_instruction()
        assert self.storage.get_program_counter() == 0o200

    def test_sdd(self) -> None:
        # STD 15
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o4015)
        self.storage.a_register = 0o0210
        self.storage.unpack_instruction()
        Instructions.STD.determine_effective_address(self.storage)
        assert Instructions.STD.perform_logic(self.hardware) == 3
        assert self.storage.z_register == 0o0210
        assert self.storage.read_direct_bank(0o15) == 0o0210
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_sbb(self) -> None:
        assert Instructions.SBB.name() == "SBB"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o3703)
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS - 3, 0o77)
        self.storage.a_register = 0o4420
        self.storage.unpack_instruction()
        Instructions.SBB.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS - 3
        assert Instructions.SBB.perform_logic(self.hardware) == 2
        assert self.storage.z_register == 0o77
        assert self.storage.a_register == 0o4321
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_sbc(self) -> None:
        assert Instructions.SBC.name() == "SBC"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o3600)
        self.storage.a_register = 0o5555
        self.storage.write_relative_bank(G_ADDRESS, 0o1234)
        self.storage.unpack_instruction()
        Instructions.SBC.determine_effective_address(self.storage)
        assert self.storage.s_register == G_ADDRESS
        assert Instructions.SBC.perform_logic(self.hardware) == 2
        assert self.storage.z_register == 0o1234
        assert self.storage.a_register -- 0o4321
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_DOUBLE_WORD_INSTRUCTION_ADDRESS)

    def test_sbd(self) -> None:
        assert Instructions.SBD.name() == "SBD"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o3440)
        self.storage.write_direct_bank(0o40, 0o14)
        self.storage.a_register = 0o4335
        self.storage.unpack_instruction()
        Instructions.SBD.determine_effective_address(self.storage)
        assert self.storage.s_register == 0o40
        assert Instructions.SBD.perform_logic(self.hardware) == 2
        assert self.storage.z_register == 0o14
        assert self.storage.a_register == 0o4321
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_sbf(self) -> None:
        assert Instructions.SBF.name() == "SBF"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o3603)
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS + 3, 0o1234)
        self.storage.a_register = 0o5555
        self.storage.unpack_instruction()
        Instructions.SBF.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 3
        assert Instructions.SBF.perform_logic(self.hardware) == 2
        assert self.storage.z_register == 0o1234
        assert self.storage.a_register == 0o4321
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_sbi(self) -> None:
        assert Instructions.SBI.name() == "SBI"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o3510)
        self.storage.write_indirect_bank(0o10, 0o13)
        self.storage.a_register = 0o4334
        self.storage.unpack_instruction()
        Instructions.SBI.determine_effective_address(self.storage)
        assert self.storage.s_register == 0o10
        assert Instructions.SBI.perform_logic(self.hardware) == 3
        assert self.storage.z_register == 0o13
        assert self.storage.a_register == 0o4321
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_srb(self) -> None:
        assert Instructions.SRB.name() == "SRB"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o4702)
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS - 2, 0o4001)
        self.storage.unpack_instruction()
        Instructions.SRB.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS - 2
        assert Instructions.SRB.perform_logic(self.hardware) == 3
        assert self.storage.storage_cycle == MCS_MODE_REL
        assert self.storage.a_register == 0o0003
        assert self.storage.z_register == 0o0003
        assert self.storage.read_relative_bank(
            INSTRUCTION_ADDRESS - 2) == 0o0003
        assert not self.storage.err_status
        assert self.storage.run_stop_status
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_src(self) -> None:
        assert Instructions.SRC.name() == "SRC"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o4600)
        self.storage.write_relative_bank(G_ADDRESS, 0o4001)
        self.storage.unpack_instruction()
        Instructions.SRC.determine_effective_address(self.storage)
        assert self.storage.s_register == G_ADDRESS
        assert Instructions.SRC.perform_logic(self.hardware) == 3
        assert self.storage.storage_cycle == MCS_MODE_REL
        assert self.storage.a_register == 0o0003
        assert self.storage.z_register == 0o0003
        assert self.storage.read_relative_bank(G_ADDRESS) == 0o0003
        assert not self.storage.err_status
        assert self.storage.run_stop_status
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_DOUBLE_WORD_INSTRUCTION_ADDRESS)

    def test_srd(self) -> None:
        assert Instructions.SRD.name() == "SRD"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o4430)
        self.storage.write_direct_bank(0o30, 0o4001)
        self.storage.unpack_instruction()
        Instructions.SRD.determine_effective_address(self.storage)
        assert self.storage.s_register == 0o30
        assert Instructions.SRD.perform_logic(self.hardware) == 3
        assert self.storage.storage_cycle == MCS_MODE_DIR
        assert self.storage.a_register == 0o0003
        assert self.storage.z_register == 0o0003
        assert self.storage.read_direct_bank(0o30) == 0o0003
        assert not self.storage.err_status
        assert self.storage.run_stop_status
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_srf(self) -> None:
        assert Instructions.SRF.name() == "SRF"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o4602)
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS + 2, 0o4001)
        self.storage.unpack_instruction()
        Instructions.SRF.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 2
        assert Instructions.SRF.perform_logic(self.hardware) == 3
        assert self.storage.storage_cycle == MCS_MODE_REL
        assert self.storage.a_register == 0o0003
        assert self.storage.z_register == 0o0003
        assert self.storage.read_relative_bank(
            INSTRUCTION_ADDRESS + 2) == 0o0003

    def test_sri(self) -> None:
        assert Instructions.SRI.name() == "SRI"
        self.storage.write_indirect_bank(0o14, 0o4001)
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o4514)
        self.storage.unpack_instruction()
        Instructions.SRI.determine_effective_address(self.storage)
        assert self.storage.s_register == 0o14
        assert Instructions.SRI.perform_logic(self.hardware) == 4
        assert self.storage.storage_cycle == MCS_MODE_IND
        assert self.storage.a_register == 0o0003
        assert self.storage.z_register == 0o0003
        assert self.storage.read_indirect_bank(0o14) == 0o0003
        assert not self.storage.err_status
        assert self.storage.run_stop_status
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_srm(self) -> None:
        assert Instructions.SRM.name() == "SRM"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o4500)
        self.storage.write_relative_bank(G_ADDRESS, READ_AND_WRITE_ADDRESS)
        self.storage.write_relative_bank(READ_AND_WRITE_ADDRESS, 0o4001)
        self.storage.unpack_instruction()
        Instructions.SRM.determine_effective_address(self.storage)
        assert self.storage.s_register == READ_AND_WRITE_ADDRESS
        assert Instructions.SRM.perform_logic(self.hardware) == 4
        assert self.storage.storage_cycle == MCS_MODE_REL
        assert self.storage.a_register == 0o0003
        assert self.storage.z_register == 0o0003
        assert self.storage.read_relative_bank(
            READ_AND_WRITE_ADDRESS) == 0o0003

    def test_srs(self) -> None:
        assert Instructions.SRS.name() == "SRS"
        self.storage.write_specific(0o4001)
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o4000)
        self.storage.unpack_instruction()
        Instructions.SRS.determine_effective_address(self.storage)
        assert self.storage.s_register == 0o7777
        assert Instructions.SRS.perform_logic(self.hardware) == 3
        assert self.storage.a_register == 0o0003
        assert self.storage.z_register == 0o0003
        assert self.storage.read_specific() == 0o0003

    def test_sbm(self) -> None:
        assert Instructions.SBM.name() == "SBM"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o3500)
        self.storage.write_relative_bank(G_ADDRESS, READ_AND_WRITE_ADDRESS)
        self.storage.write_relative_bank(READ_AND_WRITE_ADDRESS, 0o241)
        self.storage.a_register = 0o4562
        self.storage.unpack_instruction()
        Instructions.SBM.determine_effective_address(self.storage)
        assert self.storage.s_register == READ_AND_WRITE_ADDRESS
        assert Instructions.SBM.perform_logic(self.hardware) == 3
        assert self.storage.z_register == 0o241
        assert self.storage.a_register == 0o4321
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_DOUBLE_WORD_INSTRUCTION_ADDRESS)

    def test_sbn(self) -> None:
        # SBN 40
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0740)
        self.storage.a_register = 0o1274
        self.storage.unpack_instruction()
        Instructions.SBN.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS
        assert Instructions.SBN.perform_logic(self.hardware) == 1
        assert self.storage.z_register == 0o40
        assert self.storage.a_register == 0o1234
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_sbs(self) -> None:
        assert Instructions.SBS.name() == "SBS"
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o3700)
        self.storage.a_register = 0o4420
        self.storage.unpack_instruction()
        Instructions.SBS.determine_effective_address(self.storage)
        assert self.storage.s_register == 0o7777
        assert Instructions.SBS.perform_logic(self.hardware) == 2
        assert self.storage.z_register == 0o77
        assert self.storage.a_register == 0o4321
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_stc(self) -> None:
        # STC 1234
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o4200)
        self.storage.write_relative_bank(G_ADDRESS, 0o1234)
        self.storage.a_register = 0o4321
        self.storage.unpack_instruction()
        Instructions.STC.determine_effective_address(self.storage)
        assert self.storage.s_register == G_ADDRESS
        assert Instructions.STC.perform_logic(self.hardware) == 3
        self.storage.advance_to_next_instruction()
        assert self.storage.z_register == 0o4321
        assert self.storage.read_relative_bank(G_ADDRESS) == 0o4321
        assert (self.storage.get_program_counter() ==
                AFTER_DOUBLE_WORD_INSTRUCTION_ADDRESS)

    def test_ste(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0163)
        self.storage.a_register = 0o5000
        self.storage.buffer_entrance_register = 0o300
        self.storage.unpack_instruction()
        Instructions.STE.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS
        assert Instructions.STE.perform_logic(self.hardware) == 3
        assert self.storage.read_direct_bank(0o63) == 0o300
        assert self.storage.buffer_entrance_register == 0o5000
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_stf(self) -> None:
        assert Instructions.STF.name() == "STF"
        # STF 10
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o4210)
        self.storage.a_register = 0o0210
        self.storage.unpack_instruction()
        Instructions.STF.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 0o10
        Instructions.STF.perform_logic(self.hardware)
        self.storage.advance_to_next_instruction()
        assert self.storage.z_register == 0o0210
        assert (self.storage.read_relative_bank(INSTRUCTION_ADDRESS + 0o10) ==
                0o0210)
        assert self.storage.get_program_counter() == INSTRUCTION_ADDRESS + 1

    def test_sti(self) -> None:
        assert Instructions.STI.name() == "STI"
        # STI 14
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o4114)
        self.storage.a_register = 0o0210
        self.storage.unpack_instruction()
        Instructions.STI.determine_effective_address(self.storage)
        assert Instructions.STI.perform_logic(self.hardware) == 4
        assert self.storage.z_register == 0o0210
        assert self.storage.read_indirect_bank(0o14) == 0o0210
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_stm(self) -> None:
        assert Instructions.STM.name() == "STM"
        # STM 1234
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o4100)
        self.storage.write_relative_bank(G_ADDRESS, READ_AND_WRITE_ADDRESS)
        self.storage.a_register = 0o1234
        self.storage.unpack_instruction()
        Instructions.STM.determine_effective_address(self.storage)
        assert self.storage.s_register == READ_AND_WRITE_ADDRESS
        assert Instructions.STM.perform_logic(self.hardware) == 4
        assert self.storage.z_register == 0o1234
        assert self.storage.read_relative_bank(READ_AND_WRITE_ADDRESS) == 0o1234
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_DOUBLE_WORD_INSTRUCTION_ADDRESS)

    def test_stp(self) -> None:
        assert Instructions.STP.name() == "STP"
        # STP
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0155)
        self.storage.unpack_instruction()
        Instructions.STP.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS
        Instructions.STP.perform_logic(self.hardware)
        assert self.storage.read_direct_bank(0o55) == INSTRUCTION_ADDRESS

    def test_sts(self) -> None:
        # STS
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o4300)
        self.storage.a_register = 0o1234
        self.storage.unpack_instruction()
        Instructions.STS.determine_effective_address(self.storage)
        assert self.storage.s_register == 0o7777
        assert Instructions.STS.perform_logic(self.hardware)
        assert self.storage.z_register == 0o1234
        assert self.storage.read_specific() == 0o1234
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS)

    def test_zjb_a_minus_zero(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6440)
        self.storage.a_register = 0o7777
        self.storage.unpack_instruction()
        Instructions.ZJB.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS - 0o0040
        Instructions.ZJB.perform_logic(self.hardware)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_zjb_a_negative(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6440)
        self.storage.a_register = 0o7777
        self.storage.unpack_instruction()
        Instructions.ZJB.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS - 0o0040
        Instructions.ZJB.perform_logic(self.hardware)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_zjb_a_positive(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6440)
        self.storage.a_register = 1
        self.storage.unpack_instruction()
        Instructions.ZJB.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS - 0o0040
        Instructions.ZJB.perform_logic(self.hardware)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_zjb_a_zero(self) -> None:
        # ZJF
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6440)
        self.storage.a_register = 0
        self.storage.unpack_instruction()
        Instructions.ZJB.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS - 0o0040
        Instructions.ZJB.perform_logic(self.hardware)
        assert self.storage.next_address() == INSTRUCTION_ADDRESS - 0o0040
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == INSTRUCTION_ADDRESS - 0o0040

    def test_zjf_a_minus_zero(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6040)
        self.storage.a_register = 0o7777
        self.storage.unpack_instruction()
        Instructions.ZJF.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 0o0040
        Instructions.ZJF.perform_logic(self.hardware)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_zjf_a_negative(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6040)
        self.storage.a_register = 0o7777
        self.storage.unpack_instruction()
        Instructions.ZJF.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 0o0040
        Instructions.ZJF.perform_logic(self.hardware)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_zjf_a_positive(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6040)
        self.storage.a_register = 1
        self.storage.unpack_instruction()
        Instructions.ZJF.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 0o0040
        Instructions.ZJF.perform_logic(self.hardware)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_zjf_a_zero(self) -> None:
        # ZJF
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o6040)
        self.storage.a_register = 0
        self.storage.unpack_instruction()
        Instructions.ZJF.determine_effective_address(self.storage)
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 0o0040
        Instructions.ZJF.perform_logic(self.hardware)
        assert self.storage.next_address() == INSTRUCTION_ADDRESS + 0o0040
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == INSTRUCTION_ADDRESS + 0o0040

if __name__ == "__main__":
    unittest.main()
