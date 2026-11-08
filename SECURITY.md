# Security guidance

Do not store personal access tokens in source files or `output/`. Use `gh auth login` locally or `secrets.GITHUB_TOKEN` within GitHub Actions. Minimal workflow scope is `contents: write` only for auto-committing generated image files.

Before committing, inspect `git diff --cached --name-only`, and ensure `.env`, credentials, `snapshot.json`, and private data are absent. Public `output/summary.json` contains only profile-facing statistics, but it still discloses your GitHub login and activity.

Live data uses HTTPS to `api.github.com` only; the offline preview loads local art. The project has no login form, server, telemetry or third-party JavaScript dependency.
