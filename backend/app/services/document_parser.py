import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedSection:
    name: str
    text: str


@dataclass(frozen=True)
class TextChunk:
    section: str
    chunk_index: int
    text: str


KNOWN_SECTIONS = {
    "summary",
    "symptoms",
    "impact",
    "root cause",
    "root_cause",
    "cause",
    "solution",
    "resolution",
    "prevention",
    "checks",
    "verification",
    "rollback",
    "mitigation",
    "notes",
}


def normalize_section_name(name: str) -> str:
    normalized = name.strip().lower()

    normalized = re.sub(
        r"[^a-z0-9]+",
        "_",
        normalized,
    )

    return normalized.strip("_") or "content"


def _detect_heading(
    line: str,
) -> tuple[str, str] | None:

    stripped = line.strip()

    if not stripped:
        return None

    markdown_match = re.match(
        r"^#{1,6}\s+(.+?)\s*$",
        stripped,
    )

    if markdown_match:
        heading = markdown_match.group(1)

        return (
            normalize_section_name(heading),
            "",
        )

    colon_match = re.match(
        r"^([A-Za-z][A-Za-z0-9 _/-]{1,40}):\s*(.*)$",
        stripped,
    )

    if colon_match:
        heading = colon_match.group(1).strip()
        remainder = colon_match.group(2).strip()

        if heading.lower() in KNOWN_SECTIONS:
            return (
                normalize_section_name(heading),
                remainder,
            )

    return None


def parse_sections(
    text: str,
) -> list[ParsedSection]:

    lines = text.replace(
        "\r\n",
        "\n",
    ).split("\n")

    sections: list[ParsedSection] = []

    current_section = "content"
    buffer: list[str] = []


    def flush() -> None:
        nonlocal buffer

        content = "\n".join(
            buffer
        ).strip()

        if content:
            sections.append(
                ParsedSection(
                    name=current_section,
                    text=content,
                )
            )

        buffer = []


    for line in lines:
        heading = _detect_heading(line)

        if heading is not None:
            flush()

            current_section = heading[0]

            if heading[1]:
                buffer.append(
                    heading[1]
                )

            continue

        buffer.append(line)

    flush()

    if not sections and text.strip():
        sections.append(
            ParsedSection(
                name="content",
                text=text.strip(),
            )
        )

    return sections


def chunk_sections(
    sections: list[ParsedSection],
    *,
    max_chars: int = 1200,
    overlap_chars: int = 150,
) -> list[TextChunk]:

    chunks: list[TextChunk] = []

    chunk_index = 0

    for section in sections:
        text = section.text.strip()

        if not text:
            continue

        start = 0

        while start < len(text):
            end = min(
                start + max_chars,
                len(text),
            )

            if end < len(text):
                search_start = max(
                    start,
                    end - 250,
                )

                boundary_candidates = [
                    text.rfind(
                        "\n",
                        search_start,
                        end,
                    ),
                    text.rfind(
                        ". ",
                        search_start,
                        end,
                    ),
                    text.rfind(
                        " ",
                        search_start,
                        end,
                    ),
                ]

                best_boundary = max(
                    boundary_candidates
                )

                if best_boundary > start:
                    end = best_boundary + 1

            chunk_text = text[
                start:end
            ].strip()

            if chunk_text:
                chunks.append(
                    TextChunk(
                        section=section.name,
                        chunk_index=chunk_index,
                        text=chunk_text,
                    )
                )

                chunk_index += 1

            if end >= len(text):
                break

            next_start = max(
                end - overlap_chars,
                start + 1,
            )

            start = next_start

    return chunks