import os
import shlex
import shutil
import subprocess
from typing import Any

from src.models import FileEntry
from src.search import highlight_text
from src.styles import BOLD, CYAN, RESET, STATUS_COLOR, YELLOW
from src.tree_builder import build_tree


HIDDEN_SEPARATOR = "\x1f"


def get_editor_command() -> list[str]:
    editor = (
        os.environ.get("VISUAL")
        or os.environ.get("EDITOR")
        or "nano"
    )

    return shlex.split(editor)


def pluralize(
    n: int,
    singular: str,
    plural: str,
) -> str:
    return singular if n == 1 else plural


def format_file_line(
    name: str,
    entry: FileEntry,
    search: str,
    all_mode: bool,
) -> str:
    color = STATUS_COLOR.get(entry.status, RESET)

    if entry.status == "R" and entry.old_path:
        old_name = entry.old_path.split("/")[-1]
        new_name = entry.path.split("/")[-1]
        display = f"{old_name} {CYAN}→{RESET} {new_name}"
    else:
        display = name

    if search:
        display = highlight_text(display, search)

    suffix = ""

    if search:
        details = []

        if entry.content_search_count:
            details.append(f"{entry.content_search_count} contenu")

        if entry.filename_search_count:
            details.append(f"{entry.filename_search_count} nom")

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
        author_suffix = f" {CYAN}[{entry.last_author}]{RESET}"

    if all_mode and entry.status != "C":
        return (
            f"{color}{display}{RESET}"
            f"{suffix}"
            f"{author_suffix}"
        )

    return (
        f"{color}{entry.status}{RESET} "
        f"{color}{display}{RESET}"
        f"{suffix}"
        f"{author_suffix}"
    )


def build_fzf_lines(
    node: dict[str, Any],
    search: str,
    all_mode: bool,
    prefix: str = "",
) -> list[str]:
    lines = []
    items = sorted(node.items())

    for i, (name, value) in enumerate(items):
        last = i == len(items) - 1
        connector = "└── " if last else "├── "
        next_prefix = prefix + ("    " if last else "│   ")

        if isinstance(value, dict):
            display = (
                f"{prefix}{connector}"
                f"{BOLD}{name}/{RESET}"
            )

            lines.append(
                f"{display}{HIDDEN_SEPARATOR}"
            )

            lines.extend(
                build_fzf_lines(
                    value,
                    search,
                    all_mode,
                    next_prefix,
                )
            )

            continue

        entry: FileEntry = value

        display = (
            f"{prefix}{connector}"
            f"{format_file_line(name, entry, search, all_mode)}"
        )

        lines.append(
            f"{display}{HIDDEN_SEPARATOR}{entry.path}"
        )

    return lines


def build_preview_command() -> str:
    return r'''
line="$1"
path="${line##*$'\037'}"

if [ -z "$path" ]; then
  exit 0
fi

case "$GIT_TREE_PREVIEW_MODE" in
  all)
    sed -n '1,200p' "$path" 2>/dev/null
    ;;

  staged)
    git diff --cached --color=always -- "$path" 2>/dev/null
    ;;

  worktree)
    git diff --color=always HEAD -- "$path" 2>/dev/null
    ;;

  range)
    git diff --color=always "$GIT_TREE_PREVIEW_TARGET" -- "$path" 2>/dev/null
    ;;

  commit)
    git show --color=always --format= "$GIT_TREE_PREVIEW_TARGET" -- "$path" 2>/dev/null
    ;;

  *)
    git diff --color=always HEAD -- "$path" 2>/dev/null
    ;;
esac
'''


def get_preview_mode(
    target: str,
    staged: bool,
    all_mode: bool,
) -> str:
    if all_mode:
        return "all"

    if staged:
        return "staged"

    if target == "__WORKTREE__":
        return "worktree"

    if ".." in target:
        return "range"

    return "commit"


def open_with_fzf(
    entries: list[FileEntry],
    search: str,
    all_mode: bool,
    target: str,
    staged: bool,
    viewing_context: str,
) -> None:
    if not shutil.which("fzf"):
        print("git tree: fzf is not installed")
        print("Install it with: sudo apt install fzf")
        return

    if not entries:
        print("git tree: no file to select")
        return

    tree = build_tree(entries)

    lines = build_fzf_lines(
        tree,
        search,
        all_mode,
    )

    preview_mode = get_preview_mode(
        target,
        staged,
        all_mode,
    )

    env = {
        **os.environ,
        "GIT_TREE_PREVIEW_MODE": preview_mode,
        "GIT_TREE_PREVIEW_TARGET": target,
    }

    preview_command = build_preview_command()

    header = (
        f"{viewing_context}\n"
        f"{len(entries)} files"
    )

    fzf_command = [
        "fzf",
        "--ansi",
        "--prompt",
        "git-tree> ",
        "--height",
        "90%",
        "--border",
        "--layout",
        "reverse",
        "--header",
        header,
        "--delimiter",
        HIDDEN_SEPARATOR,
        "--with-nth",
        "1",
        "--preview",
        f"bash -c {shlex.quote(preview_command)} _ {{}}",
        "--preview-window",
        "right:60%:wrap",
    ]

    result = subprocess.run(
        fzf_command,
        input="\n".join(lines),
        stdout=subprocess.PIPE,
        text=True,
        env=env,
    )

    selected = result.stdout.strip()

    if not selected:
        return

    path = selected.split(HIDDEN_SEPARATOR)[-1]

    if not path:
        return

    editor_command = get_editor_command()

    subprocess.run([
        *editor_command,
        path,
    ])
