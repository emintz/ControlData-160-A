from unittest import TestCase
from pathlib import PurePath, PurePosixPath
from tempfile import gettempdir
import os

from cdc160a.PaperTapePunch import PaperTapePunch


class TestPaperTapePunch(TestCase):
    __TEST_DATA: [int] = [
        0o200,
        0o100,
        0o040,
        0o020,
        0o010,
        0o004,
        0o002,
        0o001,
        0o000,
        0o037,
        0o077,
        0o177,
        0o377,
        0o410,
        0o777,
    ]
    __EXPECTED_OUTPUT: [str] = [
        "200",
        "100",
        "040",
        "020",
        "010",
        "004",
        "002",
        "001",
        "000",
        "037",
        "077",
        "177",
        "377",
        "010",
        "377",
    ]

    # Output file path. Should be os-independent. This is
    __TEST_OUTPUT_FILE: PurePosixPath = PurePath(gettempdir(), "PaperTapeOutput.tmp.txt")

    def setUp(self) -> None:
        self.__punch = PaperTapePunch()

    def test_construction(self) -> None:
        assert not self.__punch.is_open()
        assert self.__punch.write_delay() == 1420
        assert self.__punch.initial_write_delay() == 1420
        assert not self.__punch.can_read()
        assert self.__punch.can_write()

    def test_accepts(self) -> None:
        assert not self.__punch.accepts(0o0000)
        assert not self.__punch.accepts(0o4102)
        assert not self.__punch.accepts(0o4103)
        assert self.__punch.accepts(0o4104)
        assert not self.__punch.accepts(0o4105)

    def test_external_function(self) -> None:
        request_status, response = self.__punch.external_function(0o4104)
        assert request_status
        assert response is None
        request_status, response = self.__punch.external_function(0o41042)
        assert not request_status
        assert response is None

    def test_open_write_close(self) -> None:
        try:
            os.unlink(self.__TEST_OUTPUT_FILE)
        except FileNotFoundError:
            pass
        assert not self.__punch.is_open()
        output_file_name = str(self.__TEST_OUTPUT_FILE)
        assert self.__punch.open(output_file_name)
        assert self.__punch.is_open()
        for value in self.__TEST_DATA:
            assert self.__punch.write(value)
        self.__punch.close()
        assert not self.__punch.is_open()
        index: int = 0
        with open(output_file_name, "rt") as paper_tape_output:
            for formatted_character in paper_tape_output:
                stripped_output = formatted_character.rstrip()
                expected_output = self.__EXPECTED_OUTPUT[index]
                assert stripped_output == expected_output
                index += 1

        os.unlink(self.__TEST_OUTPUT_FILE)
