# Midnight Spectrum

| Role | Hex | Use |
| :--- | :--- | :--- |
| Background | `#080B18` | Main canvas |
| Panel | `#0F1430` | Cards and controls |
| Border | `#26335A` | Quiet structure |
| Primary text | `#F1F5FF` | Names, headings, metrics |
| Muted text | `#91A0C4` | Captions and secondary labels |
| Cyan | `#45E4FF` | Primary actions, highlights |
| Violet | `#A78BFA` | Secondary accents, repo charts |
| Pink | `#FF64C8` | Rank ring, commit accents |
| Mint | `#60E9B5` | Java and secondary chart segments |
| Gold | `#FFC478` | HTML and chart contrast |

The hero, technology panels, source-stat frames, and social cards use this same palette. Language colors stay consistent between the repo and commit donuts.

The README uses animated GIFs with explicit static PNG alternatives and dedicated phone layouts. Its native interactions are links and tap-to-expand sections. The standalone preview adds hover glow, slight pointer tilt, press feedback, and a pause/play control.

Edit `scripts/build_identity.py`, `scripts/build_stack.py`, and `scripts/build_classic_stats.py` to change the generated graphics. Edit source URL colors in `scripts/fetch_classic_sources.py` and language colors in `scripts/rasterize_classic_sources.cjs` to keep provider cards coordinated.
