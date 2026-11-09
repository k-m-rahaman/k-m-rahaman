from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlencode
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import json
import re

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'assets'/'classic-stats-sources'
DEST.mkdir(parents=True,exist_ok=True)
user='k-m-rahaman'
base='https://github-profile-summary-cards.vercel.app/api/cards/'
colors={'username':user,'theme':'tokyonight','title_color':'45E4FF','text_color':'DCE5FF','bg_color':'0F1430','border_color':'344375','icon_color':'A78BFA','chart_color':'FF64C8'}
urls={name:base+name+'?'+urlencode(colors|({'timeZone':'Asia/Kolkata','utcOffset':'5.5'} if name=='productive-time' else {})) for name in ['stats','repos-per-language','most-commit-language','productive-time','profile-details']}
urls['grade']='https://github-readme-stats-eight-theta.vercel.app/api?'+urlencode({'username':user,'show_icons':'true','include_all_commits':'false','count_private':'false','hide_border':'false','bg_color':'0F1430','title_color':'45E4FF','text_color':'DCE5FF','icon_color':'A78BFA','ring_color':'FF64C8','border_color':'344375','border_radius':'14','rank_icon':'default','custom_title':'My GitHub Stats','disable_animations':'false','number_format':'long'})
urls['streak']='https://streak-stats.demolab.com/?'+urlencode({'user':user,'background':'0F1430','border':'344375','stroke':'344375','ring':'A78BFA','fire':'FF64C8','currStreakNum':'F1F5FF','sideNums':'45E4FF','currStreakLabel':'FF64C8','sideLabels':'A78BFA','dates':'91A0C4','hide_border':'false'})
manifest={'fetched_at':datetime.now(timezone.utc).isoformat(timespec='seconds'),'sources':{}}
def fetch(item):
    name,url=item
    try:
        req=Request(url,headers={'User-Agent':'Mozilla/5.0 KaziProfileREADME','Accept':'image/svg+xml'})
        with urlopen(req,timeout=60) as res:
            content=res.read()
        if b'<svg' not in content:raise ValueError('Not SVG')
        if re.search(rb'Something went wrong|API rate limit|Could not fetch',content,re.I):raise ValueError('Provider error card')
        (DEST/(name+'.svg')).write_bytes(content)
        texts=re.findall(r'<text\b[^>]*>([\s\S]*?)</text>',content.decode('utf-8'))
        preview=' | '.join(re.sub('<[^>]+>','',t).strip() for t in texts)
        return name,{'url':url,'bytes':len(content),'text_preview':preview,'ok':True}
    except Exception as error:
        return name,{'url':url,'ok':False,'error':str(error)}
with ThreadPoolExecutor(max_workers=4) as pool:
    manifest['sources']=dict(pool.map(fetch,urls.items()))
if not all(source['ok'] for source in manifest['sources'].values()):
    raise SystemExit('A stats provider failed; existing rendered cards kept. Retry later.')
(DEST/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
for name,source in manifest['sources'].items():print(name,json.dumps(source))
