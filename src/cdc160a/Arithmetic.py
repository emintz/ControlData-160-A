"""
CED 160-A one's complement arithmetic

Emulates the CDC 160-A's 12 bit one's complement complementing
subtracter, together with multiply by 10 and multiply by 100
instructions.
"""

def negate(value: int) -> int:
    """
    Return the ones complement of value.

    :param value: the value to negate (ones complement)
    :return: the negation as described above.
    """
    return (value & 0o7777) ^ 0o7777

def subtract(minuend: int, subtrahend: int) -> int:
    """
    Calculate minuend - subtrahend using one's complement arithmetic

    :param minuend: the number to subtract from
    :param subtrahend: the number to subtract
    :return: minuend - subtrahend using one's complement
             arithmetic
    """
    difference = (minuend & 0o7777) - (subtrahend & 0o7777)
    borrow = difference & ~0o7777
    if borrow != 0:
        difference -= 1
    return difference & 0o7777

def add(lhs: int, rhs: int) -> int:
    """
    Sums lhs and rhs by subtracting the one's complement of rhs from
    lhs with end-around borrow.

    :param lhs: the left hand addend, a 12-bit signed integer
    :param rhs: the right hand addend, a 12-bit signed integer
    :return: the sum, as described above, also a 12-bit signed
             integer
    """
    return subtract(lhs, negate(rhs))

def times_ten(multiplier: int) -> int:
    """
    Multiply the multiplier by 10.

    From the reference manual:

    For the range of multipliers -0o314 to +0o314, the result will be
    algebraically correct. If the multiplier is > +0o314 or < -0o314,
    the result will be correct modulo 2^12 - 1, i.e. 4095.

    :param multiplier: the value to multiply by 10
    :return: the result, multiplier * 10
    """
    doubled = add(multiplier, multiplier)
    quadrupled = add(doubled, doubled)
    octupled = add(quadrupled, quadrupled)
    return add(octupled, doubled)

def times_hundred(multiplier: int) -> int:
    """
    Multiply the multiplier by 10.

    From the reference manual:

    For the range of numbers [-0o24 .. 0o24], the result will be
    algebraically correct. If the multiplier is outside the range,
    the result will be correct modulo 2^12 - 1, i.e. 4095.

    :param multiplier: the value to multiply
    :return: multiplier * 100
    """
    by_10 = times_ten(multiplier)
    by_100 = times_ten(by_10)
    return by_100