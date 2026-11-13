/** Build a simple US-Letter PDF in the browser (no extra libraries) and trigger a download. */

const PAGE_W = 612;
const PAGE_H = 792;
const MARGIN_X = 54;
const MARGIN_TOP = 72;
const MARGIN_BOTTOM = 64;
const LEADING = 14;
const HEADER = "STANDALONE ASSISTANT";
const SUBHEADER = "Georgia legal information";

function escapePdf(text: string): string {
  return text.replace(/\\/g, "\\\\").replace(/\(/g, "\\(").replace(/\)/g, "\\)");
}

export function wrapLines(text: string, width = 88): string[] {
  const lines: string[] = [];
  for (const raw of (text || "").replace(/\r\n/g, "\n").split("\n")) {
    let line = raw.replace(/\t/g, "    ").replace(/\s+$/, "");
    if (!line) {
      lines.push("");
      continue;
    }
    while (line.length > width) {
      let cut = line.lastIndexOf(" ", width);
      if (cut < 40) cut = width;
      lines.push(line.slice(0, cut).trimEnd());
      line = line.slice(cut).trimStart();
    }
    lines.push(line);
  }
  return lines;
}

export function planText(title: string, body: string, notice: string): string {
  let text = [HEADER, SUBHEADER, title.trim() || "Your Defense Plan", "", (body || "").trim()].join("\n").trim();
  if (notice && !text.includes(notice)) text += "\n\n" + notice;
  text += "\nThis document is for personal use. It is not a court filing.\n";
  return text;
}

function pad10(n: number): string {
  return n.toString().padStart(10, "0");
}

export function buildPdf(title: string, body: string, notice = "This is legal information, not legal advice."): Uint8Array {
  const content = planText(title, body, notice);
  const wrapped = wrapLines(content);
  const linesPerPage = Math.max(20, Math.floor((PAGE_H - MARGIN_TOP - MARGIN_BOTTOM) / LEADING) - 2);
  const pages: string[][] = [];
  for (let i = 0; i < Math.max(wrapped.length, 1); i += linesPerPage) pages.push(wrapped.slice(i, i + linesPerPage));

  const today = new Date().toISOString().slice(0, 10);
  const contentStreams: Uint8Array[] = pages.map((pageLines, i) => {
    const ops: string[] = ["BT", "/F1 16 Tf", `${MARGIN_X} ${PAGE_H - 50} Td`, `(${escapePdf(HEADER)}) Tj`, "/F1 9 Tf", "0 -12 Td", `(${escapePdf(SUBHEADER + "  ·  " + today)}) Tj`, "/F1 11 Tf", "0 -24 Td"];
    pageLines.forEach((line, j) => {
      const safe = escapePdf(line || "");
      if (j === 0) ops.push(`(${safe}) Tj`);
      else ops.push(`0 -${LEADING} Td (${safe}) Tj`);
    });
    ops.push("ET", "BT", "/F1 8 Tf", `${MARGIN_X} 36 Td`, `(${escapePdf(`Page ${i + 1} of ${pages.length}  ·  ${notice}`)}) Tj`, "ET");
    return new TextEncoder().encode(ops.join("\n"));
  });

  const encoder = new TextEncoder();
  const chunks: Uint8Array[] = [];
  const offsets: number[] = [0];
  let size = 0;
  const push = (part: Uint8Array | string) => {
    const bytes = typeof part === "string" ? encoder.encode(part) : part;
    chunks.push(bytes);
    size += bytes.length;
  };
  const mark = () => {
    offsets.push(size);
  };

  push("%PDF-1.4\n%\xE2\xE3\xCF\xD3\n");
  const kids = pages.map((_, i) => `${4 + i * 2} 0 R`).join(" ");
  mark();
  push("1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n");
  mark();
  push(`2 0 obj\n<< /Type /Pages /Kids [${kids}] /Count ${pages.length} >>\nendobj\n`);
  mark();
  push("3 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Times-Roman >>\nendobj\n");
  pages.forEach((_, i) => {
    const pageId = 4 + i * 2;
    const contentId = pageId + 1;
    const stream = contentStreams[i];
    mark();
    push(
      `${pageId} 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 ${PAGE_W} ${PAGE_H}] /Resources << /Font << /F1 3 0 R >> >> /Contents ${contentId} 0 R >>\nendobj\n`,
    );
    mark();
    push(`${contentId} 0 obj\n<< /Length ${stream.length} >>\nstream\n`);
    push(stream);
    push("\nendstream\nendobj\n");
  });
  const xrefStart = size;
  push(`xref\n0 ${offsets.length}\n`);
  push("0000000000 65535 f \n");
  for (let i = 1; i < offsets.length; i++) push(`${pad10(offsets[i])} 00000 n \n`);
  push(`trailer\n<< /Size ${offsets.length} /Root 1 0 R >>\nstartxref\n${xrefStart}\n%%EOF\n`);

  const out = new Uint8Array(size);
  let offset = 0;
  for (const chunk of chunks) {
    out.set(chunk, offset);
    offset += chunk.length;
  }
  return out;
}

export function downloadPdf(title: string, body: string, notice?: string) {
  const bytes = buildPdf(title, body, notice);
  const copy = new Uint8Array(bytes.byteLength); copy.set(bytes); const blob = new Blob([copy.buffer], { type: "application/pdf" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = (title.replace(/[^A-Za-z0-9]+/g, "_").slice(0, 60) || "standalone-assistant") + ".pdf";
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
