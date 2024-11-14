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
          REM  move 0o4321 to the accumulator and halt
          BNK 3
          ORG 100
          LDC 4321
          LS3
          HLT
          END
"""