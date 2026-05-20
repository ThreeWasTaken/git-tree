from dataclasses import dataclass, field


@dataclass
class FileEntry:
    status: str
    path: str
    old_path: str | None = None
    search_count: int = 0
    content_search_count: int = 0
    filename_search_count: int = 0
    search_lines: list[tuple[int, str]] = field(default_factory=list)
    last_author: str | None = None
