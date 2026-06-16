import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class HistoryPosition:
    mode: str
    offset: int | None = None
    start_offset: int | None = None
    end_offset: int | None = None

def format_position(target: str) -> str:
    if target == "__WORKTREE__":
        return "worktree"

    return target

def offset_to_ref(offset: int) -> str:
    if offset == 0:
        return "HEAD"

    if offset == 1:
        return "HEAD^"

    return f"HEAD~{offset}"


def ref_exists(ref: str) -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--verify", f"{ref}^{{commit}}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )

    return result.returncode == 0


def ref_to_offset(ref: str) -> int | None:
    ref = ref.strip()

    if ref == "HEAD":
        return 0

    if ref == "HEAD^":
        return 1

    if ref.startswith("HEAD~"):
        raw = ref.removeprefix("HEAD~")

        if raw.isdigit():
            return int(raw)

    if ref.startswith("HEAD"):
        suffix = ref.removeprefix("HEAD")

        if suffix and set(suffix) == {"^"}:
            return len(suffix)

    return None


def parse_history_position(target: str) -> HistoryPosition | None:
    if target == "__WORKTREE__":
        return HistoryPosition(mode="worktree")

    if ".." in target:
        left, right = target.split("..", 1)

        if not left:
            left = "HEAD"

        if not right:
            right = "HEAD"

        start_offset = ref_to_offset(left)
        end_offset = ref_to_offset(right)

        if start_offset is None or end_offset is None:
            return None

        return HistoryPosition(
            mode="range",
            start_offset=start_offset,
            end_offset=end_offset,
        )

    offset = ref_to_offset(target)

    if offset is None:
        return None

    return HistoryPosition(
        mode="commit",
        offset=offset,
    )


def format_history_position(position: HistoryPosition) -> str:
    if position.mode == "worktree":
        return "__WORKTREE__"

    if position.mode == "commit":
        return offset_to_ref(position.offset or 0)

    if position.mode == "range":
        return (
            f"{offset_to_ref(position.start_offset or 0)}"
            f".."
            f"{offset_to_ref(position.end_offset or 0)}"
        )

    return "HEAD"


def move_left(position: HistoryPosition) -> HistoryPosition | None:
    if position.mode == "worktree":
        candidate = HistoryPosition(mode="commit", offset=0)
        return candidate if ref_exists("HEAD") else None

    if position.mode == "commit":
        next_offset = (position.offset or 0) + 1
        next_ref = offset_to_ref(next_offset)

        if not ref_exists(next_ref):
            return None

        return HistoryPosition(
            mode="commit",
            offset=next_offset,
        )

    if position.mode == "range":
        next_start = (position.start_offset or 0) + 1
        next_end = (position.end_offset or 0) + 1

        if not ref_exists(offset_to_ref(next_start)):
            return None

        if not ref_exists(offset_to_ref(next_end)):
            return None

        return HistoryPosition(
            mode="range",
            start_offset=next_start,
            end_offset=next_end,
        )

    return None


def move_right(position: HistoryPosition) -> HistoryPosition | None:
    if position.mode == "worktree":
        return None

    if position.mode == "commit":
        offset = position.offset or 0

        if offset == 0:
            return HistoryPosition(mode="worktree")

        return HistoryPosition(
            mode="commit",
            offset=offset - 1,
        )

    if position.mode == "range":
        start_offset = position.start_offset or 0
        end_offset = position.end_offset or 0

        if end_offset == 0:
            return None

        return HistoryPosition(
            mode="range",
            start_offset=start_offset - 1,
            end_offset=end_offset - 1,
        )

    return None


def previous_target(target: str) -> str | None:
    position = parse_history_position(target)

    if position is None:
        return None

    moved = move_left(position)

    if moved is None:
        return None

    return format_history_position(moved)


def next_target(target: str) -> str | None:
    position = parse_history_position(target)

    if position is None:
        return None

    moved = move_right(position)

    if moved is None:
        return None

    return format_history_position(moved)
