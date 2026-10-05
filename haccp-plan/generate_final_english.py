#!/usr/bin/env python3
"""Final English HACCP plan for Carne Seca Jesus Canales, LLC.

Gas oven. Lethality in a sealed moisture-impermeable bag, then dehydration.
Release is by process records. Finished-product laboratory testing is not the release step.
"""

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor
from PIL import Image, ImageDraw, ImageFont

OUT = Path("/workspace/haccp-plan/final")
GREEN = "1F4D36"
INK = RGBColor(0x1E, 0x1A, 0x16)
MUTED = RGBColor(0x4A, 0x43, 0x3A)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

FONT_R = "/usr/share/fonts/truetype/macos/Inter-Regular.ttf"
FONT_B = "/usr/share/fonts/truetype/macos/Inter-Bold.ttf"
FONT_M = "/usr/share/fonts/truetype/macos/Inter-Medium.ttf"


def shade(cell, color):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), color)
    shd.set(qn("w:val"), "clear")
    tcPr.append(shd)


def font(run, size=11, bold=False, color=INK, italic=False):
    run.font.name = "Calibri"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = color


def p(doc, text, size=11, bold=False, before=0, after=6, center=False, italic=False, color=INK):
    par = doc.add_paragraph()
    par.paragraph_format.space_before = Pt(before)
    par.paragraph_format.space_after = Pt(after)
    par.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    if center:
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = par.add_run(text)
    font(run, size=size, bold=bold, color=color, italic=italic)
    return par


def h1(doc, text):
    return p(doc, text, size=16, bold=True, before=14, after=6, color=RGBColor(0x1F, 0x4D, 0x36))


def h2(doc, text):
    return p(doc, text, size=13, bold=True, before=10, after=4, color=RGBColor(0x1F, 0x4D, 0x36))


def body(doc, text):
    return p(doc, text)


def bullet(doc, text):
    par = doc.add_paragraph()
    par.paragraph_format.left_indent = Inches(0.25)
    par.paragraph_format.space_after = Pt(2)
    par.paragraph_format.space_before = Pt(0)
    run = par.add_run("• " + text)
    font(run, size=11)
    return par


def keep_row(row):
    tr = row._tr
    trPr = tr.get_or_add_trPr()
    trPr.append(OxmlElement("w:cantSplit"))


def table(doc, headers, rows, size=8):
    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    t.style = "Table Grid"
    for i, h in enumerate(headers):
        cell = t.rows[0].cells[i]
        cell.text = ""
        run = cell.paragraphs[0].add_run(h)
        font(run, size=size, bold=True, color=WHITE)
        shade(cell, GREEN)
    keep_row(t.rows[0])
    for r, row in enumerate(rows):
        keep_row(t.rows[r + 1])
        for c, val in enumerate(row):
            cell = t.rows[r + 1].cells[c]
            cell.text = ""
            run = cell.paragraphs[0].add_run(val)
            font(run, size=size)
            if r % 2 == 1:
                shade(cell, "F4F1EA")
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    return t


def setup(doc, header):
    sec = doc.sections[0]
    sec.top_margin = Cm(1.6)
    sec.bottom_margin = Cm(1.6)
    sec.left_margin = Cm(1.6)
    sec.right_margin = Cm(1.6)
    hp = sec.header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = hp.add_run(header)
    font(r, size=8, color=MUTED)
    fp = sec.footer.paragraphs[0]
    r = fp.add_run("Carne Seca Jesus Canales, LLC  ·  Delta, UT  ·  Page ")
    font(r, size=8, color=MUTED)
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    for el in (begin, instr, end):
        run = fp.add_run()
        font(run, size=8, color=MUTED)
        run._r.append(el)


def line(doc, label):
    body(doc, label + " " + "_" * 46)


def wrap(draw, text, fnt, width):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = w if not cur else cur + " " + w
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def rounded(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def flow_chart(path):
    W, H = 1400, 1980
    img = Image.new("RGB", (W, H), (248, 246, 241))
    d = ImageDraw.Draw(img)
    title_f = ImageFont.truetype(FONT_B, 40)
    sub_f = ImageFont.truetype(FONT_R, 22)
    head_f = ImageFont.truetype(FONT_B, 26)
    body_f = ImageFont.truetype(FONT_R, 20)
    small_f = ImageFont.truetype(FONT_M, 18)
    d.text((70, 36), "Process flow — ready-to-eat beef jerky", font=title_f, fill=(31, 77, 54))
    d.text((70, 88), "Carne Seca Jesus Canales, LLC  ·  Gas oven  ·  Delta, UT", font=sub_f, fill=(74, 67, 58))

    steps = [
        ("1  Receiving", "Raw beef from an approved supplier.", False),
        ("2  Cold storage  ·  prerequisite", "Meat at or below 41°F (5°C). Jerky field checklist.", False),
        ("3  Slice and marinate  ·  prerequisite", "Written formula. Meat stays at or below 41°F.", False),
        ("4  Seal the bag", "Moisture-impermeable bag. Probe in the thickest piece.", False),
        ("CCP 1  Lethality  ·  gas oven", "Bag stays sealed.\nInternal temperature 160°F or above.\nFrom 50°F to 130°F in 6 hours or less.", True),
        ("5  Open the bag", "Opened only after CCP 1 has passed.", False),
        ("CCP 2  Dehydration  ·  same gas oven", "Dry bulb 170°F or above during drying.\nWater activity 0.85 or less.\nHighest of at least six pieces.", True),
        ("6  Pack and label", "Contains: Soy, Wheat. Net weight. Address.", False),
        ("7  Pre-shipment review", "Records signed before the lot leaves.", False),
    ]
    y = 150
    x0, x1 = 90, 1310
    for title, text, ccp in steps:
        lines = []
        for part in text.split("\n"):
            lines.extend(wrap(d, part, body_f, x1 - x0 - 48))
        box_h = 58 + 28 * len(lines)
        fill = (31, 77, 54) if ccp else (255, 255, 255)
        outline = (31, 77, 54)
        ink = (255, 255, 255) if ccp else (30, 26, 22)
        sub = (226, 232, 224) if ccp else (74, 67, 58)
        rounded(d, (x0, y, x1, y + box_h), 16, fill, outline, 3)
        d.text((x0 + 24, y + 14), title, font=head_f, fill=ink)
        ty = y + 48
        for ln in lines:
            d.text((x0 + 24, ty), ln, font=body_f, fill=sub)
            ty += 28
        y = y + box_h + 18
        if y < 1760:
            d.line((700, y - 18, 700, y), fill=(31, 77, 54), width=3)
    rounded(d, (90, y + 6, 1310, y + 70), 12, (122, 46, 28))
    d.text((114, y + 24), "If a CCP limit is missed, the lot is held and is not sold as ready-to-eat jerky.", font=small_f, fill=(255, 255, 255))
    img.save(path, "PNG")


def limits_chart(path):
    W, H = 1600, 1100
    img = Image.new("RGB", (W, H), (248, 246, 241))
    d = ImageDraw.Draw(img)
    title_f = ImageFont.truetype(FONT_B, 36)
    sub_f = ImageFont.truetype(FONT_R, 20)
    head_f = ImageFont.truetype(FONT_B, 22)
    cell_f = ImageFont.truetype(FONT_R, 18)
    d.text((48, 28), "Critical limits", font=title_f, fill=(31, 77, 54))
    d.text((48, 76), "Heat-treated, shelf-stable beef jerky  ·  gas oven  ·  no laboratory release test", font=sub_f, fill=(74, 67, 58))
    headers = ["Point", "Limit", "Where the number comes from"]
    rows = [
        ["CCP 1\nLethality", "Internal 160°F or above,\nthickest piece, coldest spot.\nReadings are not averaged.", "Appendix A, Table 2.\nAt 158°F and above the reduction\nis instantaneous. This plan uses 160°F."],
        ["CCP 1\nCome-up", "Internal temperature is between\n50°F and 130°F for 6 hours or less.", "Appendix A, page 24.\nThe temperature is internal."],
        ["CCP 1\nMoisture", "Sealed moisture-impermeable bag\nuntil the internal temperature\nhas reached 160°F.", "Appendix A, page 31.\nMoisture stays in the bag, so humidity\nis not monitored as its own limit.\nA gas oven is not sealed (page 29)."],
        ["CCP 2\nDrying", "Dry bulb 170°F or above\nfor the whole drying stage.", "Jerky model CCP 2, and the jerky\nchecklist dry-bulb temperature.\nDrying starts after CCP 1 passes."],
        ["CCP 2\nWater activity", "0.85 or less.\nHighest of at least six pieces.", "Preservation chapter: S. aureus\ngrowth minimum 0.85, and as low as\n0.86 with oxygen. Checklist is 0.88."],
        ["Prerequisite\nCooler", "Raw meat at or below 41°F.", "Jerky field checklist, cooler row.\nThis is not a critical control point."],
    ]
    cols = [220, 520, 760]
    top = 130
    row_h = 145
    x = 48
    # header
    xx = x
    for i, htxt in enumerate(headers):
        rounded(d, (xx, top, xx + cols[i] - 8, top + 48), 8, (31, 77, 54))
        d.text((xx + 14, top + 12), htxt, font=head_f, fill=(255, 255, 255))
        xx += cols[i]
    y = top + 56
    for r, row in enumerate(rows):
        xx = x
        bg = (255, 255, 255) if r % 2 == 0 else (244, 241, 234)
        for i, val in enumerate(row):
            rounded(d, (xx, y, xx + cols[i] - 8, y + row_h - 8), 8, bg, (210, 204, 192), 1)
            ty = y + 12
            for ln in val.split("\n"):
                d.text((xx + 14, ty), ln, font=cell_f, fill=(30, 26, 22))
                ty += 24
            xx += cols[i]
        y += row_h
    img.save(path, "PNG")


def build_plan(flow_png, limits_png):
    doc = Document()
    setup(doc, "HACCP plan  ·  9 CFR 417  ·  Heat-treated, shelf-stable beef jerky")
    p(doc, "HACCP PLAN", size=12, bold=True, center=True, after=2, color=RGBColor(0x1F, 0x4D, 0x36))
    p(doc, "Heat-treated, shelf-stable, ready-to-eat beef jerky", size=18, bold=True, center=True, after=2)
    p(doc, "Carne Seca Jesus Canales, LLC", size=14, bold=True, center=True, after=2)
    p(doc, "411 E Main St, Delta, UT 84624", size=12, center=True, after=0)
    p(doc, "(435) 406-1178", size=12, center=True, after=8)
    p(doc, "Process category: Heat-Treated — Shelf Stable. 9 CFR 417.2(b)(1)(vi).", size=11, center=True, after=2)
    p(doc, "Equipment: the establishment’s gas oven. The oven vent stays open.", size=11, center=True, after=2)
    p(doc, "This plan replaces the returned May plan.", size=11, italic=True, center=True, after=10)

    h1(doc, "1. What this plan is")
    body(doc, "This plan is for the beef jerky made at this plant, in this gas oven. The meat is cooked while it is still moist, inside a sealed moisture-impermeable bag. The bag is then opened and the same oven dehydrates the meat. The finished jerky is ready to eat and shelf-stable.")
    body(doc, "A lot is released when the critical-control-point records meet the limits in Section 6 and the pre-shipment review is signed. A finished-product laboratory test is not the release step. The scientific reasons for the numbers are in the companion document, Scientific Support for the Critical Limits. That document names the hazard, the number, and the page the number comes from.")
    body(doc, "The May plan was returned because the critical limits were not tied to a stated criterion. Its cooking limit was 160°F with no come-up time, no moisture criterion, and no page citation. This plan keeps 160°F as the internal temperature and adds the two criteria Appendix A requires with that table: come-up time, and moisture maintained in a sealed bag. Drying is its own critical control point.")

    h1(doc, "2. Charts")
    body(doc, "Chart 1 is the process. Chart 2 is the limits. Both are the same numbers as Section 6.")
    doc.add_picture(str(flow_png), width=Inches(6.5))
    p(doc, "Chart 1. Process flow.", size=9, italic=True, color=MUTED, before=2)
    doc.add_picture(str(limits_png), width=Inches(6.5))
    p(doc, "Chart 2. Critical limits and the criterion for each number.", size=9, italic=True, color=MUTED, before=2)

    h1(doc, "3. Product description")
    table(doc, ["Item", "This product"], [
        ["Name", "Beef jerky (carne seca). Ready to eat. Heat-treated. Shelf-stable. The bag may also say Traditional Beef Jerky."],
        ["Process", "Whole-muscle beef, sliced, marinated, sealed in a moisture-impermeable bag, cooked in the gas oven to an internal temperature of 160°F or above, then dehydrated in the same oven to a water activity of 0.85 or less."],
        ["Equipment", "Gas oven. The burner vent stays open, so the oven is not a sealed oven. Appendix A, page 29, says the sealed-oven humidity method is not used when an opening cannot be closed."],
        ["Water activity", "Finished jerky: 0.85 or less."],
        ["pH", "Not a control. This jerky is not fermented and is not acidified."],
        ["Cure", "Uncured. No nitrite, no nitrate, no erythorbate."],
        ["Intended use", "Ready to eat by the general public. No further cooking. 9 CFR 417.2(a)(2)."],
        ["Package", "Heat-sealed food-grade bag. The bag states the net weight of the jerky in that bag. The retail unit used on the returned plan is 3 oz (85 g)."],
        ["Storage on the bag", "Unopened: cool, dry, at or below 70°F (21°C). Once opened: refrigerate and consume within 3 days. Safety of the unopened jerky is the water activity of 0.85 or less, not the 70°F line."],
        ["Shelf life", "The number of days is written here after this plant’s own holding records support it: __________ days."],
        ["Where sold", "Local retail, markets, and direct sale to household consumers."],
        ["Allergens", "Soy and wheat, from Worcestershire sauce and soy sauce. Every bag says Contains: Soy, Wheat."],
    ], size=9)

    h2(doc, "3.1 Ingredients — the same list as the bag")
    body(doc, "Beef, sea salt, garlic powder, onion powder, black pepper, paprika, Worcestershire sauce (vinegar, molasses, corn syrup, water, soy sauce (water, soybeans, wheat, salt), onion, garlic, cloves, tamarind, natural flavor), soy sauce (water, soybeans, wheat, salt), apple cider vinegar, liquid smoke.")
    body(doc, "Contains: Soy, Wheat.")
    body(doc, "Salt is for flavor. It does not replace the cook or the water-activity limit. No ingredient is added after the bag is opened. A batch whose weights do not match the batch sheet for this list is not cooked.")

    h2(doc, "3.2 Label")
    bullet(doc, "Product name includes Beef Jerky. English is required. “Carne seca” may be added.")
    bullet(doc, "Ingredient statement matches Section 3.1, in descending order of predominance.")
    bullet(doc, "Contains: Soy, Wheat.")
    bullet(doc, "Net weight, the inspection legend and establishment number, the address 411 E Main St, Delta, UT 84624, and a handling statement consistent with a ready-to-eat product.")
    bullet(doc, "The word “Traditional” is on the current artwork. Before that artwork is used under inspection, the establishment confirms whether the word is a special statement or claim that requires sketch approval under 9 CFR 412.1(c). A bag with no special claim is generically approved under 9 CFR 412.2 when every required feature is present and true.")
    bullet(doc, "The safe-handling label for raw meat is not used. This jerky is ready to eat.")
    bullet(doc, "The name “jerky” has a standard of identity. The moisture-to-protein ratio is 0.75:1 or less. That ratio is checked on validation lots for the name on the bag. It is not a critical limit.")
    body(doc, "Before a lot ships, the packer checks the bag against the batch sheet. A bag that fails that check is not sold.")

    h1(doc, "4. Process steps")
    table(doc, ["Step", "What happens"], [
        ["1. Receiving", "Raw beef enters from an approved supplier."],
        ["2. Cold storage", "The meat is held at or below 41°F. This is a prerequisite."],
        ["3. Slicing", "Whole muscle is sliced. Bone and foreign material are removed by looking at the meat."],
        ["4. Marination", "The formula in Section 3.1 is weighed onto the batch sheet. The meat stays at or below 41°F."],
        ["5. Bag", "Strips go into a moisture-impermeable bag. A probe is placed in the thickest piece. The bag is sealed so moisture stays inside, including around the probe entry."],
        ["6. CCP 1 — Lethality", "The sealed bag goes into the heated gas oven. The limits in Section 6 apply. Drying does not start until this step has passed."],
        ["7. Open", "The bag is opened only after the internal temperature of 160°F or above is recorded."],
        ["8. CCP 2 — Dehydration", "The strips are racked in the same gas oven. Dry bulb stays at 170°F or above. The lot is dried until water activity is 0.85 or less."],
        ["9. Cool and handle", "Finished jerky is handled only in the clean ready-to-eat area. Bare hands do not touch it."],
        ["10. Pack and label", "The bag is checked against Section 3.2."],
        ["11. Storage", "Dry storage. The safety control is the water activity already met at CCP 2."],
        ["12. Pre-shipment review", "The lot’s records are reviewed and signed before the lot ships."],
    ], size=9)
    body(doc, "The flow was walked in the plant on __________ by ______________________________.")

    h1(doc, "5. Hazard analysis")
    body(doc, "9 CFR 417.2(a). A hazard that is controlled by a prerequisite, and is not reasonably likely to occur because of that program, is not a critical control point. Biological hazards at the cook and at drying are reasonably likely to occur and are the two critical control points.")
    table(doc, ["Step", "Hazard", "CCP?", "Reason"], [
        ["1 Receiving", "Biological: pathogens on raw beef", "No", "Approved supplier. The cook is CCP 1."],
        ["2 Cold storage", "Biological: outgrowth", "No", "Prerequisite. Meat at or below 41°F. Jerky checklist cooler row."],
        ["3 Ingredients", "Chemical: soy, wheat; nitrite", "No", "The formula contains soy and wheat and no nitrite. The batch sheet and the label check control the allergen statement."],
        ["4 Packaging", "Biological: contamination", "No", "Food-grade bags, stored clean and dry."],
        ["5 Slicing", "Physical: bone, metal. Biological: contamination from people", "No", "Visual inspection while slicing. Employee health and hygiene prerequisite."],
        ["6 Marination", "Biological: outgrowth. Chemical: wrong allergen statement", "No", "Held at or below 41°F. Weights match Section 3.1."],
        ["7–8 CCP 1 Cooking", "Biological: STEC (O157:H7, O26, O45, O103, O111, O121, O145), Salmonella, L. monocytogenes", "Yes", "Raw beef may carry these organisms. The bag keeps the surface moist while the internal temperature reaches 160°F."],
        ["9 CCP 2 Drying", "Biological: C. perfringens and C. botulinum while the meat is still moist; S. aureus toxin; L. monocytogenes in storage", "Yes", "Drying at 170°F or above, then water activity 0.85 or less."],
        ["10 Handle", "Biological: L. monocytogenes after the cook", "No", "Sanitation SOP in the ready-to-eat area. Growth in storage is prevented by CCP 2, because 0.85 is below the 0.92 growth minimum."],
        ["11 Pack", "Chemical: undeclared soy or wheat", "No", "Every bag is checked for Contains: Soy, Wheat before the lot ships."],
        ["12 Storage", "Biological: growth", "No", "Water activity is already 0.85 or less."],
        ["13 Returns", "Biological: unknown holding", "No", "Opened bags are not resold."],
    ], size=8)

    h1(doc, "6. Critical control points")
    body(doc, "9 CFR 417.2(c). Every limit in a critical control point is required. The criterion for each number is named here and is set out page by page in the scientific-support document. 9 CFR 417.3: a miss identifies the cause, brings the point back under control, stops it from happening again, and keeps injurious product out of commerce.")

    h2(doc, "6.1 CCP 1 — Lethality in the gas oven")
    body(doc, "The bag is sealed and the meat is still moist. Drying does not start until every CCP 1 limit has passed. The probe is in the thickest piece, in the coldest part of the load. That cold spot is confirmed during initial validation. Readings are not averaged.")
    table(doc, ["Critical limit", "Criterion", "Monitoring, each lot"], [
        ["Internal temperature 160°F or above.", "Appendix A, December 2021, Table 2, footnote 5. The required reduction is achieved instantly when the internal temperature reaches 158°F or above. This plan uses 160°F, which is above that line. The temperature is the minimum in the meat, not the oven air.", "Time the probed piece reaches 160°F, the temperature read, the probe identity, and the place in the oven."],
        ["The internal temperature is between 50°F and 130°F for 6 hours or less.", "Appendix A, page 24. Come-up time is an internal temperature. The meat enters from a cooler at or below 41°F, so it enters below 50°F.", "Clock time the probed piece reaches 50°F and clock time it reaches 130°F. The difference is written in hours and minutes."],
        ["The moisture-impermeable bag stays sealed until the internal temperature is 160°F or above.", "Appendix A, page 31. Cooking in a sealed moisture-impermeable bag keeps moisture around the product, so relative humidity is not monitored as its own limit. Page 29: this gas oven cannot use the sealed-oven method.", "The seal is checked when the bag enters the oven and again at the 160°F reading. The time the bag is opened is written. It is not opened before that reading."],
    ], size=8)
    body(doc, "Who monitors: the person running the oven, named on the log.")
    body(doc, "If any CCP 1 limit is missed: the lot is stopped and Jesús Canales is told. The lot is held. It is not opened for dehydration and it does not ship. The cause is written. The oven or the bag practice is corrected before the next lot. Product that missed the cook is not sold as ready-to-eat jerky. A laboratory test is not the release step.")
    body(doc, "The cook may continue inside the same sealed bag only when the piece can still reach 160°F and the time between 50°F and 130°F is still 6 hours or less. Appendix A states that a come-up clock does not start over when the first cook did not reach a lethal temperature. If that time is already over 6 hours, the lot is not released under this plan.")

    doc.add_page_break()
    h2(doc, "6.2 CCP 2 — Dehydration")
    body(doc, "This step starts only after CCP 1 has passed. The bag is opened and the strips are racked so the gas oven can dry them.")
    table(doc, ["Critical limit", "Criterion", "Monitoring, each lot"], [
        ["Dry-bulb temperature 170°F or above during drying, read before the jerky is taken out.", "The jerky field checklist prints a dry bulb above 170°F (77°C). The FSIS beef-jerky model, CCP 2, uses an oven temperature of 170°F or above so Clostridium perfringens and Clostridium botulinum do not grow while water activity is still above 0.93. That model cites the FSIS Stabilization Guideline, Revised Appendix B, December 2021. The checklist’s wet-bulb line is not a limit in this plan. Appendix A, page 27, says a wet bulb of 125–130°F for one hour is not, by itself, the humidity support for Appendix A.", "Dry-bulb reading during drying, thermometer identity, and the time."],
        ["Finished water activity 0.85 or less. At least six pieces, from different places in the lot, including a thick piece. The highest reading is the lot result. Every piece checked is 0.85 or less.", "Principles of Preservation of Shelf-Stable Dried Meat Products: the aerobic growth minimum for Staphylococcus aureus is 0.85, and it can grow as low as 0.86 when oxygen is present. The same table gives Escherichia coli O157:H7 a minimum of 0.95, Salmonella 0.94, Listeria monocytogenes 0.92, and Clostridium perfringens and proteolytic Clostridium botulinum 0.93. The jerky checklist prints water activity below 0.88. A result of 0.85 or less meets that sheet. The jerky section of the preservation chapter says safety is judged by water activity, not by the moisture-to-protein ratio.", "After drying, before packing. Calibrated water-activity meter. All six readings are written. The highest is circled."],
    ], size=8)
    body(doc, "Who monitors: the person running the oven, named on the log.")
    body(doc, "If the dry bulb is below 170°F, or if any of the six readings is above 0.85: the lot is not packed. Jesús Canales is told. If CCP 1 passed, the lot may be dried longer at 170°F or above and measured again. If it still fails, it does not ship. It is not wetted and cooked again under this plan.")

    h1(doc, "7. Prerequisite programs")
    body(doc, "These programs are part of the HACCP system. They are not critical control points. A failure is corrected under the program and recorded. If a failure creates an unforeseen hazard, 9 CFR 417.3(b) applies: the product is held, the cause is found, injurious product does not ship, and a trained person reassesses whether the hazard belongs in the plan.")
    bullet(doc, "Cold storage. Raw beef for this jerky stays at or below 41°F (5°C), measured in the meat. The jerky field checklist prints this cooler limit. The FSIS model’s example prerequisite is below 45°F. This plan uses 41°F.")
    bullet(doc, "Employee health. The establishment uses the FDA Employee Health Policy Tool (2022 Food Code, part 2-201; tool dated August 23, 2023) for restriction and exclusion of ill employees. A person who is ill does not handle meat or jerky. Hands are washed. Bare hands do not touch finished jerky. This tool does not set a critical limit.")
    bullet(doc, "Sanitation SOP, 9 CFR 416. After the bag is opened, jerky is handled only in the clean area. The sanitation SOP names Alternative 2 of 9 CFR 430.4: the finished water activity of 0.85 or less is the antimicrobial process that prevents growth of Listeria monocytogenes, together with sanitation in the ready-to-eat area. The food-contact-surface testing frequency required for that alternative is written in the sanitation SOP before a lot ships.")
    bullet(doc, "Allergens. The batch sheet lists soy and wheat. The pack-out check confirms the bag says Contains: Soy, Wheat.")
    bullet(doc, "Thermometers and the water-activity meter are checked by the method in Section 9.5. An instrument that fails calibration is removed, and the lots checked with it since the last good calibration are reviewed.")
    body(doc, "The curing-and-smoking field checklist is not a prerequisite for this jerky and is not support for these limits. This product is not brine-cured, is not dry-cured, and is not hung to dry before a smoke schedule. That checklist was read so the wrong process would not be copied into this plan.")

    h1(doc, "8. Verification and records")
    bullet(doc, "Initial validation, 9 CFR 417.4(a)(1). The scientific support is the companion document and the pages it cites. The in-plant part is repeated lots on this gas oven, this load, and this thickness, showing that CCP 1 and CCP 2 were met and showing the cold spot. The validation date below stays blank until those logs have been reviewed.")
    bullet(doc, "Ongoing verification. Each production week, a person other than the monitor watches one CCP check when product is being made. Thermometers are checked in ice water at 32°F. The water-activity meter is checked with the manufacturer’s standards. Records are reviewed before shipment.")
    bullet(doc, "Reassessment, 9 CFR 417.4(a)(3). At least once a year, and when the oven, the bag, the formula, the thickness, or the load changes. The responsible official signs the reassessment.")
    bullet(doc, "Pre-shipment review, 9 CFR 417.5(c). Before the lot ships, a person reviews that lot’s records, writes that every critical limit was met or that the corrective action is finished, and signs and dates the review. Where practical, that person did not produce the record. The lot does not ship until this review says it may ship.")
    bullet(doc, "Records, 9 CFR 417.5. Each record shows the plant, the date, the product, the lot, the actual number measured, the initials of the monitor, and the review. Shelf-stable product records are kept for at least two years.")
    bullet(doc, "Training, 9 CFR 417.7. At least one person has completed training in the seven HACCP principles for meat and poultry. Name: ______________________________  Date of training: ______________.")

    h2(doc, "8.1 Signature — inspection item 1")
    body(doc, "9 CFR 417.2(d). The responsible official signs before the plan is used. The signature is in ink. A typed name is not the signature. The same person signs the scientific-support document on the same day. The plan is signed again at least once a year and whenever it is changed.")
    body(doc, "I am the responsible establishment official of Carne Seca Jesus Canales, LLC. I have reviewed this HACCP plan for ready-to-eat beef jerky made in this gas oven. Signing accepts the hazard analysis, the critical limits, the monitoring, the corrective actions, the verification, and the records in this plan.")
    line(doc, "Signature, Jesús Canales:")
    line(doc, "Printed name:")
    line(doc, "Date:")
    line(doc, "Initial validation completed (blank until Section 13 is reviewed):")
    line(doc, "Annual reassessment:")

    h1(doc, "9. How to measure each limit")
    body(doc, "Three instruments are used. A leave-in probe thermometer stays in the meat. A second thermometer hangs in the oven air during drying. A water-activity meter reads the finished jerky. The oven dial is the setting. The number written on the log is the number on the instrument.")

    h2(doc, "9.1 Cold meat, before cooking")
    body(doc, "Put the probe in the meat, not in the air of the cooler. Write the time and the temperature on Form 10.3. The limit is 41°F or below.")

    h2(doc, "9.2 Lethality — the probe stays inside the sealed bag")
    body(doc, "Choose the thickest strip and place it in the part of the oven that heats last. Put the tip of the probe in the center of that strip. The tip does not stick out into the air and does not touch the rack. Seal the bag around the probe cable so moisture stays in the bag. The bag is not opened to read the temperature.")
    body(doc, "On Form 10.1, with that same probe, write the clock at three points.")
    table(doc, ["When the meat reads", "What is written"], [
        ["50°F", "The clock time."],
        ["130°F", "The clock time."],
        ["160°F or above", "The clock time and the exact temperature."],
    ], size=10)
    body(doc, "Come-up time is the 130°F clock time minus the 50°F clock time. Example: 50°F at 8:00 and 130°F at 10:30 is 2 hours 30 minutes. The limit is 6 hours or less. If the bag is still sealed when the meat reaches 160°F, the cook has passed. Write the time the bag is opened. If the bag is opened before that reading, the lot is held.")

    h2(doc, "9.3 Drying — oven air, after the bag is opened")
    body(doc, "Hang a thermometer in the oven air, away from the wall, not stuck in the meat. Before the strips are taken out, read that thermometer. The limit is 170°F or above. Write the degrees and the time on Form 10.2.")

    h2(doc, "9.4 Water activity — before packing")
    body(doc, "The meter reads a number between 0 and 1, such as 0.81. A meter that reports only percent moisture is not this instrument.")
    body(doc, "Let the pieces cool, covered, to the temperature in the meter’s manual. Most meters read correctly near 77°F. A strip just out of a 170°F oven gives a false reading.")
    body(doc, "Take six strips from different places: front, middle, back, top rack, bottom rack, and one thick piece. Place each piece in the sample cup the way the manual describes. Write all six readings on Form 10.2. The lot result is the highest reading. If that reading is 0.85 or less, the lot passes. If any one reading is above 0.85, the lot is not packed.")

    h2(doc, "9.5 Checking the instruments")
    body(doc, "Once each week that jerky is made:")
    bullet(doc, "Probe. A glass of ice with a little water. The probe stays in the ice water and does not touch the glass. It must read 32°F. If it does not, adjust it by the manufacturer’s instructions or remove it from use.")
    bullet(doc, "Water-activity meter. Use the salt standards supplied with the meter.")
    body(doc, "An instrument that fails the check is not used. Lots measured with it since the last good check are reviewed.")

    h2(doc, "9.6 Measurements that are not taken on every lot")
    body(doc, "A Listeria swab is taken from tables, trays, and any surface that touches the jerky after the bag is opened. The swab goes to a laboratory. It is not a test of the bag of jerky. Moisture and protein, for the name “jerky,” are sent once on the validation lots. Neither result releases the lot. The lot is released by the probe, the clock, the dry-bulb thermometer, and the water-activity meter.")

    h1(doc, "9-A. Cómo medir cada límite")
    body(doc, "Esta sección es la misma instrucción, para la persona que opera el horno. Los límites siguen siendo los de la sección 6.")
    body(doc, "Se usan tres instrumentos. Una sonda se queda dentro de la carne. Otro termómetro cuelga en el aire del horno durante el secado. Un medidor de actividad de agua lee el producto terminado. La perilla del horno es el ajuste. El número que se anota es el del instrumento.")
    bullet(doc, "Frío. La sonda va en la carne, no en el aire del refrigerador. Límite: 41°F o menos. Hoja 10.3.")
    bullet(doc, "Cocido. La tira más gruesa va en la parte del horno que se calienta menos. La punta de la sonda queda en el centro de esa tira, sin salir al aire y sin tocar la rejilla. La bolsa se cierra alrededor del cable. No se abre para ver la temperatura.")
    bullet(doc, "En la hoja 10.1 se anota la hora a 50°F, la hora a 130°F, y la hora y los grados al llegar a 160°F o más. El tiempo de subida es la hora de 130°F menos la hora de 50°F. Ejemplo: 8:00 y 10:30 son 2 horas 30 minutos. Límite: 6 horas o menos. Si a 160°F la bolsa sigue cerrada, el cocido pasó. Se anota la hora en que se abre. Si se abre antes, el lote se detiene.")
    bullet(doc, "Secado. Un termómetro cuelga en el aire del horno, lejos de la pared, sin clavarlo en la carne. Se lee antes de sacar las tiras. Límite: 170°F o más. Hoja 10.2.")
    bullet(doc, "Actividad de agua. El aparato marca un número entre 0 y 1, por ejemplo 0.81. No sirve un medidor que solo dé el porcentaje de humedad. Las piezas se enfrían tapadas hasta la temperatura del manual, casi siempre cerca de 77°F. Una tira a 170°F da una lectura falsa. Se toman seis tiras: adelante, en medio, atrás, rejilla de arriba, rejilla de abajo, y una gruesa. El resultado del lote es la lectura más alta. Si es 0.85 o menos, pasa. Si una marca más de 0.85, no se empaca.")
    bullet(doc, "Cada semana de producción: la sonda en hielo con un poco de agua, sin tocar el vaso, tiene que marcar 32°F. El medidor de actividad de agua se comprueba con las sales del fabricante. Si un aparato falla, no se usa, y se revisan los lotes medidos desde la última prueba buena.")
    bullet(doc, "El hisopo de Listeria es de mesas, charolas y superficies que tocan la carne después de abrir la bolsa. Va al laboratorio. No es un análisis de la bolsa. Humedad y proteína, para el nombre “jerky”, se mandan una vez en los lotes de validación. El lote lo sueltan la sonda, el reloj, el termómetro del aire y el medidor de actividad de agua.")

    h1(doc, "10. Forms")
    h2(doc, "10.1 CCP 1 log — lethality")
    body(doc, "Lot __________   Date __________   Oven __________   Probe __________")
    body(doc, "Bag sealed on entry: yes / no. Probe in the thickest piece: yes / no. Cold-spot location: __________")
    table(doc, ["Reading", "Clock time", "Internal °F", "Initials"], [
        ["Internal temperature reaches 50°F", "", "", ""],
        ["Internal temperature reaches 130°F", "", "", ""],
        ["Come-up (130 minus 50), hours and minutes. Limit: 6 hours or less.", "", "", ""],
        ["Internal temperature reaches 160°F or above", "", "", ""],
        ["Bag still sealed at that reading, then time opened", "", "", ""],
    ], size=9)
    body(doc, "Limit met: yes / no. If no, lot held and Form 10.4 is completed. Reviewer __________ Date __________")

    h2(doc, "10.2 CCP 2 log — dehydration")
    body(doc, "Lot __________   Date __________   Dry-bulb thermometer __________   Water-activity meter __________")
    body(doc, "CCP 1 passed before the bag was opened: yes / no.")
    body(doc, "Dry bulb during drying: __________ °F. Limit: 170°F or above. Time read: __________")
    table(doc, ["Piece", "Place in the lot", "Water activity", "Initials"], [
        ["1", "", "", ""],
        ["2", "", "", ""],
        ["3", "", "", ""],
        ["4", "", "", ""],
        ["5", "", "", ""],
        ["6 (include a thick piece)", "", "", ""],
    ], size=9)
    body(doc, "Highest reading: __________. Limit: 0.85 or less. Limit met: yes / no. Reviewer __________ Date __________")

    h2(doc, "10.3 Cooler log — prerequisite, not a CCP")
    body(doc, "Date __________  Time __________  Product temperature __________ °F  Limit: 41°F or less  Initials __________")

    h2(doc, "10.4 Corrective action")
    body(doc, "Lot __________  CCP __________  Date __________  Time __________")
    body(doc, "What was measured: ________________________________")
    body(doc, "Limit that was missed: ________________________________")
    body(doc, "Cause: ________________________________")
    body(doc, "Action that brought the point back under control: ________________________________")
    body(doc, "Action that keeps it from happening again: ________________________________")
    body(doc, "Disposition. The lot is held. It is not sold as ready-to-eat jerky unless every limit is met on the records. A laboratory test is not the release step.")
    line(doc, "Jesús Canales:")

    h2(doc, "10.5 Pre-shipment review")
    body(doc, "Lot __________  Date __________")
    bullet(doc, "CCP 1: 160°F internal, come-up 6 hours or less, bag sealed until that reading.")
    bullet(doc, "CCP 2: dry bulb 170°F or above, highest of six water-activity readings 0.85 or less.")
    bullet(doc, "Bag says Contains: Soy, Wheat, and the ingredients match the batch sheet.")
    bullet(doc, "Any corrective action is finished. No injurious product is in this shipment.")
    line(doc, "Reviewer signature and date:")

    h1(doc, "11. Documents kept with this plan")
    bullet(doc, "Scientific Support for the Critical Limits, the companion to this plan.")
    bullet(doc, "FSIS Cooking Guideline for Meat and Poultry Products (Revised Appendix A), December 2021, FSIS-GD-2021-14.")
    bullet(doc, "Principles of Preservation of Shelf-Stable Dried Meat Products, October 31, 2011.")
    bullet(doc, "HACCP Field Verification Checklist, Jerky (fully cooked, shelf-stable, ready-to-eat).")
    bullet(doc, "FDA Employee Health Policy Tool, August 23, 2023, for the employee-health prerequisite.")
    bullet(doc, "FSIS HACCP Model for Ready-to-Eat, Heat-Treated, Shelf-Stable Beef Jerky, 2021-0004, CCP 2, for the 170°F drying temperature.")
    bullet(doc, "FSIS Stabilization Guideline (Revised Appendix B), December 2021, as cited by that model.")
    body(doc, "The curing-and-smoking checklist is on file as a document that was reviewed and not used. The returned May plan is on file as the plan this one replaces. Sections 12 through 16 complete the five items an inspector still checks before this plan can be used.")

    h1(doc, "12. Item 1 — signature")
    body(doc, "The signature block is Section 8.1 of this plan and Section 6 of the scientific support. Both are signed in ink by Jesús Canales before the packet is sent. The validation date on that block stays blank until the three lots in Section 13 have been reviewed.")

    h1(doc, "13. Item 2 — in-plant validation")
    body(doc, "9 CFR 417.4(a)(1). The scientific support is already written. The in-plant part is three lots on this gas oven, with the load and the strip thickness that will be used in production. A lot that misses a limit does not count. The cause is corrected before the next validation lot. The validation date is written only after all three lots meet every limit and Jesús Canales reviews the logs.")
    bullet(doc, "Lot 1 also finds the cold spot. The same thick strip size is probed in three places in the oven: front, center, and back, or top, middle, and bottom if that is how the racks sit. The place that reaches 160°F last is the cold spot. It is written here: __________.")
    bullet(doc, "Lots 2 and 3 use that cold spot and the thickest strip. Each lot completes Form 10.1 and Form 10.2.")
    bullet(doc, "All three instruments in Section 16 have passed their checks before lot 1 starts.")
    table(doc, ["Validation lot", "Date", "Load and thickness", "CCP 1 met", "CCP 2 met", "Reviewer"], [
        ["1 (cold spot)", "", "", "yes / no", "yes / no", ""],
        ["2", "", "", "yes / no", "yes / no", ""],
        ["3", "", "", "yes / no", "yes / no", ""],
    ], size=9)
    body(doc, "Cold spot found on lot 1: __________. Thickness used: __________. Validation date, filled only when all three lots passed: __________.")

    h1(doc, "14. Item 3 — how this gas oven is run")
    body(doc, "The meat is not dehydrated until the cook in the sealed bag has passed. One lot follows these steps.")
    bullet(doc, "Hold the raw beef at or below 41°F. Weigh the formula in Section 3.1 onto the batch sheet.")
    bullet(doc, "Put the thickest strip in the cold spot. Place the probe in the center of that strip. Seal the moisture-impermeable bag around the meat and the probe cable.")
    bullet(doc, "Put the sealed bag in the heated gas oven. Leave the burner vent as the oven requires. Do not treat this oven as a sealed oven.")
    bullet(doc, "Write the clock at 50°F, at 130°F, and at 160°F or above. Open the bag only after 160°F is written and the come-up is 6 hours or less.")
    bullet(doc, "Rack the strips so air can dry them. Keep the dry-bulb thermometer at 170°F or above. Read it before the strips come out.")
    bullet(doc, "Cool six pieces, covered, to the meter temperature. Record the water activity. Pack only if the highest reading is 0.85 or less and the pre-shipment review is signed.")
    body(doc, "Para quien opera el horno: la carne no se seca hasta que la bolsa cerrada llegó a 160°F por dentro. La sonda se queda en la tira más gruesa. La bolsa se abre después de anotar 160°F y de comprobar que de 50°F a 130°F pasaron 6 horas o menos. Luego se seca a 170°F en el aire del horno y se miden seis piezas. Si la más alta pasa de 0.85, no se empaca.")

    h1(doc, "15. Item 4 — Listeria sanitation program")
    body(doc, "After the bag is opened, the jerky is post-lethality exposed. This plant uses Alternative 2, Choice 2, of 9 CFR 430.4. The antimicrobial process is the finished water activity of 0.85 or less, which is below the 0.92 growth minimum for Listeria monocytogenes. Sanitation in the ready-to-eat area goes with that process. This section is the sanitation program the regulation requires for that choice.")
    h2(doc, "15.1 Clean before the bag is opened")
    body(doc, "On each production day, before exposed jerky is handled, the person in charge looks at the racks, the table, the scale, and the utensils. They are clean to sight and touch. The result is written on the pre-operational line of Form 10.6. Jerky is not laid on a surface that fails that check.")
    h2(doc, "15.2 Food-contact surface testing")
    body(doc, "The laboratory test is for Listeria spp. on food-contact surfaces. It is not a test of the jerky in the bag.")
    bullet(doc, "Frequency. One sampling event in the first validation week, before a lot ships, and then one event each calendar quarter while jerky is made. There is one line.")
    bullet(doc, "Why this frequency is enough. FSIS recommends quarterly food-contact testing per line for Alternative 2. This plant has one line. The finished water activity prevents growth of Listeria monocytogenes during storage. The first event is done before product ships.")
    bullet(doc, "Sites, each event. (1) The rack or tray that holds jerky after the bag is opened. (2) The table where jerky is placed before packing. (3) The scale pan or the tongs that touch the jerky. If a glove or the sealer touches the meat, that surface is added.")
    bullet(doc, "Size. Up to 12 inches by 12 inches of the food-contact area. If the surface is smaller, the whole food-contact face is swabbed.")
    h2(doc, "15.3 When a swab is positive")
    body(doc, "A positive Listeria spp. result on a food-contact surface: packing stops, the lot in the room is held, the site is cleaned and sanitized, and the site is swabbed again before the next lot. If that second swab is positive, or if the laboratory reports Listeria monocytogenes, the held lot does not ship. Jesús Canales tells the inspector. The lot is not released by a finished-product laboratory test. Disposition is written on Form 10.4 and Form 10.6.")
    table(doc, ["Date", "Site", "Area swabbed", "Lab result", "Lot held", "Initials"], [
        ["", "Rack / tray", "", "", "yes / no", ""],
        ["", "Table", "", "", "yes / no", ""],
        ["", "Scale or tongs", "", "", "yes / no", ""],
    ], size=9)
    body(doc, "Form 10.6. Pre-operational check the same day: clean to sight and touch, yes / no __________. Person __________.")

    h1(doc, "16. Item 5 — instruments on site")
    body(doc, "The first validation lot does not start until these three instruments are in the plant and the checks below are written. The oven dial is not one of the three.")
    table(doc, ["Instrument", "What it measures", "Mark the ID", "Check before use"], [
        ["Leave-in probe thermometer", "Internal meat temperature, °F. It stays in the strip inside the sealed bag.", "Probe __________", "Ice water reads 32°F. The probe does not touch the glass."],
        ["Oven-air thermometer", "Dry-bulb temperature during drying, °F. It hangs in the air, off the wall, not in the meat.", "Oven __________", "Ice water reads 32°F if the thermometer can be removed. If it is fixed, hold the calibrated probe in the oven air beside it and write both numbers. The probe is the record if they differ."],
        ["Water-activity meter", "Finished jerky, a number from 0 to 1. It is not a percent-moisture meter.", "Meter __________", "Salt standards supplied with the meter, in the week jerky is made."],
    ], size=8)
    body(doc, "An instrument that fails its check is not used. Lots measured with it since the last good check are reviewed. Form 10.7: date __________, probe 32°F yes / no, oven thermometer yes / no, water-activity standards yes / no, initials __________.")
    doc.save(OUT / "HACCP-Plan-Beef-Jerky-Final.docx")


def build_support():
    doc = Document()
    setup(doc, "Scientific support for the critical limits  ·  Carne Seca Jesus Canales, LLC")
    p(doc, "SCIENTIFIC SUPPORT", size=12, bold=True, center=True, after=2, color=RGBColor(0x1F, 0x4D, 0x36))
    p(doc, "Criteria used to set each critical limit", size=18, bold=True, center=True, after=4)
    p(doc, "Ready-to-eat, heat-treated, shelf-stable beef jerky", size=12, center=True, after=2)
    p(doc, "Carne Seca Jesus Canales, LLC  ·  411 E Main St, Delta, UT 84624", size=12, center=True, after=8)
    body(doc, "This is the support requested for the critical control points. For each critical limit it names the hazard, the number, the criterion used to choose that number, and the page where that criterion is written. It is written so the reviewer can see why each limit is the limit for this ready-to-eat product.")
    body(doc, "The product is whole-muscle beef jerky cooked in this plant’s gas oven and then dehydrated in that same oven. The oven vent stays open. The jerky is not fermented, is not acidified, and contains no nitrite. Nothing is added after the heat step. pH is not a critical limit. Soy and wheat are in the formula and are declared on the bag. They are controlled by the batch sheet and the label check. They are not a critical control point.")
    body(doc, "A lot is released on the process records. This support does not rely on a finished-product laboratory test, and it does not cite a challenge study of this jerky. 9 CFR 417.4(a)(1) still has an in-plant part. The validation date on the HACCP plan stays blank until logs from this oven, this load, and this thickness have been reviewed.")

    h1(doc, "1. The process the limits belong to")
    table(doc, ["Stage", "What the plant does", "Why it is in this order"], [
        ["CCP 1, lethality", "Strips are sealed in a moisture-impermeable bag and heated in the gas oven until the internal temperature is 160°F or above, with a come-up of 6 hours or less between 50°F and 130°F.", "Appendix A says humidity has to be applied during lethality, before drying (page 26). The sealed bag is the way this oven keeps the surface moist (page 31)."],
        ["CCP 2, dehydration", "The bag is opened only after CCP 1 passes. The gas oven then dries the strips at a dry bulb of 170°F or above until water activity is 0.85 or less.", "Drying is what makes the jerky shelf-stable. It is not the lethality step."],
    ], size=9)

    h1(doc, "2. CCP 1 — lethality")
    h2(doc, "2.1 Internal temperature 160°F or above")
    bullet(doc, "Hazard. Salmonella and Shiga-toxin producing Escherichia coli, including O157:H7, on raw beef, including on the surface of a sliced strip. Listeria monocytogenes is included in the cook because the product is ready to eat.")
    bullet(doc, "Critical limit. Internal temperature 160°F or above, in the thickest piece, in the coldest part of the load. Readings are not averaged. The oven-air temperature is not the limit.")
    bullet(doc, "Criterion. FSIS Cooking Guideline for Meat and Poultry Products (Revised Appendix A), December 2021, FSIS-GD-2021-14, Table 2, page 35, “Time-Temperature Combinations for Meat Products to Achieve Lethality.” Footnote 5 on that page: the required log reductions are achieved instantly (0 seconds) when the internal temperature of a cooked meat product reaches 158°F or above. The row at 145°F on the same table is 4 minutes for both the 6.5-log column and the 7-log column. This plan does not use the 145°F row. It uses 160°F, which is above the 158°F instantaneous line, so the dwell time at 160°F is zero on that table.")
    bullet(doc, "The same table states that relative humidity and come-up time are also critical operating parameters when the table is used. Those two parameters are the next two limits. They are not optional.")
    bullet(doc, "The preservation chapter, page 167, says processors must validate a 5-log reduction of E. coli O157:H7 for products that contain beef, and that the product must be heated to achieve it. The heat step in this plan is the Table 2 endpoint above.")

    h2(doc, "2.2 Come-up time, 6 hours or less")
    bullet(doc, "Hazard. Staphylococcus aureus growth and heat-stable enterotoxin if the meat stays too long between 50°F and 130°F during heating.")
    bullet(doc, "Critical limit. The time the internal temperature is between 50°F and 130°F is 6 hours or less.")
    bullet(doc, "Criterion. Appendix A, page 24: “Come-Up-Time Option: Total time product temperature is between 50 and 130°F is 6 hours or less.” The same page says those temperatures are internal temperatures. Footnote 7 of Table 2, page 35, repeats the 6-hour limit.")
    bullet(doc, "The meat is held at or below 41°F before it is cooked, so it enters the oven below 50°F. The clock starts when the probed piece reaches 50°F and stops when it reaches 130°F.")

    h2(doc, "2.3 Sealed moisture-impermeable bag")
    bullet(doc, "Hazard. Salmonella surviving on a surface that dries before the lethal internal temperature is reached. Drying the surface early makes the organism harder to kill.")
    bullet(doc, "Critical limit. The strip stays in a sealed moisture-impermeable bag until the internal temperature is 160°F or above. The bag is opened only after that reading is recorded. Dehydration starts after that.")
    bullet(doc, "Criterion. Appendix A, page 31, “Situations when Humidity is Not Needed.” Moisture is inherently maintained when the product is cooked in a sealed, moisture-impermeable bag. Establishments that match that situation do not monitor relative humidity as its own critical operating parameter. The bag is that situation for this gas oven.")
    bullet(doc, "Appendix A, page 26: humidity is applied during the lethality treatment, before drying. Opening the bag only after 160°F puts dehydration after lethality.")
    bullet(doc, "Appendix A, page 29: if an oven has an opening that cannot be closed, the sealed-oven method is not used. This is a gas oven. The burner vent stays open. The plan therefore does not use Humidity Option 2.")
    bullet(doc, "Appendix A, page 27: a wet-bulb temperature of 125–130°F and 27–32 percent relative humidity for one hour, taken from the jerky guideline, is not adequate on its own to support the Appendix A humidity options. This plan does not use that pair as the humidity limit. The jerky checklist prints a wet bulb of 125–142°F next to its heat-lethality line. That line is not a critical limit in this plan, for the reason on page 27.")
    bullet(doc, "The preservation chapter, Jerky Products section, page 168, says the jerky guidelines call for a humidity step at the beginning of the process. The sealed-bag cook is that step. Dehydration follows it.")

    h1(doc, "3. CCP 2 — dehydration")
    h2(doc, "3.1 Dry bulb 170°F or above")
    bullet(doc, "Hazard. Outgrowth of Clostridium perfringens and Clostridium botulinum while water activity is still high enough for growth, during the drying stage.")
    bullet(doc, "Critical limit. The dry-bulb temperature of the gas oven is 170°F or above throughout drying, read before the jerky is removed.")
    bullet(doc, "Criterion. The jerky field checklist, heat-lethality row, prints a dry bulb above 77°C (170°F). This plan applies that dry-bulb temperature to the whole drying stage. The FSIS HACCP Model for Ready-to-Eat, Heat-Treated, Shelf-Stable Beef Jerky, 2021-0004, CCP 2, sets the oven at 170°F or above during drying so those sporeformers do not grow while water activity is still above 0.93, and it cites the FSIS Stabilization Guideline, Revised Appendix B, December 2021, for that temperature. Lethality itself is CCP 1, not this dry-bulb reading.")

    h2(doc, "3.2 Water activity 0.85 or less")
    bullet(doc, "Hazard. Staphylococcus aureus growth and toxin on a jerky that is stored in air. Listeria monocytogenes growth during storage. Growth of the vegetative pathogens named in the preservation table if water activity stays above their minima.")
    bullet(doc, "Critical limit. Finished water activity 0.85 or less. At least six pieces from different places in the lot, including a thick piece. The highest reading is the lot result.")
    bullet(doc, "Criterion. Principles of Preservation of Shelf-Stable Dried Meat Products, October 31, 2011, growth-minimum table (chapter pages 157–158): Staphylococcus aureus, aerobic, 0.85. The same chapter, page 160: Staphylococcus aureus can grow as low as 0.86 water activity when oxygen is present. A finished result of 0.85 or less is at or below that aerobic minimum and below 0.86. The same table: Escherichia coli O157:H7, 0.95; Salmonella, 0.94; Listeria monocytogenes, 0.92; Clostridium perfringens, 0.93; proteolytic Clostridium botulinum, 0.93. Finished jerky at 0.85 or less is below each of those minima.")
    bullet(doc, "The same chapter, page 160: dried hams, coppa, and beef jerky generally have water activity less than 0.88. The jerky field checklist, drying row, prints water activity below 0.88. The limit in this plan is 0.85 or less, which meets the checklist.")
    bullet(doc, "The same chapter, Jerky Products section, page 168: safety and shelf stability of jerky are judged by water activity, not by the moisture-to-protein ratio, and the older practice of relying on a moisture-to-protein ratio of 0.75 or below is not the safety indicator. Page 160 states that moisture-to-protein ratios are labeling standards and are not necessarily indicative of microbial safety. This plan checks 0.75:1 on validation lots for the product name. It is not a critical limit.")
    bullet(doc, "The chapter also states that if pathogens are still viable, the product is adulterated. Water activity stops growth. It is not the kill step. The kill step is CCP 1.")

    h1(doc, "4. Limits that are not critical control points")
    table(doc, ["Item", "Number used", "Why it is not a CCP"], [
        ["Cooler", "Raw meat at or below 41°F (5°C).", "Jerky field checklist, cooler-storage row. It keeps the meat below the start of the come-up range. Outgrowth before the cook is controlled by this prerequisite."],
        ["Employee health", "Restriction and exclusion under the 2022 FDA Food Code, part 2-201, using the Employee Health Policy Tool dated August 23, 2023.", "People who are ill do not handle the product. The tool does not identify a process critical limit."],
        ["Allergens", "Contains: Soy, Wheat, on every bag. Formula in the plan, Section 3.1.", "Controlled by the batch sheet and the pack-out check."],
        ["Moisture-to-protein ratio", "0.75:1 or less, on validation lots.", "Standard of identity for the name jerky. Preservation chapter, page 160 and page 168. Not a safety limit."],
        ["Curing and smoking checklist", "Not used.", "That checklist is for brine, dry cure, a salinometer, and hanging meat before smoke. This jerky is not that process. Using it would attach the wrong criteria to these critical limits."],
    ], size=8)

    h1(doc, "5. What the returned May plan did not show")
    body(doc, "The returned plan set CCP 1 at 160°F and CCP 2 at a water activity of 0.85 or less. It did not identify the Table 2 footnote that makes 158°F instantaneous, it did not set the 6-hour come-up, and it did not state how moisture is maintained in this gas oven. Section 2 of this document is that identification. The water-activity number is kept and is now tied to the preservation-chapter table and to the checklist value it also satisfies.")

    h1(doc, "6. Signature")
    body(doc, "I am providing this document as the scientific support for the critical limits in the HACCP plan for this ready-to-eat beef jerky.")
    line(doc, "Responsible establishment official, Jesús Canales:")
    line(doc, "Date:")
    doc.save(OUT / "Scientific-Support-CCPs-Final.docx")


def build_letter():
    text = """To the reviewer:

The May HACCP plan for Carne Seca Jesus Canales, LLC was returned with a request for the scientific support for the critical control points. The support had to identify the criteria used to set each critical limit for a safe ready-to-eat product.

Two documents are attached.

1. HACCP Plan — Heat-Treated, Shelf-Stable Beef Jerky.
2. Scientific Support for the Critical Limits.

The product is ready-to-eat beef jerky made in this plant’s gas oven. The oven vent stays open, so the sealed-oven humidity option in Appendix A is not used. Lethality is a cook in a sealed moisture-impermeable bag to an internal temperature of 160°F or above, with the internal temperature between 50°F and 130°F for 6 hours or less. Dehydration starts after that cook. The dry bulb is 170°F or above, and the finished water activity is 0.85 or less, using the highest of at least six pieces.

The page for each number is in the scientific-support document. A finished-product laboratory test is not the release step. The in-plant validation date is blank until logs from this oven, this load, and this thickness have been reviewed and the plan is signed.

Jesús Canales
Carne Seca Jesus Canales, LLC
411 E Main St, Delta, UT 84624
(435) 406-1178
"""
    (OUT / "Cover-Note-to-Reviewer.txt").write_text(text)


def _letter_pages():
    import fitz

    green = (31 / 255, 77 / 255, 54 / 255)
    ink = (30 / 255, 26 / 255, 22 / 255)
    muted = (74 / 255, 67 / 255, 58 / 255)
    doc = fitz.open()

    cover = doc.new_page(width=612, height=792)
    cover.insert_font(fontname="B", fontfile=FONT_B)
    cover.insert_font(fontname="R", fontfile=FONT_R)
    cover.draw_rect(fitz.Rect(0, 0, 612, 10), color=green, fill=green)
    cover.insert_textbox(fitz.Rect(54, 48, 558, 80), "PRINT THIS PACKET", fontname="B", fontsize=11, color=green)
    cover.insert_textbox(
        fitz.Rect(54, 78, 558, 160),
        "HACCP plan and scientific support\nReady-to-eat beef jerky",
        fontname="B",
        fontsize=22,
        color=ink,
    )
    cover.insert_textbox(
        fitz.Rect(54, 168, 558, 230),
        "Carne Seca Jesus Canales, LLC\n411 E Main St, Delta, UT 84624\n(435) 406-1178",
        fontname="R",
        fontsize=12,
        color=ink,
    )
    cover.draw_rect(fitz.Rect(54, 248, 558, 249), color=green, fill=green)
    order = (
        "What is in this file, in print order\n\n"
        "1. This cover.\n"
        "2. Note to the reviewer.\n"
        "3. HACCP plan, with the charts, how to measure, the logs, the signature page, the three validation lots, the oven steps, the Listeria program, and the instrument list.\n"
        "4. Scientific support for each critical limit.\n\n"
        "Print every page on letter paper. Sign in ink before the packet is sent.\n\n"
        "Sign the HACCP plan, section 8.1, Jesús Canales.\n"
        "Sign the scientific support, section 6, Jesús Canales.\n"
        "Leave the validation date blank until lots from this gas oven, this load, "
        "and this thickness have been reviewed."
    )
    cover.insert_textbox(fitz.Rect(54, 268, 558, 560), order, fontname="R", fontsize=12, color=ink, align=fitz.TEXT_ALIGN_LEFT)
    cover.insert_textbox(
        fitz.Rect(54, 700, 558, 760),
        "Gas oven. Cook in a sealed bag, then dehydrate.\nA laboratory test is not the release step.",
        fontname="R",
        fontsize=11,
        color=muted,
    )

    note = doc.new_page(width=612, height=792)
    note.insert_font(fontname="B", fontfile=FONT_B)
    note.insert_font(fontname="R", fontfile=FONT_R)
    note.draw_rect(fitz.Rect(0, 0, 612, 10), color=green, fill=green)
    note.insert_textbox(fitz.Rect(54, 46, 558, 90), "Note to the reviewer", fontname="B", fontsize=18, color=ink)
    body = (
        "The May HACCP plan for Carne Seca Jesus Canales, LLC was returned with a request "
        "for the scientific support for the critical control points. The support had to identify "
        "the criteria used to set each critical limit for a safe ready-to-eat product.\n\n"
        "This packet contains the HACCP plan and the scientific support.\n\n"
        "The product is ready-to-eat beef jerky made in this plant’s gas oven. The oven vent "
        "stays open, so the sealed-oven humidity option in Appendix A is not used. Lethality is "
        "a cook in a sealed moisture-impermeable bag to an internal temperature of 160°F or above, "
        "with the internal temperature between 50°F and 130°F for 6 hours or less. Dehydration "
        "starts after that cook. The dry bulb is 170°F or above, and the finished water activity "
        "is 0.85 or less, using the highest of at least six pieces.\n\n"
        "The page for each number is in the scientific-support document. A finished-product "
        "laboratory test is not the release step. The in-plant validation date is blank until "
        "logs from this oven, this load, and this thickness have been reviewed and the plan is signed.\n\n"
        "Jesús Canales\n"
        "Carne Seca Jesus Canales, LLC\n"
        "411 E Main St, Delta, UT 84624\n"
        "(435) 406-1178"
    )
    spare = note.insert_textbox(fitz.Rect(54, 110, 558, 740), body, fontname="R", fontsize=12, color=ink)
    if spare < 0:
        raise SystemExit("reviewer note does not fit on one page")
    return doc


def assemble_print_packet():
    import fitz

    plan = OUT / "HACCP-Plan-Beef-Jerky-Final.pdf"
    support = OUT / "Scientific-Support-CCPs-Final.pdf"
    if not plan.exists() or not support.exists():
        raise SystemExit("plan and support PDFs must exist before the print packet is built")
    packet = _letter_pages()
    packet.insert_pdf(fitz.open(plan))
    packet.insert_pdf(fitz.open(support))
    dest = OUT / "HACCP-PARA-IMPRIMIR.pdf"
    packet.save(dest, deflate=True, garbage=4)
    # Same pages as the file already cited for sending.
    packet.save(OUT / "HACCP-FINAL-ENGLISH.pdf", deflate=True, garbage=4)
    print("print packet", dest, "pages", packet.page_count)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    flow = OUT / "CHART-Process-Flow.png"
    limits = OUT / "CHART-Critical-Limits.png"
    flow_chart(flow)
    limits_chart(limits)
    build_plan(flow, limits)
    build_support()
    build_letter()
    print("wrote", OUT)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "packet":
        assemble_print_packet()
    else:
        main()
