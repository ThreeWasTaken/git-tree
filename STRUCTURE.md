# 🏗️ Project Structure

`git-tree` is split into small focused modules so each file has a clear responsibility.

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
    ├── fuzzy.py
    ├── fzf_source.py
    ├── git_utils.py
    ├── history_nav.py
    ├── models.py
    ├── render.py
    ├── search.py
    ├── styles.py
    └── tree_builder.py
```

# Root files

## `git-tree`

Executable entrypoint.

It only imports and runs:

```python
from src.cli import main
```

## `README.md`

User-facing documentation:

- installation
- usage
- examples
- configuration
- interactive navigation

## `STRUCTURE.md`

Developer-facing documentation explaining the internal layout.

## `.gitignore`

Ignores Python cache files:

```gitignore
__pycache__/
*.py[cod]
```

---

# `src/` package

## `src/cli.py`

Main orchestration layer.

Responsibilities:

- parse CLI arguments
- normalize combined short flags like `-asvl`
- detect hidden/internal modes
- decide target/path mode
- call Git data collection
- call search filtering
- call author enrichment
- call tree building
- call rendering
- launch interactive fzf mode

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

---

## `src/models.py`

Shared data structures.

Currently contains:

```python
FileEntry
```

A `FileEntry` stores:

- status (`A`, `M`, `D`, `R`, `C`, `T`)
- path
- old path for renames
- search counts
- matching lines
- last author information

---

## `src/context.py`

Git context detection and formatting.

Responsibilities:

- build the `Viewing:` block
- format commit hashes and subjects
- format author metadata
- reuse author aliases/icons from config
- summarize commit ranges
- detect ongoing rebase
- detect conflicted files

Used by both normal output and interactive fzf mode.

---

## `src/search.py`

Search logic.

Responsibilities:

- search inside file contents
- search inside filenames
- support glob patterns like `*.php`
- highlight matching text
- filter entries when `--search` is used

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

Example:

```text
[🎩 user-a • 2 hours ago]
```

---

## `src/render.py`

Terminal rendering for normal mode.

Responsibilities:

- print the context header
- render the tree
- color statuses
- display search occurrences
- display verbose matching lines
- display author suffixes
- print summary statistics
- optionally print the status legend

---

## `src/fuzzy.py`

Interactive fzf interface.

Responsibilities:

- build fzf display lines
- preserve tree-like rendering inside fzf
- build live preview commands
- display selected filename and `+/-` stats
- open selected files in `$VISUAL`, `$EDITOR`, or `nano`
- bind left/right navigation
- reload fzf data when history changes

Controls:

```text
← older commit/range
→ newer commit/range
Enter open file
Esc quit
```

---

## `src/fzf_source.py`

Internal fzf data source.

Responsibilities:

- regenerate fzf rows for a target
- regenerate header/context metadata
- apply search filters
- apply last-author enrichment
- support fzf reloads

This module powers hidden internal calls like:

```text
--fzf-source
```

It is not part of the public CLI.

---

## `src/history_nav.py`

History navigation helpers.

Responsibilities:

- parse commit positions
- move to older commits
- move to newer commits
- move ranges through history
- prevent moving before the first commit
- support worktree ↔ commit navigation

Examples:

```text
worktree
← HEAD
← HEAD^

HEAD^
→ HEAD
→ worktree
```

Range navigation:

```text
HEAD~3..HEAD~1
← HEAD~4..HEAD~2
→ HEAD~2..HEAD
```

---

## `src/tree_builder.py`

Tree construction.

Responsibilities:

- convert flat file paths into nested dictionaries
- insert `FileEntry` objects into the tree

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

## `src/styles.py`

Shared ANSI styles.

Contains:

- color constants
- bold/reset codes
- status-to-color mapping

Example:

```python
STATUS_COLOR = {
    "A": GREEN,
    "M": BLUE,
    "D": RED,
    "R": MAGENTA,
    "C": YELLOW,
}
```

---

## `src/__init__.py`

Package marker and version metadata.

---

# Data flow

## Normal mode

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
src.search optionally filters entries
   ↓
src.authors optionally adds last-author info
   ↓
src.tree_builder builds nested tree
   ↓
src.render prints output
```

## Interactive fzf mode

```text
git-tree --fzf
   ↓
src.cli.main()
   ↓
collect FileEntry objects
   ↓
src.fuzzy launches fzf
   ↓
src.fzf_source regenerates rows on reload
   ↓
src.history_nav moves target with ← / →
   ↓
src.fuzzy opens selected file
```

---

# Design goals

- Keep the executable entrypoint tiny
- Keep Git calls isolated
- Keep rendering isolated
- Keep search isolated
- Keep fzf logic isolated
- Keep history navigation isolated
- Make new features easy to add without editing one huge file
- Keep the tool dependency-free except for Python and Git
- Keep `fzf` optional