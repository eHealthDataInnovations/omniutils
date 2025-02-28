import pytest  # type: ignore

from omniutils.exceptions import DataFrameFormatError, InvalidFileFormatError


def test_invalid_file_format_error():
    with pytest.raises(InvalidFileFormatError):
        raise InvalidFileFormatError("Invalid file format test")


def test_data_frameformat_error_logging(caplog):
    with caplog.at_level("ERROR"):
        try:
            raise DataFrameFormatError("Test error")
        except DataFrameFormatError as err:
            assert "Test error" in str(err)
