"""Compose exact provider statistics into animated desktop/mobile profile cards.

Sources are refreshed and rasterized by refresh_classic_stats before this script.
This compositor requires Pillow only. It never invents or merges provider counts.
"""
from pathlib import Path
from datetime import datetime
import json
import math
from PIL import Image, ImageDraw, ImageFont
from render_grade_badge import render_grade_card

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'assets'
SOURCES=ASSETS/'classic-stats-sources'
BG='#080B18'
PANEL='#0F1430'
LINE='#26335A'
TEXT='#F1F5FF'
MUTED='#91A0C4'
CYAN='#45E4FF'
VIOLET='#A78BFA'
PINK='#FF64C8'

GROUPS=[
 ('languages','TWO WAYS TO READ THE STACK','By repository. By commit.',
  'The language mix, seen through two different lenses.',
  [('repos-per-language','Repository distribution',CYAN),('most-commit-language','Commit distribution',VIOLET)]),
 ('overview','THE STORY IN NUMBERS','My GitHub, at a glance.',
  'A snapshot of the work behind the profile.',
  [('stats','Summary Cards / provider totals',CYAN),('grade','Readme Stats / current-year card',PINK)]),
 ('activity','THE RHYTHM BEHIND THE WORK','When I build. How I show up.',
  'Commit hours in India and the current contribution streak.',
  [('productive-time','Commit hours / Asia/Kolkata',VIOLET),('streak','Streak Stats / live provider snapshot',PINK)]),
 ('profile','THE LONG VIEW','A year of building, in motion.',
  'The profile timeline, preserved from GitHub Profile Summary Cards.',
  [('profile-details','Profile Summary Cards / contribution timeline',CYAN)]),
]

def font(size,weight=500,mono=False):
    result=ImageFont.truetype(str(ASSETS/'fonts'/('JetBrainsMono.ttf' if mono else 'Manrope.ttf')),round(size))
    try:
        axes=result.get_variation_axes()
        result.set_variation_by_axes([weight if a['name']==b'Weight' else a['default'] for a in axes])
    except (OSError,AttributeError):
        pass
    return result

def rgb(color):return tuple(int(color[i:i+2],16) for i in (1,3,5))
def blend(a,b,t):return tuple(round(v*(1-t)+w*t) for v,w in zip(rgb(a),rgb(b)))

def text(d,x,y,value,size=20,color=TEXT,weight=500,mono=False,anchor=None):
    d.text((x,y),value,font=font(size,weight,mono),fill=color,anchor=anchor)

def wrap(d,value,max_width,size):
    lines=[]
    current=''
    for word in value.split():
        candidate=(current+' '+word).strip()
        if current and d.textlength(candidate,font=font(size,750))>max_width:
            lines.append(current)
            current=word
        else:current=candidate
    if current:lines.append(current)
    return lines

def load_sources():
    manifest=json.loads((SOURCES/'manifest.json').read_text(encoding='utf-8'))
    images={}
    for _,_,_,_,entries in GROUPS:
        for name,_,_ in entries:
            source=manifest['sources'].get(name,{})
            if not source.get('ok'):
                raise RuntimeError(f'Missing successful source: {name}; keep the prior rendered cards.')
            if name == 'grade':
                image = render_grade_card(SOURCES/'grade.svg', ASSETS/'fonts')
                image.save(SOURCES/'grade.png', optimize=True)
            else:
                image=Image.open(SOURCES/f'{name}.png').convert('RGB')
            images[name]=image
    return manifest,images

def card(im,d,image,rect,color,phase):
    x,y,w,h=rect
    pulse=.32+.36*(math.sin(phase*2*math.pi)+1)/2
    d.rounded_rectangle((x-3,y-3,x+w+3,y+h+3),radius=13,fill=PANEL,outline=blend(LINE,color,pulse),width=1)
    fit=image.copy()
    fit.thumbnail((w,h),Image.Resampling.LANCZOS)
    im.paste(fit,(round(x+(w-fit.width)/2),round(y+(h-fit.height)/2)))
    # Restrained light travels on the frame; it never masks source values.
    travel=(phase*1.3)%1
    segment=min(78,w*.16)
    dash_x=x+travel*(w-segment)
    d.line((dash_x,y-3,dash_x+segment,y-3),fill=color,width=2)

def frame(group, manifest, images, phase=0, mobile=False):
    key, kicker, title, subtitle, entries = group
    width = 600 if mobile else 1200
    pad = 28 if mobile else 40
    gap = 26

    probe = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    size = 31 if mobile else 36
    title_lines = wrap(probe, title, width - pad * 2, size)

    title_y = 63
    sub_y = title_y + len(title_lines) * (size + 7) + 8
    sub_lines = (
        wrap(probe, subtitle, width - pad * 2, 18)
        if mobile else [subtitle]
    )
    source_y = sub_y + len(sub_lines) * 26 + 23

    available = width - pad * 2
    ratios = [
        images[name].width / images[name].height
        for name, _, _ in entries
    ]
    rectangles = []

    if mobile:
        # Stack cards at their natural aspect ratios.
        y = source_y
        for ratio in ratios:
            h = round(available / ratio)
            rectangles.append((pad, y, available, h))
            y += h + 61
    else:
        # Equal heights, proportional widths: no stretching or padding.
        row_width = available - gap * (len(entries) - 1)
        row_height = round(row_width / sum(ratios))
        x = pad

        for index, ratio in enumerate(ratios):
            w = round(row_height * ratio)

            if index == len(ratios) - 1:
                w = width - pad - x

            rectangles.append((x, source_y, w, row_height))
            x += w + gap

    content_bottom = max(y + h for x, y, w, h in rectangles)
    height = content_bottom + 100

    im = Image.new('RGB', (width, height), BG)
    d = ImageDraw.Draw(im)

    for y in range(height):
        d.line(
            (0, y, width, y),
            fill=blend(BG, '#151635', .3 * y / height)
        )

    d.rounded_rectangle(
        (1, 1, width - 2, height - 2),
        radius=22,
        outline=LINE,
        width=2
    )
    d.line(
        (pad, 1, pad + min(300, width - 2 * pad), 1),
        fill=CYAN,
        width=2
    )
    d.rounded_rectangle(
        (pad, 31, pad + 6, 48),
        radius=3,
        fill=CYAN
    )
    text(
        d, pad + 18, 29, kicker,
        13 if mobile else 15, CYAN, 500, True
    )

    for index, line in enumerate(title_lines):
        text(
            d, pad, title_y + index * (size + 7),
            line, size, TEXT, 750
        )

    for index, line in enumerate(sub_lines):
        text(
            d, pad, sub_y + index * 26,
            line, 18, MUTED
        )

    for index, ((name, note, color), rect) in enumerate(
        zip(entries, rectangles)
    ):
        x, y, w, h = rect

        card(
            im, d, images[name], rect,
            color, (phase + index * .22) % 1
        )
        text(
            d, x, y + h + 17, note,
            13 if mobile else 14, color, 500, True
        )

    stamp = datetime.fromisoformat(
        manifest['fetched_at'].replace('Z', '+00:00')
    ).strftime('%d %b %Y').upper()

    d.line(
        (pad, height - 54, width - pad, height - 54),
        fill=LINE,
        width=1
    )

    if mobile:
        text(
            d, pad, height - 38,
            'Source links in the README.', 12, MUTED
        )
        text(
            d, pad, height - 20,
            'UPDATED ' + stamp + ' / UTC',
            11, MUTED, 500, True
        )
    else:
        text(
            d, pad, height - 37,
            'Provider snapshots may use different scopes and caches.',
            14, MUTED
        )
        text(
            d, width - pad, height - 37,
            'UPDATED ' + stamp + ' / UTC',
            13, MUTED, 500, True, 'ra'
        )

    return im

def save(group,manifest,images,mobile=False):
    name='classic-stats-'+group[0]+('-mobile' if mobile else '')
    first=frame(group,manifest,images,0,mobile)
    first.save(ASSETS/f'{name}.png',optimize=True)
    # Palette includes the original charts plus the moving frame accents.
    palette=first.quantize(colors=224,method=Image.Quantize.MEDIANCUT)
    frames=[frame(group,manifest,images,i/28,mobile).quantize(palette=palette,dither=Image.Dither.NONE) for i in range(28)]
    frames[0].save(ASSETS/f'{name}.gif',save_all=True,append_images=frames[1:],duration=130,loop=0,optimize=True,disposal=1)
    print(name,first.size,len(frames),'frames')

def main():
    manifest,images=load_sources()
    for group in GROUPS:
        save(group,manifest,images)
        save(group,manifest,images,True)

if __name__=='__main__':main()
