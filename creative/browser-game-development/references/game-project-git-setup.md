# Game Project Git Setup Pattern

## Quick Setup
```bash
cd /path/to/project
git init
git add .
git commit -m "Initial commit"
gh repo create REPO_NAME --private --source=. --push
```

## Essential .gitignore for Game Projects
```
node_modules/
dist/
assets/raw/
*.log
.DS_Store
```

**Why `assets/raw/`?** Downloaded source packs (KayKit, Kenney, etc.) are large (47+ MB) and not needed in the repo. The processed assets in `public/assets/` are what matter.

## Pitfall: Accidentally Committing node_modules
First commit may include node_modules/ and assets/raw/ if .gitignore wasn't created first.

**Fix:**
```bash
git rm -r --cached node_modules/ assets/raw/ dist/
git add .gitignore
git commit --amend --no-edit
git push --force origin master
```

## Chat Summary for Session Continuity
Create `CHAT_SUMMARY.md` at project root with:
- Project overview and tech stack
- How to run (npm install, npm run dev, npm run build)
- Project structure
- All features implemented
- What's done vs next steps
- Any gotchas or decisions made

This enables picking up work in a new chat/session without re-explaining everything.

## Private Repo Creation (gh CLI)
```bash
# Requires: gh auth login
gh repo create REPO_NAME --private --source=. --push
# --private: not publicly visible
# --source=.: uses current directory
# --push: pushes after creation
```

## Force Push After Cleanup
If you need to rewrite history (e.g., removing large files):
```bash
git push --force origin master
```
Only use on private repos or before anyone else pulls.
