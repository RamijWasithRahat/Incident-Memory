from app.services.document_parser import (
    chunk_sections,
    parse_sections,
)


def test_markdown_sections_are_detected() -> None:
    text = """
## Symptoms

API requests are slow.

## Root Cause

Connection pool exhaustion.

## Solution

Increase pool capacity.
"""

    sections = parse_sections(text)

    names = [
        section.name
        for section in sections
    ]

    assert names == [
        "symptoms",
        "root_cause",
        "solution",
    ]


def test_txt_style_sections_are_detected() -> None:
    text = """
Symptoms:
Database timeout errors.

Root Cause:
Connection pool exhaustion.

Resolution:
Reduce worker concurrency.
"""

    sections = parse_sections(text)

    assert [
        section.name
        for section in sections
    ] == [
        "symptoms",
        "root_cause",
        "resolution",
    ]


def test_long_section_creates_multiple_chunks() -> None:
    text = "A" * 3000

    sections = parse_sections(text)

    chunks = chunk_sections(
        sections,
        max_chars=1000,
        overlap_chars=100,
    )

    assert len(chunks) > 1

    assert all(
        chunk.section == "content"
        for chunk in chunks
    )