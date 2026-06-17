from typing import Any

from src.models import FileEntry
from src.search import highlight_text
from src.styles import (
    BLUE,
    BOLD,
    CYAN,
    GREEN,
    MAGENTA,
    RED,
    RESET,
    STATUS_COLOR,
    YELLOW,
)


def pluralize(
    n: int,
    singular: str,
    plural: str,
) -> str:
    return singular if n == 1 else plural


def print_match_lines(
    lines: list[tuple[int, str]],
    prefix: str,
) -> None:

    for i, (number, content) in enumerate(lines):
        last = i == len(lines) - 1
        connector = "└── " if last else "├── "

        print(
            f"{prefix}{connector}"
            f"{CYAN}{number}:{RESET} "
            f"{content}"
        )


def print_context(
    viewing_context: str,
    author_context: str | None,
    rebase_context: str | None,
    conflict_files: set[str],
) -> None:

    print(f"{BOLD}{viewing_context}{RESET}")

    if author_context:
        print(author_context)

    if rebase_context:
        print(f"{YELLOW}{rebase_context}{RESET}")

    if conflict_files:
        print(
            f"{YELLOW}{len(conflict_files)} "
            f"{pluralize(len(conflict_files), 'conflict', 'conflicts')}"
            f"{RESET}"
        )

    print()

def print_tree(
    node: dict[str, Any],
    search: str,
    verbose: bool,
    all_mode: bool,
    prefix: str = "",
) -> None:

    items = sorted(node.items())

    for i, (name, value) in enumerate(items):
        last = i == len(items) - 1
        connector = "└── " if last else "├── "
        next_prefix = prefix + ("    " if last else "│   ")

        if isinstance(value, dict):
            print(
                f"{prefix}{connector}"
                f"{BOLD}{name}/{RESET}"
            )

            print_tree(
                value,
                search,
                verbose,
                all_mode,
                next_prefix,
            )

            continue

        entry: FileEntry = value
        color = STATUS_COLOR.get(entry.status, RESET)

        if entry.status == "R" and entry.old_path:
            old_name = entry.old_path.split("/")[-1]
            new_name = entry.path.split("/")[-1]
            display = f"{old_name} {CYAN}→{RESET} {new_name}"

        else:
            display = name

        if search:
            display = highlight_text(
                display,
                search,
            )

        suffix = ""

        if search:
            details = []

            if entry.content_search_count:
                details.append(
                    f"{entry.content_search_count} contenu"
                )

            if entry.filename_search_count:
                details.append(
                    f"{entry.filename_search_count} nom"
                )

            details_text = ", ".join(details)

            suffix = (
                f" {CYAN}("
                f"{entry.search_count} "
                f"{pluralize(entry.search_count, 'occurrence', 'occurrences')} "
                f"de {YELLOW}{BOLD}{search}{RESET}"
            )

            if details_text:
                suffix += f"{CYAN}: {details_text}"

            suffix += f"{CYAN}){RESET}"

        author_suffix = ""

        if entry.last_author:
            author_suffix = (
                f" {CYAN}[{entry.last_author}]{RESET}"
            )

        if all_mode and entry.status != "C":
            print(
                f"{prefix}{connector}"
                f"{color}{display}{RESET}"
                f"{suffix}"
                f"{author_suffix}"
            )

        else:
            print(
                f"{prefix}{connector}"
                f"{color}{entry.status}{RESET} "
                f"{color}{display}{RESET}"
                f"{suffix}"
                f"{author_suffix}"
            )

        if (
            search
            and verbose
            and entry.search_lines
        ):
            print_match_lines(
                entry.search_lines,
                next_prefix,
            )


def print_summary(
    entries_before_search: list[FileEntry],
    entries_after_search: list[FileEntry],
    search: str,
    all_mode: bool,
    show_legend: bool,
) -> None:

    summary = {
        "A": 0,
        "M": 0,
        "D": 0,
        "R": 0,
        "C": 0,
    }

    for entry in entries_before_search:
        if entry.status in summary:
            summary[entry.status] += 1

    total = len(entries_before_search)

    search_total = sum(
        entry.search_count
        for entry in entries_after_search
    )

    print()

    if all_mode:
        print(
            f"{BOLD}{total} files scanned{RESET}"
        )

    else:
        print(
            f"{BOLD}{total} files changed{RESET}: "
            f"{GREEN}{summary['A']} added{RESET}, "
            f"{BLUE}{summary['M']} modified{RESET}, "
            f"{RED}{summary['D']} deleted{RESET}, "
            f"{MAGENTA}{summary['R']} renamed{RESET}, "
            f"{YELLOW}{summary['C']} conflicts{RESET}"
        )

    if search:
        print(
            f"{CYAN}{search_total} "
            f"{pluralize(search_total, 'occurrence', 'occurrences')} "
            f"de {YELLOW}{BOLD}{search}{RESET}"
        )

    if show_legend and not all_mode:
        print()

        print(
            f"Legend: "
            f"{GREEN}A added{RESET}  "
            f"{BLUE}M modified{RESET}  "
            f"{RED}D deleted{RESET}  "
            f"{MAGENTA}R renamed{RESET}  "
            f"{YELLOW}C conflict{RESET}"
        )
