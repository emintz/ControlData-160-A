"""
System-specific functions for Linux
"""
import select
import sys

def check_for_input() -> bool:
    """
    Check for keyboard input

    :return: True if keyboard input is available, False otherwise
    """
    # Lame cargo cult programming.
    return True  if select.select(
        [sys.stdin], [], [], 0)[0] else False