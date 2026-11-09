# Midnight Spectrum profile

This package is prepared for **k-m-rahaman/k-m-rahaman**. It preserves the original repo-based and commit-based language charts, summary statistics, provider-calculated grade, hourly activity, contribution timeline, and streak card in one coordinated animated theme.

## Preview

Extract the ZIP and open **PREVIEW.html** in a browser. It includes hover glow, a slight pointer tilt, touch/press feedback, keyboard focus styling, and a pause/play button. Phone layouts are included. Animations start on load; use the Pause animations button for static graphics. Pointer effects respect reduced-motion preferences.

**GitHub README behavior is different:** GitHub removes custom CSS and JavaScript, so hover/tilt/ripple and the pause button work in the standalone preview. The README itself provides GIF animation, clickable cards, native tap-to-expand sections, and explicit static PNG alternatives. [GitHub rendering rules](https://github.com/github/markup#github-markup), [native collapsed sections](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/organizing-information-with-collapsed-sections).

## Installed in your VS Code repository

The complete files have been copied into your repository. Review the changes in VS Code Source Control, then commit and push them together. No asset generation is needed before the first push.

## Upload to another checkout

1. Open your profile repository, **k-m-rahaman/k-m-rahaman**.
2. Replace `README.md`. Add `assets/`, `scripts/`, `.github/`, `requirements.txt`, `package.json`, and `.gitignore` at its root.
3. Upload the contents of `kazi-profile-v3`, rather than nesting that folder inside the repository. Keep all asset paths unchanged.
4. Commit to `main`. The bundled graphics display immediately.
5. In **Actions**, select **Refresh profile statistics** and choose **Run workflow** to verify refreshes.

If the web uploader omits `.github/`, use **Add file → Create new file** to add `.github/workflows/refresh-profile.yml` and paste the included workflow. `PREVIEW.html`, this guide, and `STYLE.md` can also be included in the repository.

## Current stats

The seven source cards were fetched from the same providers used by the original README. See `assets/stats-summary.md` for the exact values, refresh date, and source URLs. The grade is read from the provider rather than assigned by this design; it can change on later refreshes.

Different services may return different star or commit totals because their scopes and caches differ. These differences are preserved. The repo and commit donut charts keep their original definitions and are not replaced with code-byte percentages. The productive-time card now uses **Asia/Kolkata / UTC+05:30**.

The live visitor-counter link uses the same counter identifier as the original README.

## Daily refresh

The workflow runs after changes to its source files are pushed to `main`, daily at **01:23 UTC / 06:53 IST**, and supports manual runs. Scheduling can be delayed by GitHub. It downloads the seven provider SVGs, renders their final readable states, and rebuilds the animated desktop/mobile groups and source summary.

The workflow uses the repository's built-in token only to commit generated files, requesting `contents: write`. Stats services receive ordinary public requests. No personal token or secret is needed. If a provider fails or returns an error card, the workflow stops before committing; the existing published graphics remain available. If branch rules prevent bot pushes, regenerate locally and commit the output yourself.

## Regenerate locally

Use **Python 3.11+**, **Node.js 24**, and npm:

```sh
python -m pip install -r requirements.txt
npm install
python scripts/fetch_classic_sources.py
node scripts/rasterize_classic_sources.cjs
python scripts/build_classic_stats.py
python scripts/write_stats_summary.py
```

To redraw saved statistics without network access, run the compositor directly. To rebuild identity and technology graphics:

```sh
python scripts/build_identity.py
python scripts/build_stack.py
```

The preview is an included snapshot of the README. The README and stats refresh independently after upload; to see future changes in the local preview, replace its article markup with the updated rendered Markdown or regenerate a preview with your preferred Markdown renderer.

## Edit the theme

`STYLE.md` lists the exact palette and where it is used. The main combination is midnight **#080B18**, cyan **#45E4FF**, violet **#A78BFA**, and pink **#FF64C8**.

- `README.md`: biography, ordering, links, and native expandable sections.
- `scripts/build_identity.py`: animated identity, contact buttons, project cards, footer.
- `scripts/build_stack.py`: technology graphics and mobile layout.
- `scripts/build_classic_stats.py`: card composition and moving frame accents.
- `scripts/fetch_classic_sources.py`: source endpoints and provider colors.
- `scripts/rasterize_classic_sources.cjs`: consistent language colors and readable SVG final states.
- `assets/preview.css` and `assets/preview.js`: source for standalone hover/touch controls, also embedded in the supplied preview.

## Attribution

Source stat projects: [GitHub Profile Summary Cards](https://github.com/vn7n24fzkq/github-profile-summary-cards), [GitHub Readme Stats](https://github.com/anuraghazra/github-readme-stats), and [GitHub Readme Streak Stats](https://github.com/DenverCoder1/github-readme-streak-stats). The grade endpoint is the original `github-readme-stats-eight-theta.vercel.app` deployment.

Technology logos come from Simple Icons and Devicon. Fonts are Manrope and JetBrains Mono. Preserve the included icon and font license files when redistributing them.
