"""
Programs for testing the emulator. All runnable programs
start at 0100(3)
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
ADD_BACKWARD = """
          REM Test add backward: A -> A + [P - E]
          BNK 3
          ORG 77
          OCT 34
          LDC 1200
          ADB 3
          HLT
          END
"""
ADD_CONSTANT = """
          REM Test add constant: A -> A + G
          BNK 3
          ORG 100
          LDC 1200
          ADC 34
          HLT
          END
"""
ADD_DIRECT = """
          REM Test add direct A -> A + 40(d)
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
          REM Test add forward A -> A + [P + E]
          BNK 3
          ORG 100
          LDC 1200
          ADF 2
          HLT
          OCT 34
          END
"""
ADD_INDIRECT = """
          REM Test add indirect, A -> A + [40(i)
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
          REM Test add no address A -> A + 34
          BNK 3
          ORG 100
          LDC 1200
          ADN 34
          HLT
          END
"""
ADD_MEMORY = """
          REM Test add memory A -> A + [120]
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
          REM Test add specific, A -> A + [7777(0)]
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
HALT = """
          REM  Simplest possible non-vacuous program that just halts
          BNK 3
          ORG 100
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
NOOP_THEN_HALT = """
          REM  no-op followed by a halt
          BNK 3
          ORG 100
          NOP
          HLT
          END
"""
NEGATIVE_JUMP_BACKWARD_MINUS_ZERO_A = """
          REM Test negative jump backward with a set to 0
          BNK 3
          ORG 77
          HLT
          LDC 7777
          NJB 3
          HLT
          END
"""
NEGATIVE_JUMP_BACKWARD_ZERO_A = """
          REM Test negative jump backward with a set to 0
          BNK 3
          ORG 77
          HLT
          LDC 0
          NJB 3
          HLT
          END
"""
NEGATIVE_JUMP_FORWARD_ZERO_A = """
          REM Test negative jump forward with A set to 0
          BNK 3
          ORG 100
          LDN 0
          NZF 2    # +0
          HLT      # +1
          HLT      # +2
          END
"""
NEGATIVE_JUMP_FORWARD_MINUS_ZERO_A = """
          REM Test negative jump forward with A set to minus zero
          BNK 3
          ORG 100
          LDC 7777
          NZF 2    # +0
          HLT      # +1
          HLT      # +2
          END
"""
NONZERO_JUMP_FORWARD_MINUS_ZERO_A = """
          REM Test nonzero jump backward with a set to minus zero
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
          REM Test nonzero jump backward with a set to zero
          BNK 3
          ORG 77
          HLT
          LDC 0
          NZF 2
          HLT
          HLT
          END
"""
POSITIVE_JUMP_BACKWARD_MINUS_ZERO_A = """
          REM Test positive jump backward with a set to minus zero
          BNK 3
          ORG 77
          HLT
          LDC 0
          PJB 3
          HLT
          END
"""
POSITIVE_JUMP_BACKWARD_ZERO_A = """
          REM Test positive jump backward with a set to minus zero
          BNK 3
          ORG 77
          HLT
          LDC 0
          PJB 3
          HLT
          END
"""
POSITIVE_JUMP_FORWARD_MINUS_ZERO_A = """
          REM Test positive jump forward with A set to minus zero
          BNK 3
          ORG 100
          LDC 7777
          PJF 2    # +0
          HLT      # +1
          HLT      # +2
          END
"""
POSITIVE_JUMP_FORWARD_ZERO_A = """
          REM Test positive jump forward with A set to minus zero
          BNK 3
          ORG 100
          LDC 0
          PJF 2    # +0
          HLT      # +1
          HLT      # +2
          END
"""
REPLACE_ADD_BACKWARD = """
          REM Test Replace Add Backward, [(P - YY)(r)] + A -> A, [(P - YY)(r)]
          BNK 3
          ORG 77
          OCT 1200
          LDN 34
          RAB 2
          HLT
          END
"""
REPLACE_ADD_CONSTANT = """
          REM Test Replace Add Constant, [G(r)] + A -> A and [G(r)]
          BNK 3
          ORG 100
          LDC 34
          RAC 1200
          HLT
          END
"""
REPLACE_ADD_DIRECT = """
          REM Test Replace Add Direct, [YY(d)] + A -> A and [YY(d)]
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
          REM Test Replace Add Forward, [(P + YY)(r)] + A -> A and
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
          REM Test Replace Add Indirect, A + [YY(d)] -> A and [YY(i)]
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
          REM Test Replace Add Memory,  A + [G(r)] -> A and [G(r)]
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
          REM Test Replace Add Storage, A + [7777(0)] -> A and [7777(0)]
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
SET_LITERAL = """
          REM set a literal value
          BNK 3
          ORG 100
          OCT 1234
          END
"""
STORE_BACKWARD = """
          REM Test store backward, which stores the A register
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
STORE_CONSTANT = """
          REM Test store constant, store into instruction's G
          REM which seems odd, but that's what the manual says
          REM it does.
          BNK 3  Relative bank
          ORG 100
          LDC 1234
          STC 7777
          END
"""
STORE_DIRECT = """
          REM Test store direct, store A to the direct storage bank
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
          REM Test store forward, store A to the current address plus
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
          REM Test store direct, store A to the direct storage bank
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
          REM Test store memory, store A to [G](r)
          BNK 3
          ORG 100
          LDC 1234
          STM 1000
          HLT
          ORG 1000
          OCT 7777
          END
"""
STORE_SPECIFIC = """
          REM Test store specific, store A 7777(0)
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
          REM Test subtract backward
          BNK 3
          ORG 77
          OCT 31
          LDC 1265
          SBB 3
          HLT
          END
"""
SUBTRACT_CONSTANT = """
          REM Test subtract constant
          BNK 3
          ORG 100
          LDC 1265
          SBC 31
          HLT
          END
"""
SUBTRACT_DIRECT = """
          REM Test subtract direct
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
          REM Test subtract forward
          BNK 3
          ORG 100
          LDC 1265
          SBF 2
          HLT
          OCT 31
          END
"""
SUBTRACT_INDIRECT = """
          REM Test subtract indirect
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
          REM Test subtract memory
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
          REM Test subtract no address 
          BNK 3
          ORG 100
          LDC 1265
          SBN 31
          HLT
          END
"""
SUBTRACT_SPECIFIC = """
          REM Test subtract specific
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
          REM Test zero jump backward with a set to minus zero
          BNK 3
          ORG 77
          HLT
          LDC 7777
          ZJB 3
          HLT
          END
"""
ZERO_JUMP_BACKWARD_ZERO_A = """
          REM Test zero jump backward with a set to minus zero
          BNK 3
          ORG 77
          HLT
          LDC 0
          ZJB 3
          HLT
          END
"""
ZERO_JUMP_FORWARD_MINUS_ZERO_A = """
          REM Test zero jump forward with A set to minus zero
          BNK 3
          ORG 100
          LDC 0
          ZJF 2    # +0
          HLT      # +1
          HLT      # +2
          END
"""
ZERO_JUMP_FORWARD_ZERO_A = """
          REM Test zero jump forward with A set to minus zero
          BNK 3
          ORG 100
          LDC 0
          ZJF 2    # +0
          HLT      # +1
          HLT      # +2
          END
"""
