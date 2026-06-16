import os
import shlex
import shutil
import subprocess
import sys
import tempfile
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


def build_fzf_header(
    viewing_context: str,
    file_count: int,
    author_context: str | None,
    position_context: str,
) -> list[str]:
    lines = viewing_context.splitlines()

    if author_context:
        lines.extend(author_context.splitlines())

    lines.append(
        f"\033[33;1mPosition: {position_context}\033[0m"
    )

    lines.append("")
    lines.append(f"{file_count} files")
    lines.append("← older    → newer    Enter open    Esc quit")

    return lines


def build_fzf_source_output(
    entries: list[FileEntry],
    search: str,
    all_mode: bool,
    viewing_context: str,
    author_context: str | None,
    position_context: str,
) -> tuple[str, int]:
    tree = build_tree(entries)

    header_lines = build_fzf_header(
        viewing_context,
        len(entries),
        author_context,
        position_context,
    )

    tree_lines = build_fzf_lines(
        tree,
        search,
        all_mode,
    )

    output = "\n".join(
        [
            *header_lines,
            *tree_lines,
        ]
    )

    return output, len(header_lines)


def build_preview_command() -> str:
    return r'''
repo_root="$(git rev-parse --show-toplevel 2>/dev/null)"
if [ -n "$repo_root" ]; then
  cd "$repo_root" || exit 0
fi
line="$1"
path="${line##*$'\037'}"

if [ -z "$path" ]; then
  exit 0
fi

target="$(cat "$GIT_TREE_FZF_TARGET_FILE" 2>/dev/null)"

if [ "$GIT_TREE_PREVIEW_ALL" = "1" ]; then
  mode="all"
elif [ "$GIT_TREE_PREVIEW_STAGED" = "1" ]; then
  mode="staged"
elif [ "$target" = "__WORKTREE__" ]; then
  mode="worktree"
elif printf "%s" "$target" | grep -q "\.\."; then
  mode="range"
else
  mode="commit"
fi

filename="$(basename "$path")"

if [ "$mode" = "staged" ]; then
  stats="$(git diff --cached --numstat -- "$path" 2>/dev/null | awk '{print $1 " " $2}')"
elif [ "$mode" = "range" ]; then
  stats="$(git diff --numstat "$target" -- "$path" 2>/dev/null | awk '{print $1 " " $2}')"
elif [ "$mode" = "commit" ]; then
  stats="$(git show --numstat --format= "$target" -- "$path" 2>/dev/null | awk '{print $1 " " $2}')"
else
  stats="$(git diff --numstat HEAD -- "$path" 2>/dev/null | awk '{print $1 " " $2}')"
fi

added="$(printf "%s" "$stats" | awk '{print $1}')"
deleted="$(printf "%s" "$stats" | awk '{print $2}')"

printf "\033[33;1m%s\033[0m" "$filename"

if [ -n "$added" ] && [ -n "$deleted" ]; then
  printf "  \033[32m+%s\033[0m \033[31m-%s\033[0m" "$added" "$deleted"
fi

printf "\n\n"

case "$mode" in
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
    git diff --color=always "$target" -- "$path" 2>/dev/null
    ;;

  commit)
    git show --color=always --format= "$target" -- "$path" 2>/dev/null
    ;;

  *)
    git diff --color=always HEAD -- "$path" 2>/dev/null
    ;;
esac
'''


def build_fzf_source_command(
    executable: str,
    target_file: str,
    search: str,
    all_mode: bool,
    staged: bool,
    last_author: bool,
    paths: list[str],
) -> str:
    command_parts = [
        shlex.quote(executable),
        "--fzf-source",
        '"$target"',
    ]

    if all_mode:
        command_parts.append("--all")

    if staged:
        command_parts.append("--staged")

    if last_author:
        command_parts.append("--last-author")

    if search:
        command_parts.append("--search")
        command_parts.append(shlex.quote(search))

    for path in paths:
        command_parts.append(shlex.quote(path))

    script = (
        f'target="$(cat {shlex.quote(target_file)})"; '
        f'{" ".join(command_parts)}'
    )

    return f"bash -c {shlex.quote(script)}"


def build_move_command(
    executable: str,
    direction: str,
    target_file: str,
) -> str:
    helper = "--history-prev" if direction == "left" else "--history-next"

    script = (
        f'next="$({shlex.quote(executable)} {helper} "$(cat {shlex.quote(target_file)})")"; '
        f'if [ -n "$next" ]; then '
        f'printf "%s" "$next" > {shlex.quote(target_file)}; '
        f'fi'
    )

    return f"bash -c {shlex.quote(script)}"


def open_with_fzf(
    entries: list[FileEntry],
    search: str,
    all_mode: bool,
    target: str,
    staged: bool,
    viewing_context: str,
    author_context: str | None,
    last_author: bool,
    paths: list[str],
) -> None:
    if not shutil.which("fzf"):
        print("git tree: fzf is not installed")
        print("Install it with: sudo apt install fzf")
        return

    executable = sys.argv[0]

    position_context = "worktree" if target == "__WORKTREE__" else target

    source_output, header_line_count = build_fzf_source_output(
        entries,
        search,
        all_mode,
        viewing_context,
        author_context,
        position_context,
    )

    preview_command = build_preview_command()

    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        delete=False,
    ) as target_file:
        target_file.write(target)
        target_file_path = target_file.name

    try:
        source_command = build_fzf_source_command(
            executable=executable,
            target_file=target_file_path,
            search=search,
            all_mode=all_mode,
            staged=staged,
            last_author=last_author,
            paths=paths,
        )

        left_command = build_move_command(
            executable,
            "left",
            target_file_path,
        )

        right_command = build_move_command(
            executable,
            "right",
            target_file_path,
        )

        env = {
            **os.environ,
            "GIT_TREE_PREVIEW_ALL": "1" if all_mode else "0",
            "GIT_TREE_PREVIEW_STAGED": "1" if staged else "0",
            "GIT_TREE_FZF_TARGET_FILE": target_file_path,
        }

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
            "--header-lines",
            str(header_line_count),
            "--delimiter",
            HIDDEN_SEPARATOR,
            "--with-nth",
            "1",
            "--preview",
            f"bash -c {shlex.quote(preview_command)} _ {{}}",
            "--preview-window",
            "right:60%:wrap",
            "--bind",
            f"left:execute-silent({left_command})+reload({source_command})",
            "--bind",
            f"right:execute-silent({right_command})+reload({source_command})",
        ]

        result = subprocess.run(
            fzf_command,
            input=source_output,
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

    finally:
        try:
            os.unlink(target_file_path)
        except OSError:
            pass
