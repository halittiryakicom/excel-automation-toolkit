import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

import pandas as pd

from src.core.charts import ChartGenerator
from src.core.excel_processor import ExcelProcessor
from src.core.pdf_generator import PdfReportGenerator
from src.core.statistics import StatisticsEngine

EXCEL_EXTENSIONS = {".xlsx", ".xlsm", ".xls"}

ProgressCallback = Callable[[int, int, Path], None]


@dataclass
class ProcessingOptions:
    remove_empty_rows: bool = True
    remove_duplicates: bool = True
    generate_charts: bool = False
    generate_pdf: bool = False


@dataclass
class FileResult:
    source: Path
    success: bool
    output_dir: Optional[Path] = None
    summary: dict = field(default_factory=dict)
    generated: list[Path] = field(default_factory=list)
    error: str = ""


@dataclass
class BatchResult:
    results: list[FileResult] = field(default_factory=list)
    summary_path: Optional[Path] = None

    @property
    def succeeded(self) -> int:
        return sum(r.success for r in self.results)

    @property
    def failed(self) -> int:
        return len(self.results) - self.succeeded


def find_excel_files(folder: str | Path, recursive: bool = False) -> list[Path]:
    """Return Excel files in ``folder`` (skips temp files such as ``~$x.xlsx``)."""
    folder = Path(folder)
    if not folder.is_dir():
        raise NotADirectoryError(f"Folder not found: {folder}")

    pattern = "**/*" if recursive else "*"
    return sorted(
        p
        for p in folder.glob(pattern)
        if p.is_file()
        and p.suffix.lower() in EXCEL_EXTENSIONS
        and not p.name.startswith("~$")
    )


def process_file(
    source: str | Path, output_dir: str | Path, options: ProcessingOptions
) -> FileResult:
    """Run the full pipeline for one file into ``output_dir``."""
    source, output_dir = Path(source), Path(output_dir)
    result = FileResult(source=source, success=False, output_dir=output_dir)

    try:
        processor = ExcelProcessor()
        processor.load_excel(source)
        if options.remove_empty_rows:
            processor.remove_empty_rows()
        if options.remove_duplicates:
            processor.remove_duplicates()

        result.generated.append(processor.save_excel(output_dir / "cleaned_data.xlsx"))

        chart_paths: list[Path] = []
        if options.generate_charts or options.generate_pdf:
            chart_paths = ChartGenerator(processor.df).generate_all(output_dir)
            if options.generate_charts:
                result.generated.extend(chart_paths)

        stats = StatisticsEngine(processor.df).generate_summary()
        result.summary = {
            **processor.get_summary(),
            "columns": stats["columns"],
            "missing_cells": stats["missing_cells"],
        }

        if options.generate_pdf:
            pdf_path = PdfReportGenerator().generate(
                output_dir / "report.pdf",
                source.name,
                processor.df,
                processor.get_summary(),
                stats,
                chart_paths,
            )
            result.generated.append(pdf_path)

        result.success = True
    except Exception as error:  # one bad file must not stop the batch
        result.error = f"{type(error).__name__}: {error}"

    return result


def process_folder(
    input_folder: str | Path,
    output_folder: str | Path,
    options: ProcessingOptions,
    recursive: bool = False,
    on_progress: Optional[ProgressCallback] = None,
) -> BatchResult:
    """Process every Excel file in ``input_folder``.

    Each file gets its own sub-folder in ``output_folder`` and a combined
    ``batch_summary.xlsx`` lists the outcome of every file.
    """
    files = find_excel_files(input_folder, recursive)
    if not files:
        raise FileNotFoundError(f"No Excel files found in: {input_folder}")

    output_folder = Path(output_folder)
    batch = BatchResult()
    used_names: set[str] = set()

    for index, source in enumerate(files):
        if on_progress:
            on_progress(index, len(files), source)
        folder_name = _unique_name(_safe_name(source.stem), used_names)
        batch.results.append(process_file(source, output_folder / folder_name, options))

    if on_progress:
        on_progress(len(files), len(files), files[-1])

    batch.summary_path = _write_summary(batch, output_folder / "batch_summary.xlsx")
    return batch


def _safe_name(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*]+', "_", name).strip() or "file"


def _unique_name(name: str, used: set[str]) -> str:
    candidate, counter = name, 2
    while candidate.lower() in used:
        candidate = f"{name}_{counter}"
        counter += 1
    used.add(candidate.lower())
    return candidate


def _write_summary(batch: BatchResult, path: Path) -> Path:
    rows = [
        {
            "File": r.source.name,
            "Status": "OK" if r.success else "FAILED",
            "Original Rows": r.summary.get("original_rows"),
            "Rows After Cleaning": r.summary.get("current_rows"),
            "Empty Rows Removed": r.summary.get("removed_empty_rows"),
            "Duplicates Removed": r.summary.get("removed_duplicates"),
            "Columns": r.summary.get("columns"),
            "Missing Cells": r.summary.get("missing_cells"),
            "Error": r.error,
        }
        for r in batch.results
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_excel(path, index=False, engine="openpyxl")
    return path
