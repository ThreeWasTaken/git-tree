from src.authors import get_last_author, load_author_config
from src.context import get_conflict_files, get_viewing_context
from src.fuzzy import build_fzf_source_output
from src.git_utils import get_entries
from src.search import apply_search


def print_fzf_source(
    target: str,
    search: str,
    all_mode: bool,
    staged: bool,
    last_author: bool,
    paths: list[str],
) -> None:
    conflict_files = get_conflict_files()

    entries_before_search = get_entries(
        target=target,
        paths=paths,
        staged=staged,
        all_mode=all_mode,
        conflict_files=conflict_files,
    )

    entries_after_search = apply_search(
        entries_before_search,
        search,
    )

    if last_author:
        author_config = load_author_config()

        for entry in entries_after_search:
            entry.last_author = get_last_author(
                entry.path,
                author_config,
            )

    viewing_context = get_viewing_context(
        target=target,
        staged=staged,
        all_mode=all_mode,
    )

    print(
        build_fzf_source_output(
            entries_after_search,
            search,
            all_mode,
            viewing_context,
        )
    )
