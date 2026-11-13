"""Build a simple, clean PDF for a defense plan or answer (no extra dependencies).

The PDF starts with a title, then the plan or answer text (including citations and
"Questions to ask your lawyer"), and ends with the not-legal-advice notice.
"""
from __future__ import annotations

from datetime import date

from . import language as lang

# PDF points: US Letter 612 x 792.
PAGE_W, PAGE_H = 612, 792
MARGIN_X, MARGIN_TOP, MARGIN_BOTTOM = 54, 72, 64
CONTENT_W = PAGE_W - 2 * MARGIN_X
LEADING = 14
FONT_SIZE = 11
TITLE_SIZE = 16
FOOTER_SIZE = 8

HEADER = "STANDALONE ASSISTANT"
SUBHEADER = "Georgia legal information"


def _escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _wrap(text: str, width_chars: int = 88) -> list[str]:
    lines: list[str] = []
    for raw in (text or "").replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        line = raw.expandtabs(4).rstrip()
        if not line:
            lines.append("")
            continue
        while len(line) > width_chars:
            cut = line.rfind(" ", 0, width_chars)
            if cut < 40:
                cut = width_chars
            lines.append(line[:cut].rstrip())
            line = line[cut:].lstrip()
        lines.append(line)
    return lines


def build_text(title: str, body: str, language: str = "en") -> str:
    """Plain text that goes into the PDF (also used by Android/web to stay consistent)."""
    notice = lang.notice(language)
    parts = [
        HEADER,
        SUBHEADER,
        title.strip() or "Your Defense Plan",
        "",
        (body or "").strip(),
    ]
    text = "\n".join(parts).rstrip()
    if notice not in text:
        text += "\n\n" + notice
    text += "\nThis document is for personal use. It is not a court filing."
    return text + "\n"


def build_pdf(title: str, body: str, language: str = "en") -> bytes:
    """Return a PDF 1.4 document as bytes."""
    content = build_text(title, body, language)
    wrapped = _wrap(content)
    lines_per_page = int((PAGE_H - MARGIN_TOP - MARGIN_BOTTOM) / LEADING)
    # Leave two lines for the footer area.
    lines_per_page = max(20, lines_per_page - 2)
    pages: list[list[str]] = []
    for i in range(0, max(len(wrapped), 1), lines_per_page):
        pages.append(wrapped[i:i + lines_per_page])

    objects = ["%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"]
    # We'll assemble objects 1..n, then xref. Object 1 = catalog, 2 = pages, 3 = font, then page pairs.

    def obj(n: int, payload: str) -> str:
        return f"{n} 0 obj\n{payload}\nendobj\n"

    font_obj = 3
    first_page_obj = 4
    page_objs = []
    content_objs = []
    for i, page_lines in enumerate(pages):
        page_id = first_page_obj + i * 2
        content_id = page_id + 1
        y = PAGE_H - MARGIN_TOP
        stream_lines = ["BT", "/F1 11 Tf", f"{LEADING} TL", f"{MARGIN_X} {y} Td"]
        for j, line in enumerate(page_lines):
            if j == 0 and i == 0:
                stream_lines = [
                    "BT",
                    f"/F1 {TITLE_SIZE} Tf",
                    f"{MARGIN_X} {PAGE_H - 50} Td",
                    f"({_escape(HEADER)}) Tj",
                    "/F1 9 Tf",
                    "0 -12 Td",
                    f"({_escape(SUBHEADER + '  ·  ' + date.today().isoformat())}) Tj",
                    f"/F1 {FONT_SIZE} Tf",
                    "0 -24 Td",
                ]
                # After the header, print the first content line and the rest with T*.
            safe = _escape(line) if line else ""
            if j == 0 and i == 0:
                stream_lines.append(f"({safe}) Tj")
            else:
                if j == 0:
                    stream_lines.extend(["BT", f"/F1 {FONT_SIZE} Tf", f"{MARGIN_X} {y} Td", f"({safe}) Tj"])
                else:
                    stream_lines.append(f"0 -{LEADING} Td ({safe}) Tj")
        # Footer
        stream_lines.append("ET")
        footer = f"Page {i + 1} of {len(pages)}  ·  {lang.notice(language)}"
        stream_lines.extend([
            "BT",
            f"/F1 {FOOTER_SIZE} Tf",
            f"{MARGIN_X} {36} Td",
            f"({_escape(footer)}) Tj",
            "ET",
        ])
        stream = "\n".join(stream_lines).encode("latin-1", "replace")
        content_objs.append((content_id, stream))
        page_objs.append((page_id, content_id))

    kids = " ".join(f"{pid} 0 R" for pid, _ in page_objs)
    parts: list[bytes] = [b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"]
    body_objects: list[bytes] = [
        obj(1, "<< /Type /Catalog /Pages 2 0 R >>").encode("ascii"),
        obj(2, f"<< /Type /Pages /Kids [{kids}] /Count {len(page_objs)} >>").encode("ascii"),
        obj(font_obj, "<< /Type /Font /Subtype /Type1 /BaseFont /Times-Roman >>").encode("ascii"),
    ]
    for page_id, content_id in page_objs:
        body_objects.append(obj(page_id, (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PAGE_W} {PAGE_H}] "
            f"/Resources << /Font << /F1 {font_obj} 0 R >> >> /Contents {content_id} 0 R >>"
        )).encode("ascii"))
        stream = dict(content_objs)[content_id]
        body_objects.append(
            obj(content_id, f"<< /Length {len(stream)} >>\nstream\n").encode("ascii") + stream + b"\nendstream\nendobj\n"
        )

    # Object numbers must be 1..N in order for a simple xref. Re-emit in numeric order.
    # We built: 1 catalog, 2 pages, 3 font, then page/content pairs starting at 4.
    offsets = [0]
    out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    for chunk in body_objects:
        offsets.append(len(out))
        out.extend(chunk)
    xref_start = len(out)
    out.extend(f"xref\n0 {len(offsets)}\n".encode("ascii"))
    out.extend(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        out.extend(f"{off:010d} 00000 n \n".encode("ascii"))
    out.extend(
        f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF\n".encode("ascii")
    )
    return bytes(out)
