"""
An emulator with a character-mode console.
"""
from cdc160a.InputOutput import InputOutput
from cdc160a.PaperTapeReader import PaperTapeReader
from cdc160a.RunLoop import RunLoop
from cdc160a.Storage import Storage
from development.Console import create_console

def main() -> None:
    console = create_console()
    storage = Storage()
    run_loop = RunLoop(console, storage, InputOutput([PaperTapeReader]))
    run_loop.run()


if __name__ == "__main__":
    main()
