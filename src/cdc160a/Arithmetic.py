"""
CED 160-A one's complement arithmetic

Emulates the CDC 160-A's 12 bit one's complement complementing
subtracter, together with multiply by 10 and multiply by 100
instructions.
"""

def subtract(minuend: int, subtrahend: int) -> int:
    """
    Calculate lhs - rhs using one's complement arithmetic

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
    return subtract(lhs, (rhs & 0o7777) ^ 0o7777)
