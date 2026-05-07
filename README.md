# git-tree

A Git CLI extension to visualize files as a colored tree.

`git-tree` combines ideas from:

- `git diff`
- `tree`
- `git grep`

into a single command-line tool.

It can display:

- changed files
- commit contents
- staged files
- repository trees
- search results inside files and filenames
- last file authors with optional icons

all with a clean tree view.

---

# Features

- 🌳 Tree view output
- 🎨 Colored Git statuses (`A`, `M`, `D`, `R`)
- 🔍 Search inside file contents
- 📁 Search in file names
- ✨ Glob pattern support (`*.php`, `*Controller*`)
- 👤 Last file author display
- 🎭 Custom author aliases and icons
- 📦 Commit / range / staged / full repo support
- 🧠 Git-style CLI
- ⚡ Single standalone Python script
- 📝 Verbose mode with matching lines

---

# Installation

## Linux / macOS / WSL2

Copy the script:

```bash
sudo cp git-tree /usr/local/bin/git-tree
sudo chmod +x /usr/local/bin/git-tree
```

Verify installation:

```bash
git tree -h
```

---

# Requirements

- Python 3.10+
- Git

No external dependencies.

---

# Usage

## Current worktree changes

```bash
git tree
```

Example:

```text
└── src/
    ├── M auth.py
    └── A permissions.py

2 files changed: 1 added, 1 modified, 0 deleted, 0 renamed
```

---

## Show files from a commit

```bash
git tree HEAD
```

```bash
git tree HEAD^
```

```bash
git tree a1b2c3d4
```

---

## Show a commit range

```bash
git tree HEAD~3..HEAD
```

---

## Show staged files

```bash
git tree --staged
```

---

# Full Repository Tree

## Display all tracked files

```bash
git tree --all
```

## Restrict to a path

```bash
git tree --all src/
```

---

# Search

## Search inside modified files

```bash
git tree -s TODO
```

Example:

```text
└── src/
    └── M auth.py (2 occurrences de TODO)
```

---

## Search inside all tracked files

```bash
git tree -as TODO
```

Equivalent:

```bash
git tree --all --search TODO
```

---

## Search using glob patterns

```bash
git tree -as "*.php"
```

```bash
git tree -as "*Controller*"
```

Example:

```text
└── src/
    └── Controller/
        └── ProjectController.php (1 occurrence de *Controller*: 1 nom)
```

---

# Verbose Search Mode

Display matching lines:

```bash
git tree -asv TODO
```

Example:

```text
└── auth.py (2 occurrences de TODO)
    ├── 12: # TODO remove legacy auth
    └── 42: # TODO simplify permissions
```

---

# Last Author

Display the last Git author who modified each file:

```bash
git tree HEAD -l
```

Example:

```text
└── M auth.py [🎩 UserA • 2 hours ago]
```

Works with every mode:

```bash
git tree -asvl "*.php"
```

```bash
git tree HEAD~5..HEAD -l
```

```bash
git tree --staged -l
```

---

# Author Icons

Optional author aliases and icons can be configured.

Config file:

```text
~/.config/git-tree/authors.conf
```

Example:

```ini
[aliases]
UserA=user-a
DEV-12345=user-b

[icons]
user-a=🎩
user-b=🦊
```

Result:

```text
└── M auth.py [🎩 user-a • 2 hours ago]
```

If no config exists, `git-tree` simply displays the raw Git author name.

---

# Combined Short Flags

You can combine short flags:

```bash
git tree -as "*.php"
git tree -asv TODO
git tree -asvl "*.png"
```

Equivalent to:

```bash
git tree --all --search "*.php"
git tree --all --search TODO --verbose
git tree --all --search "*.png" --verbose --last-author
```

---

# Path Filtering

```bash
git tree HEAD src/
```

```bash
git tree --all app/components
```

Git-style separator also works:

```bash
git tree HEAD -- app/components
```

---

# Options

| Option | Description |
|---|---|
| `-a`, `--all` | Show/search all tracked files |
| `-s`, `--search` | Search string |
| `-v`, `--verbose` | Show matching lines |
| `-l`, `--last-author` | Show last file author |
| `--staged` | Show staged files |
| `-h`, `--help` | Show help |

---

# Examples

## Current worktree

```bash
git tree
```

## Last commit

```bash
git tree HEAD
```

## Previous commit

```bash
git tree HEAD^
```

## Commit range

```bash
git tree HEAD~5..HEAD
```

## Search in changed files

```bash
git tree -s security
```

## Search in all files

```bash
git tree -as "*.vue"
```

## Search with verbose output

```bash
git tree -asv TODO
```

## Search with authors

```bash
git tree -asvl "*.php"
```

## Search in a specific path

```bash
git tree -as "*.php" src/
```

---

# Why?

Git already provides:

- `git diff`
- `git grep`
- `git ls-tree`

But none of them provide a visual tree overview of:

- changed files
- search results
- repository structure
- file ownership

`git-tree` tries to bridge that gap with a lightweight Git-native UX.

---

# License

MIT
