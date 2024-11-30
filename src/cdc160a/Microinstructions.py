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

def add_e_to_a(storage: Storage) -> None:
    storage.add_e_to_a()

def add_direct_to_a(storage: Storage) -> None:
    storage.add_s_address_to_a(storage.direct_storage_bank)

def add_indirect_to_a(storage: Storage) -> None:
    storage.add_s_address_to_a(storage.indirect_storage_bank)

def add_relative_to_a(storage: Storage) -> None:
    storage.add_s_address_to_a(storage.relative_storage_bank)

def add_specific_to_a(storage: Storage) -> None:
    """
    Add the value at 7777(0) to A. It is presumed that
    storage.s_register is set to 7777, which it will be
    during operation.

    :param storage: register file and memory
    :return: None
    """
    storage.add_s_address_to_a(0)

def and_e_with_a(storage: Storage) -> None:
    storage.and_e_with_a()

def and_direct_with_a(storage: Storage) -> None:
    storage.and_s_address_with_a(storage.direct_storage_bank)

def and_indirect_with_a(storage: Storage) -> None:
    storage.and_s_address_with_a(storage.indirect_storage_bank)

def and_relative_with_a(storage: Storage) -> None:
    storage.and_s_address_with_a(storage.relative_storage_bank)

def and_specific_with_a(storage: Storage) -> None:
    storage.and_specific_with_a()

def bank_controls_to_a(storage: Storage) -> None:
    storage.bank_controls_to_a()

def complement_a(storage: Storage) -> None:
    """
    ~A -> A

    :param storage: memory and register file
    :return: None
    """
    storage.complement_a()

def do_nothing(_: Storage) -> None:
    """
    No-Op: Does absolutely nothing

    :param _: memory and register file (ignored)
    :return: None
    """
    pass

def e_complement_to_a(storage: Storage) -> None:
    e_to_a(storage)
    storage.complement_a()

def e_to_a(storage: Storage) -> None:
    """
    E -> A

    :param storage: memory and register file
    :return: None
    """
    storage.e_to_z()
    storage.z_to_a()

# Halt the machine and set the error status
def error(storage: Storage) -> None:
    """
    Halt the machine and set the error status to true.

    :param storage: memory and register file
    :return: None
    """
    storage.stop()
    storage.err_status = True

def half_write_indirect(storage: Storage) -> None:
    """
    Set S tp the operand address at [E](d) and store the
    lower 6 bits of the E register to [S](i)

    Preconditions: S must contain the destination address
                   in the indirect storage bank.

    :param storage: memory and register file
    :return: None
    """
    storage.half_write_to_s_indirect()

# Halt the machine without setting the error status
def halt(storage: Storage) -> None:
    storage.stop()

def jump_forward_indirect(storage: Storage) -> None:
    storage.s_relative_indirect_to_next_address()

def jump_indirect(storage: Storage) -> None:
    """
    JPI (Jump Indirect) logic. [E(d)] -> P

    :param storage: memory and register file
    :return: None
    """
    storage.direct_to_z(storage.f_e)
    storage.z_to_next_address()

def multiply_a_by_10(storage: Storage) -> None:
    storage.a_times_10()

def multiply_a_by_100(storage: Storage) -> None:
    storage.a_times_100()

def p_to_a(storage: Storage) -> None:
    storage.p_to_a()

def p_to_e_direct(storage: Storage) -> None:
    storage.p_to_s_direct()

# Replace Add Instruction Suite
def replace_add(storage: Storage, bank: int) -> None:
    """
    Add the value in S[bank] to A and store the
    result in S[bank]

    Preconditions: S contains the target memory address

    :param storage: the computers storage and register file
    :param bank: the target memory bank
    :return: None
    """
    storage.add_s_address_to_a(bank)
    storage.store_a(bank)

def replace_add_direct(storage: Storage) -> None:
    """
    Add the value in S[d] to A and store the
    result in S[d]

    Preconditions: S contains the target memory address

    :param storage: the computers storage and register file
    :return: None
    """
    replace_add(storage, storage.direct_storage_bank)

def replace_add_indirect(storage: Storage) -> None:
    """
    Add the value in S[i] to A and store the
    result in S[i]

    Preconditions: S contains the target memory address

    :param storage: the computers storage and register file
    :return: None
    """
    replace_add(storage, storage.indirect_storage_bank)

def replace_add_relative(storage: Storage) -> None:
    """
    Add the value in S[r] to A and store the
    result in S[r]

    Preconditions: S contains the target memory address

    :param storage: the computers storage and register file
    :return: None
    """
    replace_add(storage, storage.relative_storage_bank)

def replace_add_specific(storage: Storage) -> None:
    """
    Add the value in S[o] to A and store the
    result in S[o]

    Preconditions: S contains the target memory address: 0o7777

    :param storage: the computers storage and register file
    :return: None
    """
    replace_add(storage, 0)

# Replace Add One instruction suite
def replace_add_one_direct(storage: Storage) -> None:
    """
    1 + [S(d)] + 1 to A and [S(d)]

    Preconditions: S contains the target memory address

    :param storage: memory and register file
    :return: None
    """
    storage.s_direct_to_a()
    storage.add_to_a(1)
    storage.a_to_s_direct()

def replace_add_one_indirect(storage: Storage) -> None:
    """
    1 + [S(i)] + 1 to A and [S(i)]

    Preconditions: S contains the target memory address

    :param storage: memory and register file
    :return: None
    """
    storage.s_indirect_to_a()
    storage.add_to_a(1)
    storage.a_to_s_indirect()

def replace_add_one_relative(storage: Storage) -> None:
    """
    1 + [S(r)] + 1 to A and [S(r)]

    Preconditions: S contains the target memory address

    :param storage: memory and register file
    :return: None
    """
    storage.s_relative_to_a()
    storage.add_to_a(1)
    storage.a_to_s_relative()

def replace_add_one_specific(storage: Storage) -> None:
    storage.specific_to_a()
    storage.add_to_a(1)
    storage.a_to_specific()

def return_jump(storage: Storage) -> None:
    """
    [p] + 2 -> YYYY(r)
    YYYY + 1 -> P

    Subroutine call to address YYYY: store the return address (P + 2)
    at the invoked address and resume execution at YYYY + 1

    :param storage: memory and register file
    :return: None
    """
    jump_address = storage.s_register + 1
    storage.value_to_s_address_relative(storage.p_register + 2)
    storage.set_next_instruction_address(jump_address)

def rotate_a_left_one(storage: Storage) -> None:
    """
    [A] << 1 -> A

    Left shift rotates bits.

    :param storage: memory and register file
    :return: None
    """
    end_around = 0 if storage.a_register & 0o4000 == 0 else 1
    storage.a_register = ((storage.a_register << 1) & 0o7777) | end_around

def rotate_a_left_two(storage: Storage) -> None:
    """
    [A] << 2 -> A

    Left shift rotates bits.

    :param storage: memory and register file
    :return: None
    """
    end_around = (storage.a_register & 0o6000) >> 10
    storage.a_register = ((storage.a_register << 2) & 0o7777) | end_around

def rotate_a_left_six(storage: Storage) -> None:
    """
    [A] << 6 -> A

    Left shift rotates bits.

    :param storage: memory and register file
    :return: None
    """
    end_around = (storage.a_register & 0o7700) >> 6
    storage.a_register = ((storage.a_register << 6) & 0o7777) | end_around

def rotate_a_left_three(storage: Storage) -> None:
    """
    [A] << 3 -> A

    Left shift rotates bits.

    :param storage: memory and register file
    :return: None
    """
    end_around = (storage.a_register & 0o7000) >> 9
    storage.a_register = ((storage.a_register << 3) & 0O7777) | end_around

def selective_complement_direct(storage: Storage) -> None:
    """
    [A] ^ [S](d) -> A

    :param storage: memory and register file
    :return: None
    """
    storage.s_direct_to_z()
    storage.xor_a_with_z()

def selective_complement_indirect(storage: Storage) -> None:
    """
    [A] ^ [S](I) -> A

    :param storage: memory and register file
    :return: None
    """
    storage.s_indirect_to_z()
    storage.xor_a_with_z()

def selective_complement_no_address(storage: Storage) -> None:
    """
    [A] ^ [Z] -> A

    :param storage: memory and register file
    :return: None
    """
    storage.e_to_z()
    storage.xor_a_with_z()

def selective_complement_relative(storage: Storage) -> None:
    """
    [A] ^ [R](I) -> A

    :param storage: memory and register file
    :return: None
    """
    storage.s_relative_to_z()
    storage.xor_a_with_z()

def selective_complement_specific(storage: Storage) -> None:
    """
    [A] ^ [7777(0)] -> A

    :param storage: memory and register file
    :return: None
    """
    storage.specific_to_z()
    storage.xor_a_with_z()

def selective_jump(storage: Storage) -> int:
    """
    Set the next address based on E and the jump switch settings.
    E contains the required jump switches. Jump if it specifies
    any set jump switch, otherwise continue normal execution flow.

    :param storage:
    :return: the number of cycles used: 1 if no jump, 2 if jump
    """
    mask = (storage.f_e >> 3) & 0o07
    if storage.and_with_jump_switches(mask) != 0:
        storage.g_to_next_address()
        return 2
    else:
        storage.next_after_two_word_instruction()
        return 1

def selective_stop(storage: Storage) -> None:
    """
    Halt if the lower half of E has any bits set that are also
    set that match the jump switch mask. Normal execution
    flow resumes when the operator restarts the machine.

    :param storage: memory and register file
    :return: None
    """
    mask = storage.f_e & 0o07
    if storage.and_with_stop_switches(mask) != 0:
        storage.stop()

def selective_stop_and_jump(storage: Storage) -> int:
    """
    Determine the next address based on the jump switches per
    selective_jump() above. Then stop as determine by selective_stop()
    above. Execution resumes at the address determined in the first
    step.

    :param storage: memory and register file
    :return: the number of cycles used.
    """
    selective_stop(storage)
    return selective_jump(storage)

def set_buf_bank_from_e(storage: Storage) -> None:
    """
    [E] & 0o07 -> Buffer Bank Control

    Set the buffer bank control to the lower three bits of E.

    :param storage: memory and register file
    :return: None
    """
    storage.set_buffer_bank_from_e()

def set_dir_bank_from_e(storage: Storage) -> None:
    """
    [E] & 0o07 -> Direct Bank Control

    Sets the direct bank control to the lower three bits of E

    :param storage: memory and storage bank
    :return: None
    """
    storage.set_direct_bank_from_e()


def set_dir_ind_rel_bank_from_e_and_jump(storage: Storage) -> None:
    """
    [E] & 0o07 -> Direct, Indirect, and Relative Bank Control, [A] -> P

    Sets the direct and relative bank controls to the lower three bits of E
    and P to the value in A, jumping to [A](r), where r represents the
    newly set relative storage bank.

    :param storage: memory and storage bank
    :return: None
    """
    storage.set_direct_bank_from_e()
    storage.set_indirect_bank_from_e()
    storage.set_relative_bank_from_e_and_jump()

def set_dir_rel_bank_from_e_and_jump(storage: Storage) -> None:
    """
    [E] & 0o07 -> Direct and Relative Bank Control, [A] -> P

    Sets the direct and relative bank controls to the lower three bits of E
    and P to the value in A, jumping to [A](r), where r represents the
    newly set relative storage bank.

    :param storage: memory and storage bank
    :return: None
    """
    storage.set_direct_bank_from_e()
    storage.set_relative_bank_from_e_and_jump()

def set_ind_bank_from_e(storage: Storage) -> None:
    """
    [E] & 0o07 -> Indirect Bank Control

    Set the indirect bank control to the lower three bits of E

    :param storage: memory and register file
    :return: None
    """
    storage.set_indirect_bank_from_e()

def set_ind_dir_bank_from_e(storage: Storage) -> None:
    storage.set_direct_bank_from_e()
    storage.set_indirect_bank_from_e()

def set_ind_rel_bank_from_e_and_jump(storage: Storage) -> None:
    """
    [E] & 0o07 -> Indirect and Relative Bank Control, [A] -> P

    Set the indirect and relative storage banks to the lower three bits of E
    and P to the value of A, causing the program to branch to [A](r) where
    r represents the newly set relative bank.

    :param storage: memory and register file
    :return: None
    """
    storage.set_indirect_bank_from_e()
    storage.set_relative_bank_from_e_and_jump()

def set_rel_bank_from_e_and_jump(storage: Storage) -> None:
    """
    [E] & 0o07 -> Relative Storage Control, [A] -> P

    Set the relative storage bank to the lower three bits of E and
    P to the value of A, causing the program to branch to [A](r) where
    r represents the newly set relative bank.

    :param storage: register and memory file
    :return: None
    """
    storage.set_relative_bank_from_e_and_jump()

def shift_a_right_one(storage: Storage) -> None:
    """
    [A] >> 1 -> A

    Sign extended.

    :param storage: contains the A register
    :return: None
    """
    sign_extension = storage.a_register & 0o4000
    storage.a_register = (storage.a_register >> 1) | sign_extension

def shift_a_right_two(storage: Storage) -> None:
    sign_extension = 0 if storage.a_register & 0o4000 == 0 else 0o6000
    storage.a_register = (storage.a_register >> 2) | sign_extension

def shift_replace_direct(storage: Storage) -> None:
    s_direct_to_a(storage)
    rotate_a_left_one(storage)
    a_to_s_direct(storage)

def shift_replace_indirect(storage: Storage) -> None:
    s_indirect_to_a(storage)
    rotate_a_left_one(storage)
    a_to_s_indirect(storage)

def shift_replace_relative(storage: Storage) -> None:
    s_relative_to_a(storage)
    rotate_a_left_one(storage)
    a_to_s_relative(storage)

def shift_replace_specific(storage: Storage) -> None:
    specific_to_a(storage)
    rotate_a_left_one(storage)
    a_to_specific(storage)

def specific_complement_to_a(storage: Storage) -> None:
    """
    ~[0o7777](0) -> A

    :param storage: memory and register file
    :return: None
    """
    specific_to_a(storage)
    storage.complement_a()

def specific_to_a(storage: Storage) -> None:
    """
    [0o7777](0) -> A

    :param storage: memory and register file
    :return: None
    """
    storage.specific_to_a()

def s_direct_complement_to_a(storage: Storage) -> None:
    """
    ~[S](d) -> A

    :param storage: memory and register file
    :return: None
    """
    s_direct_to_a(storage)
    storage.complement_a()

def s_direct_to_a(storage: Storage) -> None:
    """
    [S](d) -> A

    :param storage: memory and register file
    :return: None
    """
    storage.s_direct_to_a()

def s_indirect_complement_to_a(storage: Storage) -> None:
    """
    ~[S](d) -> A

    :param storage: memory and register file
    :return: None
    """
    s_indirect_to_a(storage)
    storage.complement_a()

def s_indirect_to_a(storage: Storage) -> None:
    """
    [S](i) -> A

    :param storage: memory and register file
    :return: None
    """
    storage.s_indirect_to_a()

def s_relative_complement_to_a(storage: Storage) -> None:
    """
    ~[S](r) -> A

    :param storage: memory and register file
    :return: None
    """
    s_relative_to_a(storage)
    storage.complement_a()

def s_relative_to_a(storage: Storage) -> None:
    """
    [S](r) -> A

    :param storage: memory and register file
    :return: None
    """
    storage.s_relative_to_a()

def subtract_e_from_a(storage: Storage) -> None:
    storage.subtract_e_from_a()

def subtract_direct_from_a(storage: Storage) -> None:
    storage.subtract_s_address_from_a(storage.direct_storage_bank)

def subtract_indirect_from_a(storage: Storage) -> None:
    storage.subtract_s_address_from_a(storage.indirect_storage_bank)

def subtract_relative_from_a(storage: Storage) -> None:
    storage.subtract_s_address_from_a(storage.relative_storage_bank)

def subtract_specific_from_a(storage: Storage) -> None:
    storage.subtract_specific_from_a()

def a_to_buffer(storage: Storage) -> None:
    """
    A -> [S](b)

    :param storage: memory and register file
    :return: None
    """
    storage.a_to_s_buffer()

def a_to_s_direct(storage: Storage) -> None:
    """
    A -> [S](d)

    :param storage: memory and register file
    :return: None
    """
    storage.a_to_s_direct()

def a_to_s_indirect(storage: Storage) -> None:
    """
    A -> [S](i)

    :param storage: memory and register file
    :return: None
    """
    storage.a_to_s_indirect()

def a_to_s_relative(storage: Storage) -> None:
    storage.a_to_s_relative()

def a_to_specific(storage: Storage) -> None:
    """
    A -> [0o7777](0)

    :param storage: memory and register file
    :return: None
    """
    storage.a_to_specific()

def jump_if_a_negative(storage: Storage) -> None:
    if storage.a_negative():
        storage.s_to_next_address()
    else:
        storage.next_after_one_word_instruction()

def jump_if_a_nonzero(storage: Storage) -> None:
    if storage.a_not_zero():
        storage.s_to_next_address()
    else:
        storage.next_after_one_word_instruction()

def jump_if_a_positive(storage: Storage) -> None:
    if storage.a_positive():
        storage.s_to_next_address()
    else:
        storage.next_after_one_word_instruction()

def jump_if_a_zero(storage: Storage) -> None:
    if storage.a_zero():
        storage.s_to_next_address()
    else:
        storage.next_after_one_word_instruction()
