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

    def test_decode_02(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o02)
        for e in range(0, 0o100):
            assert decoder.decode(e).name() == "LPN"

    def test_decode_04(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o04)
        for e in range(0, 0o100):
            assert decoder.decode(e).name() == "LDN"

    def test_decode_05(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o05)
        for e in range(0o00, 0o100):
            assert decoder.decode(e).name() == "LCN"

    def test_decode_06(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o06)
        for e in range(0o00, 0o100):
            assert decoder.decode(e).name() == "ADN"

    def test_decode_07(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o07)
        for e in range(0, 0o100):
            assert decoder.decode(e).name() == "SBN"

    def test_decode_10(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o10)
        for e in range(0, 0o100):
            assert decoder.decode(e).name() == "LPD"

    def test_decode_11(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o11)
        assert decoder.decode(0o00).name() == "LPM"
        for e in range(0o01, 0o100):
            assert decoder.decode(e).name() == "LPI"

    def test_decode_12(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o12)
        assert decoder.decode(0o00).name() == "LPC"
        for e in (0o01, 0o100):
            assert decoder.decode(e).name() == "LPF"

    def test_decode_13(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o13)
        assert decoder.decode(0o00).name() == "LPS"
        for e in range(0o01, 0o100):
            assert decoder.decode(e).name() == "LPB"

    def test_decode_30(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o30)
        for e in range(0o00, 0o100):
            assert decoder.decode(e).name() == "ADD"

    def test_decode_31(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o31)
        assert decoder.decode(0).name() == "ADM"
        for e in range(0o01, 0o100):
            assert decoder.decode(e).name() == "ADI"

    def test_decode_32(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o32)
        assert decoder.decode(0).name() == "ADC"
        for e in range(0o01, 0o100):
            assert decoder.decode(e).name() == "ADF"

    def test_decode_34(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o34)
        for e in range(0o00, 0o100):
            assert decoder.decode(e).name() == "SBD"

    def test_decode_35(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o35)
        assert decoder.decode(0o00).name() == "SBM"
        for e in range(1, 0o100):
            assert decoder.decode(e).name() == "SBI"

    def test_decode_36(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o36)
        assert decoder.decode(0o00).name() == "SBC"
        for e in range(1, 0o100):
            assert decoder.decode(e).name() == "SBF"

    def test_decode_37(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o37)
        assert decoder.decode(0).name() == "SBS"
        for e in range(1, 0o100):
            assert decoder.decode(e).name() == "SBB"

    def test_decode_50(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o50)
        for e in range(0, 0o100):
            assert decoder.decode(e).name() == "RAD"

    def test_decide_51(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o51)
        assert decoder.decode(0o00).name() == "RAM"
        for e in (1, 0o100):
            assert decoder.decode(e).name() == "RAI"

    def test_decode_52(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o52)
        assert decoder.decode(0).name() == "RAC"
        for e in range(1, 0o100):
            assert decoder.decode(e).name() == "RAF"

    def test_decode_53(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o53)
        assert decoder.decode(0).name() == "RAS"
        for e in range(1, 0o100):
            assert decoder.decode(3).name() == "RAB"

    def test_decode_60(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o60)
        for e in range(0o00, 0o100):
            assert decoder.decode(e).name() == "ZJF"

    def test_decode_61(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o61)
        for e in range(0o00, 0o100):
            assert decoder.decode(e).name() == "NZF"

    def test_decode_62(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o62)
        for e in range(0o00, 0o100):
            assert decoder.decode(e).name() == "PJF"

    def test_decode_63(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o63)
        for e in range(0o00, 0o100):
            assert decoder.decode(e).name() == "NJF"

    def test_decode_64(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o64)
        for e in range(0o00, 0o100):
            assert decoder.decode(e).name() == "ZJB"

    def test_decode_65(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o65)
        for e in range(0o00, 0o100):
            assert decoder.decode(e).name() == "NZB"

    def test_decode_66(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o66)
        for e in range(0o00, 0o100):
            assert decoder.decode(e).name() == "PJB"

    def test_decode_67(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o67)
        for e in range(0o00, 0o100):
            assert decoder.decode(e).name() == "NJB"

    if __name__ == "__main__":
        unittest.main()
