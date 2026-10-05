#!/usr/bin/env python3
"""HACCP plan aligned to the jerky field sheet and the FSIS sheets that sheet cites."""

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor

OUT = "/workspace/haccp-plan/HACCP-Plan-Carne-Seca-Jesus-Canales.docx"
GREEN = "1F4D36"
INK = RGBColor(0x1E, 0x1A, 0x16)
MUTED = RGBColor(0x4A, 0x43, 0x3A)


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


def table(doc, headers, rows, size=8):
    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    t.style = "Table Grid"
    for i, h in enumerate(headers):
        cell = t.rows[0].cells[i]
        cell.text = ""
        run = cell.paragraphs[0].add_run(h)
        font(run, size=size, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF))
        shade(cell, GREEN)
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            cell = t.rows[r + 1].cells[c]
            cell.text = ""
            run = cell.paragraphs[0].add_run(val)
            font(run, size=size)
            if r % 2 == 1:
                shade(cell, "F4F1EA")
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    return t


def line(doc, label):
    body(doc, label + " " + "_" * 46)


def header_footer(doc):
    sec = doc.sections[0]
    sec.top_margin = Cm(1.5)
    sec.bottom_margin = Cm(1.5)
    sec.left_margin = Cm(1.6)
    sec.right_margin = Cm(1.6)
    hp = sec.header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = hp.add_run("Jerky sheet limits  ·  Carne Seca Jesus Canales, LLC  ·  Revision 1")
    font(r, size=8, color=MUTED)
    fp = sec.footer.paragraphs[0]
    r = fp.add_run("Critical limits are the ones printed on the jerky verification sheet.  ·  Page ")
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


def build():
    doc = Document()
    header_footer(doc)

    p(doc, "HACCP PLAN", size=20, bold=True, center=True, after=2, color=RGBColor(0x1F, 0x4D, 0x36))
    p(doc, "Jerky — fully cooked, shelf-stable, ready-to-eat beef", size=13, bold=True, center=True, after=2)
    p(doc, "Written to the jerky field verification sheet", size=11, italic=True, center=True, after=8)
    p(doc, "CARNE SECA JESUS CANALES, LLC", size=12, bold=True, center=True, after=2)
    p(doc, "411 E Main St, Delta, UT 84624", size=11, center=True, after=8)

    h2(doc, "Cover block — same fields as the jerky sheet")
    table(
        doc,
        ["Jerky sheet field", "This establishment"],
        [
            ["Establishment name", "Carne Seca Jesus Canales, LLC"],
            ["Address", "411 E Main St, Delta, UT 84624"],
            ["Person in charge", "Jesús Canales"],
            ["Phone / e-mail", "______________________  /  ______________________"],
            ["Food product and process", "Ready-to-eat beef jerky (carne seca). Heat treated, then dried. Shelf-stable."],
            ["Is the jerky RTE?", "Yes. The customer does not cook it."],
            ["Does it contain beef?", "Yes. Beef rounds or the whole-muscle beef named on the batch sheet."],
            ["Date written plan validated", "Filled in Section 12, after the logs show the limits were met. Blank until then."],
            ["Establishment number", "______________________"],
            ["HACCP-trained person (9 CFR 417.7)", "Name ______________________   Training date __________"],
        ],
        size=9,
    )
    body(doc, "I will run this plan. No lot ships until Section 12 is signed.")
    line(doc, "Jesús Canales:")
    line(doc, "Date:")
    line(doc, "HACCP-trained person:")
    line(doc, "Date:")

    h1(doc, "1. Which sheet controls this product")
    body(doc, "Two field sheets were provided. This product is the product named on the jerky sheet, not a brine-cured sausage.")
    table(
        doc,
        ["Sheet", "How this plan uses it"],
        [
            ["Jerky verification checklist — Fully cooked, shelf-stable, RTE", "This is the sheet for carne seca. The critical limits in Section 4 are copied from that sheet."],
            ["FSIS Cooking Guideline, Revised Appendix A, December 2021 (FSIS-GD-2021-14)", "The jerky sheet marks the lethality limit “Per FSIS Performance Standard.” Come-up time and the internal endpoint from Table 2 of that guideline sit inside the Heat Lethality CCP. They do not replace the dry-bulb and wet-bulb numbers."],
            ["Principles of Preservation of Shelf-Stable Dried Meat Products", "Drying is judged by water activity, not by moisture-to-protein ratio. The limit used is the one on the jerky sheet: aw < 0.88. Beef lethality addresses E. coli O157:H7 at the heat step. This product is not fermented, so pH and degree-hours are not limits."],
            ["Curing and smoking checklist", "Used for the prerequisite lines that match this plant (vendors, health, handwashing, calibration, separate temperature logs, post-process protection, dedicated areas). Three lines on that sheet are not this process. They are listed in Section 3.4 so they are not added by mistake."],
        ],
        size=8,
    )

    h1(doc, "2. One product, one flow, one formula")
    body(doc, "The jerky sheet asks that the food flow, the menu, the package, and the formula match the written plan.")
    table(
        doc,
        ["Item", "What is made"],
        [
            ["Product", "Beef jerky (carne seca), ready to eat, shelf-stable, not refrigerated for safety"],
            ["Process category", "Heat-treated — shelf stable (9 CFR 417.2(b)(1))"],
            ["Beef", "Inspected beef. Mark of inspection and invoice kept with the lot."],
            ["Formula, weighed before the cook", "Beef, salt, and only these spices if the batch sheet shows a weight: black pepper, garlic powder, onion powder, paprika."],
            ["Not in this formula", "Nitrite, nitrate, starter culture, sugar, and any ingredient added after the heat step."],
            ["Allergens", "None of the major allergens are in this formula. A spice without a specification that says so is rejected."],
            ["Package", "Food-grade moisture-barrier bag, heat-sealed. Lot code on the bag. The bag does not wet the jerky."],
            ["Customers", "General public. No further cooking."],
            ["Distribution", "Dry, ambient. A wet or open bag is not sold."],
        ],
        size=9,
    )
    h2(doc, "Flow — the order on the jerky sheet")
    for step in [
        "Receive inspected beef and check product temperature (Cooler Storage CCP starts here).",
        "Receive salt, spices, and bags against the specification.",
        "Cooler storage. Product stays below 41°F (5°C).",
        "Trim and slice. Record thickness on the batch sheet.",
        "Weigh the batch (recipe record). Mix. Marinate in the cooler, still below 41°F.",
        "Drain. Single layer on racks. Do not stack.",
        "Heat lethality CCP, with humidity, before drying.",
        "Drying CCP. Water activity < 0.88, measured before packing.",
        "Cool and hold in the dry ready-to-eat area. Do not rinse or mist.",
        "Pack, label, lot code. Dry storage. Distribution record.",
    ]:
        bullet(doc, step)
    body(doc, "Walk-through: this list matches the plant.")
    line(doc, "Name and date:")

    h1(doc, "3. Prerequisites — the YES/NO block on the jerky sheet")
    body(doc, "Each line below is a line on that sheet. The record is named so the inspector can see it the same day.")

    h2(doc, "3.1 Employee health and hygiene")
    bullet(doc, "A person with vomiting, diarrhea, jaundice, or fever does not handle meat or jerky and reports it to Jesús Canales.")
    bullet(doc, "Clean clothes, hair restraint, no jewelry on the hands and wrists, no eating, drinking, or smoking in the work area.")
    bullet(doc, "Hands are washed before work and after any break or raw-meat contact. Bare hands do not touch finished jerky. Use a clean glove or a utensil.")

    h2(doc, "3.2 Time and temperature controls")
    body(doc, "Covered by the three CCPs and by the separate temperature logs in Section 5. The cook log, the cooler log, and the drying log are different sheets.")

    h2(doc, "3.3 Cleaning and sanitation")
    bullet(doc, "Before slicing and before packing, food-contact surfaces are cleaned, rinsed, sanitized, and looked at. The result is written (clean or not clean).")
    bullet(doc, "The pack table is ready-to-eat product only, after that cleaning.")
    bullet(doc, "If raw beef touches a ready-to-eat surface, packing stops, the surface is cleaned again, and exposed jerky is held.")

    h2(doc, "3.4 Suppliers")
    bullet(doc, "Beef is from an inspected source. Invoice and mark of inspection are the receiving record.")
    bullet(doc, "Each spice and the salt have a specification. Bags are food-grade and stored dry, off the floor.")

    h2(doc, "3.5 Water")
    body(doc, "Water that touches product or equipment is potable. The current water report is on file. That report is not a test of the jerky.")

    h2(doc, "3.6 Chemicals")
    body(doc, "Cleaners and sanitizers are labeled and stored away from beef, spices, and bags.")

    h2(doc, "3.7 Recipe")
    body(doc, "Every lot has a batch sheet: beef weight, each spice weight or a written zero, and a check that the label matches that sheet. Nothing is added after heat lethality.")

    h2(doc, "3.8 Ovens, humidity, calibration, maintenance")
    bullet(doc, "The drying oven or smoker used for lethality has a dry-bulb thermometer and a wet-bulb thermometer, or a humidity instrument that is converted to wet bulb and written as wet bulb.")
    bullet(doc, "The manufacturer’s instructions for that oven stay with this plan.")
    bullet(doc, "Each production day, before the first lot: product probe in ice water at 32°F and against a reference near cooking temperature; dry bulb and wet bulb by the maker’s check; water-activity meter on the salt standard. An instrument that fails is not used, and lots read with it that day are held.")
    bullet(doc, "Jesús Canales is told the same day if the wet-bulb instrument is out of service. Heat lethality is not started without it.")

    h2(doc, "3.9 Training")
    body(doc, "Before a person monitors a CCP, Jesús Canales or the HACCP-trained person shows that person the three limits, the logs, and the hold procedure. The training sheet is signed and kept. Section 8.")

    h2(doc, "3.10 Packaging, storage, distribution — no rehydration")
    bullet(doc, "Jerky is packed only after the drying CCP passes.")
    bullet(doc, "Bags stay sealed and dry. Product is not soaked, steamed, or held in a wet cooler.")
    bullet(doc, "Storage is dry, off the floor, separated from raw beef.")
    bullet(doc, "The distribution log records lot, date out, and that the bag was intact and dry.")

    h2(doc, "3.11 Lines from the curing-and-smoking sheet that are not this process")
    table(
        doc,
        ["Line on the curing sheet", "This jerky plan"],
        [
            ["Smoking to extend shelf life or for flavor?", "Shelf stability is the drying CCP (aw < 0.88) after heat lethality. If the oven smokes the product, the smoke is flavor only. Smoke does not replace dry bulb, wet bulb, or water activity."],
            ["Dry curing", "Not used. Salt is weighed into the batch and the meat stays in the cooler."],
            ["Brine outside the cooler brought to ≤41°F within 4 hours, and a salinometer", "Not used. There is no brine tank and no salinometer reading."],
            ["Hang on rods and dry about 2 hours before smoking", "Not used. The jerky sheet and Appendix A require humidity during lethality, before drying. Drying the meat first is a different process and is outside this plan."],
        ],
        size=8,
    )
    body(doc, "Lines from that sheet that do apply are already in Section 3: vendor papers, health policy, handwashing, hygiene, thermometer calibration, separate temperature logs, a raw area and a ready-to-eat area, and cleaning of the equipment.")

    h1(doc, "4. Critical control points — the table on the jerky sheet")
    body(doc, "The three limits below are the starred limits on the jerky sheet. Heat lethality also carries the two Appendix A conditions the sheet’s footnote requires.")

    h2(doc, "CCP-1  Cooler storage — temperature")
    table(
        doc,
        ["Item", "As written on the jerky sheet"],
        [
            ["Process", "Cooler storage of raw beef, including receiving and marination"],
            ["Critical control point", "Temperature"],
            ["Critical limit", "Product temperature < 5°C (41°F)"],
            ["How", "Calibrated probe in the meat, not in the cooler air"],
            ["When", "Every receipt. At least once per shift while beef for jerky is in the cooler. Start and end of marination."],
            ["Who", "Trained monitor. Initials at the time of the reading."],
            ["Record", "Cooler temperature log (separate sheet)"],
            ["If the limit is missed", "Hold the meat. Beef at 41°F or above is not made into this jerky. Tell Jesús Canales. Write the corrective-action form. Do not rely on the cook to undo warm raw beef."],
        ],
        size=8,
    )

    h2(doc, "CCP-2  Heat lethality — humidity and temperature")
    table(
        doc,
        ["Item", "Requirement"],
        [
            ["Process", "Heat lethality, before the drying step"],
            ["Critical control point", "Humidity and temperature"],
            ["Critical limit from the jerky sheet", "Dry bulb > 77°C (170°F) within 30 minutes after this stage starts. Wet bulb from 52°C (125°F) to 61°C (142°F) during this stage."],
            ["From the FSIS performance standard named on that sheet (Appendix A, December 2021, Table 2)", "Internal temperature of the thickest slice, taken in the coldest part of the oven, ≥ 158°F (70°C). Table 2 gives this endpoint 0 seconds of extra hold for meat when humidity and come-up time are met. Come-up time: the product is between 50°F and 130°F internal for 6 hours or less. Readings are not averaged. The lowest internal reading is the result."],
            ["Order", "Humidity is on during this stage. Drying starts only after this CCP passes. The product is not dried first."],
            ["How", "Dry-bulb and wet-bulb instruments. Calibrated probe. Clock."],
            ["When", "Every lot. Dry bulb at the start and at or before 30 minutes. Wet bulb at the start, at 30 minutes, and when the internal temperature is recorded."],
            ["Who", "Trained monitor"],
            ["Record", "Heat-lethality temperature log (its own sheet, not the cooler log)"],
            ["If the limit is missed", "Hold the lot. Do not start drying. Do not ship. Continue heating only if the wet bulb has stayed inside 125–142°F and the only miss is that the internal temperature is not at 158°F yet. If the dry bulb missed 170°F inside 30 minutes, or the wet bulb left the range, or the come-up passed 6 hours, the lot does not ship as jerky. Jesús Canales writes the disposition. A pathogen test on the finished piece is not the release step in this plan."],
        ],
        size=8,
    )
    body(doc, "For beef, this heat step is the step that addresses E. coli O157:H7 and Salmonella. The support is Appendix A used with the humidity on the jerky sheet, plus the in-plant logs in Section 12. This plan does not cite a laboratory challenge study.")

    h2(doc, "CCP-3  Drying — water activity")
    table(
        doc,
        ["Item", "As written on the jerky sheet"],
        [
            ["Process", "Drying, after heat lethality has passed"],
            ["Critical control point", "Water activity"],
            ["Critical limit", "aw < 0.88"],
            ["What is not the limit", "Moisture-to-protein ratio. The preservation sheet treats that ratio as a labeling description, not as the safety measurement."],
            ["pH", "Not a critical limit. This jerky is not fermented and not acidified."],
            ["How", "Calibrated water-activity meter. Three pieces from different places in the oven, including the thickest piece. The highest reading is the lot result."],
            ["When", "Every lot, after drying, before packing"],
            ["Who", "Trained monitor"],
            ["Record", "Drying log (its own sheet)"],
            ["If the limit is missed", "Do not pack. If CCP-2 passed, dry longer and read aw again. If the highest reading is still 0.88 or above, do not ship. Hold the lot and call Jesús Canales. Do not wet the product and cook it again under this plan."],
        ],
        size=8,
    )

    h1(doc, "5. Monitoring records — the list on the jerky sheet")
    body(doc, "The sheet asks whether each record exists, how often it is made, how it is made, and where it is kept. Records for this plant are kept in the HACCP binder in the office. Entries are made when the event happens (9 CFR 417.5). The value written is the value read.")
    table(
        doc,
        ["Record on the jerky sheet", "Frequency and procedure", "Where kept"],
        [
            ["Receiving", "Each delivery. Beef: supplier, invoice, mark of inspection, product °F. Spices and bags: specification checked.", "HACCP binder, receiving section"],
            ["Recipe / production", "Each lot. Weights on the batch sheet. Label checked against that sheet.", "HACCP binder, with the lot"],
            ["CCPs", "Each lot. Cooler log, heat-lethality log, and drying log, on separate sheets. Actual °F, wet bulb, minutes, and aw.", "HACCP binder, CCP section"],
            ["Sanitation", "Each production day, before slicing and before packing. Clean or not clean, and the correction.", "HACCP binder, sanitation section"],
            ["Calibration / monitoring equipment", "Each production day, before the first lot. Probe, dry bulb, wet bulb, aw meter.", "HACCP binder, calibration section"],
            ["Corrective actions", "Each miss. Lot held, cause, correction, disposition, signature of Jesús Canales.", "HACCP binder, with the lot"],
            ["Training", "Before a person monitors a CCP, and when the plan changes. Topic and signature.", "HACCP binder, training section"],
            ["Verification", "Each lot, before it ships: the pre-shipment review compares the logs with the three limits. Weekly: Jesús Canales reads the week’s logs.", "HACCP binder, with the lot and the weekly sheet"],
            ["Product inventory / distribution", "Each lot out. Date, quantity, destination, bag dry and intact.", "HACCP binder, distribution section"],
        ],
        size=8,
    )

    h1(doc, "6. Examining the logs — laboratory tests of the jerky")
    body(doc, "The jerky sheet asks whether today’s records match what is happening in the plant, and whether monitoring follows the plan. It does not require a laboratory pathogen test of every bag.")
    body(doc, "Routine release is the pre-shipment review. The reviewer looks at the lot and writes Met or Not met:")
    bullet(doc, "Cooler log: product < 41°F (5°C).")
    bullet(doc, "Heat log: dry bulb > 170°F within 30 minutes; wet bulb between 125°F and 142°F; internal ≥ 158°F on the lowest slice; come-up ≤ 6 hours.")
    bullet(doc, "Drying log: highest aw < 0.88.")
    bullet(doc, "Calibration for that day was acceptable.")
    bullet(doc, "Sanitation signed before the work.")
    bullet(doc, "Any corrective action is finished and the food is still on hold if it failed.")
    body(doc, "A blank, a check mark, or the word “yes” where a number belongs is Not met. The lot stays. The reviewer’s name and the time are written on the form. That page is how the establishment examines the information.")
    body(doc, "A laboratory test for Salmonella or E. coli on the finished jerky is not the monitoring method and is not the way a failed lot is released under this plan.")

    h1(doc, "7. Hazard analysis — why these three CCPs")
    table(
        doc,
        ["Step", "Hazard", "Control", "CCP"],
        [
            ["Receive and cool beef", "Salmonella, E. coli O157:H7", "Killed at heat lethality if humidity and temperature are met", "No — controlled at CCP-2"],
            ["Receive and cool beef", "Warm meat before the cook", "CCP-1, < 41°F", "Yes, CCP-1"],
            ["Spices", "Salmonella on a spice", "Spice is in the batch before the cook", "No — controlled at CCP-2. None added after."],
            ["Slice and racks", "A thick or buried slice misses the heat", "Single layer. Thickness written on the batch sheet. Probe the thickest slice in the coldest spot.", "Enforced at CCP-2"],
            ["Heat lethality", "Pathogens survive if the surface dries first or the temperature is short", "CCP-2", "Yes, CCP-2"],
            ["Drying", "Growth in a shelf-stable bag if aw stays high", "CCP-3, aw < 0.88", "Yes, CCP-3"],
            ["Pack and storage", "Listeria on the jerky after the cook; water getting back in", "Sanitation, bare-hand rule, dedicated ready-to-eat area, no rehydration. Growth is limited by aw < 0.88.", "No"],
        ],
        size=8,
    )
    body(doc, "Person responsible for the system and for seeing that records are kept: Jesús Canales. The HACCP-trained person named on the cover does the annual reassessment and any change to a limit (9 CFR 417.4 and 417.7).")

    h1(doc, "8. Corrective actions — what the employee does and says")
    body(doc, "The jerky sheet asks the employee to show this without looking it up from memory alone. The contact, the form, and the hold are:")
    bullet(doc, "Stop. Do not pack and do not ship the affected food.")
    bullet(doc, "Tell Jesús Canales, person in charge, before the lot moves.")
    bullet(doc, "Fill the corrective-action form: limit, actual number, lot, cause, what was done, and where the food is held.")
    bullet(doc, "Food that is not fit is not sold. Disposal or rejection is written on that form and signed by Jesús Canales.")
    bullet(doc, "The action taken is the action in Section 4 for that CCP, not a different one decided at the door.")
    body(doc, "What the employee says if asked the limits:")
    bullet(doc, "Cooler: product colder than 41°F (5°C).")
    bullet(doc, "Heat: dry bulb hotter than 170°F (77°C) within 30 minutes, wet bulb between 125°F and 142°F (52°C to 61°C), inside of the thickest piece at least 158°F, and no more than 6 hours between 50°F and 130°F.")
    bullet(doc, "Drying: water activity under 0.88, read on the meter, before the bag is sealed.")

    h1(doc, "9. Training")
    body(doc, "The training record lists the date, the person, and the topics: the three limits, how to calibrate, how to fill the logs with numbers, who to call, and how to hold food. The record is in the binder. A person who has not signed it does not monitor a CCP. On request, that person demonstrates the probe, the wet bulb, or the water-activity meter.")

    h1(doc, "10. Managers")
    body(doc, "Jesús Canales can state the three limits, the hold rule, and where the binder is. He signs weekly record review and every disposition.")

    h1(doc, "11. Validation date")
    body(doc, "The jerky sheet asks for the date the written plan was validated. That date is the day the HACCP-trained person has reviewed production logs that show this oven, this load, and this thickness met CCP-1, CCP-2, and CCP-3, and Jesús Canales signs here. Until that date is written, the plan is not the authority to ship.")
    line(doc, "Lots reviewed:")
    line(doc, "Oven (make or plant name) and fullest load:")
    line(doc, "HACCP-trained person and date:")
    line(doc, "Jesús Canales and date — this is the validation date:")
    body(doc, "A thicker cut, a different oven, a heavier load, a brine, a dry-cure, or a spice added after the cook is not this plan. Those wait for a reassessment.")
    body(doc, "Reassessment is at least once a year and after any of those changes. 9 CFR 417.4.")

    h1(doc, "12. Forms — copies of these sheets go in the binder")

    h2(doc, "12.1 Receiving")
    table(doc, ["Date", "Item", "Supplier / invoice", "Beef °F (if beef)", "Spec ok?", "Initials"], [["", "", "", "", "", ""]], size=8)

    h2(doc, "12.2 Recipe / batch")
    table(
        doc,
        ["Lot", "Beef lb", "Salt", "Pepper", "Garlic", "Onion", "Paprika", "Label matches? "],
        [["", "", "", "", "", "", "", ""]],
        size=8,
    )
    body(doc, "Write 0 if that spice was not used. Do not add anything after heat lethality.")

    h2(doc, "12.3 Cooler temperature log — CCP-1")
    body(doc, "Limit: product < 41°F (5°C).")
    table(doc, ["Date / time", "Lot", "Receipt, cooler, or marinade", "Product °F", "Initials"], [["", "", "", "", ""], ["", "", "", "", ""]], size=8)

    h2(doc, "12.4 Heat lethality log — CCP-2")
    body(doc, "Separate sheet from the cooler log. Write the numbers.")
    table(
        doc,
        ["Reading", "Lot result"],
        [
            ["Date and lot", ""],
            ["Time stage started", ""],
            ["Dry bulb at start (°F)", ""],
            ["Time dry bulb first went above 170°F (must be within 30 minutes)", ""],
            ["Dry bulb then (°F). Limit: > 170°F", ""],
            ["Wet bulb at start, at 30 min, and at the internal check (°F). Limit: 125 to 142 the whole stage", ""],
            ["Time from 50°F to above 130°F internal. Limit: 6 hours or less", ""],
            ["Coldest spot probed, and internal °F of the thickest slice. Limit: ≥ 158°F. Not an average.", ""],
            ["Initials and clock time", ""],
        ],
        size=8,
    )

    h2(doc, "12.5 Drying log — CCP-3")
    body(doc, "Limit: highest aw < 0.88. pH is not a limit; write “not used” in the pH cell so the sheet’s pH question has an answer.")
    table(
        doc,
        ["Lot", "aw 1", "aw 2", "aw 3", "Highest aw", "pH", "Meter", "Initials"],
        [["", "", "", "", "", "Not used", "", ""]],
        size=8,
    )

    h2(doc, "12.6 Calibration")
    table(
        doc,
        ["Date", "Instrument", "Check", "Result", "Fit for use?", "Initials"],
        [
            ["", "Probe", "32°F ice and hot reference", "", "", ""],
            ["", "Dry bulb", "Maker’s check", "", "", ""],
            ["", "Wet bulb", "Maker’s check", "", "", ""],
            ["", "aw meter", "Salt standard", "", "", ""],
        ],
        size=8,
    )

    h2(doc, "12.7 Sanitation")
    table(doc, ["Date", "Slicer, tables, racks clean before use?", "Pack table clean before RTE?", "Correction", "Initials"], [["", "", "", "", ""]], size=8)

    h2(doc, "12.8 Corrective action")
    table(
        doc,
        ["Field", "Entry"],
        [
            ["Date, time, CCP, lot", ""],
            ["Limit and the number read", ""],
            ["Food held? Where?", ""],
            ["Jesús Canales notified? Time", ""],
            ["Cause and what was fixed before the next lot", ""],
            ["Disposition (rejected, discarded, dried longer after a passed heat step, or other). Failed heat lots do not ship as jerky.", ""],
            ["Signatures: monitor and Jesús Canales", ""],
        ],
        size=8,
    )

    h2(doc, "12.9 Pre-shipment review — verification of the lot")
    table(
        doc,
        ["Check", "Met / Not met", "Number on the log"],
        [
            ["Product < 41°F", "", ""],
            ["Dry bulb > 170°F within 30 min", "", ""],
            ["Wet bulb 125–142°F", "", ""],
            ["Come-up ≤ 6 hours", "", ""],
            ["Internal ≥ 158°F, lowest slice", "", ""],
            ["Highest aw < 0.88", "", ""],
            ["Calibration fit for use", "", ""],
            ["Sanitation signed", "", ""],
            ["Corrective action closed if there was a miss", "", ""],
        ],
        size=8,
    )
    line(doc, "Lot:")
    line(doc, "Reviewer, date, and time:")
    line(doc, "Ship? Yes / No:")

    h2(doc, "12.10 Training")
    table(doc, ["Date", "Person", "Topics (limits, calibration, logs, hold, who to call)", "Trainer", "Signatures"], [["", "", "", "", ""]], size=8)

    h2(doc, "12.11 Distribution")
    table(doc, ["Date", "Lot", "Quantity", "Destination", "Bag dry and intact?", "Initials"], [["", "", "", "", "", ""]], size=8)

    h2(doc, "12.12 Weekly review")
    body(doc, "Jesús Canales: the logs this week match the limits and the plant.")
    line(doc, "Week of:")
    line(doc, "Gaps:")
    line(doc, "Signature and date:")

    p(
        doc,
        "End of Revision 1. Cooler, heat lethality, and drying use the critical limits printed on the jerky verification sheet. Appendix A adds the internal endpoint and the come-up time inside heat lethality, because that sheet says the lethality limit follows the FSIS performance standard.",
        size=10,
        italic=True,
        before=10,
    )
    doc.save(OUT)
    print(OUT)


if __name__ == "__main__":
    build()
