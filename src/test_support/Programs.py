"""
Programs for testing the emulator.

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

By convention, the relative bank is 3 and programs start
at 0100(3).

Note: the following programs must be kept consistent with
the tests in test_RunLoop.py and elsewhere. Change with care.

Caveat coder!
"""

# Assembler sanity checks.
VACUOUS_THREE_LINE_PROGRAM_WITH_BLANK_LINE = """
          REM This is a three instruction vacuous program staring with a blank line.
          END
          INVALID INSTRUCTION
"""
SET_STORAGE_BANK = """
          REM  Set the storage bank to 3
          BNK  3
          END
"""
SET_ADDRESS = """
          REM  Set the address to 1234
          ORG  1234
          END
"""

# Individual instructions
A_TO_BUFFER_ENTRANCE = """
          REM A to Buffer Entrance Register A -> BER
          BNK 3
          ORG 100
          LDC 3000     3000 -> A
          ATE 200      A -> BER
          HLT
          END
"""
A_TO_BUFFER_EXIT = """
          REM A to Buffer Exit Register A -> BXR
          BNK 3
          ORG 100
          LDC 3000    3000 -> A
          ATX 200     A -> BTX
          HLT
          END
"""
ADD_BACKWARD = """
          REM Add backward: A -> A + [P - E]
          BNK 3
          ORG 77
          OCT 34
          LDC 1200
          ADB 3
          HLT
          END
"""
ADD_CONSTANT = """
          REM Add constant: A -> A + G
          BNK 3
          ORG 100
          LDC 1200
          ADC 34
          HLT
          END
"""
ADD_DIRECT = """
          REM Add direct A -> A + 40(d)
          BNK 2
          ORG 40
          OCT 34
          BNK 3
          ORG 100
          LDC 1200
          ADD 40
          HLT
          END
"""
ADD_FORWARD = """
          REM Add forward A -> A + [P + E]
          BNK 3
          ORG 100
          LDC 1200
          ADF 2
          HLT
          OCT 34
          END
"""
ADD_INDIRECT = """
          REM Add indirect, A -> A + [40(i)
          BNK 1
          ORG 40
          OCT 34
          BNK 3
          ORG 100
          LDC 1200
          ADI 40
          HLT
          END
"""
ADD_NO_ADDRESS = """
          REM Add no address A -> A + 34
          BNK 3
          ORG 100
          LDC 1200
          ADN 34
          HLT
          END
"""
ADD_MEMORY = """
          REM Add memory A -> A + [120]
          BNK 3
          ORG 100
          LDC 1200
          ADM 120
          HLT
          ORG 120
          OCT 34
          END
"""
ADD_SPECIFIC = """
          REM Add specific, A -> A + [7777(0)]
          BNK 0
          ORG 7777
          OCT 34
          BNK 3
          ORG 100
          LDC 1200
          ADS
          HLT
          END
"""
BANK_CONTROLS_TO_A = """
          REM Bank Controls to A
          REM     Buffer Bank Control Register -> A(11 - 9)
          REM     Direct Bank Control Register -> A(8 - 6)
          REM     Indirect Bank Control Register -> A(5 - 3)
          REM     Relative Bank Control Register -> A(2 - 0)
          REM
          REM     Note: subscripts indicate the bit positions in A with
          REM           11 being the most significant.
          BNK 3
          ORG 100
          SBU 1
          SDC 2
          SIC 3
          LDC 200
          SRJ 4
          BNK 4
          ORG 200
          CTA
          HLT
          END
"""
BLOCK_STORE = """
          REM Block Store Test. See page 3-12 (page 32 in the PDF reader)
          REM in the 160-A Program Reference Manual
          BNK 3
          ORG 100
          LDC 1000      1000 -> A
          ATE 200       A -> BER, BER will contain 1000 as FWA
          LDC 4001      4001 -> A
          ATX 200       A -> BXR, BXR will contain 4001 as LWA + 1
          LDC 6000      6000 -> A
          BLS           6000 -> [1000(3) .. 4000(3)]
          HLT
          ORG 200       If buffer is active (shouldn't happen)
          HLT
          END
"""
BUFFER_ENTRANCE_TO_A = """
          REM Buffer Entrance to A, BER -> A
          REM Note: Must set the BER first.
          BNK 3
          ORG 100
          LDC 3000     3000 -> A
          ATE 200      A -> BER
          LDN 0        0 - > A      
          ETA          BER -> A
          HLT
          END    
"""
BUFFER_IN_FROM_BI_TAPE = """
          REM Buffer in from the HyperLoopQuantumGravityBiTape
          REM
          REM Bank settings:
          REM Bank          Selected
          REM ------------- --------
          REM Buffer               0
          REM Direct               2
          REM Indirect             1
          REM Relative             3
          REM
          BNK 3
          ORG 20       Interrupt 20 handler
          OCT 0        Return address goes here
          JFI 1
          OCT 400      Interrupt handler location

          ORG 100
          LDC 200      200 -> A
          ATE 301      [A] -> BER, FWA == 200
          LDC 212      212 -> A
          ATX 302      [A] -> BXR, LWA + 1 = 212
          EXC 3700     Select the BiTape
          CIL          External functions lock interrupts
          REM          We will buffer 10 words of input
          LDN 0        The interrupt handler will set A nonzero
          IBI 300
          REM
          REM          Buffer wait loop
          REM
          NOP          Probably not needed, but why not?
          ZJB 1        Interrupt 20 handler will set A positive
          REM
          HLT          Success halt at buffer loop exit.

          ORG 300
          HLT          IBI error halt
          HLT          ATE error halt
          HLT          ATX error halt.

          ORG 400      Interrupt handler
          LDN 1        Nonzero A causes the buffer wait loop to
          REM          exit.
          CIL
          JPI 20       Back to the buffer wait loop
          END
"""
BUFFER_OUT_TO_BI_TAPE = """
          REM Buffer out to the HyperLoopQuantumGravityBiTape
                    REM
          REM Bank settings:
          REM Bank          Selected
          REM ------------- --------
          REM Buffer               0
          REM Direct               2
          REM Indirect             1
          REM Relative             3
          REM
          BNK 3
          ORG 20       Interrupt 20 handler
          OCT 0        Return address goes here
          JFI 1
          OCT 400      Interrupt handler address

          ORG 100      Program start
          LDC 200      200 -> A
          ATE 301      [A] -> BER, FWA == 200
          LDC 212      212 -> A
          ATX 302      [A] -> BXR, LWA + 1 = 212
          EXC 3700     Select the BiTape
          CIL          External functions lock interrupts
          REM          We will buffer 10 words of input
          LDN 0        The interrupt handler will set A nonzero
          IBO 300
          REM
          REM          Buffer wait loop
          REM
          NOP          Probably not needed, but why not?
          ZJB 1        Interrupt 20 handler will set A positive
          HLT          Success halt

          ORG 200      Data to write
          OCT          10
          OCT          06
          OCT          04
          OCT          02
          OCT          00
          OCT          01
          OCT          03
          OCT          05
          OCT          07
          OCT          11

          ORG 300      Error halts
          HLT          IBI error halt
          HLT          ATE error halt
          HLT          ATX error halt.

          ORG 400      Interrupt handler
          LDN 1        Nonzero A causes the buffer wait loop to
          REM          exit.
          CIL
          JPI 20       Back to the buffer wait loop
          END

"""
CLEAR_BUFFER_CONTROLS = """
          REM Test clear buffer controls. The test must start
          REM buffering before running this program.
          BNK 3
          ORG 100
          CBC        Stop buffering and deselect the peripheral
          HLT
          END
"""
CLEAR_INTERRUPT_LOCKOUT = """
          REM Test interrupt lockout. The test must lock interrupts
          REM before running this.
          BNK 3
          ORG 100
          CIL   Interrupt lock -> Unlock Pending
          NOP   Interrupt lock -> Free
          HLT
          END 
"""
ERROR_HALT = """
          REM Error halt execution and set the error flag.
          ERR
          END
"""
EXTERNAL_FUNCTION_CONSTANT = """
          REM Selects the paper tape reader with a external function constant
          REM instruction. Note that 4102 selects the reader, and provides
          REM no device status
          BNK 3
          ORG 100
          EXC 4102
          HLT
          END
"""
EXTERNAL_FUNCTION_FORWARD = """
          REM Selects the paper tape reader with an external function forward
          REM instruction. Note that 4102 selects the reader, and provides
          REM no device status
          BNK 3
          ORG 100
          EXF 40
          HLT
          ORG 140
          OCT 4102
          END
"""
HALF_WRITE_INDIRECT = """
          REM Half Write Indirect: [E](d) -> S, A(0 .. 6) -> [S](i)
          REM Form the effective address from the value at E in the
          REM indirect storage bank, and store the lower 6 bits
          REM of A at the effective address in the direct storage
          REM bank. The upper 6 bits of the destination are unchanged.
          REM
          BNK 2     Indirect storage bank.
          ORG 44    E in the half write indirect instruction
          OCT 2100  Destination address in the indirect bank.
          BNK 1     Indirect storage bank
          ORG 2100  Destination address
          OCT 4377
          BNK 3     Relative storage bank
          ORG 100   Program start address
          LDC 7621
          HWI 44    Half write indirect via [44](i)
          HLT
          END
"""
HALT = """
          REM  Simplest possible non-vacuous program that just halts
          BNK 3
          ORG 100
          HLT
          END
"""
INITIATE_BUFFER_INPUT_CHANNEL_BUSY = """
          REM Initiate buffer input from the BiTape with
          REM the buffer channel busy
          BNK 3
          ORG 100
          IBI 200        Start buffered input, branch to 200 if failure
          REM            Throws the buffer channel into an endless loop.
          EXC 3700       Select the BiTape
          CIL            External functions lock interrupts
          IBI 300        Start buffered input, branch to 300 if failure
          HLT            Error halt for second IBI instruction
          ORG 200
          HLT            Error halt for first IBI instruction
          ORG 300
          HLT            Success halt
          END
"""
INITIATE_BUFFER_INPUT_CHANNEL_FREE = """
          REM Initiate buffer input from the BiTape with
          REM the buffer channel free
          BNK 3
          ORG 100
          EXC 3700       Select the BiTape
          CIL            External functions lock interrupts
          IBI 300        Start buffered input, branch to 300 if failure
          HLT            Success halt
          ORG 300
          HLT            Error halt
          END
"""
INPUT_TO_A = """
          REM Reads one word from the HyperLoopQuantumGravityBiTape
          REM to A. Device must be on and have one or more words
          REM of input available. We only need one.
          REM
          REM Bank settings:
          REM   Buffer: 0
          REM   Direct: 2
          REM   Indirect: 1
          REM   Relative: 3
          REM
          BNK 3
          ORG 100
          EXC 3700   Select the HyperLoopQuantumGravityBiTape
          SBN 1      Return should be 0001 -- Input Available
          ZJF 2      Should skip the next instruction
          HLT        Halt if device is off or has no available input
          INA        One word if input to the A register
          HLT        Success halt.
          END
"""
INPUT_TO_MEMORY = """
          REM Reads 0o10 (decimal 8) words from the 
          REM HyperLoopQuantumGravityBiTape to the indirect storage
          REM bank starting at 0o300 and ending at 0o307. Note that
          REM the last word address + 1 will be 0o310. The 
          REM HyperLoopQuantumGravityBiTape must be on-line and
          REM have 8 or more input words available.
          REM
          REM Bank settings:
          REM   Buffer: 0
          REM   Direct: 2
          REM   Indirect: 1
          REM   Relative: 3
          REM
          BNK 3
          ORG 100
          EXC 3700   Select the HyperLoopQuantumGravityBiTape
          SBN 1      Return should be 0001 -- Input Available
          ZJF 2      Should skip the next instruction
          HLT        Halt if device is off or has no available input
          INP 3 310  Normal input, LWA + 1 is 310
          HLT        Success halt.
          OCT 300    FWA (first word address)
          END
"""
INTERRUPT_10_SIMPLE = """
          REM A simple program for testing interrupt 10. The program is
          REM completely contrived and not at all representative of
          REM production interrupt handling.
          REM
          REM Bank settings:
          REM   Buffer: 0
          REM   Direct: 2
          REM   Indirect: 1
          REM   Relative: 3
          REM
          BNK 3     Emit to the relative bank.
          ORG 11    Interrupt 10 handler
          JFI 1     Jump to the address in the following location
          OCT 200   Interrupt handler at 200(r)
          ORG 100   Canonical start address.
          LDN 0
          REM       The test should generate interrupt 10 before running
          REM       the following instruction.
          HLT
          ORG 200    Interrupt routine
          ADN 1      Test succeeds if A contains 1 ...
          CIL        ... and interrupt lockout is cleared.
          JPI 10
          END
"""
JUMP_FORWARD_INDIRECT = """
          REM Jump Forward Indirect [)[P] + XX)(r)](r) -> P
          BNK 3
          ORG 100
          JFI 2
          NOP
          OCT 200
          ORG 200
          HLT
          END
"""
JUMP_INDIRECT = """
          REM Jump Indirect: [E(d)] -> P
          BNK 2    Direct Storage Bank
          ORG 30   Contains the address
          OCT 200  Jump to 200
          BNK 3
          ORG 100
          JPI 30
          HLT
          ORG 200  JPI branches here
          HLT
          END
"""
LDC_THEN_HALT = """
          REM  move 0o4321 to the accumulator and halt
          BNK 3
          ORG 100
          LDC 4321
          HLT
          END
"""
LDC_SHIFT_HALT = """
          REM  move 0o4321 to the accumulator, shift left by 3 bits,
          REM  and halt
          BNK 3
          ORG 100
          LDC 4321
          LS3
          HLT
          END
"""
LOGICAL_PRODUCT_BACKWARD = """
          REM logical product backward, A -> A & [P - E]
          BNK 3
          ORG 77
          OCT 77
          LDC 4321
          LPB 3
          HLT
          END
"""
LOGICAL_PRODUCT_CONSTANT = """
          REM logical product constant, A -> A & [G](r)
          BNK 3
          ORG 100
          LDC 4321
          LPC 77
          HLT
          END
"""
LOGICAL_PRODUCT_DIRECT = """
          REM logical product direct, A -> A & E(d)
          BNK 2
          ORG 40
          OCT 77
          BNK 3
          ORG 100
          LDC 4321
          LPD 40
          HLT
          END
"""
LOGICAL_PRODUCT_FORWARD = """
          REM Logical product forward: A -> A & [P + E]
          BNK 3
          ORG 100
          LDC 4321
          LPF 2
          HLT
          OCT 77
          END
"""
LOGICAL_PRODUCT_INDIRECT = """
          REM logical product indirect A -> A & E(i)
          BNK 1
          ORG 40
          OCT 77
          BNK 3
          ORG 100
          LDC 4321
          LPI 40
          HLT
          END
"""
LOGICAL_PRODUCT_MEMORY = """
          REM logical product from memory, A -> A & [G](r)
          BNK 3
          ORG 100
          LDC 4321
          LPM 40
          HLT
          ORG 40
          OCT 77
          END
"""
LOGICAL_PRODUCT_NONE = """
          REM logical product no address with A
          BNK 3
          ORG 100
          LDC 4321
          LPN 77
          HLT
          END
"""
LOGICAL_PRODUCT_SPECIFIC = """
          REM logical product specific, A -> A & [7777(0)]
          BNK 0
          ORG 7777
          OCT 77
          BNK 3
          ORG 100
          LDC 4321
          LPS
          HLT
"""
MULTIPLY_BY_10 = """
          REM Multiply By 100 A * 100 -> A
          BNK 3
          ORG 100
          LDN 1
          MUT
          HLT
          END
"""
MULTIPLY_BY_100 = """
          REM Multiply By 100 A * 100 -> A
          BNK 3
          ORG 100
          LDN 1
          MUH
          HLT
          END
"""
NOOP_THEN_HALT = """
          REM  no-op followed by a halt
          BNK 3
          ORG 100
          NOP
          HLT
          END
"""
NEGATIVE_JUMP_BACKWARD_MINUS_ZERO_A = """
          REM Negative jump backward with a set to 0
          BNK 3
          ORG 77
          HLT
          LDC 7777
          NJB 3
          HLT
          END
"""
NEGATIVE_JUMP_BACKWARD_ZERO_A = """
          REM Negative jump backward with a set to 0
          BNK 3
          ORG 77
          HLT
          LDC 0
          NJB 3
          HLT
          END
"""
NEGATIVE_JUMP_FORWARD_ZERO_A = """
          REM Negative jump forward with A set to 0
          BNK 3
          ORG 100
          LDN 0
          NZF 2    # +0
          HLT      # +1
          HLT      # +2
          END
"""
NEGATIVE_JUMP_FORWARD_MINUS_ZERO_A = """
          REM Negative jump forward with A set to minus zero
          BNK 3
          ORG 100
          LDC 7777
          NZF 2    # +0
          HLT      # +1
          HLT      # +2
          END
"""
NONZERO_JUMP_FORWARD_MINUS_ZERO_A = """
          REM Nonzero jump backward with a set to minus zero
          BNK 3
          ORG 77
          HLT
          LDC 7777
          NZF 2
          HLT
          HLT
          END
"""
NONZERO_JUMP_FORWARD_ZERO_A = """
          REM Nonzero jump backward with a set to zero
          BNK 3
          ORG 77
          HLT
          LDC 0
          NZF 2
          HLT
          HLT
          END
"""
OUTPUT_FROM_A = """
          REM Write one word from the A register to the 
          REM HyperLoopQuantumGravityBiTape.
          BNK 3
          ORG 100
          EXC 3700    Select the HyperLoopQuantumGravityBiTape
          CIL         External functions lock interrupts
          LDN 34      Value to write
          OTA         Write to the BiTape
          HLT         We done
          END
"""
OUTPUT_FROM_MEMORY = """
          REM Write from the indirect bank to the
          REM HyperLoopQuantumGravityBiTape. The
          REM program writes the data to memory
          REM
          REM Storage banks are initialized as follows:
          REM
          REM   Bank             Setting
          REM   ---------------- -------
          REM   Buffer                 0
          REM   Direct                 2
          REM   Indirect               1
          REM   Relative               3
          REM
          BNK 3
          ORG 100
          EXC 3700    Select the HyperLoopQuantumGravityBiTape
          CIL         External functions lock out interrupts
          OUT 3 211   Write data from indirect memory bank. Start at address
          REM         found at * + 3 up to but not including 211 
          HLT         Success!
          OCT 200     Write from address 200.
          REM Initialize the output buffer.
          BNK 1
          ORG 200     9 words of output data starts here.
          OCT 10
          OCT  6
          OCT  4
          OCT  2
          OCT  0
          OCT  1
          OCT  3
          OCT  5
          OCT  7
          END
"""
OUTPUT_NO_ADDRESS = """
          REM Write one word to the HyperLoopQuantumGravityBiTape
          REM and verify the results.
          BNK 3
          ORG 100
          EXC 3700    Select the HyperLoopQuantumGravityBiTape
          CIL         External functions lock interrupts
          OTN 34      Write to the BiTape
          HLT         We done
          END
"""
P_TO_A = """
          REM P to A, [P] -> A
          BNK 3
          ORG 100
          PTA
          HLT
"""
POSITIVE_JUMP_BACKWARD_MINUS_ZERO_A = """
          REM Positive jump backward with a set to minus zero
          BNK 3
          ORG 77
          HLT
          LDC 0
          PJB 3
          HLT
          END
"""
POSITIVE_JUMP_BACKWARD_ZERO_A = """
          REM Positive jump backward with a set to minus zero
          BNK 3
          ORG 77
          HLT
          LDC 0
          PJB 3
          HLT
          END
"""
POSITIVE_JUMP_FORWARD_MINUS_ZERO_A = """
          REM Positive jump forward with A set to minus zero
          BNK 3
          ORG 100
          LDC 7777
          PJF 2    # +0
          HLT      # +1
          HLT      # +2
          END
"""
POSITIVE_JUMP_FORWARD_ZERO_A = """
          REM Positive jump forward with A set to minus zero
          BNK 3
          ORG 100
          LDC 0
          PJF 2    # +0
          HLT      # +1
          HLT      # +2
          END
"""
PUNCH_PAPER_TAPE = """
          REM Punch a paper tape. The test must open the punch
          REM before running this script
          REM
          REM Storage banks are initialized as follows:
          REM
          REM   Bank             Setting
          REM   ---------------- -------
          REM   Buffer                 0
          REM   Direct                 2
          REM   Indirect               1
          REM   Relative               3
          REM
          BNK 3
          ORG 100
          EXC 4104     Select the paper tape punch
          OUT 03 0217  Output LWA + 1
          HLT
          REM
          REM          Output data. Note that 150-A normal
          REM          output writes from the indirect bank.
          REM
          OCT 0200     Output FWA
          REM
          REM Data to punch -- indirect bank
          BNK 1
          ORG 200
          OCT 0200
          OCT 0100
          OCT 0040
          OCT 0020
          OCT 0010
          OCT 0004
          OCT 0002
          OCT 0001
          OCT 0000
          OCT 0037
          OCT 0077
          OCT 0177
          OCT 0377
          OCT 0410
          OCT 0777
          END
"""
REPLACE_ADD_BACKWARD = """
          REM Replace Add Backward, [(P - YY)(r)] + A -> A, [(P - YY)(r)]
          BNK 3
          ORG 77
          OCT 1200
          LDN 34
          RAB 2
          HLT
          END
"""
REPLACE_ADD_CONSTANT = """
          REM Replace Add Constant, [G(r)] + A -> A and [G(r)]
          BNK 3
          ORG 100
          LDC 34
          RAC 1200
          HLT
          END
"""
REPLACE_ADD_DIRECT = """
          REM Replace Add Direct, [YY(d)] + A -> A and [YY(d)]
          REM Direct 2, Indirect 1, Relative 3
          BNK 2
          ORG 20
          OCT 1200
          BNK 3
          ORG 100
          LDC 34
          RAD 20
          HLT
          END
"""
REPLACE_ADD_FORWARD = """
          REM Replace Add Forward, [(P + YY)(r)] + A -> A and
          REM [(P + YY)(r)]
          BNK 3
          ORG 100
          LDC 34
          RAF 2
          HLT
          OCT 1200
          END
"""
REPLACE_ADD_INDIRECT = """
          REM Replace Add Indirect, A + [YY(d)] -> A and [YY(i)]
          BNK 1
          ORG 14
          OCT 1200
          BNK 3
          ORG 100
          LDC 34
          RAI 14
          HLT
          END
"""
REPLACE_ADD_MEMORY = """
          REM Replace Add Memory,  A + [G(r)] -> A and [G(r)]
          BNK 3
          ORG 100
          LDC 34
          RAM 200
          HLT
          ORG 200
          OCT 1200
          END 
"""
REPLACE_ADD_ONE_BACKWARD = """
          REM Replace Add One Backward [(P - YY)(r)] + 1 -> A and [(P - YY)(r)]
          BNK 3
          ORG 77
          OCT 1233
          AOB 1
          HLT
          END
"""
REPLACE_ADD_ONE_CONSTANT = """
          REM Replace Add One Constant [G(r)} + 1 -> A and [G(r)]
          BNK 3
          ORG 100
          AOC 1233
          HLT
          END
"""
REPLACE_ADD_ONE_DIRECT = """
          REM Replace Add One Direct [XX(d)] + 1 -> A and [XX(d)]
          BNK 2
          ORG 40
          OCT 1233
          BNK 3
          ORG 100
          AOD 40
          HLT
          END
"""
REPLACE_ADD_ONE_FORWARD = """
          REM Replace Add One Forward, [(P + YY)(r)] + 1 -> A and [(P + YY)(r)]
          BNK 3
          ORG 100
          AOF 2
          HLT
          OCT 1233
          END
"""
REPLACE_ADD_ONE_INDIRECT = """
          REM Replace Add One Indirect  [XX(i)] + 1 -> A and [XX(i)]
          BNK 1
          ORG 40
          OCT 1233
          BNK 3
          ORG 100
          AOI 40
          HLT
          END
"""
REPLACE_ADD_ONE_MEMORY = """
          REM Replace Add One Memory [G(r)] + 1 -> A, [G(r)]
          BNK 3
          ORG 100
          AOM 200
          HLT
          ORG 200
          OCT 1233
          END
"""
REPLACE_ADD_ONE_SPECIFIC = """
          REM Replace Add One Specific [7777(0)] + 1 -> A and [7777(0)]
          BNK 0
          ORG 7777
          OCT 1233
          BNK 3
          ORG 100
          AOS
          HLT
"""
REPLACE_ADD_SPECIFIC = """
          REM Replace Add Storage, A + [7777(0)] -> A and [7777(0)]
          BNK 0
          ORG 7777
          OCT 1200
          BNK 3
          ORG 100
          LDC 34
          RAS
          HLT
          END
"""
RETURN_JUMP = """
          REM Return Jump [P] + 2 -> YYYY(r), YYY + 1 -> P
          BNK 3
          ORG 100
          JPR 200
          ERR
          ORG 200
          OCT 0
          HLT
          END
"""
SELECTIVE_COMPLEMENT_BACKWARD = """
          REM Selective Complement Backward [A] ^ [(P - YY)(r)] -> A
          BNK 3
          ORG 76
          OCT 12
          ORG 100
          LDN 14
          SCB 3
          END
"""
SELECTIVE_COMPLEMENT_CONSTANT = """
          REM Selective Complement Constant [A] ^ [G(r)] -> A
          BNK 3
          ORG 100
          LDC 14
          SCC 12
          HLT
          END
"""
SELECTIVE_COMPLEMENT_DIRECT = """
          REM Selective Complement Direct [A] ^ [YY(d)] -> A
          BNK 2
          ORG 40
          OCT 14
          BNK 3
          ORG 100
          LDN 12
          SCD 40
          HLT
          END
"""
SELECTIVE_COMPLEMENT_INDIRECT = """
          REM Selective Complement Direct [A] ^ [YY(i)] -> A
          BNK 1
          ORG 20
          OCT 14
          BNK 3
          ORG 100
          LDN 12
          SCI 20
          HLT
          END
"""
SELECTIVE_COMPLEMENT_MEMORY = """
          REM Selective Complement Memory [A] ^ [G(r)] -> A
          BNK 3
          ORG 100
          LDN 12
          SCM 200
          HLT
          ORG 200
          OCT 14
          END
"""
SELECTIVE_COMPLEMENT_NO_ADDRESS = """
          REM Selective Complement No Address [A] ^ YY -> A
          BNK 3
          ORG 100
          LDN 12
          SCN 14
          HLT
          END
"""
SELECTIVE_COMPLEMENT_SPECIFIC = """
          REM Selective Complement Specific [A] ^ [7777(0)] -> A
          BNK 0
          ORG 7777
          OCT 14
          BNK 3
          ORG 100
          LDN 12
          SCS
          HLT
          END
"""
SELECTIVE_JUMP = """
          REM Selective Jump: branch if any bit in E matches a set jump switch
          BNK 3
          ORG 100
          SLJ 2 200
          HLT
          ORG 200
          HLT
          END
"""
SELECTIVE_STOP = """
          REM Selective stop, stop if any bits in E specify a set Stop Switch
          BNK 3
          ORG 100
          SLS 2
          HLT
          END
"""
SELECTIVE_STOP_AND_JUMP = """
          REM Selective Stop and Jump, stop if any bits in E specifies a
          REM set Stop Switch, then jump if any bits in E match a set
          REM jump switch.
          BNK 3
          ORG 100
          SJS 52 200
          HLT
          ORG 200
          HLT
          END
"""
SET_BUFFER_STORAGE_BANK = """
          REM Set Buffer Bank Control: low E -> Buffer Bank Control
          BNK 3
          ORG 100
          SBU 6
          HLT
          END
"""
SET_DIRECT_BANK_CONTROL = """
          REM Set Direct Bank Control: low E -> Direct Bank Control
          BNK 3
          ORG 100
          SDC 6
          HLT
          END
"""
SET_DIRECT_INDIRECT_AND_RELATIVE_BANK_CONTROL_AND_JUMP = """
          REM Set Direct, Indirect, and Relative Bank Control and jump
          REM Low E -> Direct, Indirect, and Relative Bank Controls
          REM [A] -> P
          BNK 3
          ORG 100
          LDC 0o200
          ACJ 6
          BNK 6
          ORG 200
          HLT
          END
"""
SET_DIRECT_AND_RELATIVE_BANK_CONTROL_AND_JUMP = """
          REM Set Direct and Relative Bank Controls and Jump
          REM Low E -> Direct and Relative Storage Banks
          REM [A] -> P
          BNK 3
          ORG 100
          LDC 200
          DRJ 6
          HLT
          END
"""
SET_INDIRECT_BANK_CONTROL = """
          REM Set Indirect Bank Control: low E -> Indirect Bank Control
          BNK 3
          ORG 100
          SIC 6
          HLT
          END
"""
SET_INDIRECT_AND_DIRECT_BANK_CONTROL = """
          REM Set Indirect and Direct Bank Control
          REM Low E -> Indirect and Direct Bank Controls
          BNK 3
          ORG 100
          SID 6
          HLT
          END
"""
SET_INDIRECT_AND_RELATIVE_BANK_CONTROL_AND_JUMP = """
          REM Set Indirect and Relative Bank Control and Jump
          REM Low E -> indirect and relative bank controls,
          REM [A] -> P
          BNK 3
          ORG 100
          LDC 200
          IRJ 6
          BNK 6
          ORG 200
          HLT
          END
"""
SET_LITERAL = """
          REM set a literal value
          BNK 3
          ORG 100
          OCT 1234
          END
"""
SET_RELATIVE_BANK_CONTROL_AND_JUMP = """
          REM Set Relative Bank Control and Jump low E -> Relative Bank Control,
          REM [A] -> P
          BNK 3
          ORG 100
          LDC 0o200
          SRJ 6
          BNK 6
          ORG 200
          HLT
          END
"""
SHIFT_REPLACE_BACKWARD = """
          REM Shift Replace Backward [(P - YY)(r)] << 1 -> A and (P - YY)(r)
          BNK 3
          ORG 76
          OCT 4001
          ORG 100
          SRB 2
          HLT
          END
"""
SHIFT_REPLACE_CONSTANT = """
          REM Shift Replace Direct [G} << 1 -> A and G
          BNK 3
          ORG 100
          SRC 4001
          HLT
          END
"""
SHIFT_REPLACE_DIRECT = """
          REM Shift Replace Direct YY(d) << 1 -> A and YY(d)
          BNK 2
          ORG 14
          OCT 4001
          BNK 3
          ORG 100
          SRD 14
          HLT
          END
"""
SHIFT_REPLACE_FORWARD = """
          REM Shift Replace Forward [(P + XX)(r)] << 1 -> A and (P + XX)(r)
          BNK 3
          ORG 100
          SRF 2
          HLT
          OCT 4001
          END
"""
SHIFT_REPLACE_INDIRECT = """
          REM Shift Replace Indirect  YY(i) << 1 -> A and YY(i)
          BNK 1
          ORG 24
          OCT 4001
          BNK 3
          ORG 100
          SRI 24
          HLT
          END
"""
SHIFT_REPLACE_MEMORY = """
          REM Shift Replace Memory YYYY(r) << 1 -> A and YYYY(r)
          BNK 3
          ORG 100
          SRM 200
          HLT
          ORG 200
          OCT 4001
          END
"""
SHIFT_REPLACE_SPECIFIC = """
          REM Shift Replace Specific [7777(0)] << 1 -> A and 7777(0)
          BNK 0
          ORG 7777
          OCT 4001
          BNK 3
          ORG 100
          SRS
          HLT
          END 
"""
STORE_BACKWARD = """
          REM Store backward, which stores the A register
          REM contents to the current location minus the E
          REM value (which specifies a nonzero backwards offset).
          BNK 3
          ORG 77
          OCT 7777
          LDC 1234
          STB 3
          HLT
          END
"""
STORE_BUFFER_ENTRANCE_DIRECT_AND_A_TO_BUFFER_ENTRANCE = """
          REM Store Buffer Entrance, BER -> [E](d), A -> BER
          BNK 3        Relative storage bank by convention
          ORG 100      Program start address by convention
          LDC 5000     5000 -> A
          ATE 200      [A] -> BTE (BTE will contain 5000)
          LDC 3000     3000 -> A
          STE 67
          HLT
          ORG 200
          HLT
          END
          
"""
STORE_CONSTANT = """
          REM Store constant, store into instruction's G
          REM which seems odd, but that's what the manual says
          REM it does.
          BNK 3  Relative bank
          ORG 100
          LDC 1234
          STC 7777
          END
"""
STORE_DIRECT = """
          REM Store direct, store A to the direct storage bank
          BNK 2   Direct bank
          ORG 40
          OCT 7777
          BNK 3
          ORG 100
          LDC 1234
          STD 40
          HLT
          END
"""
STORE_FORWARD = """
          REM Store forward, store A to the current address plus
          REM the offset in E
          BNK 3
          ORG 100
          LDC 1234
          STF 2
          HLT
          OCT 7777
          END
"""
STORE_INDIRECT = """
          REM Store direct, store A to the direct storage bank
          BNK 1   Indirect bank
          ORG 40
          OCT 7777
          BNK 3
          ORG 100
          LDC 1234
          STI 40
          HLT
          END
"""
STORE_MEMORY = """
          REM Store memory, store A to [G](r)
          BNK 3
          ORG 100
          LDC 1234
          STM 1000
          HLT
          ORG 1000
          OCT 7777
          END
"""
STORE_P_REGISTER = """
          REM Store P, [P] -> E(d), 50 <= E <= 57
          BNK 3
          ORG 100
          STP 56
          HLT
          END
"""
STORE_SPECIFIC = """
          REM Store specific, store A 7777(0)
          BNK 0
          ORG 7777
          OCT 7777
          BNK 3
          ORG 100
          LDC 1234
          STS
          HLT
          END
"""
SUBTRACT_BACKWARD = """
          REM Subtract backward
          BNK 3
          ORG 77
          OCT 31
          LDC 1265
          SBB 3
          HLT
          END
"""
SUBTRACT_CONSTANT = """
          REM Subtract constant
          BNK 3
          ORG 100
          LDC 1265
          SBC 31
          HLT
          END
"""
SUBTRACT_DIRECT = """
          REM Subtract direct
          BNK 2 Direct storage bank
          ORG 40
          OCT 31
          BNK 3
          ORG 100
          LDC 1265
          SBD 40
          HLT
          END
"""
SUBTRACT_FORWARD = """
          REM Subtract forward
          BNK 3
          ORG 100
          LDC 1265
          SBF 2
          HLT
          OCT 31
          END
"""
SUBTRACT_INDIRECT = """
          REM Subtract indirect
          BNK 1 indirect storage bank
          ORG 40
          OCT 31
          BNK 3
          ORG 100
          LDC 1265
          SBI 40
          HLT
          END
"""
SUBTRACT_MEMORY = """
          REM Subtract memory
          BNK 3
          ORG 100
          LDC 1265
          SBM 110
          HLT
          ORG 110
          OCT 31
          END
"""
SUBTRACT_NO_ADDRESS = """
          REM Subtract no address 
          BNK 3
          ORG 100
          LDC 1265
          SBN 31
          HLT
          END
"""
SUBTRACT_SPECIFIC = """
          REM Subtract specific
          BNK 0
          ORG 7777
          OCT 31
          BNK 3
          ORG 100
          LDC 1265
          SBS
          HLT
          END
"""
ZERO_JUMP_BACKWARD_MINUS_ZERO_A = """
          REM Zero jump backward with a set to minus zero
          BNK 3
          ORG 77
          HLT
          LDC 7777
          ZJB 3
          HLT
          END
"""
ZERO_JUMP_BACKWARD_ZERO_A = """
          REM Zero jump backward with a set to minus zero
          BNK 3
          ORG 77
          HLT
          LDC 0
          ZJB 3
          HLT
          END
"""
ZERO_JUMP_FORWARD_MINUS_ZERO_A = """
          REM Zero jump forward with A set to minus zero
          BNK 3
          ORG 100
          LDC 0
          ZJF 2    # +0
          HLT      # +1
          HLT      # +2
          END
"""
ZERO_JUMP_FORWARD_ZERO_A = """
          REM Zero jump forward with A set to minus zero
          BNK 3
          ORG 100
          LDC 0
          ZJF 2    # +0
          HLT      # +1
          HLT      # +2
          END
"""

# More complex programs: invoke a subroutine and return from
# same.
CALL_AND_RETURN = """
          REM Invoke a subroutine and return
          BNK 3
          ORG 100
          JPR 200
          HLT
          ORG 200
          OCT 0  Return address goes here.
          LDB 1  Return address -> A
          STF 2  Store return address into the jump address
          JFI 1
          OCT 240
          ORG 240
          ERR
          END
"""
