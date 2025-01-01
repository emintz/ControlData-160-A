import msvcrt
def check_for_input_win() -> bool:
    return msvcrt.kbhit()
