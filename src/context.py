import os

from src.authors import format_author, load_author_config
from src.git_utils import run_git
from src.styles import BLUE, BOLD, CYAN, MAGENTA, RED, RESET, YELLOW


def commit_hash(
    ref: str,
    color: str | None = None,
) -> str:
    output = run_git(
        ["show", "-s", "--format=%h", ref],
        exit_on_error=False,
    ).strip()

    value = output or ref

    if color:
        return f"{color}{value}{RESET}"

    return value


def commit_subject(
    ref: str,
    color: str | None = None,
) -> str:
    subject = run_git(
        ["show", "-s", "--format=%s", ref],
        exit_on_error=False,
    ).strip()

    if color and subject:
        return f"{color}{subject}{RESET}"

    return subject


def raw_commit_author(ref: str) -> tuple[str, str] | None:
    output = run_git(
        ["show", "-s", "--format=%an%x09%ar", ref],
        exit_on_error=False,
    ).strip()

    if not output:
        return None

    try:
        author, relative_date = output.split("\t", 1)
    except ValueError:
        return None

    return author, relative_date


def commit_author(ref: str) -> str:
    raw = raw_commit_author(ref)

    if raw is None:
        return ""

    author, relative_date = raw
    config = load_author_config()

    return format_author(
        author,
        relative_date,
        config,
    )


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
        f"\n  From {commit_hash(left, RED)}\n"
        f"       {commit_subject(left, RED)}\n"
        f"  {BOLD}..{RESET}\n"
        f"  To   {commit_hash(right, BLUE)}\n"
        f"       {commit_subject(right, BLUE)}"
    )


def get_viewing_context(
    target: str,
    staged: bool,
    all_mode: bool,
) -> str:
    if all_mode:
        return f"{CYAN}Viewing:{RESET} all tracked files"

    if staged:
        return f"{CYAN}Viewing:{RESET} staged changes"

    if target == "__WORKTREE__":
        return f"{CYAN}Viewing:{RESET} worktree changes"

    if ".." in target:
        return f"{CYAN}Viewing:{RESET}{range_summary(target)}"

    return (
        f"{CYAN}Viewing:{RESET} "
        f"{commit_hash(target, BLUE)}\n"
        f"  {commit_subject(target, BLUE)}"
    )


def get_author_context(
    target: str,
    staged: bool,
    all_mode: bool,
) -> str | None:
    if all_mode or staged or target == "__WORKTREE__":
        return None

    if ".." in target:
        left, right = target.split("..", 1)

        if not left:
            left = "HEAD"

        if not right:
            right = "HEAD"

        left_author = commit_author(left)
        right_author = commit_author(right)

        if not left_author and not right_author:
            return None

        return (
            f"{MAGENTA}Authors: "
            f"{left_author} "
            f"{CYAN}→{MAGENTA} "
            f"{right_author}"
            f"{RESET}"
        )

    author = commit_author(target)

    if not author:
        return None

    return f"{MAGENTA}Author: {author}{RESET}"


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
