# Git Workflow & Branching Strategy

## Branch Structure

We use a simplified Git Flow strategy suitable for this project.

### Main Branches

```
main (production-ready code)
└── develop (integration branch for features)
    ├── feature/* (new features)
    ├── bugfix/* (bug fixes)
    └── hotfix/* (urgent production fixes)
```

### Branch Descriptions

**`main`**
- Production-ready code only
- Always stable and deployable
- Protected branch (no direct commits)
- Tagged with version numbers (v1.0.0, v1.1.0, etc.)

**`develop`**
- Integration branch for ongoing development
- Contains latest development changes
- Base branch for feature branches
- Must pass all tests before merging to main

**`feature/*`**
- New features or enhancements
- Branch from: `develop`
- Merge back to: `develop`
- Naming: `feature/short-description`
- Examples:
  - `feature/admin-panel`
  - `feature/email-notifications`
  - `feature/search-functionality`

**`bugfix/*`**
- Non-urgent bug fixes
- Branch from: `develop`
- Merge back to: `develop`
- Naming: `bugfix/issue-description`
- Examples:
  - `bugfix/spider-date-parsing`
  - `bugfix/pagination-error`

**`hotfix/*`**
- Urgent fixes for production issues
- Branch from: `main`
- Merge to: both `main` AND `develop`
- Naming: `hotfix/critical-issue`
- Examples:
  - `hotfix/database-connection-leak`
  - `hotfix/api-security-vulnerability`

## Workflow Examples

### Working on a New Feature

```bash
# 1. Update develop branch
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/admin-panel

# 3. Make changes and commit
git add .
git commit -m "Add admin authentication"

# 4. Push to remote
git push -u origin feature/admin-panel

# 5. Create Pull Request on GitHub
# (develop ← feature/admin-panel)

# 6. After review and approval, merge via GitHub

# 7. Delete feature branch
git branch -d feature/admin-panel
git push origin --delete feature/admin-panel
```

### Fixing a Bug

```bash
# 1. Create bugfix branch from develop
git checkout develop
git pull origin develop
git checkout -b bugfix/spider-encoding

# 2. Fix the bug
# ... make changes ...

# 3. Commit and push
git add .
git commit -m "Fix encoding issue in spider"
git push -u origin bugfix/spider-encoding

# 4. Create PR to develop
# 5. Merge and delete branch
```

### Emergency Hotfix

```bash
# 1. Create hotfix from main
git checkout main
git pull origin main
git checkout -b hotfix/api-crash

# 2. Fix the critical issue
# ... make changes ...

# 3. Commit
git add .
git commit -m "Fix API crash on null values"

# 4. Merge to main
git checkout main
git merge hotfix/api-crash
git push origin main

# 5. Merge to develop too
git checkout develop
git merge hotfix/api-crash
git push origin develop

# 6. Delete hotfix branch
git branch -d hotfix/api-crash
```

### Release Process

```bash
# 1. Create release branch from develop
git checkout develop
git pull origin develop
git checkout -b release/v1.0.0

# 2. Update version numbers, final testing
# ... bump versions ...

# 3. Merge to main
git checkout main
git merge release/v1.0.0

# 4. Tag the release
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin main --tags

# 5. Merge back to develop
git checkout develop
git merge release/v1.0.0
git push origin develop

# 6. Delete release branch
git branch -d release/v1.0.0
```

## Commit Message Convention

Use conventional commit format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Build process, dependencies, etc.

### Examples:

```bash
# Feature
git commit -m "feat(spider): add support for image extraction"

# Bug fix
git commit -m "fix(backend): resolve pagination offset error"

# Documentation
git commit -m "docs(readme): update deployment instructions"

# Multiple changes
git commit -m "feat(frontend): add news search component

- Add search input in header
- Implement debounced search API call
- Display search results with highlighting

Closes #15"
```

## Pull Request Guidelines

### Before Creating PR:
1. Update from base branch
2. Test thoroughly
3. Write clear description
4. Link related issues

### PR Template:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How has this been tested?

## Checklist
- [ ] Code follows project style
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Tests pass
```

## Protecting Branches

On GitHub, configure branch protection for `main` and `develop`:

1. Require pull request reviews
2. Require status checks to pass
3. Require branches to be up to date
4. Include administrators in restrictions

## Initial Setup

For this project, we'll create the `develop` branch after the first commit:

```bash
# After initial commit to main
git checkout -b develop
git push -u origin develop

# Set develop as default branch for PRs on GitHub
```

## Best Practices

1. **Commit Often:** Small, focused commits
2. **Write Clear Messages:** Describe what and why
3. **Keep Branches Updated:** Regularly merge from base branch
4. **Review Code:** Use pull requests, never commit directly to main/develop
5. **Delete Merged Branches:** Keep repository clean
6. **Tag Releases:** Use semantic versioning (v1.0.0)

## Quick Reference

```bash
# Check current branch
git branch

# Switch branch
git checkout <branch-name>

# Create and switch
git checkout -b <new-branch>

# Update current branch
git pull

# View status
git status

# View commit history
git log --oneline --graph

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Discard local changes
git checkout -- <file>
```
