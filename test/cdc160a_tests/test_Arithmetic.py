import unittest
from unittest import TestCase
from cdc160a import Arithmetic

class Test(TestCase):

    def test_0_minus_0(self) -> None:
        assert Arithmetic.subtract(0, 0) == 0

    def test_negative_0_minus_negative_0(self) -> None:
        assert Arithmetic.subtract(0o7777, 0o7777) == 0

    def test_negative_0_minus_0(self) -> None:
        assert Arithmetic.subtract(0o7777, 0) == 0o7777

    # TODO(emintz): verify that this is correct. A strict reading of
    # https://en.wikipedia.org/wiki/Ones%27_complement indicates that
    # is is.
    def test_0_minus_negative_0(self) -> None:
        assert Arithmetic.subtract(0, 0o7777) == 0

    def test_1_minus_0(self) -> None:
        assert Arithmetic.subtract(1, 0) == 1

    def test_1_minus_1(self) -> None:
        assert Arithmetic.subtract(1, 1) == 0

    def test_0_minus_1(self) -> None:
        assert Arithmetic.subtract(0, 1) == 0o7776

    def test_negative_0_minus_1(self) -> None:
        assert Arithmetic.subtract(0o7777, 1) == 0o7776

    def test_1_minus_2(self) -> None:
        assert Arithmetic.subtract(1, 2) == 0o7776

    def test_2_minus_1(self) -> None:
        assert Arithmetic.subtract(2, 1) == 1

    def test_0_plus_0(self) -> None:
        assert Arithmetic.add(0, 0) == 0

    def test_minus_0_plus_minus_0(self) -> None:
        assert Arithmetic.add(0o7777, 0o7777) == 0o7777

    def test_minus_0_plus_0(self) -> None:
        assert Arithmetic.add(0o7777, 0) == 0

    def test_0_plus_minus_0(self) -> None:
        assert Arithmetic.add(0, 0o7777) == 0

    def test_1_plus_0(self) -> None:
        assert Arithmetic.add(1, 0) == 1

    def test_0_plus_1(self) -> None:
        assert Arithmetic.add(0, 1) == 1

    def test_minus_0_plus_1(self) -> None:
        assert Arithmetic.add(0o7777, 1) == 1

    def test_1_plus_minus_0(self) -> None:
        assert Arithmetic.add(1, 0o7777) == 1

    def test_1_plus_minus_1(self) -> None:
        assert Arithmetic.add(1, 0o7776) == 0

    def test_minus_1_plus_1(self) -> None:
        assert Arithmetic.add(0o7776, 1) == 0

    def test_1_plus_2047(self) -> None:
        assert Arithmetic.add(1, 0o3775) == 0o3776

    def test_1_plus_2048(self) -> None:
        assert Arithmetic.add(1, 0o3777) == 0o4000

    def test_1_plus_2(self) -> None:
        assert Arithmetic.add(1, 2) == 3

    def test_2_plus_1(self) -> None:
        assert Arithmetic.add(2, 1) == 3


if __name__ == "__main__":
    unittest.main()
