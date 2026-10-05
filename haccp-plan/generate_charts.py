#!/usr/bin/env python3
"""Word file whose first pages are the flow chart, so it is visible when opened."""

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor, Twips

OUT = "/workspace/haccp-plan/CHARTS-Diagrama-de-flujo.docx"
INK = RGBColor(0x1E, 0x1A, 0x16)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GREEN = "1F4D36"
CREAM = "FFFDF9"
LINE = "D9CFC3"
CLAY = "8C3D24"
HOLD = "F8EBE4"
GOLD = "F3E6C8"


def font(run, size=11, bold=False, color=INK, italic=False):
    run.font.name = "Calibri"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = color


def shade(cell, color):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), color)
    shd.set(qn("w:val"), "clear")
    tcPr.append(shd)


def borders(cell, color):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement("w:tcBorders")
    for edge in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "12")
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), color)
        tcBorders.append(el)
    tcPr.append(tcBorders)


def set_width(table, inches):
    table.autofit = False
    table.allow_autofit = False
    tbl = table._tbl
    tblPr = tbl.tblPr
    tblW = tblPr.find(qn("w:tblW"))
    if tblW is None:
        tblW = OxmlElement("w:tblW")
        tblPr.append(tblW)
    tblW.set(qn("w:w"), str(int(inches * 1440)))
    tblW.set(qn("w:type"), "dxa")
    jc = tblPr.find(qn("w:jc"))
    if jc is None:
        jc = OxmlElement("w:jc")
        tblPr.append(jc)
    jc.set(qn("w:val"), "center")
    for row in table.rows:
        for cell in row.cells:
            cell.width = Inches(inches)


def margins(cell):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcMar = OxmlElement("w:tcMar")
    for edge, val in (("top", "80"), ("left", "120"), ("bottom", "80"), ("right", "120")):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:w"), val)
        el.set(qn("w:type"), "dxa")
        tcMar.append(el)
    tcPr.append(tcMar)


def box(doc, lines, fill, ink, border, width=6.3):
    t = doc.add_table(rows=1, cols=1)
    set_width(t, width)
    cell = t.cell(0, 0)
    shade(cell, fill)
    borders(cell, border)
    margins(cell)
    cell.text = ""
    for i, (text, size, bold) in enumerate(lines):
        par = cell.paragraphs[0] if i == 0 else cell.add_paragraph()
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        par.paragraph_format.space_before = Pt(0)
        par.paragraph_format.space_after = Pt(1)
        par.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        run = par.add_run(text)
        font(run, size=size, bold=bold, color=ink)
    # small gap after the box
    gap = doc.add_paragraph()
    gap.paragraph_format.space_before = Pt(0)
    gap.paragraph_format.space_after = Pt(0)
    gap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = gap.add_run("↓")
    font(run, size=14, bold=True, color=RGBColor(0x1F, 0x4D, 0x36))
    return t


def build():
    doc = Document()
    sec = doc.sections[0]
    sec.top_margin = Cm(1.4)
    sec.bottom_margin = Cm(1.4)
    sec.left_margin = Cm(1.5)
    sec.right_margin = Cm(1.5)
    sec.page_width = Inches(8.5)
    sec.page_height = Inches(11)

    hp = sec.header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = hp.add_run("Charts  ·  Carne Seca Jesus Canales, LLC")
    font(r, size=8, color=RGBColor(0x4A, 0x43, 0x3A))

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.paragraph_format.space_after = Pt(2)
    run = title.add_run("CHART 1  ·  Process flow")
    font(run, size=20, bold=True, color=RGBColor(0x1F, 0x4D, 0x36))

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub.paragraph_format.space_after = Pt(2)
    run = sub.add_run("Ready-to-eat beef jerky  ·  Delta, UT")
    font(run, size=12, bold=True)

    sub2 = doc.add_paragraph()
    sub2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub2.paragraph_format.space_after = Pt(8)
    run = sub2.add_run("The customer does not cook it. It contains beef. It is sold shelf-stable, without refrigeration.")
    font(run, size=11)

    legend = doc.add_paragraph()
    legend.alignment = WD_ALIGN_PARAGRAPH.CENTER
    legend.paragraph_format.space_after = Pt(8)
    a = legend.add_run("Light box = process step    ")
    font(a, size=10)
    b = legend.add_run("Green box = critical control point    ")
    font(b, size=10, bold=True, color=RGBColor(0x1F, 0x4D, 0x36))
    c = legend.add_run("Red box = the lot does not ship")
    font(c, size=10, bold=True, color=RGBColor(0x8C, 0x3D, 0x24))

    steps = [
        ([("1. Receive inspected beef", 12, True), ("Invoice and mark of inspection. Measure product temperature.", 10, False)], CREAM, INK, LINE),
        ([("2. Receive salt, spices, and bags", 12, True), ("Specification matches. No nitrite. No soy. No wheat.", 10, False)], CREAM, INK, LINE),
        ([("3. Cold storage — not a CCP", 12, True), ("Product below 41°F. Prerequisite, stricter than the model’s 45°F.", 10, False)], CREAM, INK, LINE),
        ([("4. Slice, weigh, marinate, single layer", 12, True), ("Still below 41°F. Do not stack. Do not dry before the cook.", 10, False)], CREAM, INK, LINE),
        ([
            ("CCP 1  ·  COOKING, BEFORE DRYING", 11, True),
            ("Internal 145°F for at least 4 minutes", 10, False),
            ("Wet bulb at least 125°F for at least 1 hour", 10, False),
            ("Relative humidity at least 27% for at least 1 hour", 10, False),
            ("Oven sealed for 1 hour or 50% of the cook, whichever is longer", 10, False),
            ("Dampers closed within 30 minutes. Come-up 6 hours or less.", 10, False),
        ], GREEN, WHITE, GREEN),
        ([
            ("CCP 2  ·  DRYING", 11, True),
            ("Dry bulb at least 170°F during drying", 10, False),
            ("Water activity 0.85 or less", 10, False),
            ("At least six pieces. The highest reading is the result.", 10, False),
        ], GREEN, WHITE, GREEN),
        ([("5. Cool dry, pack, and label", 12, True), ("Do not rinse. Only if both CCPs passed. Lot code on the bag.", 10, False)], CREAM, INK, LINE),
        ([("6. Review the numbers and sign", 12, True), ("Pre-shipment review under 9 CFR 417.5(c). Then dry storage.", 10, False)], CREAM, INK, LINE),
    ]
    for lines, fill, ink, border in steps:
        box(doc, lines, fill, ink, border)

    # replace the last arrow with the hold box: the helper always adds an arrow.
    # Add the hold box after the last arrow.
    t = doc.add_table(rows=1, cols=1)
    set_width(t, 6.3)
    cell = t.cell(0, 0)
    shade(cell, HOLD)
    borders(cell, CLAY)
    margins(cell)
    cell.text = ""
    par = cell.paragraphs[0]
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = par.add_run("If a CCP limit is missed, the lot is held and is not sold as ready-to-eat beef jerky.")
    font(run, size=11, bold=True, color=RGBColor(0x8C, 0x3D, 0x24))

    doc.add_page_break()

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("CHART 2  ·  The three limits")
    font(run, size=20, bold=True, color=RGBColor(0x1F, 0x4D, 0x36))
    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub.paragraph_format.space_after = Pt(10)
    run = sub.add_run("From the FSIS beef jerky HACCP model, 2021-0004, and Appendix A")
    font(run, size=12)

    headers = ["Point", "What is measured", "The lot passes if"]
    rows = [
        ["Prerequisite", "Product temperature", "Below 41°F. Not a CCP."],
        ["CCP 1 Cooking", "Internal temperature", "145°F or above for at least 4 minutes"],
        ["CCP 1 Cooking", "Wet bulb", "At least 125°F for at least 1 hour"],
        ["CCP 1 Cooking", "Relative humidity", "At least 27% for at least 1 hour"],
        ["CCP 1 Cooking", "Sealed oven", "Dampers closed within 30 minutes, and kept closed for 1 hour or 50% of the cook, whichever is longer"],
        ["CCP 1 Cooking", "Come-up time", "From 50°F to 130°F, 6 hours or less"],
        ["CCP 2 Drying", "Dry bulb", "At least 170°F during drying"],
        ["CCP 2 Drying", "Water activity", "0.85 or less. Highest of at least six pieces."],
    ]
    table = doc.add_table(rows=1 + len(rows), cols=3)
    table.style = "Table Grid"
    set_width(table, 6.6)
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ""
        shade(cell, GREEN)
        par = cell.paragraphs[0]
        run = par.add_run(h)
        font(run, size=11, bold=True, color=WHITE)
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            cell = table.rows[r + 1].cells[c]
            cell.text = ""
            if r % 2 == 1:
                shade(cell, "F4F1EA")
            par = cell.paragraphs[0]
            run = par.add_run(val)
            font(run, size=11, bold=(c == 0))

    note = doc.add_paragraph()
    note.paragraph_format.space_before = Pt(10)
    run = note.add_run("A blank or the word “yes” does not count. The measured number has to be written. If a CCP number is missing, the lot does not ship. 9 CFR 417.5.")
    font(run, size=11)

    foot = doc.add_paragraph()
    foot.paragraph_format.space_before = Pt(8)
    run = foot.add_run("Carne Seca Jesus Canales, LLC · 411 E Main St, Delta, UT 84624 · Limits from the FSIS beef jerky HACCP model (2021-0004) and Appendix A (December 2021).")
    font(run, size=9, italic=True, color=RGBColor(0x4A, 0x43, 0x3A))

    doc.save(OUT)
    doc.save("/workspace/haccp-plan/CHARTS-Flow-Diagram.docx")
    print(OUT)


if __name__ == "__main__":
    build()
