"""
Decodes 12-bit CDC 160-A words into instructions

The instruction interpreter determines the CDC 160-A instruction
that an (F, E) pair represents and returns that instruction. It
exploits the instruction format, a sux bit op-code called F and
a 6-bit address called E. Toe op-code is used to select an instruction
recognizer that examines E to determine the instruction.

There are three types of op-codes. (All number are octal unless otherwise
noted.)

1. Singleton: an op-code that is associated with a single instruction
   no patter its E value, for example

   04 XX  LDN  Load no address

2. Bimodal: op-codes that stand for one address when E is 0 and
   another when E is non-zero, for example

   22 00 XXXX  LDC Load constant
   22 XX       LDF Load forward

3. Irregular: all other op-codes

Instructions are decoded as follows:

1. Use F (the op-code) to pick an op-code decoder.
2. Pass E to the selected op-code decoder's decode() method to get
   the desired instruction. Op-code decoders must provide
   a decode method having the following signature:

   def decode(e: int) -> Instruction
"""
import Instructions
from Instructions import Instruction

class Singleton:
    """
    Decoder for an op-code that has a single meaning for all possible
    E values.
    """
    def __init__(self, instruction: Instruction, opcode: int):
        self.__instruction = instruction
        self.opcode = opcode

    def decode(self, _) -> Instruction:
        return self.__instruction

class Bimodal:
    """
    Decoder for bimodal op-codes, which means one instruction when e == 0
    and another when e != 0
    """
    def __init__(self, e_zero: Instruction, e_nonzero: Instruction, opcode: int):
        self.__e_zero = e_zero
        self.__e_nonzero = e_nonzero
        self.opcode = opcode

    def decode(self, e: int) -> Instruction:
        if e == 0:
            return self.__e_zero
        else:
            return self.__e_nonzero

class Unimplemented:
    """
    Temporary interpreter for as-yet unsupported op-codes.
    """
    def decode(self, _) -> Instruction:
        return Instructions.ERR

class Opcode00:

    def __init__(self):
        self.opcode = 0o00

    def decode(self, e: int) -> Instruction:
        decoded_instruction = Instructions.ERR
        if e in range(0o01, 0o010) :
            decoded_instruction = Instructions.NOP
        return decoded_instruction

class OpCode01:
    # TODO(emintz): the remaining instructions
    __e_to_instruction = {
        0o00: Instructions.ERR,
        0o02: Instructions.LS1,
        0o03: Instructions.LS2,
        0o10: Instructions.LS3,
        0o11: Instructions.LS6,
        0o12: Instructions.MUT,
        0o13: Instructions.MUH,
        0o14: Instructions.RS1,
        0o15: Instructions.RS2,
    }

    def __init__(self):
        self.opcode = 0o01

    def decode(self, e: int) -> Instruction:
        return Instructions.ERR if e not in self.__e_to_instruction \
            else self.__e_to_instruction[e]

class OpCode77:
    def __init__(self):
        self.opcode = 0o77

    def decode(self, e: int) -> Instruction:
        if e == 0o00 or e == 0o77:
            return Instructions.HLT
        # TODO(emintz): missing values of E
        return Instructions.ERR

__UNIMPLEMENTED = Unimplemented()

__DECODERS = [
    Opcode00(),                                                  # 00
    OpCode01(),                                                  # 01
    Singleton(Instructions.LPN, 0o02),                   # 02
    Singleton(Instructions.SCN, 0o03),                   # 03
    Singleton(Instructions.LDN, 0o04),                   # 04
    Singleton(Instructions.LCN, 0o05),                   # 05
    Singleton(Instructions.ADN, 0o06),                   # 06
    Singleton(Instructions.SBN, 0o07),                   # 07
    Singleton(Instructions.LPD, 0o10),                   # 10
    Bimodal(Instructions.LPM, Instructions.LPI, 0o11),   # 11
    Bimodal(Instructions.LPC, Instructions.LPF, 0o12),   # 12
    Bimodal(Instructions.LPS, Instructions.LPB, 0o13),   # 13
    Singleton(Instructions.SCD, 0o14),                   # 14
    Bimodal(Instructions.SCM, Instructions.SCI, 0o15),   # 15
    Bimodal(Instructions.SCC, Instructions.SCF, 0o16),   # 16
    Bimodal(Instructions.SCS, Instructions.SCB, 0o17),   # 17
    Singleton(Instructions.LDD, 0o20),                   # 20
    Bimodal(Instructions.LDM, Instructions.LDI, 0o21),   # 21
    Bimodal(Instructions.LDC, Instructions.LDF, 0o22),   # 22
    Bimodal(Instructions.LDS, Instructions.LDB, 0o23),   # 23
    Singleton(Instructions.LCD, 0o24),                   # 24
    Bimodal(Instructions.LCM, Instructions.LCI, 0o25),   # 25
    Bimodal(Instructions.LCC, Instructions.LCF, 0o26),   # 26
    Bimodal(Instructions.LCS, Instructions.LCB, 0o27),   # 27
    Singleton(Instructions.ADD, 0o30),                   # 30
    Bimodal(Instructions.ADM, Instructions.ADI, 0o31),   # 31
    Bimodal(Instructions.ADC, Instructions.ADF, 0o32),   # 32
    Bimodal(Instructions.ADS, Instructions.ADB, 0o33),   # 33
    Singleton(Instructions.SBD, 0o34),                   # 34
    Bimodal(Instructions.SBM, Instructions.SBI, 0o35),   # 35
    Bimodal(Instructions.SBC, Instructions.SBF, 0o36),   # 36
    Bimodal(Instructions.SBS, Instructions.SBB, 0o37),   # 37
    Singleton(Instructions.STD, 0o40),                   # 40
    Bimodal(Instructions.STM, Instructions.STI, 0o41),   # 41
    Bimodal(Instructions.STC, Instructions.STF, 0o42),   # 42
    Bimodal(Instructions.STS, Instructions.STB, 0o43),   # 43
    Singleton(Instructions.SRD, 0o44),                   # 44
    Bimodal(Instructions.SRM, Instructions.SRI, 0o45),   # 45
    Bimodal(Instructions.SRC, Instructions.SRF, 0o46),   # 46
    Bimodal(Instructions.SRS, Instructions.SRB, 0o47),   # 47
    Singleton(Instructions.RAD, 0o50),                   # 50
    Bimodal(Instructions.RAM, Instructions.RAI, 0o51),   # 51
    Bimodal(Instructions.RAC, Instructions.RAF, 0o52),   # 52
    Bimodal(Instructions.RAS, Instructions.RAB, 0o53),   # 53
    Singleton(Instructions.AOD, 0o54),                   # 54
    Bimodal(Instructions.AOM, Instructions.AOI, 0o55),   # 55
    Bimodal(Instructions.AOC, Instructions.AOF, 0o56),   # 56
    Bimodal(Instructions.AOS, Instructions.AOB, 0o57),   # 57
    Singleton(Instructions.ZJF, 0o60),                   # 60
    Singleton(Instructions.NZF, 0o61),                   # 61
    Singleton(Instructions.PJF, 0o62),                   # 62
    Singleton(Instructions.NJF, 0o63),                   # 63
    Singleton(Instructions.ZJB, 0o64),                   # 64
    Singleton(Instructions.NZB, 0o65),                   # 65
    Singleton(Instructions.PJB, 0o66),                   # 66
    Singleton(Instructions.NJB, 0o67),                   # 67
    __UNIMPLEMENTED,            # 70
    Bimodal(Instructions.JPR, Instructions.JFI, 0o71),   # 71
    __UNIMPLEMENTED,            # 72
    __UNIMPLEMENTED,            # 73
    __UNIMPLEMENTED,            # 74
    __UNIMPLEMENTED,            # 75
    __UNIMPLEMENTED,            # 76
    OpCode77(),                 # 77
]

def decoder_at(e: int):
    return __DECODERS[e]


def decode(f: int, e: int) -> Instruction:
    return __DECODERS[f].decode(e)