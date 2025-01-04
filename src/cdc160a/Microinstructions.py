"""
CDC 160A operations that used in instruction CPU instruction
emulation.

Copyright © 2025 The System Source Museum, the authors and maintainers,
and others

This file is part of the System Source Museum Control Data 160-A Emulator.

The System Source Museum Control Data 160-A Emulator is free software: you
can redistribute it and/or modify it under the terms of the GNU General
Public License as published by the Free Software Foundation, either version
3 of the License, or (at your option) any later version.

The System Source Museum Control Data 160-A Emulator is distributed in the
hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with the System Source Museum Control Data 160-A Emulator. If not, see
<https://www.gnu.org/licenses/.

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

TODO(emintz): compatibility with Instructions.py refactoring, if come.
"""
from cdc160a.InputOutput import InitiationStatus
from cdc160a.Hardware import Hardware
from cdc160a.Storage import Storage

def a_to_buffer_entrance(hardware: Hardware) -> int:
    """
    Logic for ATE, A to BER (Buffer Entrance Register) instruction, 0105 YYYY

    :param hardware: emulator hardware including storage and I/O
    :return: the number of cycles the instruction used.
    """
    storage = hardware.storage
    if storage.buffering:
        storage.g_to_next_address()
        cycles_used = 2
    else:
        storage.a_to_buffer_entrance_register()
        storage.next_after_two_word_instruction()
        cycles_used = 1
    return cycles_used

def a_to_buffer_exit(hardware: Hardware) -> int:
    """
    Logic for ATX, A to BXR (buffer exit register) instruction, 0106 YYYY

    :param hardware: emulator hardware including storage and I/O
    :return: the number of cycles that the instruction used
    """
    storage = hardware.storage
    if storage.buffering:
        storage.g_to_next_address()
        cycles_used = 2
    else:
        storage.a_to_buffer_exit_register()
        cycles_used = 1
        storage.next_after_two_word_instruction()
    return cycles_used

def add_e_to_a(hardware: Hardware) -> None:
    hardware.storage.add_e_to_a()

def add_direct_to_a(hardware: Hardware) -> None:
    storage = hardware.storage
    storage.add_s_address_to_a(storage.direct_storage_bank)

def add_indirect_to_a(hardware: Hardware) -> None:
    storage = hardware.storage
    storage.add_s_address_to_a(storage.indirect_storage_bank)

def add_relative_to_a(hardware: Hardware) -> None:
    storage = hardware.storage
    storage.add_s_address_to_a(storage.relative_storage_bank)

def add_specific_to_a(hardware: Hardware) -> None:
    """
    Add the value at 7777(0) to A. It is presumed that
    storage.s_register is set to 7777, which it will be
    during operation.

    :param hardware: emulator hardware including storage and I/O
    :return: None
    """
    hardware.storage.add_s_address_to_a(0)

def and_e_with_a(hardware: Hardware) -> None:
    hardware.storage.and_e_with_a()

def and_direct_with_a(hardware: Hardware) -> None:
    hardware.storage.and_s_address_with_a(
        hardware.storage.direct_storage_bank)

def and_indirect_with_a(hardware:Hardware) -> None:
    hardware.storage.and_s_address_with_a(
        hardware.storage.indirect_storage_bank)

def and_relative_with_a(hardware:Hardware) -> None:
    hardware.storage.and_s_address_with_a(
        hardware.storage.relative_storage_bank)

def and_specific_with_a(hardware: Hardware) -> None:
    hardware.storage.and_specific_with_a()

def bank_controls_to_a(hardware: Hardware) -> None:
    hardware.storage.bank_controls_to_a()

def block_store(hardware: Hardware) -> int:
    """
    Block Store instruction.

    If the machine is already buffering data, jump to the address in G.
    Otherwise, move the contents of the A register to the BFR (buffer
    data register) and buffer it into the buffer storage bank, starting
    at the FWA and ending at the LWA.

    The user must set the BER (buffer entrance register) to the
    FWA (first word address, the first storage location to set) and
    the BXR (buffer exit register) to the LWA + 1 (the last storage
    address to be set plus 1) before running the instruction.

    :param hardware: emulator hardware including storage and I/O
    :return: the number of cycles that the instruction used
    """
    # cycles_used = 0
    storage = hardware.storage
    if storage.buffering:
        cycles_used = 2
        storage.g_to_next_address()
    else:
        cycles_used = 1
        storage.a_to_buffer_data_register()
        storage.start_buffering()
        while storage.buffer_data_to_memory():
            cycles_used += 1
        storage.stop_buffering()
        storage.next_after_two_word_instruction()
    return cycles_used

def buffer_entrance_to_a(hardware: Hardware) -> None:
    hardware.storage.buffer_entrance_to_a()

def buffer_entrance_to_direct_and_set_from_a(
        hardware: Hardware) -> None:
    """
    Store BER (buffer entrance register) contents at [E] in the
    direct storage bank, then load the contents of A into the BER.
    Do not check for ongoing buffering, just make the change regardless.

    :param hardware: emulator hardware including storage and I/O
    :return: None
    """
    storage = hardware.storage
    storage.buffer_entrance_register_to_direct_storage()
    storage.a_to_buffer_entrance_register()

def buffer_exit_to_a(hardware: Hardware) -> None:
    hardware.storage.buffer_exit_to_a()

def clear_buffer_controls(hardware: Hardware) -> None:
    """
    Clear the buffer status.
    :param hardware:
    :return:
    """
    hardware.input_output.clear_buffer_controls()

def clear_interrupt_lock(hardware: Hardware) -> None:
    """
    Clear the interrupt lock if locked and no unlock is pending

    :param hardware: emulator hardware including storage and I/O
    :return: None
    """
    hardware.storage.clear_interrupt_lock()

def complement_a(storage: Storage) -> None:
    """
    ~A -> A

    :param storage: memory and register file
    :return: None
    """
    storage.complement_a()

def do_nothing(_: Hardware) -> None:
    """
    No-Op: Does absolutely nothing

    :param _: memory and register file (ignored)
    :return: None
    """
    pass

def e_complement_to_a(hardware: Hardware) -> None:
    storage = hardware.storage
    e_to_a(hardware)
    storage.complement_a()

def e_to_a(hardware: Hardware) -> None:
    """
    E -> A

    :param hardware: emulator hardware including storage and I/O
    :return: None
    """
    storage = hardware.storage
    storage.e_to_z()
    storage.z_to_a()

def error(hardware: Hardware) -> None:
    """
    Halt the machine and set the error status to true.

    :param hardware: emulator hardware including storage and I/O
    :return: None
    """
    storage = hardware.storage
    storage.stop()
    storage.err_status = True

def external_function(hardware: Hardware) -> None:
    """
    Perform an external function using [S](r) as the operand.

    :param hardware: emulator hardware bundle including I/O and Storage

    :return: None
    """
    storage = hardware.storage
    storage.set_interrupt_lock()
    operand = storage.s_relative_address_contents()
    response, status = hardware.input_output.external_function(operand)
    storage.machine_hung = not status
    if response is not None:
        hardware.storage.a_register = response

def half_write_indirect(hardware: Hardware) -> None:
    """
    Set S tp the operand address at [E](d) and store the
    lower 6 bits of the E register to [S](i)

    Preconditions: S must contain the destination address
                   in the indirect storage bank.

    :param hardware: emulator hardware including storage and I/O
    :return: None
    """
    hardware.storage.half_write_to_s_indirect()

def halt(hardware: Hardware) -> None:
    """
    Halt the machine without setting the error status

    :param hardware: emulator hardware subsystems
    :return: None
    """
    hardware.storage.stop()

def initiate_buffer_input(hardware: Hardware) -> int:
    """
    Start buffered input and set the address of the next
    instruction to be run. If buffered I/O was already running,
    set the address of the next instruction to [G]. Otherwise,
    set the address of the next instruction to [P] + 2.

    :param hardware: emulator hardware, including I/O and
                     storage
    :return: elapsed cycles
    """
    elapsed_cycles = 1  # Assume no jump for now
    storage = hardware.storage
    match hardware.input_output.initiate_buffer_input(storage):
        case InitiationStatus.STARTED:
            storage.next_after_two_word_instruction()
        case InitiationStatus.ALREADY_RUNNING:
            storage.g_to_next_address()
            elapsed_cycles = 2
    return elapsed_cycles

def initiate_buffer_output(hardware: Hardware) -> int:
    elapsed_cycles = 1
    storage = hardware.storage
    match hardware.input_output.initiate_buffer_output(storage):
        case InitiationStatus.STARTED:
            storage.next_after_two_word_instruction()
        case InitiationStatus.ALREADY_RUNNING:
            storage.g_to_next_address()
            elapsed_cycles = 2
    return elapsed_cycles

def input_to_a(hardware: Hardware) -> int:
    """
    Read one word from the normal input channel to the accumulator.

    :param hardware: the emulated hardware, including storage
                     and I/O
    :return: elapsed cycles
    """
    status, value = hardware.input_output.read_normal()
    if status:
        hardware.storage.a_register = value
    else:
        hardware.storage.indefinite_delay()
    return hardware.input_output.read_delay()

def input_to_memory(hardware: Hardware) -> int:
    """
    Read from the normal input channel to the indirect memory
    bank. When this method is invoked, the S register must contain
    the input memory's FWA, and [G] must contain its LWA + 1.
    Input is read to the indirect memory bank.

    :param hardware: the emulated hardware, including storage
                     and I/O
    :return: elapsed cycles
    """
    hardware.storage.normal_input_active()
    elapsed_cycles = 0
    lwa_plus_one = hardware.storage.g_contents()
    while hardware.storage.s_register < lwa_plus_one and not \
        hardware.storage.machine_hung:
        read_status, input_word = hardware.input_output.read_normal()
        if read_status:
            hardware.storage.store_at_s_indirect_and_increment_s(input_word)
        else:
            hardware.storage.indefinite_delay()
        elapsed_cycles += hardware.input_output.read_delay()
    return elapsed_cycles

def jump_forward_indirect(hardware: Hardware) -> None:
    hardware.storage.s_relative_to_next_address()

def jump_indirect(hardware: Hardware) -> None:
    """
    JPI (Jump Indirect) logic. [E(d)] -> P

    :param hardware: emulator hardware including storage and I/O
    :return: None
    """
    storage = hardware.storage
    storage.direct_to_z(storage.f_e)
    storage.z_to_next_address()

def multiply_a_by_10(hardware: Hardware) -> None:
    hardware.storage.a_times_10()

def multiply_a_by_100(hardware: Hardware) -> None:
    hardware.storage.a_times_100()

def p_to_a(hardware: Hardware) -> None:
    hardware.storage.p_to_a()

def p_to_e_direct(hardware: Hardware) -> None:
    hardware.storage.p_to_e_direct()

# Replace Add Instruction Suite
def replace_add(hardware: Hardware, bank: int) -> None:
    """
    Add the value in S[bank] to A and store the
    result in S[bank]

    Preconditions: S contains the target memory address

    :param hardware: emulator hardware including storage and I/O
    :param bank: the target memory bank
    :return: None
    """
    storage = hardware.storage
    storage.add_s_address_to_a(bank)
    storage.store_a(bank)

def replace_add_direct(hardware: Hardware) -> None:
    """
    Add the value in S[d] to A and store the
    result in S[d]

    Preconditions: S contains the target memory address

    :param hardware: emulator hardware including storage and I/O
    :return: None
    """
    replace_add(hardware, hardware.storage.direct_storage_bank)

def replace_add_indirect(hardware: Hardware) -> None:
    """
    Add the value in S[i] to A and store the
    result in S[i]

    Preconditions: S contains the target memory address

    :param hardware: emulator hardware including storage and I/O
    :return: None
    """
    replace_add(hardware, hardware.storage.indirect_storage_bank)

def replace_add_relative(hardware: Hardware) -> None:
    """
    Add the value in S[r] to A and store the
    result in S[r]

    Preconditions: S contains the target memory address

    :param hardware: emulator hardware including storage and I/O
    :return: None
    """
    replace_add(hardware, hardware.storage.relative_storage_bank)

def replace_add_specific(hardware: Hardware) -> None:
    """
    Add the value in S[o] to A and store the
    result in S[o]

    Preconditions: S contains the target memory address: 0o7777

    :param hardware: emulator hardware including storage and I/O
    :return: None
    """
    replace_add(hardware, 0)

# Replace Add One instruction suite
def replace_add_one_direct(hardware: Hardware) -> None:
    """
    1 + [S(d)] + 1 to A and [S(d)]

    Preconditions: S contains the target memory address

    :param hardware: emulator hardware including storage and I/O
    :return: None
    """
    storage = hardware.storage
    storage.s_direct_to_a()
    storage.add_to_a(1)
    storage.a_to_s_direct()

def replace_add_one_indirect(hardware: Hardware) -> None:
    """
    1 + [S(i)] + 1 to A and [S(i)]

    Preconditions: S contains the target memory address

    :param hardware: emulator hardware including storage and I/O
    :return: None
    """
    storage = hardware.storage
    storage.s_indirect_to_a()
    storage.add_to_a(1)
    storage.a_to_s_indirect()

def replace_add_one_relative(hardware: Hardware) -> None:
    """
    1 + [S(r)] + 1 to A and [S(r)]

    Preconditions: S contains the target memory address

    :param hardware: emulator hardware including storage and I/O
    :return: None
    """
    storage = hardware.storage
    storage.s_relative_to_a()
    storage.add_to_a(1)
    storage.a_to_s_relative()

def replace_add_one_specific(hardware: Hardware) -> None:
    storage = hardware.storage
    storage.specific_to_a()
    storage.add_to_a(1)
    storage.a_to_specific()

def return_jump(hardware: Hardware) -> None:
    """
    [p] + 2 -> YYYY(r)
    YYYY + 1 -> P

    Subroutine call to address YYYY: store the return address (P + 2)
    at the invoked address and resume execution at YYYY + 1

    :param hardware: emulator hardware including storage and I/O
    :return: None
    """
    storage = hardware.storage
    jump_address = storage.s_register + 1
    storage.value_to_s_address_relative(storage.p_register + 2)
    storage.set_next_instruction_address(jump_address)

def rotate_a_left_one(hardware: Hardware) -> None:
    """
    [A] << 1 -> A

    Left shift rotates bits.

    :param hardware: emulator hardware including storage and I/O
    :return: None
    """
    storage = hardware.storage
    end_around = 0 if storage.a_register & 0o4000 == 0 else 1
    storage.a_register = ((storage.a_register << 1) & 0o7777) | end_around

def rotate_a_left_two(hardware: Hardware) -> None:
    """
    [A] << 2 -> A

    Left shift rotates bits.

    :param hardware: emulator hardware including storage and I/O
    :return: None
    """
    storage = hardware.storage
    end_around = (storage.a_register & 0o6000) >> 10
    storage.a_register = ((storage.a_register << 2) & 0o7777) | end_around

def rotate_a_left_six(hardware: Hardware) -> None:
    """
    [A] << 6 -> A

    Left shift rotates bits.

    :param hardware: emulator hardware including storage and I/O
    :return: None
    """
    storage = hardware.storage
    end_around = (storage.a_register & 0o7700) >> 6
    storage.a_register = ((storage.a_register << 6) & 0o7777) | end_around

def rotate_a_left_three(hardware: Hardware) -> None:
    """
    [A] << 3 -> A

    Left shift rotates bits.

    :param hardware: emulator hardware including storage and I/O
    :return: None
    """
    storage = hardware.storage
    end_around = (storage.a_register & 0o7000) >> 9
    storage.a_register = ((storage.a_register << 3) & 0O7777) | end_around

def selective_complement_direct(hardware: Hardware) -> None:
    """
    [A] ^ [S](d) -> A

    :param hardware: emulator hardware including storage and I/O
    :return: None
    """
    storage = hardware.storage
    storage.s_direct_to_z()
    storage.xor_a_with_z()

def selective_complement_indirect(hardware: Hardware) -> None:
    """
    [A] ^ [S](I) -> A

    :param hardware: emulator hardware including storage and I/O
    :return: None
    """
    storage = hardware.storage
    storage.s_indirect_to_z()
    storage.xor_a_with_z()

def selective_complement_no_address(hardware: Hardware) -> None:
    """
    [A] ^ [Z] -> A

    :param hardware: emulator hardware including storage and I/O
    :return: None
    """
    storage = hardware.storage
    storage.e_to_z()
    storage.xor_a_with_z()

def selective_complement_relative(hardware: Hardware) -> None:
    """
    [A] ^ [R](I) -> A

    :param hardware: emulator hardware including storage and I/O
    :return: None
    """
    storage = hardware.storage
    storage.s_relative_to_z()
    storage.xor_a_with_z()

def selective_complement_specific(hardware: Hardware) -> None:
    """
    [A] ^ [7777(0)] -> A

    :param hardware: emulator hardware including storage and I/O
    :return: None
    """
    storage = hardware.storage
    storage.specific_to_z()
    storage.xor_a_with_z()

def selective_jump(hardware: Hardware) -> int:
    """
    Set the next address based on E and the jump switch settings.
    E contains the required jump switches. Jump if it specifies
    any set jump switch, otherwise continue normal execution flow.

    :param hardware: emulator hardware including storage and I/O
    :return: the number of cycles used: 1 if no jump, 2 if jump
    """
    storage = hardware.storage
    mask = (storage.f_e >> 3) & 0o07
    if storage.and_with_jump_switches(mask) != 0:
        storage.g_to_next_address()
        return 2
    else:
        storage.next_after_two_word_instruction()
        return 1

def selective_stop(hardware: Hardware) -> None:
    """
    Halt if the lower half of E has any bits set that are also
    set that match the jump switch mask. Normal execution
    flow resumes when the operator restarts the machine.

    :param hardware: emulator hardware including storage and I/O
    :return: None
    """
    storage = hardware.storage
    mask = storage.f_e & 0o07
    if storage.and_with_stop_switches(mask) != 0:
        storage.stop()

def selective_stop_and_jump(hardware: Hardware) -> int:
    """
    Determine the next address based on the jump switches per
    selective_jump() above. Then stop as determine by selective_stop()
    above. Execution resumes at the address determined in the first
    step.

    :param hardware: emulator hardware including storage and I/O
    :return: the number of cycles used.
    """
    selective_stop(hardware)
    return selective_jump(hardware)

def set_buf_bank_from_e(hardware: Hardware) -> None:
    """
    [E] & 0o07 -> Buffer Bank Control

    Set the buffer bank control to the lower three bits of E.

    :param hardware: emulator hardware including storage and I/O
    :return: None
    """
    hardware.storage.set_buffer_bank_from_e()

def set_dir_bank_from_e(hardware: Hardware) -> None:
    """
    [E] & 0o07 -> Direct Bank Control

    Sets the direct bank control to the lower three bits of E

    :param hardware: emulator hardware including storage and I/O
    :return: None
    """
    hardware.storage.set_direct_bank_from_e()


def set_dir_ind_rel_bank_from_e_and_jump(hardware: Hardware) -> None:
    """
    [E] & 0o07 -> Direct, Indirect, and Relative Bank Control, [A] -> P

    Sets the direct and relative bank controls to the lower three bits of E
    and P to the value in A, jumping to [A](r), where r represents the
    newly set relative storage bank.

    :param hardware: emulator hardware including storage and I/O
    :return: None
    """
    storage = hardware.storage
    storage.set_direct_bank_from_e()
    storage.set_indirect_bank_from_e()
    storage.set_relative_bank_from_e_and_jump()

def set_dir_rel_bank_from_e_and_jump(hardware: Hardware) -> None:
    """
    [E] & 0o07 -> Direct and Relative Bank Control, [A] -> P

    Sets the direct and relative bank controls to the lower three bits of E
    and P to the value in A, jumping to [A](r), where r represents the
    newly set relative storage bank.

    :param hardware: emulator hardware including storage and I/O
    :return: None
    """
    hardware.storage.set_direct_bank_from_e()
    hardware.storage.set_relative_bank_from_e_and_jump()

def set_ind_bank_from_e(hardware: Hardware) -> None:
    """
    [E] & 0o07 -> Indirect Bank Control

    Set the indirect bank control to the lower three bits of E

    :param hardware: emulator hardware including storage and I/O
    :return: None
    """
    hardware.storage.set_indirect_bank_from_e()

def set_ind_dir_bank_from_e(hardware: Hardware) -> None:
    hardware.storage.set_direct_bank_from_e()
    hardware.storage.set_indirect_bank_from_e()

def set_ind_rel_bank_from_e_and_jump(hardware: Hardware) -> None:
    """
    [E] & 0o07 -> Indirect and Relative Bank Control, [A] -> P

    Set the indirect and relative storage banks to the lower three bits of E
    and P to the value of A, causing the program to branch to [A](r) where
    r represents the newly set relative bank.

    :param hardware: emulator hardware including storage and I/O
    :return: None
    """
    hardware.storage.set_indirect_bank_from_e()
    hardware.storage.set_relative_bank_from_e_and_jump()

def set_rel_bank_from_e_and_jump(hardware: Hardware) -> None:
    """
    [E] & 0o07 -> Relative Storage Control, [A] -> P

    Set the relative storage bank to the lower three bits of E and
    P to the value of A, causing the program to branch to [A](r) where
    r represents the newly set relative bank.

    :param hardware: emulator hardware including storage and I/O
    :return: None
    """
    hardware.storage.set_relative_bank_from_e_and_jump()

def shift_a_right_one(hardware: Hardware) -> None:
    """
    [A] >> 1 -> A

    Sign extended.

    :param hardware: emulator hardware including storage and I/O
    :return: None
    """
    storage = hardware.storage
    sign_extension = storage.a_register & 0o4000
    storage.a_register = (storage.a_register >> 1) | sign_extension

def shift_a_right_two(hardware: Hardware) -> None:
    storage = hardware.storage
    sign_extension = 0 if storage.a_register & 0o4000 == 0 else 0o6000
    storage.a_register = (storage.a_register >> 2) | sign_extension

def shift_replace_direct(hardware: Hardware) -> None:
    s_direct_to_a(hardware)
    rotate_a_left_one(hardware)
    a_to_s_direct(hardware)

def shift_replace_indirect(hardware: Hardware) -> None:
    s_indirect_to_a(hardware)
    rotate_a_left_one(hardware)
    a_to_s_indirect(hardware)

def shift_replace_relative(hardware: Hardware) -> None:
    s_relative_to_a(hardware)
    rotate_a_left_one(hardware)
    a_to_s_relative(hardware)

def shift_replace_specific(hardware: Hardware) -> None:
    specific_to_a(hardware)
    rotate_a_left_one(hardware)
    a_to_specific(hardware)

def specific_complement_to_a(hardware: Hardware) -> None:
    """
    ~[0o7777](0) -> A

    :param hardware: emulator hardware including storage and I/O
    :return: None
    """
    specific_to_a(hardware)
    hardware.storage.complement_a()

def specific_to_a(hardware: Hardware) -> None:
    """
    [0o7777](0) -> A

    :param hardware: emulator hardware including storage and I/O
    :return: None
    """
    hardware.storage.specific_to_a()

def s_direct_complement_to_a(hardware: Hardware) -> None:
    """
    ~[S](d) -> A

    :param hardware: emulator hardware including storage and I/O
    :return: None
    """
    s_direct_to_a(hardware)
    hardware.storage.complement_a()

def s_direct_to_a(hardware: Hardware) -> None:
    """
    [S](d) -> A

    :param hardware: emulator hardware including storage and I/O
    :return: None
    """
    hardware.storage.s_direct_to_a()

def s_indirect_complement_to_a(hardware: Hardware) -> None:
    """
    ~[S](d) -> A

    :param hardware: emulator hardware including storage and I/O
    :return: None
    """
    s_indirect_to_a(hardware)
    hardware.storage.complement_a()

def s_indirect_to_a(hardware: Hardware) -> None:
    """
    [S](i) -> A

    :param hardware: emulator hardware including storage and I/O
    :return: None
    """
    hardware.storage.s_indirect_to_a()

def s_relative_complement_to_a(hardware: Hardware) -> None:
    """
    ~[S](r) -> A

    :param hardware: emulator hardware including storage and I/O
    :return: None
    """
    s_relative_to_a(hardware)
    hardware.storage.complement_a()

def s_relative_to_a(hardware: Hardware) -> None:
    """
    [S](r) -> A

    :param hardware: emulator hardware including storage and I/O
    :return: None
    """
    hardware.storage.s_relative_to_a()

def subtract_e_from_a(hardware: Hardware) -> None:
    hardware.storage.subtract_e_from_a()

def subtract_direct_from_a(hardware: Hardware) -> None:
    hardware.storage.subtract_s_address_from_a(
        hardware.storage.direct_storage_bank)

def subtract_indirect_from_a(hardware: Hardware) -> None:
    hardware.storage.subtract_s_address_from_a(
        hardware.storage.indirect_storage_bank)

def subtract_relative_from_a(hardware: Hardware) -> None:
    hardware.storage.subtract_s_address_from_a(
        hardware.storage.relative_storage_bank)

def subtract_specific_from_a(hardware: Hardware) -> None:
    hardware.storage.subtract_specific_from_a()

def a_to_buffer(storage: Storage) -> None:
    """
    A -> [S](b)

    :param storage: memory and register file
    :return: None
    """
    storage.a_to_s_buffer()

def a_to_s_direct(hardware: Hardware) -> None:
    """
    A -> [S](d)

    :param hardware: emulator hardware including storage and I/O
    :return: None
    """
    hardware.storage.a_to_s_direct()

def a_to_s_indirect(hardware: Hardware) -> None:
    """
    A -> [S](i)

    :return: None
    """
    hardware.storage.a_to_s_indirect()

def a_to_s_relative(hardware: Hardware) -> None:
    hardware.storage.a_to_s_relative()

def a_to_specific(hardware: Hardware) -> None:
    """
    A -> [0o7777](0)

    :return: None
    """
    hardware.storage.a_to_specific()

def jump_if_a_negative(hardware: Hardware) -> None:
    storage = hardware.storage
    if storage.a_negative():
        storage.s_to_next_address()
    else:
        storage.next_after_one_word_instruction()

def jump_if_a_nonzero(hardware: Hardware) -> None:
    storage = hardware.storage
    if storage.a_not_zero():
        storage.s_to_next_address()
    else:
        storage.next_after_one_word_instruction()

def jump_if_a_positive(hardware: Hardware) -> None:
    storage = hardware.storage
    if storage.a_positive():
        storage.s_to_next_address()
    else:
        storage.next_after_one_word_instruction()

def jump_if_a_zero(hardware: Hardware) -> None:
    storage = hardware.storage
    if storage.a_zero():
        storage.s_to_next_address()
    else:
        storage.next_after_one_word_instruction()

def __write_word_normal(hardware: Hardware, value: int) -> bool:
    """
    Write one word to the selected output device.

   :param hardware: the emulated hardware, including storage
                     and I/O
    :param value: the word to write
    :return: True if the write succeeds, False otherwise. The write
             will fail when no output device is selected or if the
             selected device is off-line.
    """
    hardware.storage.normal_output_active()
    status = hardware.input_output.write_normal(value)
    if not status:
        hardware.storage.indefinite_delay()
    return status

def output_from_a(hardware: Hardware) -> int:
    """
    Write the contents of the A register to the device on the
    normal output channel. Hang the computer if the write fails.

    :param hardware: the emulated hardware, including storage
                     and I/O
    :return: the number of cycles used
    """
    __write_word_normal(hardware, hardware.storage.a_register)
    return hardware.input_output.write_delay()

def output_no_address(hardware: Hardware) -> int:
    """
    Write the contents of the F_E register to the device on the
    normal output channel. Hang the computer if the write fails.

    :param hardware: the emulated hardware, including storage
                     and I/O
    :return: the number of cycles used
    """
    __write_word_normal(hardware, hardware.storage.f_e)
    return hardware.input_output.write_delay()

def output_from_memory(hardware: Hardware) -> int:
    """
    Synchronous write from the indirect memory bank to the device
    on the normal channel. G contains the LWA to write and S,
    the effective address, contains the FWA. At the end of
    a successful write, S will contain the LWA written from.
    Hang if the write fails.

    :param hardware: the emulated hardware, including storage
                     and I/O
    :return: the number of cycles used
    """
    elapsed_cycles = 0
    lwa_plus_one = hardware.storage.g_contents()
    i_o_status = True
    while i_o_status and hardware.storage.s_register < lwa_plus_one and not \
        hardware.storage.machine_hung:
        i_o_status = __write_word_normal(
            hardware,
            hardware.storage.read_from_s_indirect_and_increment_s())
        elapsed_cycles += hardware.input_output.write_delay()

    return elapsed_cycles
