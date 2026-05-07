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

all with a clean tree view.

---

# Features

- 🌳 Tree view output
- 🎨 Colored Git statuses (`A`, `M`, `D`, `R`)
- 🔍 Search inside file contents
- 📁 Search in file names
- ✨ Glob pattern support (`*.php`, `*Controller*`)
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
└── application/
    ├── M security.yaml
    └── A auth.php

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
git tree c47e32142
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

## Search in the whole repository

```bash
git tree -as TODO
```

Equivalent:

```bash
git tree --all --search TODO
```

---

## Combined short flags

```bash
git tree -asv TODO
```

Equivalent:

```bash
git tree --all --search TODO --verbose
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
└── application/
    └── Controller/
        └── ProjectController.php (1 occurrence de *Controller*: 1 nom)
```

---

## Verbose search mode

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

# Full repository tree

```bash
git tree --all
```

```bash
git tree --all src/
```

Example:

```text
└── application/
    └── modules/
        └── ...
```

---

# Path filtering

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

`git-tree` tries to bridge that gap with a lightweight Git-native UX.

---

# License

MIT
