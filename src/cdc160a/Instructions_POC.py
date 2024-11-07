"""
    CDC 160A Instructions

    Provides CDC 160A instructions.

    Instructions are functions taking a single argument, a Storage (q.v.)
    and returning the number of cycles they used.

    Note: all numbers in the comments are octal unless otherwise stated.
    Numeric ranges are represented as follows:

        X       A single octal digit, a value between 0 and 7 inclusive
        XX      Two octal digits, a value between 0 and 63, inclusive
        XXXX    Four octal digits, a value between 0 and 4095 inclusive

    Addresses are represented by Y's as above.
"""

from cdc160a import Storage

# Error: set error status and halt execution.
#   F: 00   E: 00
def err(storage: Storage) -> int:
    storage.err_status = True
    storage.run_stop_status = False
    storage.next_after_one_word_instruction()
    return 1

# Halt: halt execution without setting error status
#   F: 00   E: 00
#   F: 00   E: 77
def hlt(storage: Storage) -> int:
    storage.stop()
    storage.next_after_one_word_instruction()
    return 1

# Load Backward: Transfer the value at a fixed memory location BEFORE
# the current instruction into the A register.
#   F: 23   E: XX, cannot be 0
def ldb(storage: Storage) -> int:
    storage.relative_backward_to_s()
    storage.s_address_relative_to_z()
    storage.z_to_a()
    storage.next_after_one_word_instruction()
    return 2

# Load Constant: load the A register with G, the word following the
# instruction.
#   F: 22   E: 00
def ldc(storage: Storage) -> int:
    storage.g_to_z()
    storage.z_to_a()
    storage.next_after_two_word_instruction()
    return 2

# Load Direct: loads the A register with the contents of a direct
# address. The address is specified by E and resides in the direct
# bank.
#   F: 20   E: YY
def ldd(storage: Storage) -> int:
    storage.e_to_s()
    storage.s_direct_to_z()
    storage.z_to_a()
    storage.next_after_one_word_instruction()
    return 2

# Load Forward: loads find the operand at P + E in the relative bank
# and load it into the A register
#   F: 22   E: XX, cannot be 0.
def ldf(storage: Storage) -> int:
    storage.relative_forward_to_s()
    storage.s_address_relative_to_z()
    storage.z_to_a()
    storage.next_after_one_word_instruction()
    return 2

# Load Indirect:  loads the A register with the contents of an indirect
# address. The address is specified by E and resides in the indirect
# bank.
#   F: 21   E: YY, nonzero
def ldi(storage: Storage) -> int:
    storage.e_to_s()
    storage.s_indirect_to_z()
    storage.z_to_a()
    storage.next_after_one_word_instruction()
    return 3

# Load Memory: load the A register with a word in the indirect bank. The
# word's address resides in the instruction's second word.
#   F: 21   E: 00   G: YYYY
def ldm(storage: Storage) -> int:
    storage.g_to_s()
    storage.s_indirect_to_z()
    storage.z_to_a()
    storage.next_after_two_word_instruction()
    return 3

# Load No Address: load the A register with E. Since E is unsigned,
# A will contain a value between 0 and 63 inclusive.
#   F: 04   E: XX
def ldn(storage: Storage) -> int:
    storage.e_to_z()
    storage.z_to_a()
    storage.next_after_one_word_instruction()
    return 1

# No-op: do nothing
#   F: 00   E: 0X
def nop(storage: Storage) -> int:
    return 1

if __name__ == "__main__":
    print("Running instructions in stand-alone mode.")
    print("Nothing to do.")
