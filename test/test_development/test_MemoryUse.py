from unittest import TestCase

from development.MemoryUse import MemoryUsedInBank, MemoryUse

class TestMemoryUse(TestCase):

    def setUp(self) -> None:
        self.__single_bank_use: MemoryUsedInBank = MemoryUsedInBank()
        self.__memory_use = MemoryUse()

    def test_memory_used_in_bank(self) -> None:
        assert self.__single_bank_use.is_empty()
        assert self.__single_bank_use.first_word_address() is None
        assert self.__single_bank_use.last_word_address_plus_one() is None
        assert str(self.__single_bank_use) == "Empty"

        self.__single_bank_use.mark_used(0o0100)
        assert not self.__single_bank_use.is_empty()
        assert self.__single_bank_use.first_word_address() == 0o100
        assert self.__single_bank_use.last_word_address_plus_one() == 0o101
        assert str(self.__single_bank_use) == "fwa = 100, lwa + 1 = 101"

        self.__single_bank_use.mark_used(0o40)
        assert self.__single_bank_use.first_word_address() == 0o40
        assert self.__single_bank_use.last_word_address_plus_one() == 0o0101

        self.__single_bank_use.mark_used(0o200)
        assert self.__single_bank_use.first_word_address() == 0o40
        assert self.__single_bank_use.last_word_address_plus_one() == 0o0201

    def test_memory_use_construction(self) -> None:
        for bank in range(0o0, 0o10):
            assert self.__memory_use.memory_use(bank).is_empty()

    def test_memory_use_marking(self) -> None:
        self.__memory_use.mark_used(0o1, 0o100)
        self.__memory_use.mark_used(0o01, 0o240)

        self.__memory_use.mark_used(0o3, 0o40)
        self.__memory_use.mark_used(0o3, 0o47)

        assert self.__memory_use.memory_use(0o0).is_empty()
        assert not self.__memory_use.memory_use(0o1).is_empty()
        assert (self.__memory_use.memory_use(0o1).
                first_word_address() == 0o100)
        assert (self.__memory_use.memory_use(0o1).
                last_word_address_plus_one() == 0o241)
        assert self.__memory_use.memory_use(0o2).is_empty()
        assert not self.__memory_use.memory_use(0o3).is_empty()
        assert (self.__memory_use.memory_use(0o3).
                first_word_address() == 0o40)
        assert (self.__memory_use.memory_use(0o03).
                last_word_address_plus_one() == 0o50)
        assert self.__memory_use.memory_use(0o4).is_empty()
        assert self.__memory_use.memory_use(0o5).is_empty()
        assert self.__memory_use.memory_use(0o6).is_empty()
        assert self.__memory_use.memory_use(0o7).is_empty()
