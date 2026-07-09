"""Tests for the file reader."""

from pathlib import Path
import pytest
import pandas as pd

from n2s.ingest.reader import FileReader


@pytest.fixture
def fixtures_dir():
    return Path(__file__).resolve().parent.parent / "fixtures" / "ingest"


def test_read_csv(fixtures_dir):
    reader = FileReader()
    df = reader.read(fixtures_dir / "sample.csv", "csv")

    assert len(df) == 3
    assert list(df.columns) == ["id", "name", "value"]
    assert df.iloc[0]["name"] == "alice"


def test_read_json(fixtures_dir):
    reader = FileReader()
    df = reader.read(fixtures_dir / "sample.json", "json")

    assert len(df) == 2
    assert list(df.columns) == ["id", "name", "value"]


def test_read_nonexistent_file():
    reader = FileReader()
    with pytest.raises(FileNotFoundError):
        reader.read(Path("nonexistent.csv"), "csv")


def test_read_unsupported_type(fixtures_dir):
    reader = FileReader()
    with pytest.raises(ValueError, match="Unsupported file type"):
        reader.read(fixtures_dir / "sample.csv", "xml")
