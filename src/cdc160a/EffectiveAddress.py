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

def constant(storage: Storage) -> None:
    """
    Constant Address Mode (C): G, the second word of a 2 word instruction,
    contains the operand.

    :param storage: memory and register file
    :return: None
    """
    storage.g_address_to_s()
    storage.mode_relative()

def direct(storage: Storage) -> None:
    """
    Direct Address Mode (D): E selects one of the first 64 (100 octal)
    addresses  in the direct storage bank.

    :param storage: memory and register file
    :return: None
    """
    storage.e_to_s()
    storage.mode_direct()

def forward_indirect(storage: Storage) -> None:
    """
    Forward Indirect Mode (FI): E is added to the contents of P. The result
    specifies an address in the relative storage bank which specifies the
    operand address or a jump address in the relative storage bank.

    :param storage: memory and register file
    :return: None
    """
    storage.forward_indirect_to_s()
    storage.mode_relative()

def indirect(storage: Storage) -> None:
    """
    Indirect Address Mode (I): E selects one of the first 64 (100 octal)
    addresses in the indirect storage bank.

    :param storage: memory and register file
    :return: None
    """
    storage.e_to_s()
    storage.mode_indirect()

def memory(storage: Storage) -> None:
    """
    Memory Address Mode (M): G contains the operand address in the indirect
    storage bank

    :param storage: memory and register file
    :return: None
    """
    storage.g_to_s()
    storage.mode_relative()

def no_address(storage: Storage) -> None:
    """
    No Address Mode (N): E contains the operand. Since
    instructions always run from the relative bank, access becomes relative.

    :param storage: memory and register file
    :return: None
    """
    storage.p_to_s()
    storage.mode_relative()

def relative_backward(storage: Storage) -> None:
    """
    Relative Backward Address: E is subtracted to the contents of P
    to determine the address in the relative storage bank.

    :param storage: memory and register file
    :return: None
    """
    storage.relative_backward_to_s()
    storage.mode_relative()

def relative_forward(storage: Storage) -> None:
    """
    Relative Forward Address: E is added to the contents of P to determine
    the address in the relative storage bank.

    :param storage: memory and register file
    :return: None
    """
    storage.relative_forward_to_s()
    storage.mode_relative()

def specific(storage: Storage) -> None:
    """
    Specific Address Mode: the operation resides in bank 0 at
    address 0o7777

    :param storage: memory and register file
    :return: None
    """
    storage.specific_to_s()
    storage.mode_specific()

def via_direct_at_e(storage: Storage) -> None:
    """
    Take the effective address from [S](d)

    :param storage: memory and register file
    :return: None
    """
    storage.e_direct_to_s()

def vacuous(storage: Storage) -> None:
    """
    No effective address, loaves S unchanged

    :param storage:  memory and register file
    :return: None
    """
    pass
