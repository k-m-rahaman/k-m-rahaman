"""Write a readable source summary for the exact provider cards in the README."""
from pathlib import Path
import json
import html

ROOT=Path(__file__).resolve().parents[1]

def main():
    manifest=json.loads((ROOT/'assets'/'classic-stats-sources'/'manifest.json').read_text(encoding='utf-8'))
    labels={'stats':'Summary statistics','grade':'GitHub grade card','repos-per-language':'Languages by repository','most-commit-language':'Languages by commit','productive-time':'Commit hours in Kolkata','streak':'Contribution streaks','profile-details':'Contribution timeline'}
    lines=['# Current GitHub statistics','',f"Fetched: **{manifest['fetched_at']}**.",'',
           'These are snapshots of the same provider cards used in the original README. The layout, colors, and frame animations are customized; the counts, language distributions, and grade are preserved.','',
           'Each provider uses its own data scope, calculation, and cache. Differences between the summary card and grade card are shown as returned, rather than merged into a new total. The grade is provider-calculated and can change on future refreshes.','',
           'The commit-hours card uses **Asia/Kolkata, UTC+05:30**. Repo-based and commit-based language distributions remain separate; neither is a proficiency score.','']
    for name,label in labels.items():
        source=manifest['sources'][name]
        lines += ['## '+label,'',f"[Live provider card]({source['url']}) · [Saved SVG](./classic-stats-sources/{name}.svg)",'']
        parts=[html.unescape(part) for part in source['text_preview'].split(' | ')]
        if name=='stats' and len(parts)==11:
            lines += ['| Metric | Value |','| :--- | ---: |']
            lines += [f'| {metric.rstrip(":")} | {value} |' for metric,value in zip(parts[1:6],parts[6:11])]
        elif name=='grade' and len(parts)>=12:
            lines += [f'**Current provider grade: {parts[1]}**','', '| Metric | Value |','| :--- | ---: |']
            lines += [f'| {parts[index].rstrip(":")} | {parts[index+1]} |' for index in range(2,len(parts)-1,2)]
        else:
            lines += [' · '.join(parts)]
        lines += ['']
    lines += ['## Update behavior','',
              'The scheduled workflow refreshes all seven source SVGs, renders them, and rebuilds the animated desktop/mobile panels. A failed provider fetch stops the workflow before it commits. Existing published images remain available.','',
              'Source projects: [GitHub Profile Summary Cards](https://github.com/vn7n24fzkq/github-profile-summary-cards), [GitHub Readme Stats](https://github.com/anuraghazra/github-readme-stats), [GitHub Readme Streak Stats](https://github.com/DenverCoder1/github-readme-streak-stats).','']
    (ROOT/'assets'/'stats-summary.md').write_text('\n'.join(lines),encoding='utf-8')

if __name__=='__main__':main()
