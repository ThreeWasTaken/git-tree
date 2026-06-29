from dataclasses import dataclass


@dataclass(frozen=True)
class NavigationState:
    target: str
    history_position: int | None = None
    history_total: int | None = None


def format_position(target: str) -> str:
    if target == "__WORKTREE__":
        return "worktree"

    return target
