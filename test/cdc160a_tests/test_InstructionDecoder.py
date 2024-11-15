import unittest
from unittest import TestCase

from InstructionDecoder import decode
from InstructionDecoder import decoder_at
from cdc160a import InstructionDecoder
from cdc160a import Instructions

class Test(TestCase):
    def test_singleton(self):
        target = InstructionDecoder.Singleton(Instructions.ERR, 0)
        for e in range(0o00, 0o77):
            assert target.decode(e) == Instructions.ERR


    def test_bimodal(self):
        target = InstructionDecoder.Bimodal(Instructions.LDC, Instructions.LDI, 0)
        assert target.decode(0o00) == Instructions.LDC
        for e in range(0o01, 0o77):
            assert target.decode(e) == Instructions.LDI

    def test_unimplemented(self):
        target = InstructionDecoder.Singleton(Instructions.ERR, 0)
        for e in range(0o00, 0o77):
            assert target.decode(e) == Instructions.ERR

    def test_verify_opcode_1_decoder(self) -> None:
        decoder_00 = decoder_at(0o01)
        assert decoder_00.opcode == 0o01


    def test_decode_singleton(self) -> None:
        assert decoder_at(0o04).opcode == 0o04
        expected_instruction = Instructions.LDN
        for e in range(0o00, 0o77):
            instruction = decode(0o04, e)
            assert instruction.name() == expected_instruction.name()

    def test_decode_01(self) -> None:
        decoder = InstructionDecoder.decoder_at(0x01)
        assert decoder.opcode == 0o01
        for e in range(0o00, 0o100):
            instruction_name = decoder.decode(e).name()
            match e:
                case 0o00:
                    assert instruction_name == "ERR"
                case 0o02:
                    assert instruction_name == "LS1"
                case 0o03:
                    assert instruction_name == "LS2"
                case 0o10:
                    assert instruction_name == "LS3"
                case 0o11:
                    assert instruction_name == "LS6"
                case 0o14:
                    assert instruction_name == "RS1"
                case 0o15:
                    assert instruction_name == "RS2"
                case _:
                    assert instruction_name == "ERR", \
                           f"At {e} expected ERR and got {instruction_name}"



    if __name__ == "__main__":
        unittest.main()
