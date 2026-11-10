from pathlib import Path

import pytest

from cleaner.pipeline import run

ROOT = Path(__file__).resolve().parent.parent


def write_config(tmp_path, text="numeric_columns: [price]\n"):
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text(text, encoding="utf-8")
    return str(cfg)


def test_empty_file_gives_clear_error(tmp_path):
    empty = tmp_path / "empty.csv"
    empty.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="empty"):
        run(str(empty), str(tmp_path / "o.csv"), write_config(tmp_path),
            str(tmp_path / "r.json"))


def test_header_only_file_gives_clear_error(tmp_path):
    f = tmp_path / "header_only.csv"
    f.write_text("id,price\n", encoding="utf-8")
    with pytest.raises(ValueError, match="no data rows"):
        run(str(f), str(tmp_path / "o.csv"), write_config(tmp_path),
            str(tmp_path / "r.json"))


def test_bad_encoding_gives_clear_error(tmp_path):
    f = tmp_path / "bad.csv"
    f.write_bytes(b"id,price\n1,caf\xe9\n")
    with pytest.raises(ValueError, match="UTF-8"):
        run(str(f), str(tmp_path / "o.csv"), write_config(tmp_path),
            str(tmp_path / "r.json"))


def test_config_column_missing_from_csv_fails_loudly(tmp_path):
    f = tmp_path / "data.csv"
    f.write_text("id,name\n1,Ravi\n", encoding="utf-8")
    with pytest.raises(ValueError, match="not found"):
        run(str(f), str(tmp_path / "o.csv"), write_config(tmp_path),
            str(tmp_path / "r.json"))


def test_end_to_end_on_sample_data(tmp_path):
    report = run(
        str(ROOT / "sample_data" / "messy.csv"),
        str(tmp_path / "out.csv"),
        str(ROOT / "config.yaml"),
        str(tmp_path / "report.json"),
    )
    assert report["rows_in"] == 17
    assert report["rows_out"] == 14
    assert report["duplicates_removed"] == 3
    assert (tmp_path / "out.csv").exists()