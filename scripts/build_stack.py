"""Build the custom technology mosaic from bundled fonts and icon PNGs.

Requires Pillow. Icon PNGs in assets/icons are generated from the respective
Simple Icons SVG source files, with Java and VS Code marks from Devicon.
SQL uses a small custom database symbol.
The panel describes technologies used or being learned, not skill ratings.
"""
from pathlib import Path
import math
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
SCALE = 2
WIDTH, HEIGHT = 1200, 550
BG = '#080B18'
WHITE, MUTED = '#F1F5FF', '#91A0C4'
CYAN, VIOLET, PINK = '#45E4FF', '#A78BFA', '#FF64C8'
ICON_COLORS = {'python':'#54C9FF','c':'#A8B9CC','javascript':'#F7DF1E','typescript':'#45A6FF',
               'html5':'#FF7C50','css':'#B278F5','sql':'#56D7FF','numpy':'#57BCFF','pandas':'#C7B4FF',
               'git':'#F27660','github':'#F1F5FF','linux':'#FFD66B','figma':'#FF8DAA'}
GROUPS = [
    ('01', 'LANGUAGES', CYAN, [('python','Python'),('c','C'),('java','Java'),('javascript','JavaScript'),('typescript','TypeScript')]),
    ('02', 'WEB & DATA', VIOLET, [('html5','HTML'),('css','CSS'),('sql','SQL'),('numpy','NumPy'),('pandas','Pandas')]),
    ('03', 'TOOLS & DESIGN', PINK, [('git','Git'),('github','GitHub'),('vscode','VS Code'),('linux','Linux'),('figma','Figma')]),
]

def rgb(value):
    return tuple(int(value[i:i+2],16) for i in (1,3,5))

def mix(a,b,p):
    return tuple(round(x+(y-x)*p) for x,y in zip(rgb(a),rgb(b)))

@lru_cache(maxsize=32)
def font(size,weight=500,mono=False):
    f=ImageFont.truetype(str(ASSETS/'fonts'/('JetBrainsMono.ttf' if mono else 'Manrope.ttf')),round(size*SCALE))
    f.set_variation_by_axes([weight])
    return f

def text(d,xy,label,size,color=WHITE,weight=500,mono=False,anchor=None):
    d.text(tuple(round(n*SCALE) for n in xy),label,font=font(size,weight,mono),fill=color,anchor=anchor)

def rect(d,xy,fill,outline=None,r=12,width=1):
    d.rounded_rectangle(tuple(round(n*SCALE) for n in xy),round(r*SCALE),fill=fill,outline=outline,width=round(width*SCALE))

def line(d,points,fill,width=1):
    d.line([(round(x*SCALE),round(y*SCALE)) for x,y in points],fill=fill,width=round(width*SCALE))

def custom_icon(slug,color):
    """Small recognizable semantic marks; these are not claimed official logos."""
    im=Image.new('RGBA',(96*SCALE,96*SCALE))
    d=ImageDraw.Draw(im)
    c=color
    def ellipse(box,fill=None,outline=c,w=2):
        d.ellipse(tuple(v*SCALE for v in box),fill=fill,outline=outline,width=w*SCALE)
    if slug=='sql':
        rect(d,(20,25,76,76),None,c,5,3)
        ellipse((20,14,76,36),fill='#111A34',w=3)
        d.arc((20*SCALE,43*SCALE,76*SCALE,65*SCALE),0,180,fill=c,width=3*SCALE)
        d.arc((20*SCALE,61*SCALE,76*SCALE,83*SCALE),0,180,fill=c,width=3*SCALE)
    elif slug=='java':
        # A cup and two flowing steam strokes, echoing Java's familiar concept.
        d.arc((22*SCALE,34*SCALE,65*SCALE,80*SCALE),0,180,fill=c,width=4*SCALE)
        line(d,[(22,53),(22,56)],c,4)
        line(d,[(65,53),(65,56)],c,4)
        d.arc((55*SCALE,45*SCALE,80*SCALE,66*SCALE),270,95,fill=c,width=4*SCALE)
        line(d,[(17,83),(69,83)],c,3)
        line(d,[(37,42),(46,31),(39,21),(48,11)],c,3)
        line(d,[(53,37),(60,28),(54,20)],c,2)
    elif slug=='vscode':
        pts=[(73,12),(88,18),(88,78),(73,85),(27,49),(14,59),(7,53),(23,39),(7,25),(14,19),(27,29)]
        d.polygon([(x*SCALE,y*SCALE) for x,y in pts],fill=c)
        d.polygon([(73*SCALE,29*SCALE),(42*SCALE,39*SCALE),(73*SCALE,66*SCALE)],fill='#111A34')
    else:
        text(d,(48,48),slug[:2].upper(),30,c,700,anchor='mm')
    return im

ICON_CACHE={}
def icon(slug,color):
    key=(slug,color)
    if key in ICON_CACHE:
        return ICON_CACHE[key]
    candidate=ASSETS/'icons'/f'{slug}.png'
    if candidate.exists():
        raw=Image.open(candidate).convert('RGBA')
        # Keep official multicolor Devicon marks; tint monochrome Simple Icons.
        if slug in ('java','vscode'):
            out=raw
        else:
            alpha=raw.getchannel('A')
            out=Image.new('RGBA',raw.size,ICON_COLORS.get(slug,color))
            out.putalpha(alpha)
        out.thumbnail((42*SCALE,42*SCALE),Image.Resampling.LANCZOS)
    else:
        if slug not in ('java','sql','vscode'):
            raise FileNotFoundError(f'Missing technology icon: {candidate}')
        out=custom_icon(slug,color)
        out.thumbnail((42*SCALE,42*SCALE),Image.Resampling.LANCZOS)
    ICON_CACHE[key]=out
    return out

def background():
    im=Image.new('RGB',(WIDTH*SCALE,HEIGHT*SCALE),BG)
    glows=Image.new('RGB',im.size)
    d=ImageDraw.Draw(glows)
    d.ellipse((-220*SCALE,-210*SCALE,560*SCALE,200*SCALE),fill='#0B344E')
    d.ellipse((720*SCALE,250*SCALE,1400*SCALE,800*SCALE),fill='#30154C')
    glows=glows.filter(ImageFilter.GaussianBlur(110*SCALE))
    im=Image.blend(im,glows,.28)
    d=ImageDraw.Draw(im)
    rect(d,(1,1,1198,548),None,'#26335A',18)
    for x in range(32,1180,26):
        for y in range(26,530,26):
            d.ellipse((x*SCALE,y*SCALE,(x+.6)*SCALE,(y+.6)*SCALE),fill='#1A2443')
    return im

BASE=None
MOBILE_BASE=None
def render(active=None):
    im=BASE.copy()
    d=ImageDraw.Draw(im)
    text(d,(36,26),'THE STACK / ALWAYS EVOLVING',17,CYAN,500,True)
    text(d,(34,62),'Ideas are better with the right tools.',33,WHITE,750)
    rect(d,(969,36,1164,78),'#111A34','#34436B',20)
    text(d,(1066,56),'15 TECHNOLOGIES',17,VIOLET,600,True,anchor='mm')
    text(d,(36,111),'Learning and applying these across coursework, experiments, and projects.',17,MUTED)
    global_index=0
    for group_index,(num,label,color,items) in enumerate(GROUPS):
        gx=36+group_index*384
        rect(d,(gx,158,gx+360,479),'#0D142C','#243155',14)
        line(d,[(gx+18,158),(gx+342,158)],color,2)
        text(d,(gx+20,180),num,17,color,500,True)
        text(d,(gx+60,178),label,17,WHITE,650,True)
        for index,(slug,name) in enumerate(items):
            if index<3:
                tx=gx+18+index*109
                ty=220
            else:
                tx=gx+72+(index-3)*109
                ty=343
            strength=0
            if active is not None:
                dist=abs((global_index-active+7.5)%15-7.5)
                strength=max(0,1-dist/1.1)
            border=mix('#253457',color,.25+.75*strength)
            fill=mix('#111A34',color,.025+.075*strength)
            if strength>.05:
                halo=Image.new('RGBA',im.size)
                hd=ImageDraw.Draw(halo)
                rect(hd,(tx-2,ty-2,tx+102,ty+105),(*rgb(color),round(65*strength)),None,14)
                halo=halo.filter(ImageFilter.GaussianBlur(10*SCALE))
                im=Image.alpha_composite(im.convert('RGBA'),halo).convert('RGB')
                d=ImageDraw.Draw(im)
            rect(d,(tx,ty,tx+100,ty+104),fill,border,11)
            graphic=icon(slug,color)
            ix=round((tx+50)*SCALE-graphic.width/2)
            iy=round((ty+36)*SCALE-graphic.height/2)
            im.paste(graphic,(ix,iy),graphic)
            text(d,(tx+50,ty+79),name,17,WHITE,600,anchor='mm')
            global_index+=1
    text(d,(36,510),'FOUNDATIONS → EXPERIMENTS → REAL PROJECTS',17,CYAN,500,True)
    text(d,(1164,510),'BUILD · LEARN · REPEAT',17,MUTED,500,True,anchor='ra')
    return im.resize((WIDTH,HEIGHT),Image.Resampling.LANCZOS)

def mobile_background():
    im=Image.new('RGB',(600*SCALE,1120*SCALE),BG)
    glow=Image.new('RGB',im.size)
    gd=ImageDraw.Draw(glow)
    gd.ellipse((-300*SCALE,-80*SCALE,500*SCALE,400*SCALE),fill='#0B344E')
    gd.ellipse((220*SCALE,530*SCALE,900*SCALE,1200*SCALE),fill='#30154C')
    im=Image.blend(im,glow.filter(ImageFilter.GaussianBlur(110*SCALE)),.25)
    d=ImageDraw.Draw(im)
    rect(d,(1,1,598,1118),None,'#26335A',18)
    for x in range(24,580,24):
        for y in range(20,1100,24):
            d.ellipse((x*SCALE,y*SCALE,(x+.6)*SCALE,(y+.6)*SCALE),fill='#1A2443')
    return im

def render_mobile(active=None):
    """Art-directed mobile layout rather than shrinking the desktop mosaic."""
    im=MOBILE_BASE.copy()
    d=ImageDraw.Draw(im)
    text(d,(24,22),'THE STACK / ALWAYS EVOLVING',21,CYAN,500,True)
    text(d,(23,58),'My technology toolkit.',35,WHITE,750)
    text(d,(24,111),'Tools I’m learning and applying.',22,MUTED)
    global_index=0
    for group_index,(num,label,color,items) in enumerate(GROUPS):
        gy=160+group_index*308
        rect(d,(24,gy,576,gy+290),'#0D142C','#243155',15)
        line(d,[(44,gy),(556,gy)],color,2)
        text(d,(46,gy+20),num,23,color,500,True)
        text(d,(99,gy+18),label,23,WHITE,650,True)
        for index,(slug,name) in enumerate(items):
            tx=52+index*174 if index<3 else 139+(index-3)*174
            ty=gy+65 if index<3 else gy+176
            strength=0
            if active is not None:
                dist=abs((global_index-active+7.5)%15-7.5)
                strength=max(0,1-dist/1.1)
            border=mix('#253457',color,.3+.7*strength)
            fill=mix('#111A34',color,.025+.075*strength)
            rect(d,(tx,ty,tx+148,ty+99),fill,border,11,width=1+int(strength>.6))
            graphic=icon(slug,color).resize((48*SCALE,48*SCALE),Image.Resampling.LANCZOS)
            ix=round((tx+74)*SCALE-graphic.width/2)
            iy=round((ty+30)*SCALE-graphic.height/2)
            im.paste(graphic,(ix,iy),graphic)
            text(d,(tx+74,ty+78),name,24,WHITE,600,anchor='mm')
            global_index+=1
    text(d,(300,1086),'FOUNDATIONS → EXPERIMENTS → PROJECTS',19,CYAN,500,True,anchor='mm')
    return im.resize((600,1120),Image.Resampling.LANCZOS)

def write_animation(final,renderer,path,count,step):
    palette=final.quantize(colors=192,method=Image.Quantize.MEDIANCUT)
    frames=[palette]
    durations=[1000]
    for i in range(count):
        frames.append(renderer(i/step).quantize(palette=palette,dither=Image.Dither.NONE))
        durations.append(100)
    frames.append(palette.copy())
    durations.append(1200)
    frames[0].save(path,save_all=True,append_images=frames[1:],duration=durations,loop=0,optimize=True,disposal=1)

def main():
    global BASE,MOBILE_BASE
    ASSETS.mkdir(parents=True,exist_ok=True)
    BASE=background()
    final=render()
    final.save(ASSETS/'tech-stack.png',optimize=True)
    write_animation(final,render,ASSETS/'tech-stack.gif',45,3)
    MOBILE_BASE=mobile_background()
    mobile=render_mobile()
    mobile.save(ASSETS/'tech-stack-mobile.png',optimize=True)
    write_animation(mobile,render_mobile,ASSETS/'tech-stack-mobile.gif',30,2)
    print('Built desktop and mobile technology mosaics: static PNGs and animated GIFs.')

if __name__=='__main__':
    main()
