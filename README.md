# 🌳 git-tree

A Git CLI extension that visualizes files as a colored tree.

`git-tree` combines ideas from:

- 🔀 `git diff`
- 🔍 `git grep`
- 🌲 `tree`
- ⚡ `fzf`

into a single Git-native developer tool.

It provides a fast visual overview of changed files, commits, ranges, searches, ownership, conflicts, and interactive navigation — all without leaving the terminal.

---

<img width="1656" height="898" alt="tn9Sjj0" src="https://github.com/user-attachments/assets/76e0a12d-6c39-4ccb-b154-d9140c2942aa" />

---

# ✨ Features

- 🌳 Tree-based Git visualization
- 🎨 Colored Git statuses (`A`, `M`, `D`, `R`, `C`)
- 🔍 Search inside file contents
- 📁 Search in filenames
- ✨ Glob pattern support (`*.php`, `*Controller*`)
- 👤 Last author display
- 🎭 Custom author aliases and icons
- 📦 Commit / range / staged / repository support
- ⚡ Interactive `fzf` navigation
- 👀 Live diff and file preview
- ⬅️➡️ Commit history navigation
- 🔥 Rebase and conflict awareness
- 🚫 No external Python dependencies

---

# 🚀 Installation

## Requirements

Required:

- Python 3.10+
- Git

Optional:

- `fzf`

```bash
sudo apt install fzf
```

## Clone

```bash
git clone https://github.com/ThreeWasTaken/git-tree.git
cd git-tree
```

## Install with a symlink

```bash
sudo ln -s "$(pwd)/git-tree" /usr/local/bin/git-tree
sudo chmod +x git-tree
```

Verify:

```bash
git tree -h
```

---

# 📖 Usage

## Worktree changes

```bash
git tree
```

## Staged files

```bash
git tree --staged
```

## Single commit

```bash
git tree HEAD
git tree HEAD^
git tree a1b2c3d4
```

## Commit range

```bash
git tree HEAD~5..HEAD
```

## Full repository tree

```bash
git tree --all
```

Restrict to a path:

```bash
git tree --all src/
```

---

# 🔍 Search

Search changed files:

```bash
git tree -s TODO
```

Search all tracked files:

```bash
git tree -as TODO
```

Search filenames with globs:

```bash
git tree -as "*.php"
git tree -as "*Controller*"
```

Verbose search:

```bash
git tree -asv TODO
```

---

# ⚡ Interactive Navigation

Launch the interactive `fzf` interface:

```bash
git tree HEAD --fzf
```

Search and browse interactively:

```bash
git tree -as "*.php" --fzf
```

Interactive mode includes:

- fuzzy filtering
- live diff preview
- selected filename + `+/-` stats
- commit metadata
- author metadata
- tree-aware display
- editor integration
- history navigation

Controls:

```text
← older commit/range
→ newer commit/range
Enter open file
Esc quit
```

Examples:

```text
HEAD
← HEAD^
← HEAD^^
```

```text
HEAD^..HEAD
← HEAD^^..HEAD^
← HEAD~3..HEAD~2
```

Selected files open with:

1. `$VISUAL`
2. `$EDITOR`
3. `nano`

---

# 👤 Last Author

Display the last Git author who modified each file:

```bash
git tree HEAD -l
```

Example:

```text
└── M auth.py [🎩 user-a • 2 hours ago]
```

Works with every mode:

```bash
git tree -asvl "*.php"
git tree HEAD~5..HEAD -l
git tree --staged -l
```

---

# 🎭 Author Icons

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

The same aliases/icons are also used in the interactive `fzf` header.

If no config exists, raw Git author names are displayed.

---

# 🔥 Rebase & Conflict Awareness

When a rebase is in progress, `git-tree` can display:

- the currently replayed commit
- conflicted files

Example:

```text
Rebase: applying abc123 fix permissions
2 conflicts
```

Conflicted files are displayed with status:

```text
C
```

---

# 🧩 Combined Short Flags

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

# 📁 Path Filtering

```bash
git tree HEAD src/
git tree --all app/components
```

Git-style separator also works:

```bash
git tree HEAD -- app/components
```

---

# ⚙️ Options

| Option | Description |
|---|---|
| `-a`, `--all` | Show/search all tracked files |
| `-s`, `--search` | Search string |
| `-v`, `--verbose` | Show matching lines |
| `-l`, `--last-author` | Show last file author |
| `--staged` | Show staged files |
| `--fzf` | Interactive navigation |
| `--legend` | Show status legend |
| `-h`, `--help` | Show help |

---

# 🖥️ Supported Platforms

Officially supported:

- Linux
- macOS
- WSL

Experimental:

- Git Bash

Not supported:

- Windows CMD
- Windows PowerShell

The interactive `--fzf` mode relies on a Unix-like shell environment.

---

# 🏗️ Project Structure

Internal architecture is documented in:

```text
STRUCTURE.md
```

Main modules:

```text
src/
├── cli.py
├── git_utils.py
├── render.py
├── search.py
├── authors.py
├── context.py
├── fuzzy.py
├── history_nav.py
└── ...
```

---

# 🤔 Why?

Git already provides:

- `git diff`
- `git grep`
- `git ls-tree`

But none of them provide a visual tree overview of:

- changed files
- search results
- repository structure
- file ownership
- interactive history navigation

`git-tree` tries to bridge that gap with a lightweight Git-native user experience.

---

# 📜 License

MIT
