import sys
from typing import Callable
from system_specific.linux import Linux

def vacuous() -> bool:
    return True

def check_console_for_input() -> Callable[[], bool]:
    match sys.platform:
        case "linux":
            return Linux.check_for_input
        case _:
            exception = NotImplemented()
            exception.add_note(
                "No keyboard input checker implemented for {0}.".format(
                    sys.platform))