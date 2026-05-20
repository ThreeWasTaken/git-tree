from typing import Any

from src.models import FileEntry


def insert(
    tree: dict[str, Any],
    parts: list[str],
    entry: FileEntry,
) -> None:

    current = tree

    for part in parts[:-1]:
        current = current.setdefault(part, {})

    current[parts[-1]] = entry


def build_tree(
    entries: list[FileEntry],
) -> dict[str, Any]:

    tree: dict[str, Any] = {}

    for entry in entries:
        insert(
            tree,
            entry.path.split("/"),
            entry,
        )

    return tree
