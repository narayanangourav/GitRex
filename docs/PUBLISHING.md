# Publish GitRex to GitHub (Windows PowerShell)

## 0. Preflight

1. Read `ASSET_PROVENANCE.md` and `LICENSE`.
2. The bundled demo GIF uses invented figures and is stamped `DEMO DATA`.
3. Never publish `.venv`, `.env`, `snapshot.json`, tokens, keys, or other private files.
4. Run `RUN_TESTS.bat` and then `RUN_DEMO.bat` locally. Optionally test `RUN_LIVE.bat` to verify the actual GraphQL API connection.

## 1. Authenticate

```powershell
git --version
gh --version
py -3 --version
gh auth login
gh api user --jq .login
```

Make sure the login is the account you intend to publish from.

## 2. Initialize the **separate** GitRex repository

The published repository is public at `narayanangourav/GitRex` on the `master` branch. When continuing this existing checkout, keep using that repository and branch; do not initialize another repository or create a duplicate. These commands are only for a new, separate project folder:

Open PowerShell inside the extracted project folder:

```powershell
git init -b master
git add .
git diff --cached --name-only
git diff --cached --check
git status --short
```

Inspect every staged file, especially under `assets/` and `output/`. If you see any secret or unexpected file, run `git restore --staged path/to/file` and add it to `.gitignore` before continuing.

```powershell
git commit -m "feat: release GitRex v2 with original procedural artwork"
gh repo create narayanangourav/GitRex --public --source=. --remote=origin --push
```

**Do not run `gh repo create` if that remote already exists**. Inspect it first with `gh repo view narayanangourav/GitRex`. Replace the username if different.

## 3. Enable scheduled output generation

The workflow declares only `contents: write` in its YAML and commits generated files with the built-in `GITHUB_TOKEN`; the repository-wide default remains read-only. This least-privilege setup completed the first live run successfully. If an organization policy blocks the workflow's explicit permission, adjust only the permission required to write the generated files.

Run `Actions` → `GitRex profile evolution` → `Run workflow` on `master`.

After a successful run, the workflow commits the updated GIF, PNG, preview, and level summary. Future runs are scheduled nightly and may be delayed or disabled after inactivity by GitHub.

## 4. Embed the animation in your profile

After the first successful live workflow run, add the animation to the separate **profile** repository called `narayanangourav/narayanangourav`. Append this section to its existing `README.md`; preserve the other profile content:

```markdown
## 🦖 GitRex Evolution

<img src="https://raw.githubusercontent.com/narayanangourav/GitRex/master/output/trex.gif" alt="GitRex level evolution" width="100%">
```

Verify the GIF loads on `https://github.com/narayanangourav`. Do not claim it shows your live figures until the first successful workflow run.

## 5. Security and release notes

- Review third-party Actions and pin to approved commit SHAs in a production environment.
- Enable Dependabot alerts and secret scanning if available.
- Do not commit an authenticated snapshot or a token, even temporarily; removing them in a later commit does not remove them from Git history.
- Read GitHub Actions billing and permissions settings before enabling optional resources.
- Publish the `v2.0.0` GitHub release from the reviewed live-output commit, not from an unverified ZIP containing demos.
