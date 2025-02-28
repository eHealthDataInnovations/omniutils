import os
from pathlib import Path
import tempfile
from omniutils.file_operator import FileOperator


def test_rename_file(tmp_path):
    file_path = tmp_path / "testfile.txt"
    file_path.write_text("Sample text")

    new_file_path = FileOperator.rename_file(str(file_path), insert_text="v2")
    assert os.path.exists(new_file_path)


def test_extract_filename(tmp_path):
    file_path = tmp_path / "example.txt"
    file_path.write_text("data")
    result = FileOperator.extract_filename(str(file_path))
    assert result == "example.txt"


def test_extract_extension(tmp_path):
    file_path = tmp_path / "example.txt"
    file_path.write_text("data")
    result = FileOperator.extract_extension(str(file_path))
    assert result == ".txt"
