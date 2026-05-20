import fnmatch
import os
import re

from src.models import FileEntry
from src.styles import BOLD, RESET, YELLOW


def highlight_text(
    text: str,
    needle: str,
) -> str:

    if not needle:
        return text

    if "*" in needle or "?" in needle:
        return text

    pattern = re.compile(
        re.escape(needle),
        re.IGNORECASE,
    )

    return pattern.sub(
        lambda m: (
            f"{YELLOW}{BOLD}"
            f"{m.group(0)}"
            f"{RESET}"
        ),
        text,
    )


def search_file(
    path: str,
    needle: str,
) -> tuple[int, list[tuple[int, str]]]:

    if (
        not needle
        or not os.path.isfile(path)
    ):
        return 0, []

    if "*" in needle or "?" in needle:
        return 0, []

    count = 0

    lines: list[tuple[int, str]] = []

    pattern = re.compile(
        re.escape(needle),
        re.IGNORECASE,
    )

    try:
        with open(
            path,
            "r",
            encoding="utf-8",
            errors="replace",
        ) as file:

            for number, line in enumerate(
                file,
                1,
            ):
                matches = len(
                    pattern.findall(line)
                )

                if not matches:
                    continue

                count += matches

                cleaned = line.rstrip("\n")

                highlighted = pattern.sub(
                    lambda m: (
                        f"{YELLOW}{BOLD}"
                        f"{m.group(0)}"
                        f"{RESET}"
                    ),
                    cleaned,
                )

                lines.append(
                    (
                        number,
                        highlighted,
                    )
                )

    except OSError:
        return 0, []

    return count, lines


def filename_match_count(
    path: str,
    needle: str,
) -> int:

    if not needle:
        return 0

    basename = os.path.basename(path).lower()

    lowered = needle.lower()

    if "*" in needle or "?" in needle:
        return (
            1
            if fnmatch.fnmatch(
                basename,
                lowered,
            )
            else 0
        )

    return len(
        re.findall(
            re.escape(needle),
            path,
            flags=re.IGNORECASE,
        )
    )


def apply_search(
    entries: list[FileEntry],
    needle: str,
) -> list[FileEntry]:

    if not needle:
        return entries

    kept: list[FileEntry] = []

    for entry in entries:
        content_count, lines = search_file(
            entry.path,
            needle,
        )

        name_count = filename_match_count(
            entry.path,
            needle,
        )

        entry.content_search_count = content_count
        entry.filename_search_count = name_count
        entry.search_count = (
            content_count + name_count
        )

        entry.search_lines = lines

        if entry.search_count > 0:
            kept.append(entry)

    return kept
