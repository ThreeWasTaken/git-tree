import os
import subprocess


def load_author_config() -> dict[str, dict[str, str]]:
    config_path = os.path.expanduser(
        "~/.config/git-tree/authors.conf"
    )

    config = {
        "aliases": {},
        "icons": {},
    }

    if not os.path.isfile(config_path):
        return config

    current_section = None

    try:
        with open(
            config_path,
            "r",
            encoding="utf-8",
        ) as file:

            for raw_line in file:
                line = raw_line.strip()

                if (
                    not line
                    or line.startswith("#")
                ):
                    continue

                if line == "[aliases]":
                    current_section = "aliases"
                    continue

                if line == "[icons]":
                    current_section = "icons"
                    continue

                if (
                    current_section
                    and "=" in line
                ):
                    key, value = line.split("=", 1)

                    config[current_section][
                        key.strip()
                    ] = value.strip()

    except OSError:
        return config

    return config


def format_author(
    raw_author: str,
    relative_date: str,
    config: dict[str, dict[str, str]],
) -> str:

    aliases = config["aliases"]
    icons = config["icons"]

    display_name = aliases.get(
        raw_author,
        raw_author,
    )

    icon = icons.get(display_name, "")

    if icon:
        return (
            f"{icon} "
            f"{display_name} "
            f"• "
            f"{relative_date}"
        )

    return (
        f"{display_name} "
        f"• "
        f"{relative_date}"
    )


def get_last_author(
    path: str,
    config: dict[str, dict[str, str]],
) -> str:

    try:
        result = subprocess.run(
            [
                "git",
                "log",
                "-1",
                "--format=%an%x09%ar",
                "--",
                path,
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )

        output = result.stdout.strip()

        if not output:
            return "unknown"

        raw_author, relative_date = output.split(
            "\t",
            1,
        )

        return format_author(
            raw_author,
            relative_date,
            config,
        )

    except (
        subprocess.CalledProcessError,
        ValueError,
    ):
        return "unknown"
