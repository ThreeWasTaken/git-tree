from src.git_utils import run_git


def get_author_commits(
    author: str,
) -> list[str]:
    output = run_git(
        [
            "log",
            "--author",
            author,
            "--format=%H",
        ],
        exit_on_error=False,
    )

    return [
        line
        for line in output.splitlines()
        if line.strip()
    ]

def get_author_target(
    commits: list[str],
    index: int,
) -> str | None:
    if index < 0 or index >= len(commits):
        return None

    return commits[index]


def get_author_position(
    commits: list[str],
    target: str,
) -> tuple[int, int] | None:
    if target not in commits:
        return None

    raw_index = commits.index(target)

    # commits are newest -> oldest from git log.
    # Display should be oldest = 1, newest = total.
    position = len(commits) - raw_index
    total = len(commits)

    return position, total


def get_previous_author_target(
    commits: list[str],
    target: str,
) -> str | None:
    if target not in commits:
        return None

    index = commits.index(target)

    if index + 1 >= len(commits):
        return None

    return commits[index + 1]


def get_next_author_target(
    commits: list[str],
    target: str,
) -> str | None:
    if target not in commits:
        return None

    index = commits.index(target)

    if index == 0:
        return None

    return commits[index - 1]
