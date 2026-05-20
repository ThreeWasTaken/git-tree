# Project Structure

`git-tree` is split into small modules so each file has a clear responsibility.

```text
git-tree/
├── git-tree
├── README.md
├── STRUCTURE.md
├── .gitignore
└── src/
    ├── __init__.py
    ├── authors.py
    ├── cli.py
    ├── context.py
    ├── git_utils.py
    ├── models.py
    ├── render.py
    ├── search.py
    ├── styles.py
    └── tree_builder.py
```

## Root files

### `git-tree`

Executable entrypoint.

It only imports and runs:

```python
from src.cli import main
```

This keeps the executable file small and lets the real logic live in `src/`.

### `README.md`

User-facing documentation:

- installation
- usage
- examples
- options
- author icons configuration

### `STRUCTURE.md`

Developer-facing documentation explaining the internal project layout.

### `.gitignore`

Ignores Python cache files:

```gitignore
__pycache__/
*.py[cod]
```

---

# `src/` package

## `src/__init__.py`

Package marker and version metadata.

```python
__version__ = "0.1.0"
```

---

## `src/cli.py`

Main orchestration layer.

Responsibilities:

- parse CLI arguments
- normalize combined short flags like `-asvl`
- decide target/path mode
- call Git data collection
- call search filtering
- call author enrichment
- call tree building
- call rendering

This is the main control flow of the application.

---

## `src/git_utils.py`

Git command integration.

Responsibilities:

- run Git commands
- collect file entries for:
  - worktree changes
  - commits
  - ranges
  - staged files
  - all tracked files
- parse Git `--name-status` output
- mark conflicted files as `C`

This file is the bridge between Git and the internal `FileEntry` model.

---

## `src/models.py`

Shared data structures.

Currently contains:

```python
FileEntry
```

A `FileEntry` represents one file displayed by `git-tree`.

It stores:

- status (`A`, `M`, `D`, `R`, `C`, `T`)
- path
- old path for renames
- search counts
- matching lines
- last author information

---

## `src/context.py`

Git context detection.

Responsibilities:

- build the `Viewing:` line
- summarize commits and ranges
- color old/new commits in ranges
- detect ongoing rebase
- detect conflicted files

Examples:

```text
Viewing: worktree changes
Viewing: old_commit .. new_commit
Rebase: applying abc123 commit message
```

---

## `src/search.py`

Search logic.

Responsibilities:

- search inside file contents
- search inside file names
- support glob patterns like `*.php`
- highlight matching text
- filter entries when `--search` is used

Notes:

- glob searches apply to filenames
- plain text searches apply to filenames and file contents

---

## `src/authors.py`

Author enrichment.

Responsibilities:

- read optional config from:

```text
~/.config/git-tree/authors.conf
```

- map raw Git author names to aliases
- map aliases to icons
- fetch last author information with Git
- format author display

Example output:

```text
[🎩 user-a • 2 hours ago]
```

If no config exists, raw Git author names are used.

---

## `src/tree_builder.py`

Tree construction.

Responsibilities:

- convert flat file paths into a nested tree structure
- insert `FileEntry` objects into that tree

Example:

```text
src/foo/bar.py
```

becomes:

```text
src/
└── foo/
    └── bar.py
```

---

## `src/render.py`

Terminal rendering.

Responsibilities:

- print the context header
- render the tree
- color statuses
- display search occurrences
- display verbose matching lines
- display author suffixes
- print summary statistics
- optionally print the status legend

This file owns all terminal output formatting.

---

## `src/styles.py`

Shared ANSI styles.

Contains color constants like:

```python
GREEN
BLUE
RED
YELLOW
RESET
```

and status-to-color mapping:

```python
STATUS_COLOR
```

---

# Data flow

Typical execution flow:

```text
git-tree
   ↓
src.cli.main()
   ↓
parse arguments
   ↓
src.context builds Viewing/Rebase/Conflict context
   ↓
src.git_utils collects FileEntry objects
   ↓
src.search optionally filters/enriches entries
   ↓
src.authors optionally adds last-author info
   ↓
src.tree_builder builds nested tree
   ↓
src.render prints output
```

---

# Design goals

- Keep the executable entrypoint tiny
- Keep Git calls isolated
- Keep rendering isolated
- Keep search isolated
- Make new features easy to add without editing one huge file
- Keep the tool dependency-free except for Python and Git
