"""Create the original neon profile identity assets with Pillow and bundled OFL fonts."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'assets'
S=2
BG='#080B18'
TEXT='#F1F5FF'
MUTED='#91A0C4'
CYAN='#45E4FF'
VIOLET='#A78BFA'
PINK='#FF64C8'

def rgb(color):
    return tuple(int(color[i:i+2],16) for i in (1,3,5))

def font(size,weight=500,mono=False):
    result=ImageFont.truetype(str(ASSETS/'fonts'/('JetBrainsMono.ttf' if mono else 'Manrope.ttf')),round(size*S))
    result.set_variation_by_axes([weight])
    return result

def tx(draw,x,y,value,size,color=TEXT,weight=500,mono=False,anchor=None):
    draw.text((round(x*S),round(y*S)),value,font=font(size,weight,mono),fill=color,anchor=anchor)

def ln(draw,points,color,width=1):
    draw.line([(round(x*S),round(y*S)) for x,y in points],fill=color,width=round(width*S),joint='curve')

def rr(draw,rect,fill,outline=None,r=14,width=1):
    draw.rounded_rectangle(tuple(round(x*S) for x in rect),radius=round(r*S),fill=fill,outline=outline,width=round(width*S))

def dot(draw,x,y,r,color):
    draw.ellipse(((x-r)*S,(y-r)*S,(x+r)*S,(y+r)*S),fill=color)

def gradient_text(im,x,y,value,size,weight=800,start=CYAN,end=PINK):
    mask=Image.new('L',im.size)
    d=ImageDraw.Draw(mask)
    d.text((x*S,y*S),value,font=font(size,weight),fill=255)
    bbox=mask.getbbox()
    if not bbox:return
    grad=Image.new('RGB',im.size)
    gd=ImageDraw.Draw(grad)
    a,b=rgb(start),rgb(end)
    for px in range(bbox[0],bbox[2]):
        t=(px-bbox[0])/max(1,bbox[2]-bbox[0]-1)
        color=tuple(round(v*(1-t)+w*t) for v,w in zip(a,b))
        gd.line((px,bbox[1],px,bbox[3]),fill=color)
    im.paste(grad,(0,0),mask)

def background(w,h):
    im=Image.new('RGB',(w*S,h*S),BG)
    glow=Image.new('RGBA',im.size)
    d=ImageDraw.Draw(glow)
    d.ellipse((680*S,-140*S,1280*S,490*S),fill=(65,45,175,100))
    d.ellipse((850*S,130*S,1330*S,650*S),fill=(20,145,215,65))
    d.ellipse((-90*S,240*S,410*S,720*S),fill=(85,35,145,65))
    im=Image.alpha_composite(im.convert('RGBA'),glow.filter(ImageFilter.GaussianBlur(90*S))).convert('RGB')
    return im

def sphere_points(phase):
    curves=[]
    rotation=phase*2*math.pi
    def project(x,y,z):
        xx=x*math.cos(rotation)+z*math.sin(rotation)
        zz=-x*math.sin(rotation)+z*math.cos(rotation)
        return (954+xx*145,255+y*145,zz)
    for lat in [-60,-30,0,30,60]:
        la=math.radians(lat)
        curves.append([project(math.cos(la)*math.cos(a*math.pi/90),math.sin(la),math.cos(la)*math.sin(a*math.pi/90)) for a in range(181)])
    for meridian in range(0,180,30):
        me=math.radians(meridian)
        curves.append([project(math.cos(a*math.pi/90)*math.cos(me),math.sin(a*math.pi/90),math.cos(a*math.pi/90)*math.sin(me)) for a in range(181)])
    return curves,project

def hero(phase):
    im=background(1200,540)
    d=ImageDraw.Draw(im)
    rr(d,(1,1,1199,539),None,'#29315B',22)
    # Sparse star field and the perspective floor establish depth without text noise.
    for i in range(45):
        x=744+(i*103)%420
        y=86+(i*67)%350
        dot(d,x,y,0.8,'#455789' if i%3 else '#7B79A9')
    for y in [412,444,482,530]:
        ln(d,[(750,y),(1183,y)],'#202547')
    for x in range(620,1400,80):
        ln(d,[(954,350),(x,538)],'#202547')
    gradient_text(im,51,25,'KMR.',27,800,CYAN,VIOLET)
    d=ImageDraw.Draw(im)
    tx(d,146,36,'CODE / LEARN / CREATE',13,MUTED,500,True)
    dot(d,976,44,3,CYAN)
    tx(d,992,35,'KOLKATA, INDIA',13,MUTED,500,True)
    rr(d,(52,97,491,128),'#11162F','#38416B',15)
    tx(d,70,103,'B.TECH CSE  /  AI & MACHINE LEARNING',13,VIOLET,500,True)
    tx(d,48,151,'Kazi Mustafijur',59,TEXT,800)
    gradient_text(im,45,212,'Rahaman.',102,800,CYAN,VIOLET)
    d=ImageDraw.Draw(im)
    tx(d,54,342,'Exploring AI. Engineering possibilities.',25,TEXT,650)
    tx(d,55,384,'Student. Builder. Always curious.',19,MUTED,500)
    rr(d,(52,436,711,501),'#0D1228','#2B365D',13)
    for i,c in enumerate([PINK,VIOLET,CYAN]):dot(d,73+i*14,453,3,c)
    tx(d,70,470,'>',16,CYAN,600,True)
    phrase='code. learn. build. repeat.'
    # Reveal, hold, then reset once per slow, continuous sphere rotation.
    shown=len(phrase) if phase<.17 else min(len(phrase),int((phase-.17)*len(phrase)/.49))
    tx(d,94,467,phrase[:shown],17,TEXT,500,True)
    if int(phase*12)%2==0:
        xx=94+ImageDraw.Draw(im).textlength(phrase[:shown],font=font(17,500,True))/S
        rr(d,(xx+3,474,xx+11,490),CYAN,r=0)
    # Draw a glowing model globe, then its crisp wireframe.
    sphere=Image.new('RGBA',im.size)
    sd=ImageDraw.Draw(sphere)
    curves,project=sphere_points(phase)
    for i,curve in enumerate(curves):
        ln(sd,[(x,y) for x,y,z in curve],rgb(CYAN if i%3==0 else VIOLET)+(78,),1)
    sphere_glow=sphere.filter(ImageFilter.GaussianBlur(6*S))
    im=Image.alpha_composite(im.convert('RGBA'),sphere_glow)
    d=ImageDraw.Draw(im)
    for i,curve in enumerate(curves):
        for p,q in zip(curve,curve[1:]):
            front=(p[2]+q[2])/2
            c=CYAN if i%3==0 else VIOLET
            alpha=155 if front>0 else 36
            ln(d,[(p[0],p[1]),(q[0],q[1])],rgb(c)+(alpha,),.7)
    orbit=[]
    for i in range(121):
        a=i/120*2*math.pi
        x,y=191*math.cos(a),71*math.sin(a)
        ang=-.44
        orbit.append((954+x*math.cos(ang)-y*math.sin(ang),255+x*math.sin(ang)+y*math.cos(ang)))
    ln(d,orbit,rgb(PINK)+(145,),1)
    a=phase*2*math.pi
    x,y=191*math.cos(a),71*math.sin(a)
    px,py=954+x*math.cos(-.44)-y*math.sin(-.44),255+x*math.sin(-.44)+y*math.cos(-.44)
    dot(d,px,py,4,PINK)
    rr(d,(904,221,1004,286),'#0D1430','#4A548E',15)
    tx(d,954,253,'AI',38,TEXT,800,anchor='mm')
    tx(d,954,320,'ALWAYS LEARNING',11,CYAN,500,True,anchor='mm')
    for x,y,label,c in [(825,140,'PYTHON',CYAN),(1080,351,'ML',PINK)]:
        rr(d,(x,y,x+96,y+31),'#111832',c,10)
        tx(d,x+48,y+15,label,12,c,600,True,anchor='mm')
    tx(d,954,464,'IDEAS  →  MODELS  →  IMPACT',11,VIOLET,500,True,anchor='mm')
    return im.convert('RGB').resize((1200,540),Image.Resampling.LANCZOS)

def save_animation(name,images,duration=100):
    images[0].save(ASSETS/f'{name}.png',optimize=True)
    palette=images[0].quantize(colors=224,method=Image.Quantize.MEDIANCUT)
    frames=[im.quantize(palette=palette,dither=Image.Dither.NONE) for im in images]
    frames[0].save(ASSETS/f'{name}.gif',save_all=True,append_images=frames[1:],duration=duration,loop=0,optimize=True,disposal=1)

def hero_mobile(phase):
    im=background(600,690)
    d=ImageDraw.Draw(im)
    rr(d,(1,1,599,689),None,'#29315B',20)
    gradient_text(im,29,21,'KMR.',25,800,CYAN,VIOLET)
    d=ImageDraw.Draw(im)
    tx(d,566,35,'KOLKATA, INDIA',12,MUTED,500,True,anchor='rm')
    rr(d,(30,77,570,112),'#11162F','#38416B',16)
    tx(d,300,94,'B.TECH CSE / AI & MACHINE LEARNING',14,VIOLET,500,True,anchor='mm')
    tx(d,27,135,'Kazi Mustafijur',43,TEXT,800)
    gradient_text(im,25,189,'Rahaman.',78,800,CYAN,VIOLET)
    d=ImageDraw.Draw(im)
    tx(d,32,290,'Exploring AI.',26,TEXT,700)
    tx(d,32,329,'Engineering possibilities.',24,TEXT,600)
    tx(d,32,389,'CODE.',29,CYAN,750)
    tx(d,32,434,'LEARN.',29,VIOLET,750)
    tx(d,32,479,'CREATE.',29,PINK,750)
    curves,project=sphere_points(phase)
    def mobile(x,y):return (419+(x-954)*.77,459+(y-255)*.77)
    for i,curve in enumerate(curves):
        ln(d,[mobile(x,y) for x,y,z in curve],CYAN if i%3==0 else '#6866A0',.7)
    orbit=[]
    for i in range(121):
        a=i/120*2*math.pi
        x,y=143*math.cos(a),53*math.sin(a)
        orbit.append((419+x*math.cos(-.44)-y*math.sin(-.44),459+x*math.sin(-.44)+y*math.cos(-.44)))
    ln(d,orbit,PINK,1)
    a=phase*2*math.pi
    x,y=143*math.cos(a),53*math.sin(a)
    dot(d,419+x*math.cos(-.44)-y*math.sin(-.44),459+x*math.sin(-.44)+y*math.cos(-.44),3,PINK)
    rr(d,(378,430,460,489),'#0D1430','#4A548E',12)
    tx(d,419,459,'AI',31,TEXT,800,anchor='mm')
    rr(d,(30,601,570,659),'#0D1228','#2B365D',12)
    tx(d,50,618,'> code. learn. build. repeat.',17,CYAN,500,True)
    return im.convert('RGB').resize((600,690),Image.Resampling.LANCZOS)

def build_footer():
    frames=[]
    for n in range(30):
        im=background(1200,184)
        d=ImageDraw.Draw(im)
        rr(d,(1,1,1199,183),None,'#29315B',18)
        tx(d,600,48,'LET’S BUILD SOMETHING MEANINGFUL.',30,TEXT,750,anchor='mm')
        tx(d,600,98,'AI / DATA / CODE / CURIOSITY',15,VIOLET,500,True,anchor='mm')
        ln(d,[(180,140),(1020,140)],'#2B365D',1)
        x=180+n/29*840
        dot(d,x,140,3,CYAN)
        frames.append(im.resize((1200,184),Image.Resampling.LANCZOS))
    save_animation('footer',frames,130)

def build_social():
    for slug,label,color in [('linkedin','LINKEDIN  ↗',CYAN),('email','LET’S TALK  ↗',PINK),('github','REPOSITORIES  ↗',VIOLET),('instagram','INSTAGRAM  ↗',PINK)]:
        im=background(260,58)
        d=ImageDraw.Draw(im)
        rr(d,(1,1,259,57),'#11162F','#3B426E',12)
        rr(d,(1,13,4,45),color,r=1)
        tx(d,134,29,label,21,color,600,True,anchor='mm')
        im.resize((260,58),Image.Resampling.LANCZOS).save(ASSETS/f'{slug}.png',optimize=True)

def build_projects():
    data=[('project-ecolens','01 / SUSTAINABILITY','EcoLens','AI-assisted waste sorting.','Multilingual guidance. Campus impact.',CYAN,[(70,245),(126,150),(180,245)]),
          ('project-dronemap','02 / GEOSPATIAL AI','DroneMap AI','From aerial imagery to insight.','Building footprints and survey exports.',VIOLET,[(72,163),(111,143),(158,166),(159,216),(117,238),(73,214)]),
          ('project-data','03 / DATA & ANALYTICS','Data Analysis Journey','Ask better questions of data.','NumPy. Pandas. Visualization. SQL.',PINK,[])]
    for slug,label,title,tag,desc,color,points in data:
        im=background(1200,238)
        d=ImageDraw.Draw(im)
        rr(d,(1,1,1199,237),None,'#29315B',18)
        rr(d,(31,29,191,209),'#111832','#303D69',20)
        if 'ecolens' in slug:
            ln(d,[(73,148),(111,83),(151,148),(73,148)],color,3)
            for x,y in [(73,148),(111,83),(151,148)]:dot(d,x,y,7,color)
            tx(d,112,182,'AI / ECO',12,color,500,True,anchor='mm')
        elif 'dronemap' in slug:
            for off in [0,22,44]:
                ln(d,[(58+off,94),(97+off,73),(141+off,96),(101+off,119),(58+off,94)],color,2)
            tx(d,112,182,'MAP / AI',12,color,500,True,anchor='mm')
        else:
            for i,h in enumerate([35,67,48,92]):rr(d,(56+i*29,159-h,73+i*29,159),[CYAN,VIOLET,PINK,CYAN][i],r=4)
            tx(d,112,182,'DATA / SQL',12,color,500,True,anchor='mm')
        tx(d,226,30,label,13,color,500,True)
        tx(d,224,64,title,40,TEXT,800)
        tx(d,228,126,tag,23,TEXT,600)
        tx(d,228,170,desc,18,MUTED,500)
        rr(d,(1016,93,1154,143),'#151C38','#41476E',24)
        tx(d,1085,118,'EXPLORE ↗',14,color,600,True,anchor='mm')
        im.resize((1200,238),Image.Resampling.LANCZOS).save(ASSETS/f'{slug}.png',optimize=True)
        mobile=background(600,325)
        md=ImageDraw.Draw(mobile)
        rr(md,(1,1,599,324),None,'#29315B',18)
        tx(md,28,26,label,16,color,500,True)
        tx(md,27,77,title,36,TEXT,800)
        tx(md,30,141,tag,22,TEXT,600)
        # Explicit short line breaks keep real project descriptions readable on phones.
        desc_lines={'project-ecolens':['Multilingual guidance.','Campus sustainability.'],
                    'project-dronemap':['Building footprints','and survey exports.'],
                    'project-data':['NumPy. Pandas.','Visualization. SQL.']}[slug]
        for i,value in enumerate(desc_lines):tx(md,30,187+i*31,value,21,MUTED,500)
        tx(md,566,286,'EXPLORE ↗',16,color,600,True,anchor='rm')
        mobile.resize((600,325),Image.Resampling.LANCZOS).save(ASSETS/f'{slug}-mobile.png',optimize=True)

if __name__=='__main__':
    ASSETS.mkdir(parents=True,exist_ok=True)
    save_animation('hero',[hero(i/54) for i in range(54)],100)
    save_animation('hero-mobile',[hero_mobile(i/36) for i in range(36)],150)
    build_footer()
    build_social()
    build_projects()
    print('Built neon identity, social buttons, project cards and animated footer.')
