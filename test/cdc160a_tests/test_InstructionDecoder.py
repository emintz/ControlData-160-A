"""
Validates InstructionDecoder.py

Copyright © 2025 The System Source Museum, the authors and maintainers,
and others

This file is part of the System Source Museum Control Data 160-A Emulator.

The System Source Museum Control Data 160-A Emulator is free software: you
can redistribute it and/or modify it under the terms of the GNU General
Public License as published by the Free Software Foundation, either version
3 of the License, or (at your option) any later version.

The System Source Museum Control Data 160-A Emulator is distributed in the
hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with the System Source Museum Control Data 160-A Emulator. If not, see
<https://www.gnu.org/licenses/.
"""

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

    def test_decode_00(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o00)
        assert decoder.opcode == 0o00
        assert decoder.decode(0o00).name() == "ERR"
        for e in range(0o01, 0o10):
            assert decoder.decode(e).name() == "NOP"
        for e in range(0o10, 0o20):
            assert decoder.decode(e).name() == "SRJ"
        for e in range(0o20, 0o30):
            assert decoder.decode(e).name() == "SIC"
        for e in range(0o30, 0o40):
            assert decoder.decode(e).name() == "IRJ"
        for e in range(0o40, 0o50):
            assert decoder.decode(e).name() == "SDC"
        for e in range(0o50, 0o60):
            assert decoder.decode(e).name() == "DRJ"
        for e in range(0o60, 0o70):
            assert decoder.decode(e).name() == "SID"
        for e in range(0o70, 0o100):
            assert decoder.decode(e).name() == "ACJ"

    def test_decode_01(self) -> None:
        decoder = InstructionDecoder.decoder_at(0x01)
        assert decoder.opcode == 0o01
        for e in range(0o00, 0o100):
            instruction_name = decoder.decode(e).name()
            if 0o40 <= e < 0o50:
                assert instruction_name == "SBU"
            elif 0o50 <= e < 0o60:
                assert instruction_name == "STP"
            elif 0o60 <= e < 0o70:
                assert instruction_name == "STE"
            elif 0o70 <= e < 0o100:
                assert instruction_name == "NOP"
            else:
                match e:
                    case 0o00:
                        assert instruction_name == "BLS"
                    case 0o01:
                        assert instruction_name == "PTA"
                    case 0o02:
                        assert instruction_name == "LS1"
                    case 0o03:
                        assert instruction_name == "LS2"
                    case 0o04:
                        assert instruction_name == "CBC"
                    case 0o05:
                        assert instruction_name == "ATE"
                    case 0o06:
                        assert instruction_name == "ATX"
                    case 0o07:
                        assert instruction_name == "ETA"
                    case 0o10:
                        assert instruction_name == "LS3"
                    case 0o11:
                        assert instruction_name == "LS6"
                    case 0o12:
                        assert instruction_name == "MUT"
                    case 0o13:
                        assert instruction_name == "MUH"
                    case 0o14:
                        assert instruction_name == "RS1"
                    case 0o15:
                        assert instruction_name == "RS2"
                    case 0o15:
                        assert instruction_name == "NOP"
                    case 0o16:
                        assert instruction_name == "NOP"
                    case 0o17:
                        assert instruction_name == "NOP"
                    case 0o20:
                        assert instruction_name == "CIL"
                    case 0o30:
                        assert instruction_name == "CTA"
                    case _:
                        assert instruction_name == "ERR", \
                               f"At {e} expected ERR and got {instruction_name}"

    def test_decode_02(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o02)
        assert decoder.opcode == 0o02
        for e in range(0, 0o100):
            assert decoder.decode(e).name() == "LPN"

    def test_decode_03(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o03)
        assert decoder.opcode == 0o03
        for e in range(0, 0o100):
            assert decoder.decode(e).name() == "SCN"

    def test_decode_04(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o04)
        assert decoder.opcode == 0o04
        for e in range(0, 0o100):
            assert decoder.decode(e).name() == "LDN"

    def test_decode_05(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o05)
        assert decoder.opcode == 0o05
        for e in range(0o00, 0o100):
            assert decoder.decode(e).name() == "LCN"

    def test_decode_06(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o06)
        assert decoder.opcode == 0o06
        for e in range(0o00, 0o100):
            assert decoder.decode(e).name() == "ADN"

    def test_decode_07(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o07)
        assert decoder.opcode == 0o07
        for e in range(0, 0o100):
            assert decoder.decode(e).name() == "SBN"

    def test_decode_10(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o10)
        assert decoder.opcode == 0o10
        for e in range(0, 0o100):
            assert decoder.decode(e).name() == "LPD"

    def test_decode_11(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o11)
        assert decoder.opcode == 0o11
        assert decoder.decode(0o00).name() == "LPM"
        for e in range(0o01, 0o100):
            assert decoder.decode(e).name() == "LPI"

    def test_decode_12(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o12)
        assert decoder.opcode == 0o12
        assert decoder.decode(0o00).name() == "LPC"
        for e in (0o01, 0o100):
            assert decoder.decode(e).name() == "LPF"

    def test_decode_13(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o13)
        assert decoder.opcode == 0o13
        assert decoder.decode(0o00).name() == "LPS"
        for e in range(0o01, 0o100):
            assert decoder.decode(e).name() == "LPB"

    def test_decode_14(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o14)
        assert decoder.opcode == 0o14
        for e in range(0, 0o100):
            assert decoder.decode(e).name() == "SCD"

    def test_decode_15(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o15)
        assert decoder.opcode == 0o15
        assert decoder.decode(0).name() == "SCM"
        for e in range(1, 0o100):
            assert decoder.decode(e).name() == "SCI"

    def test_decode_16(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o16)
        assert decoder.decode(0).name() == "SCC"
        for e in range(1, 0o100):
            assert decoder.decode(e).name() == "SCF"

    def test_decode_17(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o17)
        assert decoder.opcode == 0o17
        assert decoder.decode(0).name() == "SCS"
        for e in range(1, 0o100):
            assert decoder.decode(e).name() == "SCB"

    def test_decode_20(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o20)
        assert decoder.opcode == 0o20
        for e in range(0, 0o100):
            assert decoder.decode(e).name() == "LDD"

    def test_decode_21(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o21)
        assert decoder.opcode == 0o21
        assert decoder.decode(0).name() == "LDM"
        for e in range(1, 0o100):
            assert decoder.decode(e).name() == "LDI"

    def test_decode_22(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o22)
        assert decoder.opcode == 0o22
        assert decoder.decode(0).name() == "LDC"
        for e in range(1, 0o100):
            assert decoder.decode(e).name() == "LDF"

    def test_decode_23(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o23)
        assert decoder.opcode == 0o23
        assert decoder.decode(0).name() == "LDS"
        for e in range(1, 0o100):
            assert decoder.decode(e).name() == "LDB"

    def test_decode_24(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o24)
        assert decoder.opcode == 0o24
        for e in range(0, 0o100):
            assert decoder.decode(e).name() == "LCD"

    def test_decode_25(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o25)
        assert decoder.opcode == 0o25
        assert decoder.decode(0).name() == "LCM"
        for e in range(1, 0o100):
            assert decoder.decode(e).name() == "LCI"

    def test_decode_26(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o26)
        assert decoder.opcode == 0o26
        assert decoder.decode(0).name() == "LCC"
        for e in range(1, 0o100):
            assert decoder.decode(e).name() == "LCF"

    def test_decode_27(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o27)
        assert decoder.opcode == 0o27
        assert decoder.decode(0).name() == "LCS"
        for e in range(1, 0o100):
            assert decoder.decode(e).name() == "LCB"

    def test_decode_30(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o30)
        assert decoder.opcode == 0o30
        for e in range(0o00, 0o100):
            assert decoder.decode(e).name() == "ADD"

    def test_decode_31(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o31)
        assert decoder.opcode == 0o31
        assert decoder.decode(0).name() == "ADM"
        for e in range(0o01, 0o100):
            assert decoder.decode(e).name() == "ADI"

    def test_decode_32(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o32)
        assert decoder.opcode == 0o32
        assert decoder.decode(0).name() == "ADC"
        for e in range(0o01, 0o100):
            assert decoder.decode(e).name() == "ADF"

    def test_decode_34(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o34)
        assert decoder.opcode == 0o34
        for e in range(0o00, 0o100):
            assert decoder.decode(e).name() == "SBD"

    def test_decode_35(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o35)
        assert decoder.opcode == 0o35
        assert decoder.decode(0o00).name() == "SBM"
        for e in range(1, 0o100):
            assert decoder.decode(e).name() == "SBI"

    def test_decode_36(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o36)
        assert decoder.opcode == 0o36
        assert decoder.decode(0o00).name() == "SBC"
        for e in range(1, 0o100):
            assert decoder.decode(e).name() == "SBF"

    def test_decode_37(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o37)
        assert decoder.opcode == 0o37
        assert decoder.decode(0).name() == "SBS"
        for e in range(1, 0o100):
            assert decoder.decode(e).name() == "SBB"

    def test_decode_40(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o40)
        assert decoder.opcode == 0o40
        for e in range(0, 0o100):
            assert decoder.decode(e).name() == "STD"

    def test_decode_41(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o41)
        assert decoder.opcode == 0o41
        assert decoder.decode(0).name() == "STM"
        for e in range(1, 0o100):
            assert decoder.decode(e).name() == "STI"

    def test_decode_42(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o42)
        assert decoder.opcode == 0o42
        assert decoder.decode(0).name() == "STC"
        for e in range(1, 0o100):
            assert decoder.decode(e).name() == "STF"

    def test_decode_43(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o43)
        assert decoder.opcode == 0o43
        assert decoder.decode(0).name() == "STS"
        for e in range(1, 0o100):
            assert decoder.decode(e).name() == "STB"

    def test_decode_44(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o44)
        assert decoder.opcode == 0o44
        for e in range(0, 0o100):
            assert decoder.decode(e).name() == "SRD"

    def test_decode_45(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o45)
        assert decoder.opcode == 0o45
        assert decoder.decode(0).name() == "SRM"
        for e in range(1, 0o100):
            assert decoder.decode(e).name() == "SRI"

    def test_decode_46(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o46)
        assert decoder.opcode == 0o46
        assert decoder.decode(0).name() == "SRC"
        for e in range(1, 0o100):
            assert decoder.decode(e).name() == "SRF"

    def test_decode_47(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o47)
        assert decoder.opcode == 0o47
        assert decoder.decode(0).name() == "SRS"
        for e in range(1, 0o100):
            assert decoder.decode(e).name() == "SRB"

    def test_decode_50(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o50)
        assert decoder.opcode == 0o50
        for e in range(0, 0o100):
            assert decoder.decode(e).name() == "RAD"

    def test_decide_51(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o51)
        assert decoder.opcode == 0o51
        assert decoder.decode(0o00).name() == "RAM"
        for e in (1, 0o100):
            assert decoder.decode(e).name() == "RAI"

    def test_decode_52(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o52)
        assert decoder.opcode == 0o52
        assert decoder.decode(0).name() == "RAC"
        for e in range(1, 0o100):
            assert decoder.decode(e).name() == "RAF"

    def test_decode_53(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o53)
        assert decoder.opcode == 0o53
        assert decoder.decode(0).name() == "RAS"
        for e in range(1, 0o100):
            assert decoder.decode(3).name() == "RAB"

    def test_decode_54(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o54)
        assert decoder.opcode == 0o54
        for e in range(0, 0o100):
            assert decoder.decode(e).name() == "AOD"

    def test_decode_55(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o55)
        assert decoder.opcode == 0o55
        assert decoder.decode(0o00).name() == "AOM"
        for e in range(1, 0o100):
            assert decoder.decode(e).name() == "AOI"

    def test_decode_56(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o56)
        assert decoder.opcode == 0o56
        assert decoder.decode(0).name() == "AOC"
        for e in range(1, 0o100):
            assert decoder.decode(e).name() == "AOF"

    def test_decode_57(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o57)
        assert decoder.opcode == 0o57
        assert decoder.decode(0).name() == "AOS"
        for e in range(1, 0o100):
            assert decoder.decode(e).name() == "AOB"

    def test_decode_60(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o60)
        assert decoder.opcode == 0o60
        for e in range(0o00, 0o100):
            assert decoder.decode(e).name() == "ZJF"

    def test_decode_61(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o61)
        assert decoder.opcode == 0o61
        for e in range(0o00, 0o100):
            assert decoder.decode(e).name() == "NZF"

    def test_decode_62(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o62)
        assert decoder.opcode == 0o62
        for e in range(0o00, 0o100):
            assert decoder.decode(e).name() == "PJF"

    def test_decode_63(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o63)
        assert decoder.opcode == 0o63
        for e in range(0o00, 0o100):
            assert decoder.decode(e).name() == "NJF"

    def test_decode_64(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o64)
        assert decoder.opcode == 0o64
        for e in range(0o00, 0o100):
            assert decoder.decode(e).name() == "ZJB"

    def test_decode_65(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o65)
        assert decoder.opcode == 0o65
        for e in range(0o00, 0o100):
            assert decoder.decode(e).name() == "NZB"

    def test_decode_66(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o66)
        assert decoder.opcode == 0o66
        for e in range(0o00, 0o100):
            assert decoder.decode(e).name() == "PJB"

    def test_decode_67(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o67)
        assert decoder.opcode == 0o67
        for e in range(0o00, 0o100):
            assert decoder.decode(e).name() == "NJB"

    def test_decode_70(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o70)
        assert decoder.opcode == 0o70
        for e in range(0, 0o100):
            assert decoder.decode(e).name() == "JPI"

    def test_decode_71(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o71)
        assert decoder.opcode == 0o71
        assert decoder.decode(0).name() == "JPR"
        for e in range(1, 0o100):
            assert decoder.decode(e).name() == "JFI"

    def test_decode_72(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o72)
        assert decoder.opcode == 0o72
        assert decoder.decode(0).name() == "IBI"
        for e in range(1, 0o100):
            assert decoder.decode(e).name() == "INP"

    def test_decode_73(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o73)
        assert decoder.opcode == 0o73
        assert decoder.decode(0o00).name() == "IBO"
        for e in range(0o01, 0o100):
            assert decoder.decode(e).name() == "OUT"

    def test_decode_74(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o74)
        assert decoder.opcode == 0o74
        for e in range(0o00, 0o100):
            assert decoder.decode(e).name() == "OTN"

    def test_decode_75(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o75)
        assert decoder.opcode == 0o75
        assert decoder.decode(0o00).name() == "EXC"
        for e in range(0o01, 0o100):
            assert decoder.decode(e).name() == "EXF"

    def test_decode_76(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o76)
        assert decoder.opcode == 0o76
        assert decoder.decode(0o00).name() == "INA"
        for e in range(0o01, 0o77):
            assert decoder.decode(e).name() == "HWI"
        assert decoder.decode(0o77).name() == "OTA"

    def test_decode_77(self) -> None:
        decoder = InstructionDecoder.decoder_at(0o77)
        assert decoder.opcode == 0o77
        assert decoder.decode(0o00).name() == "HLT"
        assert decoder.decode(0o77).name() == "HLT"
        for e in range(0o01, 0o77):
            expected_name = "SJS"
            if e & 0o07 == 0:
                expected_name = "SLJ"
            elif e & 0o70 == 0:
                expected_name = "SLS"
            assert decoder.decode(e).name() == expected_name

    if __name__ == "__main__":
        unittest.main()
