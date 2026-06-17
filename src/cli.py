import argparse
import sys

from src.authors import get_last_author, load_author_config
from src.context import (
    get_author_context,
    get_conflict_files,
    get_rebase_context,
    get_viewing_context,
)
from src.fuzzy import open_with_fzf
from src.fzf_source import print_fzf_source
from src.git_utils import get_entries
from src.history_nav import next_target, previous_target
from src.render import print_context, print_summary, print_tree
from src.search import apply_search
from src.tree_builder import build_tree


def normalize_short_flags(
    argv: list[str],
) -> list[str]:

    normalized = []
    i = 0

    while i < len(argv):
        arg = argv[i]

        if (
            arg.startswith("-")
            and not arg.startswith("--")
            and len(arg) > 2
        ):
            chars = arg[1:]
            valid = {
                "a",
                "s",
                "v",
                "l",
            }

            if all(char in valid for char in chars):
                for char in chars:
                    normalized.append(f"-{char}")

                    if (
                        char == "s"
                        and i + 1 < len(argv)
                    ):
                        normalized.append(argv[i + 1])
                        i += 1

                i += 1
                continue

        normalized.append(arg)
        i += 1

    return normalized


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="git tree",
        description="Display Git files as a colored tree.",
        add_help=False,
    )

    parser.add_argument(
        "args",
        nargs="*",
        help="commit/range and optional paths",
    )

    parser.add_argument(
        "-h",
        "--help",
        action="store_true",
        dest="help",
    )

    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="show/search all tracked files",
    )

    parser.add_argument(
        "-s",
        "--search",
        metavar="STRING",
        help="search in file contents and names",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="show matching lines",
    )

    parser.add_argument(
        "-l",
        "--last-author",
        action="store_true",
        help="show last author",
    )

    parser.add_argument(
        "--legend",
        action="store_true",
        help="show status legend",
    )

    parser.add_argument(
        "--staged",
        action="store_true",
        help="show staged files",
    )

    parser.add_argument(
        "--fzf",
        action="store_true",
        help="select a file with fzf and open it in $VISUAL/$EDITOR",
    )

    parser.add_argument(
        "--fzf-source",
        metavar="TARGET",
        help=argparse.SUPPRESS,
    )

    parser.add_argument(
        "--history-prev",
        metavar="TARGET",
        help=argparse.SUPPRESS,
    )

    parser.add_argument(
        "--history-next",
        metavar="TARGET",
        help=argparse.SUPPRESS,
    )

    parsed = parser.parse_args(
        normalize_short_flags(sys.argv[1:])
    )

    if parsed.help:
        print_help()
        sys.exit(0)

    return parsed


def print_help() -> None:
    print(
        """usage:
  git tree
  git tree HEAD
  git tree HEAD~3..HEAD
  git tree <commit> [path...]
  git tree --staged
  git tree --all
  git tree -s <string>
  git tree -as <string>
  git tree -asv <string>
  git tree -asvl <string>
  git tree --fzf

examples:
  git tree
  git tree HEAD^
  git tree HEAD~5..HEAD
  git tree --staged
  git tree HEAD src/
  git tree HEAD -- app/components
  git tree --all
  git tree --all src/
  git tree -s TODO
  git tree HEAD -s TODO
  git tree -as "*.php"
  git tree -asv TODO
  git tree -asvl "*.png"
  git tree HEAD --fzf
  git tree -as "*.php" --fzf
  git tree --legend
"""
    )


def split_target_and_paths(
    raw_args: list[str],
    staged: bool,
) -> tuple[str, list[str]]:

    if staged:
        return "HEAD", raw_args

    if not raw_args:
        return "__WORKTREE__", []

    return raw_args[0], raw_args[1:]


def main() -> None:
    options = parse_args()

    if options.history_prev:
        target = previous_target(options.history_prev)

        if target:
            print(target)

        return

    if options.history_next:
        target = next_target(options.history_next)

        if target:
            print(target)

        return

    if options.fzf_source:
        print_fzf_source(
            target=options.fzf_source,
            search=options.search or "",
            all_mode=options.all,
            staged=options.staged,
            last_author=options.last_author,
            paths=options.args,
        )
        return

    target, paths = split_target_and_paths(
        options.args,
        options.staged,
    )

    conflict_files = get_conflict_files()

    viewing_context = get_viewing_context(
        target=target,
        staged=options.staged,
        all_mode=options.all,
    )

    author_context = get_author_context(
        target=target,
        staged=options.staged,
        all_mode=options.all,
    )

    rebase_context = get_rebase_context()

    entries_before_search = get_entries(
        target=target,
        paths=paths,
        staged=options.staged,
        all_mode=options.all,
        conflict_files=conflict_files,
    )

    entries_after_search = apply_search(
        entries_before_search,
        options.search or "",
    )

    if (
        options.search
        and not entries_after_search
    ):
        from src.styles import BOLD, CYAN, RESET, YELLOW

        print_context(
            viewing_context=viewing_context,
            author_context=author_context,
            rebase_context=rebase_context,
            conflict_files=conflict_files,
        )

        print(
            f"{CYAN}No occurrence found for "
            f"{YELLOW}{BOLD}{options.search}{RESET}"
        )

        sys.exit(0)

    if options.last_author:
        author_config = load_author_config()

        for entry in entries_after_search:
            entry.last_author = get_last_author(
                entry.path,
                author_config,
            )

    if options.fzf:
        open_with_fzf(
            entries_after_search,
            options.search or "",
            options.all,
            target,
            options.staged,
            viewing_context,
            author_context,
            options.last_author,
            paths,
        )
        return

    tree = build_tree(
        entries_after_search
    )

    print_context(
        viewing_context=viewing_context,
        author_context=author_context,
        rebase_context=rebase_context,
        conflict_files=conflict_files,
    )

    print_tree(
        tree,
        options.search or "",
        options.verbose,
        options.all,
    )

    print_summary(
        entries_before_search,
        entries_after_search,
        options.search or "",
        options.all,
        options.legend,
    )
