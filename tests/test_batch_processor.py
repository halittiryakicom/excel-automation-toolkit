import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.core.batch_processor import (  # noqa: E402
    ProcessingOptions,
    find_excel_files,
    process_file,
    process_folder,
)


@pytest.fixture
def input_folder(tmp_path):
    folder = tmp_path / "in"
    folder.mkdir()
    pd.DataFrame({"Ad": ["Çağrı", None, "Şule", "Şule"], "Maaş": [1, None, 2, 2]}).to_excel(
        folder / "türkçe.xlsx", index=False
    )
    pd.DataFrame({"A": [1, 2, 3]}).to_excel(folder / "numbers.xlsx", index=False)
    (folder / "broken.xlsx").write_text("not an excel file")
    (folder / "~$lock.xlsx").write_text("temp")
    (folder / "notes.txt").write_text("ignore me")
    return folder


def test_find_excel_files_skips_temp_and_non_excel(input_folder):
    names = [p.name for p in find_excel_files(input_folder)]
    assert names == ["broken.xlsx", "numbers.xlsx", "türkçe.xlsx"]


def test_process_file_cleans_and_writes_pdf(input_folder, tmp_path):
    out = tmp_path / "out"
    result = process_file(
        input_folder / "türkçe.xlsx", out, ProcessingOptions(generate_pdf=True)
    )

    assert result.success
    assert result.summary["original_rows"] == 4
    assert result.summary["removed_empty_rows"] == 1
    assert result.summary["removed_duplicates"] == 1
    pdf = out / "report.pdf"
    assert pdf.read_bytes().startswith(b"%PDF")
    assert (out / "cleaned_data.xlsx").exists()


def test_batch_continues_after_a_bad_file(input_folder, tmp_path):
    progress = []
    batch = process_folder(
        input_folder,
        tmp_path / "out",
        ProcessingOptions(generate_pdf=True),
        on_progress=lambda done, total, path: progress.append((done, total)),
    )

    assert (batch.succeeded, batch.failed) == (2, 1)
    assert progress[0] == (0, 3) and progress[-1] == (3, 3)

    summary = pd.read_excel(batch.summary_path)
    assert list(summary["Status"]) == ["FAILED", "OK", "OK"]
    assert summary.loc[0, "Error"]


def test_empty_folder_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        process_folder(tmp_path, tmp_path / "out", ProcessingOptions())
