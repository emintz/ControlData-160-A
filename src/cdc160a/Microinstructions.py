"""
   Low level CDC 160A operations that can be composed into instructions and
   other functionality.

   Micro-instructions are low level operations, typically, but not
   necessarily data movement, that can be assembled into instructions
   and non-instruction operations like interrupt and buffered I/O handlers.
   Note that the operand address and bank must be selected before
   a micro-instruction can be run.

   Note that [ ... ] means "address specified by the contents of", so
   [S] indicates the address contained in the S register. Registers
    are specified by capital letters.

    A full address specification requires both an address and a bank. Banks
    are represented by lower case letters, b for Buffer, d for Direct,
    i for Indirect, and r for relative.

    The full specification has the form [<register>](<bank>), as in
    [S](r)
"""
from cdc160a.Storage import Storage

# No operation
def do_nothing(storage: Storage) -> None:
    pass

# A -> ~A
def complement_a(storage: Storage) -> None:
    storage.complement_a()

def e_complement_to_a(storage: Storage) -> None:
    e_to_a(storage)
    storage.complement_a()

# E -> A
def e_to_a(storage: Storage) -> None:
    storage.e_to_z()
    storage.z_to_a()

# Halt the machine and set the error status
def error(storage: Storage) -> None:
    storage.stop()
    storage.err_status = True

# Halt the machine without setting the error status
def halt(storage: Storage) -> None:
    storage.stop()

# A -> A rotated left by one
def rotate_a_left_one(storage: Storage) -> None:
    end_around = 0 if storage.a_register & 0o4000 == 0 else 1
    storage.a_register = ((storage.a_register << 1) & 0o7777) | end_around

# A -> A rotated left by 2
def rotate_a_left_two(storage: Storage) -> None:
    end_around = (storage.a_register & 0o6000) >> 10
    storage.a_register = ((storage.a_register << 2) & 0o7777) | end_around

# A -> A rotated left by 6, exchange high and low half words
def rotate_a_left_six(storage: Storage) -> None:
    end_around = (storage.a_register & 0o7700) >> 6
    storage.a_register = ((storage.a_register << 6) & 0o7777) | end_around

# A -> A rotated left by three
def rotate_a_left_three(storage: Storage) -> None:
    end_around = (storage.a_register & 0o7000) >> 9
    storage.a_register = ((storage.a_register << 3) & 0O7777) | end_around

# A -> A shifted right by 1 with extended sign.
def shift_a_right_one(storage: Storage) -> None:
    sign_extension = storage.a_register & 0o4000
    storage.a_register = (storage.a_register >> 1) | sign_extension

def shift_a_right_two(storage: Storage) -> None:
    sign_extension = 0 if storage.a_register & 0o4000 == 0 else 0o6000
    storage.a_register = (storage.a_register >> 2) | sign_extension

# ~[0o7777](0) -> A
def specific_complement_to_a(storage: Storage) -> None:
    specific_to_a(storage)
    storage.complement_a()

# [0o7777](0) -> A
def specific_to_a(storage: Storage) -> None:
    storage.z_register = storage.read_specific()
    storage.z_to_a()

# ~[S](d) -> A
def s_direct_complement_to_a(storage: Storage) -> None:
    s_direct_to_a(storage)
    storage.complement_a()

# [S](d) -> A
def s_direct_to_a(storage: Storage) -> None:
    storage.z_register = storage.read_direct_bank(storage.s_register)
    storage.z_to_a()

# ~[S](d) -> A
def s_indirect_complement_to_a(storage: Storage) -> None:
    s_indirect_to_a(storage)
    storage.complement_a()

# [S](i) -> A
def s_indirect_to_a(storage: Storage) -> None:
    storage.z_register = storage.read_indirect_bank(storage.s_register)
    storage.z_to_a()

# ~[S](r) -> A
def s_relative_complement_to_a(storage: Storage) -> None:
    s_relative_to_a(storage)
    storage.complement_a()

# [S](r) -> A
def s_relative_to_a(storage: Storage) -> None:
    storage.z_register = storage.read_relative_bank(storage.s_register)
    storage.z_to_a()

# A -> [S](b)
def a_to_buffer(storage: Storage) -> None:
    storage.a_to_s_buffer()

# A -> [S](d)
def a_to_direct(storage: Storage) -> None:
    storage.a_to_s_direct()

# A -> [S](i)
def a_to_indirect(storage: Storage) -> None:
    storage.a_to_s_indirect()

def a_to_relative(storage: Storage) -> None:
    storage.a_to_s_relative()

# A -> [0o7777](0)
def a_to_specific(storage: Storage) -> None:
    storage.a_to_z()
    storage.write_specific(storage.z_register)
