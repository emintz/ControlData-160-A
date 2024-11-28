from unittest import TestCase
from test_support.SwitchBank import SwitchBank

class TestSwitchBank(TestCase):

    def setUp(self) -> None:
        self.__switch_bank = SwitchBank()

    def test_unset(self) -> None:
        assert not self.__switch_bank.any_down()
        assert self.__switch_bank.mask() == 0

    def test_0_up(self) -> None:
        self.__switch_bank.set_up(0)
        assert not self.__switch_bank.any_down()
        assert self.__switch_bank.mask() == 1

    def test_0_down(self) -> None:
        self.__switch_bank.set_down(0)
        assert self.__switch_bank.any_down()
        assert self.__switch_bank.mask() == 1

    def test_1_up(self) -> None:
        self.__switch_bank.set_up(1)
        assert not self.__switch_bank.any_down()
        assert self.__switch_bank.mask() == 2

    def test_1_down(self) -> None:
        self.__switch_bank.set_down(1)
        assert self.__switch_bank.any_down()
        assert self.__switch_bank.mask() == 2

    def test_2_up(self) -> None:
        self.__switch_bank.set_up(2)
        assert not self.__switch_bank.any_down()
        assert self.__switch_bank.mask() == 4

    def test_2_down(self) -> None:
        self.__switch_bank.set_down(2)
        assert self.__switch_bank.any_down()
        assert self.__switch_bank.mask() == 4

    def set_0_and_2_up(self) -> None:
        self.__switch_bank.set_up(0)
        self.__switch_bank.set_up(2)
        assert not self.__switch_bank.any_down()
        assert self.__switch_bank.mask() == 5

    def set_0_up_2_down(self) -> None:
        self.__switch_bank.set_up(0)
        self.__switch_bank.set_down(2)
        assert self.__switch_bank.any_down()
        assert self.__switch_bank.mask() == 5

    def set_0_and_2_down(self) -> None:
        self.__switch_bank.set_down(0)
        self.__switch_bank.set_down(2)
        assert self.__switch_bank.any_down()
        assert self.__switch_bank.mask() == 5
