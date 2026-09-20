from datetime import datetime
from pathlib import Path
from typing import Any, Iterable
from xml.sax.saxutils import escape

import matplotlib
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

_FONT = "ReportFont"
_FONT_BOLD = "ReportFont-Bold"
_fonts_ready = False


def _register_fonts() -> None:
    """Register the DejaVu fonts bundled with matplotlib (full Unicode, e.g. Turkish)."""
    global _fonts_ready
    if _fonts_ready:
        return

    font_dir = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
    pdfmetrics.registerFont(TTFont(_FONT, str(font_dir / "DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont(_FONT_BOLD, str(font_dir / "DejaVuSans-Bold.ttf")))
    pdfmetrics.registerFontFamily(_FONT, normal=_FONT, bold=_FONT_BOLD)
    _fonts_ready = True


class PdfReportGenerator:
    """Build a PDF report for one processed Excel file."""

    PREVIEW_ROWS = 15
    PREVIEW_COLUMNS = 8
    ACCENT = colors.HexColor("#2F5D8C")

    def __init__(self) -> None:
        _register_fonts()
        styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            "ReportTitle", parent=styles["Title"], fontName=_FONT_BOLD,
            fontSize=22, textColor=self.ACCENT, spaceAfter=4,
        )
        self.heading_style = ParagraphStyle(
            "ReportHeading", parent=styles["Heading2"], fontName=_FONT_BOLD,
            fontSize=13, textColor=self.ACCENT, spaceBefore=14, spaceAfter=6,
        )
        self.body_style = ParagraphStyle(
            "ReportBody", parent=styles["BodyText"], fontName=_FONT, fontSize=9.5,
        )
        self.cell_style = ParagraphStyle(
            "ReportCell", parent=self.body_style, fontSize=8, leading=10,
        )

    def generate(
        self,
        output_path: str | Path,
        source_name: str,
        dataframe: pd.DataFrame,
        processor_summary: dict[str, Any],
        stats_summary: dict[str, Any],
        chart_paths: Iterable[str | Path] = (),
    ) -> Path:
        """Write the report and return its path."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        doc = SimpleDocTemplate(
            str(output_path), pagesize=A4,
            leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm,
            title=f"Report - {source_name}", author="Excel Automation Toolkit",
        )

        story: list = [
            Paragraph("Excel Processing Report", self.title_style),
            Paragraph(
                f"Source: <b>{escape(source_name)}</b><br/>"
                f"Generated: {datetime.now():%Y-%m-%d %H:%M}",
                self.body_style,
            ),
            Paragraph("Processing Summary", self.heading_style),
            self._key_value_table([
                ("Original rows", processor_summary["original_rows"]),
                ("Rows after cleaning", processor_summary["current_rows"]),
                ("Empty rows removed", processor_summary["removed_empty_rows"]),
                ("Duplicate rows removed", processor_summary["removed_duplicates"]),
            ]),
            Paragraph("Data Statistics", self.heading_style),
            self._key_value_table([
                ("Columns", stats_summary["columns"]),
                ("Numeric columns", stats_summary["numeric_columns"]),
                ("Text columns", stats_summary["text_columns"]),
                ("Missing cells", stats_summary["missing_cells"]),
                ("Memory usage", stats_summary["memory_usage"]),
            ]),
        ]

        numeric_table = self._numeric_table(dataframe)
        if numeric_table is not None:
            story += [Paragraph("Numeric Column Statistics", self.heading_style), numeric_table]

        story += [Paragraph("Data Preview", self.heading_style), self._preview_table(dataframe)]

        charts = [Path(p) for p in chart_paths if Path(p).exists()]
        if charts:
            story.append(PageBreak())
            story.append(Paragraph("Charts", self.heading_style))
            for chart in charts:
                story += [self._scaled_image(chart), Spacer(1, 0.4 * cm)]

        doc.build(story, onFirstPage=self._footer, onLaterPages=self._footer)
        return output_path

    # ---- building blocks -------------------------------------------------

    def _key_value_table(self, rows: list[tuple[str, Any]]) -> Table:
        data = [
            [
                Paragraph(escape(str(key)), self.body_style),
                Paragraph(f"<b>{escape(str(value))}</b>", self.body_style),
            ]
            for key, value in rows
        ]
        table = Table(data, colWidths=[7 * cm, 6 * cm], hAlign="LEFT")
        table.setStyle(TableStyle([
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.whitesmoke, colors.white]),
            ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.lightgrey),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        return table

    def _numeric_table(self, df: pd.DataFrame) -> Table | None:
        numeric = df.select_dtypes(include="number")
        if numeric.empty:
            return None

        header = ["Column", "Mean", "Median", "Min", "Max", "Std"]
        data = [[Paragraph(f"<b>{h}</b>", self.cell_style) for h in header]]
        for name in numeric.columns[:20]:
            col = numeric[name]
            values = (col.mean(), col.median(), col.min(), col.max(), col.std())
            data.append([
                Paragraph(escape(str(name)), self.cell_style),
                *[Paragraph(self._fmt(v), self.cell_style) for v in values],
            ])
        return self._styled_grid(data, [4.5 * cm] + [2.5 * cm] * 5)

    def _preview_table(self, df: pd.DataFrame) -> Table | Paragraph:
        if df.empty:
            return Paragraph("The dataset has no rows.", self.body_style)

        preview = df.iloc[: self.PREVIEW_ROWS, : self.PREVIEW_COLUMNS]
        data = [[Paragraph(f"<b>{escape(str(c))}</b>", self.cell_style) for c in preview.columns]]
        for _, row in preview.iterrows():
            data.append([Paragraph(escape(self._cell_text(v)), self.cell_style) for v in row])

        width = 17 * cm / max(len(preview.columns), 1)
        return self._styled_grid(data, [width] * len(preview.columns))

    def _styled_grid(self, data: list, col_widths: list) -> Table:
        table = Table(data, colWidths=col_widths, repeatRows=1, hAlign="LEFT")
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DCE6F2")),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.whitesmoke]),
        ]))
        return table

    @staticmethod
    def _scaled_image(path: Path, max_width: float = 16 * cm) -> Image:
        image = Image(str(path))
        ratio = max_width / image.imageWidth
        image.drawWidth = max_width
        image.drawHeight = image.imageHeight * ratio
        return image

    @staticmethod
    def _fmt(value: Any) -> str:
        return "-" if pd.isna(value) else f"{value:,.2f}"

    @staticmethod
    def _cell_text(value: Any) -> str:
        if pd.isna(value):
            return ""
        if isinstance(value, float) and value.is_integer():
            value = int(value)
        text = str(value)
        return text if len(text) <= 40 else text[:37] + "..."

    @staticmethod
    def _footer(canvas, doc) -> None:
        canvas.saveState()
        canvas.setFont(_FONT, 8)
        canvas.setFillColor(colors.grey)
        canvas.drawString(2 * cm, 1.2 * cm, "Excel Automation Toolkit")
        canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Page {doc.page}")
        canvas.restoreState()
