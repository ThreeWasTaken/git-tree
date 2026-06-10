import os

from src.git_utils import run_git
from src.styles import BLUE, BOLD, RED, RESET, YELLOW


def commit_summary(
    ref: str,
    color: str | None = None,
) -> str:
    output = run_git(
        ["show", "-s", "--format=%h %s", ref],
        exit_on_error=False,
    ).strip()

    summary = output or ref

    if color:
        return f"{color}{summary}{RESET}"

    return summary


def range_summary(target: str) -> str:
    left, right = target.split("..", 1)

    if not left:
        left = "HEAD"

    if not right:
        right = "HEAD"

    return (
        f"\n  {commit_summary(left, RED)}\n"
        f"  {BOLD}..{RESET}\n"
        f"  {commit_summary(right, BLUE)}"
    )


def get_viewing_context(
    target: str,
    staged: bool,
    all_mode: bool,
) -> str:
    if all_mode:
        return "Viewing: all tracked files"

    if staged:
        return "Viewing: staged changes"

    if target == "__WORKTREE__":
        return "Viewing: worktree changes"

    if ".." in target:
        return f"Viewing:{range_summary(target)}"

    return f"Viewing: {commit_summary(target, BLUE)}"


def get_git_dir() -> str:
    return run_git(
        ["rev-parse", "--git-dir"],
        exit_on_error=False,
    ).strip()


def read_first_existing(paths: list[str]) -> str | None:
    for path in paths:
        if not os.path.isfile(path):
            continue

        try:
            with open(path, "r", encoding="utf-8") as file:
                value = file.read().strip()

            if value:
                return value

        except OSError:
            pass

    return None


def get_rebase_context() -> str | None:
    git_dir = get_git_dir()

    if not git_dir:
        return None

    rebase_merge = os.path.join(git_dir, "rebase-merge")
    rebase_apply = os.path.join(git_dir, "rebase-apply")

    if os.path.isdir(rebase_merge):
        sha = read_first_existing(
            [
                os.path.join(rebase_merge, "stopped-sha"),
                os.path.join(rebase_merge, "current"),
            ]
        )

        if sha:
            return f"Rebase: applying {commit_summary(sha, YELLOW)}"

        return "Rebase: in progress"

    if os.path.isdir(rebase_apply):
        sha = read_first_existing(
            [
                os.path.join(rebase_apply, "original-commit"),
                os.path.join(rebase_apply, "stopped-sha"),
            ]
        )

        if sha:
            return f"Rebase: applying {commit_summary(sha, YELLOW)}"

        return "Rebase: in progress"

    return None


def get_conflict_files() -> set[str]:
    output = run_git(
        ["diff", "--name-only", "--diff-filter=U"],
        exit_on_error=False,
    )

    return {
        line.strip()
        for line in output.splitlines()
        if line.strip()
    }
