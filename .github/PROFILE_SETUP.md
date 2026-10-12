# Profile README: how it works

Everything on the profile is either a hand-written animated SVG in `assets/` or a card that a GitHub Action rebuilds every day. No JavaScript, so it all renders on github.com, in dark and light mode.

| What | File | Updated by | Needs |
|---|---|---|---|
| Hero, terminal, section headers, divider, tech orbit, "Ask my agent" chat, footer, badges | `assets/*.svg` | `python3 scripts/build_svgs.py` (run by hand when text changes) | nothing |
| Telemetry, language mix, contribution pulse, "Currently building", 8 project cards | `assets/generated/*.svg` | `profile-stats.yml` (daily 07:11 IST) runs `scripts/build_stats.py` | Actions write permission |
| Contribution snake, Pac-Man, 3D contribution city | `output` branch | `profile-art.yml` (daily 05:47 IST, and once right after merge) | Actions write permission |
| Latest blog posts + latest YouTube videos | `README.md` between the `BLOG-POST-LIST` / `YOUTUBE-VIDEO-LIST` markers | `blog-posts.yml` (daily 06:53 IST) | Actions write permission |
| Metrics (isocalendar, languages, habits, achievements) | `output/metrics.svg` | `metrics.yml` | **off by default**: a personal token (see below) |
| WakaTime coding time | `README.md` | `wakatime.yml` | **off by default**: a WakaTime account |

## One-time setup after merging
1. Settings → Actions → General → Workflow permissions → **Read and write permissions** → Save.
2. Actions tab → run **Profile art (snake, Pac-Man, 3D)** once (it also starts by itself on merge). This creates the `output` branch the arcade images load from.
3. Actions tab → run **Profile stats cards** and **Latest blog posts and videos** once.

## Optional
- **Metrics**: create a classic personal access token with the `read:user` scope → Settings → Secrets and variables → Actions → add secret `METRICS_TOKEN`; under Variables add `ENABLE_METRICS` = `true`; run **Metrics**; then remove the comment wrapper around the Metrics block in `README.md`.
- **WakaTime**: add secret `WAKATIME_API_KEY` and variable `ENABLE_WAKATIME` = `true`, then add the waka-readme start/end markers where the README comment says.

## Editing
- Change words in the hero, terminal or chat: edit `scripts/build_svgs.py`, run it, commit `assets/`.
- Change featured projects: edit `PROJECTS` in `scripts/build_stats.py` and the project table in `README.md`.
- Colours for both themes live in `scripts/svgkit.py` (`PAL`).
