from unittest import TestCase
from cdc160a import Instructions_POC
from cdc160a.Storage import Storage
from typing import Final

INSTRUCTION_ADDRESS: Final[int] = 0o1000
AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS: Final[int] = INSTRUCTION_ADDRESS + 1
AFTER_DOUBLE_WORD_INSTRUCTION_ADDRESS: Final[int] = INSTRUCTION_ADDRESS + 2
G_ADDRESS: Final[int] = INSTRUCTION_ADDRESS + 1

class Test(TestCase):

    def setUp(self) -> None:
        self.storage = Storage()
        self.storage.buffer_storage_bank = 1
        self.storage.direct_storage_bank = 2
        self.storage.indirect_storage_bank = 3
        self.storage.relative_storage_bank = 4
        self.storage.p_register = INSTRUCTION_ADDRESS

    def tearDown(self) -> None:
        self.storage = None

    def test_err(self) -> None:
        self.storage.err_status = False
        self.storage.run()
        self.storage.unpack_instruction()
        assert Instructions_POC.err(self.storage) == 1
        assert not self.storage.run_stop_status
        assert self.storage.err_status
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_hlt(self) -> None:
        self.storage.err_status = False
        self.storage.run()
        self.storage.unpack_instruction()
        assert Instructions_POC.hlt(self.storage) == 1
        assert not self.storage.run_stop_status
        assert not self.storage.err_status
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_ldb(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o2310)
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS - 0o10, 0o5555)
        self.storage.run()
        self.storage.unpack_instruction()
        assert Instructions_POC.ldb(self.storage) == 2
        assert self.storage.z_register == 0O5555
        assert self.storage.a_register == 0o5555
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        assert self.storage.run_stop_status
        assert self.storage.run_stop_status

    def test_ldc(self) -> None:
        # LDC 6666
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o2200)
        self.storage.write_relative_bank(G_ADDRESS, 0o6666)
        self.storage.p_register = INSTRUCTION_ADDRESS
        self.storage.run()
        self.storage.unpack_instruction()
        assert Instructions_POC.ldc(self.storage) == 2
        assert self.storage.s_register == G_ADDRESS
        assert self.storage.z_register == 0o6666
        assert self.storage.a_register == 0o6666
        assert self.storage.p_register == AFTER_DOUBLE_WORD_INSTRUCTION_ADDRESS
        assert self.storage.run_stop_status

    def test_ldd(self) -> None:
        # LDD 45
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o2045)
        self.storage.write_direct_bank(0o45, 0o7654)
        self.storage.run()
        self.storage.unpack_instruction()
        assert Instructions_POC.ldd(self.storage) == 2
        assert self.storage.s_register == 0o45
        assert self.storage.z_register == 0o7654
        assert self.storage.a_register == 0o7654
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        assert self.storage.run_stop_status

    def test_ldf(self) -> None:
        # LDF 20
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o2220)
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS + 0o20, 0o2222)
        self.storage.p_register = INSTRUCTION_ADDRESS
        self.storage.run()
        self.storage.unpack_instruction()
        assert Instructions_POC.ldf(self.storage) == 2
        assert self.storage.s_register == INSTRUCTION_ADDRESS + 0o20
        assert self.storage.z_register == 0o2222
        assert self.storage.a_register ==0o2222
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        assert self.storage.run_stop_status

    def test_ldi(self) -> None:
        # LDI 45
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o2145)
        self.storage.write_indirect_bank(0o45, 0o7654)
        self.storage.run()
        self.storage.unpack_instruction()
        assert Instructions_POC.ldi(self.storage) == 3
        assert self.storage.s_register == 0o45
        assert self.storage.z_register == 0o7654
        assert self.storage.a_register == 0o7654
        assert self.storage.p_register == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        assert self.storage.run_stop_status

    def test_ldm(self) -> None:
        # LDM 137
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o2100)
        self.storage.write_relative_bank(G_ADDRESS, 0o137)
        self.storage.write_indirect_bank(0o137, 0o1370)
        self.storage.run()
        self.storage.unpack_instruction()
        assert Instructions_POC.ldm(self.storage) == 3
        assert self.storage.s_register == 0o137
        assert self.storage.z_register == 0o1370
        assert self.storage.a_register == 0o1370
        assert self.storage.p_register == AFTER_DOUBLE_WORD_INSTRUCTION_ADDRESS
        assert self.storage.run_stop_status

    def test_ldn(self) -> None:
        # LDN 37
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0437)
        self.storage.run()
        self.storage.unpack_instruction()
        assert Instructions_POC.ldn(self.storage) == 1
        assert self.storage.s_register == INSTRUCTION_ADDRESS
        assert self.storage.z_register == 0o37
        assert self.storage.a_register == 0o37

