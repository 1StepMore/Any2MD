# CI/CD Release Process

This file documents the release workflow for Any2MD-1StepMore to PyPI via GitHub Actions.

## Overview

Releases are triggered by pushing a git tag matching `v*` (e.g., `v0.3.0`). The CI pipeline:
1. Runs tests on Python 3.10, 3.11, 3.12
2. Runs linting (ruff, flake8)
3. Runs type checking (mypy)
4. If all pass → builds and publishes to PyPI via trusted publishing

## Prerequisites

### One-time setup (already done):
1. Trusted publishing configured at https://pypi.org/manage/account/publishing/
   - Repository: `1StepMore/Any2MD`
   - Workflow: `ci.yml`
   - Environment: `pypi`
2. GitHub repo default branch set to `main`

## Release Steps

### 1. Ensure all changes are committed on `main`

```bash
git status  # verify clean
git log --oneline -3  # verify correct commits
```

### 2. Update version in `pyproject.toml`

```toml
# Before releasing, bump version to match tag
version = "0.4.0"  # replace with your target version
```

### 3. Commit version bump

```bash
git add pyproject.toml
git commit -m "bump version to 0.4.0"
git push
```

### 4. Create and push git tag

```bash
git tag v0.4.0
git push origin v0.4.0
```

This triggers GitHub Actions. The `publish` job runs only if:
- All tests pass
- Lint passes
- Type check passes
- Tag format matches `v*`

### 5. Monitor the release

- Check workflow: https://github.com/1StepMore/Any2MD/actions
- Check PyPI: https://pypi.org/project/Any2MD-1StepMore/

Expected workflow duration: ~3-5 minutes

## Troubleshooting

### Publish job skipped
- Verify the workflow file has `environment: pypi` in the publish job
- Check the tag points to the latest commit with the workflow

### Trusted publishing error
- Ensure the PyPI trusted publisher is configured for `Any2MD-1StepMore` (not `any2md`)
- Verify environment name matches in both PyPI and workflow file

### PyPI shows wrong version
- The PyPI version comes from `pyproject.toml`'s `version` field, NOT the git tag
- Always update `version` in `pyproject.toml` before tagging

## Important Notes

- Version in `pyproject.toml` MUST match the git tag for consistency
- Trusted publishing uses OIDC - no tokens needed
- The workflow uses `fail-fast: true` on the test matrix
- Lint and type-check use `|| true` to not block (they're non-blocking for now)