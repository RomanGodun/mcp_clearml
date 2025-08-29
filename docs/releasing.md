# Release Memo

This project uses tag-triggered releases via GitHub Actions and uv.

## Prerequisites
- Git pushed changes on `main` are green in CI
- Decide next version using SemVer (e.g., 0.1.0 → 0.2.0)
- Optional: PyPI publishing configured with `PYPI_API_TOKEN` repository secret

## Version bump
1. Update version in `pyproject.toml`:
   - `[project] version = "X.Y.Z"`
2. Commit the change:
   ```bash
   git add pyproject.toml
   git commit -m "chore(release): vX.Y.Z"
   git push
   ```

## Create a release tag
```bash
git tag vX.Y.Z
git push origin vX.Y.Z
```
This triggers `.github/workflows/release.yml`:
- `uv build`
- Twine check
- GitHub Release with artifacts
- PyPI publish (if `PYPI_API_TOKEN` is set)

## Verify
- GitHub → Releases: check the new release and attached artifacts
- If PyPI enabled: verify package on https://pypi.org/project/mcp_clearml/

## Troubleshooting
- Missing artifacts: check `release` workflow logs
- Twine check fails: verify `pyproject.toml` metadata and package contents
- PyPI upload fails: ensure `PYPI_API_TOKEN` secret exists and is valid

## Useful commands
```bash
uv build
uvx twine check dist/*
uvx twine upload dist/*  # requires PYPI_API_TOKEN env
```
