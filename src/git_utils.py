import subprocess
import sys

from src.models import FileEntry


def run_git(
    args: list[str],
    exit_on_error: bool = True,
) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        return result.stdout

    except subprocess.CalledProcessError as exc:
        if exit_on_error:
            print(exc.stderr.strip(), file=sys.stderr)
            sys.exit(exc.returncode)

        return ""


def parse_entries(
    output: str,
    conflict_files: set[str],
) -> list[FileEntry]:

    entries: list[FileEntry] = []
    seen_paths: set[str] = set()

    for line in output.splitlines():
        if not line.strip():
            continue

        cols = line.split("\t")
        raw_status = cols[0]

        if raw_status.startswith("R"):
            path = cols[2]

            status = (
                "C"
                if path in conflict_files
                else "R"
            )

            entries.append(
                FileEntry(
                    status=status,
                    old_path=cols[1],
                    path=path,
                )
            )

            seen_paths.add(path)
            continue

        path = cols[-1]
        status = raw_status[0]

        if (
            path in conflict_files
            or "U" in raw_status
        ):
            status = "C"

        entries.append(
            FileEntry(
                status=status,
                path=path,
            )
        )

        seen_paths.add(path)

    for conflict_path in conflict_files:
        if conflict_path not in seen_paths:
            entries.append(
                FileEntry(
                    status="C",
                    path=conflict_path,
                )
            )

    return entries


def get_entries(
    target: str,
    paths: list[str],
    staged: bool,
    all_mode: bool,
    conflict_files: set[str],
) -> list[FileEntry]:

    if all_mode:
        output = run_git(
            ["ls-files", "--", *paths]
        )

        return [
            FileEntry(
                status=(
                    "C"
                    if line in conflict_files
                    else "T"
                ),
                path=line,
            )
            for line in output.splitlines()
            if line.strip()
        ]

    if staged:
        output = run_git(
            [
                "diff",
                "--cached",
                "--name-status",
                "--",
                *paths,
            ]
        )

    elif target == "__WORKTREE__":
        output = run_git(
            [
                "diff",
                "--name-status",
                "HEAD",
                "--",
                *paths,
            ]
        )

    elif ".." in target:
        output = run_git(
            [
                "diff",
                "--name-status",
                target,
                "--",
                *paths,
            ]
        )

    else:
        output = run_git(
            [
                "diff-tree",
                "--no-commit-id",
                "--name-status",
                "-r",
                target,
                "--",
                *paths,
            ]
        )

    return parse_entries(
        output,
        conflict_files,
    )
