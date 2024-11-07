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

# A -> [S](d)

# No operation
def do_nothing(storage: Storage) -> None:
    pass

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

# [0o7777](0) -> A
def specific_to_a(storage: Storage) -> None:
    storage.z_register = storage.read_specific()
    storage.z_to_a()

# [S](d) -> A
def s_direct_to_a(storage: Storage) -> None:
    storage.z_register = storage.read_direct_bank(storage.s_register)
    storage.z_to_a()

# [S](i) -> A
def s_indirect_to_a(storage: Storage) -> None:
    storage.z_register = storage.read_indirect_bank(storage.s_register)
    storage.z_to_a()

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



