"""Tests for the directory scanner."""

from pathlib import Path
import pytest

from n2s.ingest.scanner import DirectoryScanner, ScanResult, ScannedFile


@pytest.fixture
def fixtures_dir():
    return Path(__file__).resolve().parent.parent / "fixtures" / "ingest"


def test_scan_finds_csv_and_json(fixtures_dir):
    scanner = DirectoryScanner()
    result = scanner.scan(fixtures_dir)

    assert isinstance(result, ScanResult)
    assert len(result.files) >= 2

    extensions = [f.extension for f in result.files]
    assert ".csv" in extensions
    assert ".json" in extensions


def test_scan_classifies_by_type(fixtures_dir):
    scanner = DirectoryScanner()
    result = scanner.scan(fixtures_dir)

    csv_file = next(f for f in result.files if f.extension == ".csv")
    assert csv_file.file_type == "csv"
    assert csv_file.table_name == "sample"

    json_file = next(f for f in result.files if f.extension == ".json")
    assert json_file.file_type == "json"


def test_scan_empty_directory(tmp_path):
    scanner = DirectoryScanner()
    result = scanner.scan(tmp_path)

    assert result.files == []
    assert result.skipped == []


def test_scan_skips_unsupported_files(tmp_path):
    (tmp_path / "readme.txt").write_text("not data")
    (tmp_path / "data.csv").write_text("a,b\n1,2")

    scanner = DirectoryScanner()
    result = scanner.scan(tmp_path)

    assert len(result.files) == 1
    assert result.files[0].extension == ".csv"
    assert len(result.skipped) == 1
    assert result.skipped[0].name == "readme.txt"
