from functools import lru_cache
from pathlib import Path

from pypdf import PdfReader


REFERENCE_DIRECTORY = Path(__file__).parent / "references"

COMMUNICATION_PDF = (
    "Codebook for rating clinical communication skills based on "
    "the Calgary-Cambridge Guide.pdf"
)

CHEST_PAIN_PDF = (
    "recentonset-chest-pain-of-suspected-cardiac-origin-"
    "assessment-and-diagnosis-pdf-975751034821.pdf"
)


def read_markdown(filename):
    path = REFERENCE_DIRECTORY / filename
    return path.read_text(encoding="utf-8")


def read_pdf_pages(filename, page_numbers):
    path = REFERENCE_DIRECTORY / filename
    reader = PdfReader(path)

    sections = []

    for page_number in page_numbers:
        page = reader.pages[page_number - 1]
        text = page.extract_text() or ""

        sections.append(
            f"[Source: {filename}, PDF page {page_number}]\n{text}"
        )

    return "\n\n".join(sections)


@lru_cache(maxsize=1)
def load_references():
    return {
        "case": read_markdown("case_01_chest_pain.md"),
        "checklist": read_markdown("case_01_history_checklist.md"),
        "communication": read_pdf_pages(
            COMMUNICATION_PDF,
            page_numbers=[4, 5],
        ),
        "guideline": read_pdf_pages(
            CHEST_PAIN_PDF,
            page_numbers=[7, 8, 9, 10, 11, 12],
        ),
    }