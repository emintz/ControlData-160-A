import unittest
from time import monotonic_ns
from unittest import TestCase
from cdc160a import Arithmetic

class Test(TestCase):

    def test_negate_0(self) -> None:
        assert Arithmetic.negate(0) == 0o7777

    def test_negate_minus_0(self) -> None:
        assert Arithmetic.negate(0o7777) == 0

    def test_negate_one(self) -> None:
        assert Arithmetic.negate(1) == 0o7776

    def test_negate_minus_one(self) -> None:
        assert Arithmetic.negate(0o7776) == 1

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

    def test_1_times_ten(self) -> None:
        assert Arithmetic.times_ten(1) == 10

    def test_minus_0_times_ten(self) -> None:
        result = Arithmetic.times_ten(0o7777)
        assert result == 0o7777

    def test_minus_1_times_ten(self) -> None:
        result = Arithmetic.times_ten(0o7776)
        assert result == 0o7765

    def test_ten_times_ten(self) -> None:
        assert Arithmetic.times_ten(10) == 100

    def test_hundred_times_ten(self) -> None:
        assert Arithmetic.times_ten(100) == 1000

    def test_five_hundred_times_ten(self) -> None:
        result = Arithmetic.times_ten(500)
        # 5000 mod 4095 == 905
        assert result == 905

    def test_minus_ten_times_ten(self) -> None:
        # 10 == 0o12
        # ~0o12 == 0o7765
        minus_10 = 0o7765
        # 100 == 0o146
        # ~0o146 == 0o7631
        result = Arithmetic.times_ten(minus_10) == 0o7631

    def test_minus_hundred_times_ten(self) -> None:
        # 100 == 0o144
        # ~0O144 == 0O7633
        minus_100 = 0o7633
        # 1000 == 0o1750
        # ~0o1750 ==  0o6027
        expected = 0o6027
        result = Arithmetic.times_ten(minus_100)
        assert result == expected

    def test_minus_500_times_ten(self) -> None:
        # 500 == 0o764
        # ~0o764 == 0o7013
        minus_500 = 0o7013
        # 5000 mod 4095 == 905
        # 905 == 0o1611
        # ~0o1611 == 0o6166
        expected = 0o6166
        result = Arithmetic.times_ten(minus_500)
        assert result == expected

    def test_zero_times_hundred(self) -> None:
        assert Arithmetic.times_hundred(0) == 0

    def test_minus_zero_times_hundred(self) -> None:
        assert Arithmetic.times_hundred(0o7777) == 0o7777

    def test_one_times_hundred(self) -> None:
        assert Arithmetic.times_hundred(1) == 100

    def test_minus_one_times_hundred(self) -> None:
        result = Arithmetic.times_hundred(0o7776)
        # 100 == 0o144
        # ~0O144 == 0O7633
        expected = 0o7633
        assert result == expected

    def test_fifty_times_hundred(self) -> None:
        result = Arithmetic.times_hundred(50)
        # 5000 mod 4095 == 905
        assert result == 905

    def test_minus_fifty_times_hundred(self) -> None:
        # 50 = 0o62
        # ~0o62 == 0o7715
        minus_50 = 0o7715
        # 5000 mod 4095 == 905
        # 905 == 0o1611
        # ~0o1611 == 0o6166
        expected = 0o6166
        result = Arithmetic.times_hundred(minus_50)
        assert result == expected

if __name__ == "__main__":
    unittest.main()
