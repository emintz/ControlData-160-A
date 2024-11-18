"""
Programs for testing the emulator. All runnable programs
start at 0100(3)
"""

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
HALT = """
          REM  Simplest possible non-vacuous program that just halts
          BNK 3
          ORG 100
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
SET_LITERAL = """
          REM set a literal value
          BNK 3
          ORG 100
          OCT 1234
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
