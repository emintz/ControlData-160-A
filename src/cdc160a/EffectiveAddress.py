"""
    Supports CDC 160A Addressing Modes

    The following functions calculate a decoded instructions effective address
    and places it in the S register. This serves two purposes:
        1. Should the machine halt, the S register will contain the
           next address to be accessed. The reference manual appears to
           indicate that this is the desired behavior, though this could
           be open to interpretation.
        2. It relieves the instruction from the burden of determining its
           effective address, thus simplifying the logic and reusing
           code in this module.

    Note that the instruction must be moved to the F and E registers
    before any of the following are invoked.
"""
from cdc160a.Storage import Storage

# Constant Address Mode (C): G, the second word of a 2 word instruction,
# contains the operand.
def constant(storage: Storage) -> None:
    storage.g_address_to_s()
    storage.mode_relative()

# Direct Address Mode (D): E selects one of the first 64 (100 octal) addresses
# in the direct storage bank.
def direct(storage: Storage) -> None:
    storage.e_to_s()
    storage.mode_direct()

# Forward Indirect Mode (FI): E is added to the contents of P. The result
# specifies an address in the relative storage bank which specifies the
# operand address or a jump address in the relative storage bank.
def forward_indirect(storage: Storage) -> None:
    storage.forward_indirect_to_s()
    storage.mode_relative()

# Indirect Address Mode (I): E selects one of the first 64 (100 octal) addresses
# in the indirect storage bank.
def indirect(storage: Storage) -> None:
    storage.e_to_s()
    storage.mode_indirect()

# Memory Address Mode (M): G contains the operand address in the indirect
# storage bank
def memory(storage: Storage) -> None:
    storage.g_to_s()
    storage.mode_indirect()

# No Address Mode (N): E contains the operand. Since
# instructions always run from the relative bank, access becomes relative.
def no_address(storage: Storage) -> None:
    storage.p_to_s()
    storage.mode_relative()

# Relative Backward Address: E is subtracted to the contents of P
# to determine the address in the relative storage bank.
def relative_backward(storage: Storage) -> None:
    storage.relative_backward_to_s()
    storage.mode_relative()

# Relative Forward Address: E is added to the contents of P to determine
# the address in the relative storage bank.
def relative_forward(storage: Storage) -> None:
    storage.relative_forward_to_s()
    storage.mode_relative()

# Specific Address Mode: the operation resides in bank 0 at
# address 0o7777
def specific(storage: Storage) -> None:
    storage.specific_to_s()
    storage.mode_specific()
