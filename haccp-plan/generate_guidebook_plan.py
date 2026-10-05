#!/usr/bin/env python3
"""Establishment HACCP plan in the form of the FSIS guidebook, using the 2021 jerky model."""

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor

OUT = "/workspace/haccp-plan/HACCP-Plan-Beef-Jerky-Guidebook.docx"
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
    body(doc, label + " " + "_" * 42)


def header_footer(doc):
    sec = doc.sections[0]
    sec.top_margin = Cm(1.5)
    sec.bottom_margin = Cm(1.5)
    sec.left_margin = Cm(1.5)
    sec.right_margin = Cm(1.5)
    hp = sec.header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = hp.add_run("9 CFR 417  ·  FSIS Guidebook  ·  Jerky model 2021-0004  ·  Carne Seca Jesus Canales, LLC")
    font(r, size=8, color=MUTED)
    fp = sec.footer.paragraphs[0]
    r = fp.add_run("Heat-treated, shelf-stable, ready-to-eat beef jerky  ·  Page ")
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
    p(doc, "Ready-to-eat, heat-treated, shelf-stable beef jerky", size=13, bold=True, center=True, after=2)
    p(doc, "Written in the order of the FSIS Guidebook for the Preparation of HACCP Plans", size=11, italic=True, center=True, after=6)
    p(doc, "CARNE SECA JESUS CANALES, LLC", size=12, bold=True, center=True, after=2)
    p(doc, "411 E Main St, Delta, UT 84624", size=11, center=True, after=8)

    body(doc, "This plan is specific to this plant and this jerky. It is not a copy of a generic model. The generic model is an example. FSIS says the model is not to be used as-is, and that the establishment tailors it to its own operation.")
    table(
        doc,
        ["Document", "How this plan uses it"],
        [
            ["9 CFR Part 417 (2020 edition, govinfo)", "This is the regulation. The plan has a hazard analysis, a flow chart, the intended use, critical limits, monitoring, corrective actions, records with the actual numbers, verification, a signature, and pre-shipment review."],
            ["FSIS Guidebook for the Preparation of HACCP Plans, FSIS-GD-2020-0008", "The sections below follow the guidebook’s preliminary steps and the seven principles. The guidebook’s worksheets are optional. The regulation is not optional."],
            ["FSIS HACCP Model for Ready-to-Eat, Heat-Treated, Shelf-Stable Beef Jerky, 2021-0004", "The two critical control points and their limits are the ones in that model: cooking, then drying. The model’s example product is cured and contains soy sauce. This jerky is not that product. The differences are in Section 2."],
            ["FSIS Cooking Guideline, Revised Appendix A, December 2021, FSIS-GD-2021-14", "The model says its cooking critical limit comes from Appendix A. The 145°F for 4 minutes, the sealed-oven humidity, and the come-up time come from that guideline."],
            ["Jerky field verification checklist", "The checklist’s cooler limit, below 41°F, is the prerequisite limit in Section 1. The checklist’s drying limit, water activity below 0.88, is met by the stricter model limit of 0.85 or less."],
        ],
        size=8,
    )
    h2(doc, "Guidelines on the FSIS index that this plan uses")
    body(doc, "The page at fsis.usda.gov/policy/fsis-guidelines is a list of guidance. Guidance is not the regulation. 9 CFR Part 417 is the regulation. The guidelines below are the ones on that list that apply to this ready-to-eat, heat-treated, shelf-stable beef jerky. Each one is kept with the plan when the establishment has the copy.")
    table(
        doc,
        ["Guideline on the FSIS list", "What this plan takes from it"],
        [
            ["Guidebook for the Preparation of HACCP Plans, FSIS-GD-2020-0008", "The order of this plan: prerequisites, product description, ingredients, flow chart, hazard analysis, then the seven principles."],
            ["HACCP Model for Ready-to-Eat, Heat-Treated, Shelf-Stable Beef Jerky, 2021-0004", "CCP 1 is cooking. CCP 2 is drying. The critical limits in Section 5 are the limits in that model, tailored to this uncured jerky."],
            ["Compliance Guideline for Meat and Poultry Jerky Produced by Small and Very Small Establishments, 2014-0010", "Humidity is applied during the cook, before drying. Water activity, not the moisture-to-protein ratio, is the safety measurement for the finished jerky."],
            ["Cooking Guideline for Meat and Poultry Products, Revised Appendix A, December 2021 (2021-0014)", "145°F for at least 4 minutes, the sealed-oven humidity option, and a come-up of 6 hours or less between 50°F and 130°F."],
            ["Compliance Guideline: HACCP Systems Validation, 2015-0011", "Validation has two parts: the scientific support, and in-plant records showing this oven meets the limits. The validation date stays blank until those records exist. 9 CFR 417.4."],
            ["Stabilization Guideline, Revised Appendix B, December 2021 (2021-0013)", "The jerky model cites this guideline for the water-activity level that limits Clostridium perfringens and Clostridium botulinum. This plan does not add a cooling critical control point. Those sporeformers are controlled by drying at 170°F or above until the finished water activity is 0.85 or less."],
            ["Compliance Guideline: Controlling Listeria monocytogenes in Post-lethality Exposed Ready-to-Eat Meat and Poultry Products, 2014-0001", "The jerky is handled after the cook, so it is post-lethality exposed. Water activity of 0.85 or less is below the growth minimum for Listeria monocytogenes. The sanitation SOP names the 9 CFR 430.4 alternative before any lot ships."],
        ],
        size=7,
    )
    body(doc, "Other guidelines on that index, including slaughter, raw ground beef, and canned products, are not the process in this plant. They are not part of this plan. If the formula later adds an allergen or a nitrite cure, the allergen guideline and 9 CFR 424.22 are added and the hazard analysis is reassessed.")

    h1(doc, "1. Preliminary steps")
    h2(doc, "1.1 Prerequisite programs")
    body(doc, "These procedures keep some hazards from being reasonably likely to occur. Each one is written, and the record is kept with this plan (9 CFR 417.5(a)).")
    bullet(doc, "Sanitation SOP. Food-contact surfaces are cleaned before slicing and before packing. The result is written as clean or not clean.")
    bullet(doc, "Temperature control. Raw beef for this jerky stays below 41°F (5°C), measured in the meat. The FSIS model uses a prerequisite of below 45°F (Tompkin, 1996) and does not make cold storage a critical control point. This plan uses 41°F, which is colder than 45°F, because that is the limit on the jerky field checklist.")
    bullet(doc, "Receiving. Beef is from an inspected source. The invoice and the mark of inspection are kept. Spices and bags have a specification.")
    bullet(doc, "Employee hygiene. A person who is ill does not handle meat or jerky. Hands are washed. Bare hands do not touch finished jerky.")
    bullet(doc, "Equipment check. The slicer is looked at before use. A damaged blade stops the work. This plant does not claim a history of metal-detector results, because that history is not on file.")
    bullet(doc, "Allergen and ingredient control. The batch sheet lists every ingredient and its weight. Nothing in this formula is a major allergen. Nitrite is not used.")
    bullet(doc, "Ready-to-eat area. After the cook, jerky is handled only in the clean pack area. The bag is not wetted.")
    bullet(doc, "Returned product. An opened bag is not taken back into production. If returned product is accepted, the local FSIS office is told.")
    bullet(doc, "Recall. Written recall procedures are kept, as required by 9 CFR 418.3. If adulterated product from this plant has entered commerce, the local FSIS District Office is notified within 24 hours (9 CFR 418.2).")

    h2(doc, "1.2 HACCP team")
    body(doc, "9 CFR 417.7: the person who develops this plan, and the person who reassesses it, must have completed a course in the seven HACCP principles for meat or poultry, including a HACCP plan for a specific product and record review. That person does not have to be an employee.")
    line(doc, "HACCP-trained person:")
    line(doc, "Course and date:")
    line(doc, "Responsible establishment official: Jesús Canales")

    h2(doc, "1.3 Product description — guidebook worksheet 1")
    table(
        doc,
        ["Guidebook question", "This product"],
        [
            ["Common name", "Beef jerky (carne seca), ready to eat, heat-treated, shelf-stable."],
            ["Composition", "Whole-muscle beef, salt, and only these spices if the batch sheet shows a weight: black pepper, garlic powder, onion powder, paprika. Uncured. No nitrite, no nitrate, no erythorbate, no sugar, no soy, no wheat. Not fermented. Water activity of the finished jerky: 0.85 or less. pH is not a control."],
            ["Ready-to-eat?", "Yes. The customer does not cook it. 9 CFR 417.2(a)(2)."],
            ["Where sold, and who eats it", "Household consumers, including children, older adults, and immunocompromised people. Also restaurants or stores if a lot is sold there."],
            ["Intended use", "Eaten as sold. No further cooking."],
            ["Package and storage", "Food-grade moisture-barrier bag, heat-sealed, lot code on the bag. Stored and shipped at ambient temperature. The bag stays dry. This plan does not claim a vacuum package unless the batch sheet says that bag was vacuum sealed."],
            ["Shelf life", "Unopened, not refrigerated. The number of days is written here after this plant’s own holding records support it: __________ days. The model’s example of 240 days is for the model’s cured, vacuum-packed product. It is not copied onto this jerky."],
            ["Label statements", "Product name, ingredients, net weight, name and place of business, lot code. No allergen statement, because this formula has none of the major allergens. Inspection legend and establishment number are applied when the plant is under inspection."],
            ["Special distribution controls", "None for temperature. A wet or open bag is not sold."],
            ["Process category", "Heat-treated — shelf stable. 9 CFR 417.2(b)(1)(vi). The guidebook names meat jerky as the example of this category."],
        ],
        size=8,
    )

    h2(doc, "1.4 Ingredients and incoming materials — guidebook worksheet 2")
    table(
        doc,
        ["Item", "This plant"],
        [
            ["Meat", "Inspected boneless beef, whole muscle."],
            ["Other food ingredients", "Salt. Black pepper, garlic powder, onion powder, and paprika only when the batch sheet shows a weight."],
            ["Antimicrobials and processing aids", "None."],
            ["Restricted ingredients", "None. Sodium nitrite is not used. The model’s footnote 2 says jerky may be cured or uncured and that sodium nitrite is not required."],
            ["Allergens", "None in this formula. Soy sauce is not used. The model’s example contains soy and wheat. This product does not."],
            ["Packaging", "Food-grade moisture-barrier bags."],
        ],
        size=8,
    )

    h2(doc, "1.5 Process flow — guidebook worksheet 3")
    body(doc, "9 CFR 417.2(a)(2) requires a flow chart of the steps. The order below is the plant’s order. It follows the model’s order and leaves out steps this plant does not have.")
    for step in [
        "1. Receive inspected beef. Check the mark of inspection and the product temperature.",
        "1a. Receive salt, spices, and bags. Check the specification.",
        "2. Cold storage. Product temperature below 41°F. Prerequisite, not a CCP.",
        "3. Slice. Record the thickness.",
        "4. Weigh and mix the ingredients on the batch sheet.",
        "5. Marinate in the cooler, still below 41°F. Drain. Single layer on racks. Do not stack. Do not dry before the cook.",
        "6. Cooking — CCP 1, the lethality step.",
        "7. Drying — CCP 2.",
        "8. Cool dry. Do not rinse or mist. Pack and label in the ready-to-eat area.",
        "9. Dry storage and distribution.",
        "10. Returned product, if any. Separate from the main flow. Opened bags are not reused.",
    ]:
        bullet(doc, step)
    body(doc, "The flow chart is verified by walking the plant. Name and date of that walk-through:")
    line(doc, "Name and date:")
    body(doc, "There is no metal-detector step in this flow. There is no brine step, no fermentation step, and no ingredient added after CCP 1.")

    h1(doc, "2. What was changed from the FSIS jerky model")
    table(
        doc,
        ["Model example", "This establishment"],
        [
            ["Cured with sodium nitrite and sodium erythorbate", "Uncured. No nitrite. Footnote 2 of the model allows uncured jerky."],
            ["Soy sauce, so the example has soy and wheat allergens", "No soy and no wheat. No allergen in the formula."],
            ["Sugar and a flavor mixture", "Salt and the spices named on the batch sheet only."],
            ["Vacuum-packed, 240 days", "Heat-sealed moisture-barrier bag. Shelf-life days are filled in from this plant’s records."],
            ["Cold storage prerequisite below 45°F", "Prerequisite below 41°F, which also meets the field checklist."],
            ["Metal detection, supported by that plant’s history", "Not in this plan. This plant does not have that history on file."],
            ["CCP 1 cooking and CCP 2 drying", "Same two CCPs, same limits, written in Section 5."],
        ],
        size=8,
    )

    h1(doc, "3. Principle 1 — Hazard analysis")
    body(doc, "9 CFR 417.2(a). A hazard reasonably likely to occur is one a prudent plant would control because it has happened, or because it could happen in this kind of product if it is not controlled. Hazards are biological, chemical, or physical (guidebook, Principle 1).")
    table(
        doc,
        ["Step", "Hazard", "RLTO?", "Basis", "Control", "CCP?"],
        [
            ["1 Beef receiving", "B: STEC, Salmonella", "Yes", "Raw beef can carry these pathogens. The model treats this as reasonably likely.", "Killed at CCP 1 if the cooking limits are met.", "No. Later step."],
            ["1 Beef receiving", "B: BSE prion", "No", "Inspected beef. Specified risk materials are not in this cut.", "Receiving record.", "No"],
            ["1 Beef receiving", "P: Foreign material", "No", "Containers and meat are looked at when they arrive.", "Receiving record.", "No"],
            ["1a Spices", "B: Salmonella", "Yes", "A spice can carry Salmonella. It is mixed in before the cook.", "Killed at CCP 1. Nothing is added after CCP 1.", "No. Later step."],
            ["1a Spices", "C: Allergen or nitrite", "No", "The formula has no major allergen and no nitrite. A delivery that does not match the specification is rejected.", "Batch sheet and specification.", "No"],
            ["1a Bags", "C: Not food grade", "No", "Bags are food grade, from the specification.", "Receiving record.", "No"],
            ["2 Cold storage", "B: Outgrowth", "No", "Product stays below 41°F, which is colder than the model’s 45°F prerequisite (Tompkin, 1996). The cook is not used to fix warm raw beef.", "Temperature log.", "No"],
            ["3 Slice", "B: Higher load from abuse", "No", "Slicing stays under the temperature procedure so the load is not higher than the cook is designed to reduce.", "Temperature log and thickness on the batch sheet.", "No"],
            ["3 Slice", "P: Metal from the slicer", "No", "The blade is checked before use. This decision does not rest on metal-detector history.", "Equipment check.", "No"],
            ["5 Marinate", "B: Outgrowth", "No", "Marination stays below 41°F.", "Temperature log.", "No"],
            ["6 Cooking", "B: STEC, Salmonella, L. monocytogenes", "Yes", "Raw beef may be contaminated. The model’s control is a cook that achieves at least a 5.0-log reduction of Salmonella and at least a 5.0-log reduction of STEC, with humidity so the surface does not dry first.", "CCP 1.", "Yes. CCP 1"],
            ["7 Drying", "B: C. perfringens and C. botulinum outgrowth; S. aureus toxin; L. monocytogenes during storage", "Yes", "The model: drying while water activity is still high can allow sporeformers to grow, and a finished water activity above 0.85 can allow S. aureus to grow and make toxin. L. monocytogenes can grow during storage if water activity stays at or above 0.92.", "CCP 2.", "Yes. CCP 2"],
            ["8 Pack", "B: L. monocytogenes after the cook", "No", "Sanitation and no bare-hand contact in the pack area. Growth during storage is prevented by CCP 2, because 0.85 is below 0.92. The 9 CFR 430.4 alternative and any surface-testing schedule are written in the sanitation SOP before this plan is the authority to ship.", "Sanitation log and CCP 2.", "No"],
            ["9 Storage", "B: Rehydration", "No", "Dry storage. A wet or open bag is not sold.", "Distribution log.", "No"],
            ["10 Returned product", "B: Unknown holding", "No", "Opened bags are rejected. Accepted returns are held and the FSIS office is notified.", "Return record.", "No"],
        ],
        size=7,
    )

    h1(doc, "4. Principle 2 — Why these two steps are the CCPs")
    body(doc, "The guidebook’s decision questions, applied to the two hazards that need a CCP:")
    table(
        doc,
        ["Question", "Cooking", "Drying", "Cold storage"],
        [
            ["Can a control be applied here?", "Yes. Time, temperature, and humidity.", "Yes. Oven temperature and water activity.", "Yes. Keep the meat cold."],
            ["Does this step eliminate the hazard or reduce it to an acceptable level?", "Yes. This is CCP 1.", "Yes. This is CCP 2.", "No. Cold holding does not kill the bacteria that are already there."],
            ["Will a later step do that?", "No later step replaces the cook. Drying is not a substitute for the cook.", "No later step replaces the drying limit.", "Yes. CCP 1 addresses the pathogens, if the meat was kept cold so the load did not grow."],
            ["Decision", "CCP 1", "CCP 2", "Not a CCP. Prerequisite below 41°F."],
        ],
        size=8,
    )

    h1(doc, "5. Principles 3, 4, and 5 — Limits, monitoring, corrective actions")
    body(doc, "9 CFR 417.2(c)(3) through (c)(5). Critical limits come from the FSIS jerky model, which cites Appendix A. The scientific support for each number is named in the table. 9 CFR 417.3: a deviation identifies the cause, brings the point back under control, prevents it from happening again, and keeps injurious product out of commerce.")

    h2(doc, "CCP 1 — Cooking (lethality), before drying")
    body(doc, "Hazards: STEC (O157:H7, O26, O45, O103, O111, O121, and O145), Salmonella, and Listeria monocytogenes. All of the limits below are required. Drying does not start until this CCP has passed.")
    table(
        doc,
        ["Critical limit", "Where that criterion is written", "Monitoring"],
        [
            ["Internal temperature at least 145°F for at least 4 minutes, in every part of the meat. The probe is in the thickest piece, in the coldest part of the oven. Readings are not averaged.", "Jerky model CCP 1, from Appendix A. Appendix A gives 145°F a dwell of 4 minutes for meat when humidity and come-up time are also met.", "Each lot, at the end of the cook. The monitor writes the temperature, the time it reached 145°F, and the time it had held at least 4 minutes."],
            ["Wet-bulb temperature at least 125°F for at least 1 hour.", "Jerky model CCP 1. The model also allows the plant to record this with relative humidity.", "Each lot. Start time, and the readings that show the hour was met."],
            ["Relative humidity at least 27 percent for at least 1 hour.", "Jerky model CCP 1, which points to the jerky compliance guideline’s sealed-oven example.", "Each lot, from the wet-bulb and dry-bulb readings, or from a humidity sensor. The number is written."],
            ["Oven dampers closed, and the oven sealed, for 50 percent of the cooking time or 1 hour, whichever is longer. Dampers are closed within 30 minutes after the product is placed in the heated oven.", "Jerky model CCP 1 and the hazard analysis: dampers close within 30 minutes so the surface does not dry and make Salmonella harder to kill. Appendix A Humidity Option 2 is a sealed oven for 50 percent of the cook or 1 hour, whichever is longer.", "Each lot. Time the meat went into the heated oven, time the dampers closed, and time the dampers opened."],
            ["Come-up: the internal temperature is between 50°F and 130°F for 6 hours or less.", "Appendix A, pages 23–24, which the model names as the source of the cooking limit. This option keeps Staphylococcus aureus growth to about 2-log or less and is the option that prevents enterotoxin during the come-up.", "Each lot. Time the internal temperature passed 50°F and time it passed 130°F."],
        ],
        size=7,
    )
    body(doc, "Who monitors: the trained designee, at the time of the reading. The entry has the date, the time, and the initials (9 CFR 417.5(b)).")
    body(doc, "If any CCP 1 limit is missed: the designee stops the lot and tells Jesús Canales. The lot is held. It does not go to drying and it does not ship. The cause is written. The oven is corrected before the next lot. Product that missed the cook is not sold as ready-to-eat jerky. A laboratory test is not the release step. This is the corrective action required by 9 CFR 417.3(a).")

    h2(doc, "CCP 2 — Drying, after CCP 1 has passed")
    table(
        doc,
        ["Critical limit", "Where that criterion is written", "Monitoring"],
        [
            ["Oven temperature setting at least 170°F during drying, read with the dry-bulb thermometer.", "Jerky model CCP 2. The model uses this temperature so Clostridium perfringens and Clostridium botulinum do not grow while the water activity is still above 0.93.", "Each lot. The dry-bulb reading during drying, before the jerky is taken out of the oven."],
            ["Finished water activity 0.85 or less. At least six pieces, taken from different places in the lot, including a thick piece. The highest reading is the lot result. Every piece checked is 0.85 or less.", "Jerky model CCP 2: dry to a water activity of 0.85 or less so Staphylococcus aureus does not grow and make toxin, and so Listeria monocytogenes does not grow in storage (its growth minimum is below 0.92). The model checks at least six pieces. The product-description line in the model says water activity below 0.85. This plan uses 0.85 or less, and the highest piece must not be above 0.85.", "Each lot, after drying, before packing. Calibrated water-activity meter."],
        ],
        size=7,
    )
    body(doc, "Water activity is the safety measurement. The moisture-to-protein ratio is the standard of identity for the name “jerky” (the model’s footnote 31, often 0.75:1 or less). It is checked during validation for labeling. It is not the critical limit.")
    body(doc, "If the oven is below 170°F, or if any of the six readings is above 0.85: do not pack. The lot is held. Jesús Canales is told. If CCP 1 passed, the lot may be dried longer at 170°F or above and measured again. If it still fails, it does not ship. It is not wetted and cooked again under this plan.")

    h1(doc, "6. Principle 6 — Verification")
    body(doc, "9 CFR 417.4.")
    bullet(doc, "Initial validation. The scientific support is the jerky model, Appendix A, and the pages cited above. The in-plant part is repeated lots on this oven, this load, and this thickness, showing that CCP 1 and CCP 2 were met. The validation date below stays blank until those logs have been reviewed. 9 CFR 417.4(a)(1).")
    bullet(doc, "Calibration. Product probe, dry bulb, and wet bulb on the schedule in the instrument instructions, and at least every two weeks, which is the frequency in the model. The water-activity meter is checked on its salt standard before each use.")
    bullet(doc, "Direct observation. At least once a week, Jesús Canales or the HACCP-trained person watches the monitor take a cooking reading and a water-activity reading.")
    bullet(doc, "Records review. Before the lot ships, and at least once a week for the week’s logs. 9 CFR 417.4(a)(2) and 417.5(c).")
    bullet(doc, "Reassessment. At least once a year, and when the beef source, the formula, the oven, the thickness, the package, or the intended user changes. The reassessment is done by the HACCP-trained person. The plan is signed again. 9 CFR 417.4(a)(3) and 417.2(d).")
    line(doc, "Lots reviewed for initial validation:")
    line(doc, "Oven and fullest load:")
    line(doc, "HACCP-trained person and date:")
    line(doc, "Jesús Canales and date — this is the validation date:")

    h1(doc, "7. Principle 7 — Records")
    body(doc, "9 CFR 417.5. The hazard analysis, this plan, and the support documents are kept for the life of the plan. Monitoring records for this shelf-stable product are kept for at least two years (9 CFR 417.5(e)(1)). After six months they may be stored off site if they can be back on site within 24 hours of an FSIS request. Each entry is made when the event happens and includes the date, the time, and the initials. The value written is the value read. A blank, a check mark, or the word “yes” where a number belongs is not a complete record.")
    body(doc, "Pre-shipment review, 9 CFR 417.5(c): before the lot ships, a person reviews that lot’s records, writes that every critical limit was met or that the corrective action is finished, and signs and dates the review. Where practical, that person did not produce the record. The lot does not ship until this review says it may ship.")

    h1(doc, "8. Signature — 9 CFR 417.2(d)")
    body(doc, "The responsible establishment official signs and dates this plan on first acceptance, after any change, and at least once a year at reassessment. The signature means the establishment will implement the plan. The plan is not signed until the HACCP-trained person is named and the sanitation SOP names the Listeria alternative.")
    line(doc, "Jesús Canales, responsible establishment official:")
    line(doc, "Date:")
    line(doc, "HACCP-trained person:")
    line(doc, "Date:")

    h1(doc, "9. Forms")
    h2(doc, "9.1 Cooking log — CCP 1")
    table(
        doc,
        ["Reading", "Lot result"],
        [
            ["Date, time, and lot", ""],
            ["Time the product entered the heated oven", ""],
            ["Time the dampers closed (within 30 minutes)", ""],
            ["Time the dampers opened. Sealed time is at least 1 hour or 50 percent of the cook, whichever is longer.", ""],
            ["Wet bulb at least 125°F for at least 1 hour. Write the readings.", ""],
            ["Relative humidity at least 27 percent for at least 1 hour. Write the number.", ""],
            ["Time internal temperature rose from 50°F to above 130°F. Limit: 6 hours or less.", ""],
            ["Coldest spot, thickest piece, internal °F, and the minutes it stayed at or above 145°F. Limit: at least 4 minutes.", ""],
            ["Monitor initials", ""],
        ],
        size=8,
    )

    h2(doc, "9.2 Drying log — CCP 2")
    body(doc, "Dry bulb during drying at least 170°F. Highest of at least six pieces: 0.85 or less.")
    table(
        doc,
        ["Lot", "Dry bulb °F", "aw 1", "aw 2", "aw 3", "aw 4", "aw 5", "aw 6", "Highest aw", "Initials"],
        [["", "", "", "", "", "", "", "", "", ""]],
        size=7,
    )

    h2(doc, "9.3 Cooler log — prerequisite, not a CCP")
    body(doc, "Product temperature below 41°F. Probe in the meat.")
    table(doc, ["Date / time", "Lot", "Where (receipt, cooler, marinade)", "Product °F", "Initials"], [["", "", "", "", ""]], size=8)

    h2(doc, "9.4 Pre-shipment review")
    table(
        doc,
        ["Check", "Met / Not met", "Number on the log"],
        [
            ["Product stayed below 41°F", "", ""],
            ["Dampers closed within 30 minutes and stayed closed long enough", "", ""],
            ["Wet bulb at least 125°F for at least 1 hour", "", ""],
            ["Relative humidity at least 27 percent for at least 1 hour", "", ""],
            ["Come-up 6 hours or less", "", ""],
            ["Internal at least 145°F for at least 4 minutes", "", ""],
            ["Drying dry bulb at least 170°F", "", ""],
            ["Highest of six water-activity readings 0.85 or less", "", ""],
            ["Calibration acceptable, sanitation signed", "", ""],
            ["Corrective action closed if there was a miss", "", ""],
        ],
        size=8,
    )
    line(doc, "Lot:")
    line(doc, "Reviewer, date, and time:")
    line(doc, "Ship? Yes or No:")

    h2(doc, "9.5 Corrective action")
    table(
        doc,
        ["417.3 item", "Entry"],
        [
            ["Date, time, CCP, lot, limit, and the number read", ""],
            ["Product held? Where?", ""],
            ["Cause, and what was fixed before the next lot", ""],
            ["How the CCP is back under control", ""],
            ["What will stop a repeat", ""],
            ["Disposition. No injurious product is shipped. A failed cook is not sold as jerky.", ""],
            ["Signatures: monitor and Jesús Canales", ""],
        ],
        size=8,
    )

    p(
        doc,
        "Support kept with this plan: 9 CFR Part 417; the seven FSIS guidelines named in the opening table; the jerky field verification checklist; Principles of Preservation of Shelf-Stable Dried Meat Products.",
        size=10,
        italic=True,
        before=8,
    )
    doc.save(OUT)
    print(OUT)


if __name__ == "__main__":
    build()
