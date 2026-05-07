# git-tree

A small Git CLI extension to visualize changed files as a colored tree.

`git-tree` combines:
- `git diff`
- `tree`
- `grep`

into a single command-line tool.

---

## Features

- 🌳 Tree view of changed files
- 🎨 Colored statuses (`A`, `M`, `D`, `R`)
- 🔍 Search inside file contents
- 📁 Search in file names
- ✨ Glob support (`*.php`, `*Controller*`, etc.)
- 📦 Works with commits, ranges, staged files, or the whole repo
- 🧠 Git-style CLI (`git tree ...`)

---

# Installation

## Linux / WSL2 / macOS

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

# Usage

## Show current worktree changes

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

## Show files modified by a commit

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
git tree -s patate
```

Example:

```text
└── application/
    └── RoleEnum.php (6 occurrences de patate)
```

---

## Search in the whole repository

```bash
git tree -as patate
```

Equivalent:

```bash
git tree --all --search patate
```

---

## Search file names with glob patterns

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
git tree -as patate -v
```

Example:

```text
└── RoleEnum.php (2 occurrences de patate)
    ├── 12: PATATE_ADMIN
    └── 42: // patate legacy
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
| `--all`, `-a` | Search / display the whole repository |
| `--search`, `-s` | Search string |
| `--verbose`, `-v` | Display matching lines |
| `--staged` | Show staged files |
| `-h` | Help |

---

# Examples

```bash
git tree
```

```bash
git tree HEAD~5..HEAD
```

```bash
git tree -s TODO
```

```bash
git tree -as "*.vue"
```

```bash
git tree -as "Atom*.php"
```

```bash
git tree HEAD --search security
```

---

# Why?

Git already provides:
- `git diff`
- `git grep`
- `git ls-tree`

But none of them provide a structured visual overview of:
- changed files
- search results
- repository structure

`git-tree` tries to bridge that gap with a lightweight Git-native UX.

---

# Requirements

- Bash
- Python 3
- Git

---

# License

MIT
