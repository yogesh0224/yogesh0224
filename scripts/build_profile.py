"""Build Yogesh Luitel's animated observation-field profile.
Requires Pillow and Noto Sans Display, Inter Display, Liberation Mono fonts.
Font binaries are not committed. The output GIFs are committed by GitHub Actions.
"""
from pathlib import Path
import math
import subprocess
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
ASSET=ROOT/'assets'
ASSET.mkdir(exist_ok=True)
W,H=1440,550
BG=(15,17,21)
IVORY=(241,240,231)
ACID=(219,255,83)
GRID=(39,43,48)
LINE=(85,91,88)
SUB=(157,160,156)
BURNT=(251,104,75)
def resolve_font(filename, family):
    """Find the actual system font location on the GitHub runner."""
    matches=list(Path('/usr/share/fonts').rglob(filename))
    if matches:
        return str(matches[0])
    path=subprocess.check_output(
        ['fc-match','-f','%{file}',family],text=True).strip()
    if not Path(path).is_file():
        raise FileNotFoundError(f'Cannot resolve font {family}')
    return path

FONT_DISPLAY=resolve_font('NotoSansDisplay-CondensedBlack.ttf','Noto Sans Display:style=Condensed Black')
FONT_TEXT=resolve_font('InterDisplay-Medium.otf','Inter Display:style=Medium')
FONT_MONO=resolve_font('LiberationMono-Regular.ttf','Liberation Mono:style=Regular')
FONT_MONO_BOLD=resolve_font('LiberationMono-Bold.ttf','Liberation Mono:style=Bold')
def fitted_font(path, texts, size, max_width):
    """Retain strong display type without clipping across font package versions."""
    measure=ImageDraw.Draw(Image.new('RGB',(2,2)))
    while size>20:
        font=ImageFont.truetype(path,size)
        widest=max(measure.textbbox((0,0),text,font=font)[2] for text in texts)
        if widest<=max_width:
            return font
        size-=1
    raise ValueError('Unable to fit display typography')

FD=fitted_font(FONT_DISPLAY,['YOGESH','LUITEL.'],211,745)
FMAIN=ImageFont.truetype(FONT_TEXT,27)
FM=ImageFont.truetype(FONT_MONO,17)
FM2=ImageFont.truetype(FONT_MONO_BOLD,17)
FM3=ImageFont.truetype(FONT_MONO_BOLD,15)

def text_top(draw,xy,msg,font,fill,**kwargs):
    x,y=xy
    b=draw.textbbox((0,0),msg,font=font,**kwargs)
    if x+b[2]-b[0] > W-28 or y+(b[3]-b[1]) > H-20:
        raise ValueError(f'Overflow for {msg!r}: {(x,y,b)}')
    draw.text((x-b[0],y-b[1]),msg,font=font,fill=fill,**kwargs)
    return x+b[2]-b[0],y+(b[3]-b[1])

def frame_base():
    im=Image.new('RGB',(W,H),BG)
    d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,10),fill=ACID)
    d.line((69,77,1372,77),fill=LINE,width=2)
    text_top(d,(70,38),'YL / 0224',FM2,ACID)
    text_top(d,(1120,39),'NEPAL  •  2026',FM,SUB)
    right1,bottom1=text_top(d,(62,105),'YOGESH',FD,IVORY)
    right2,bottom2=text_top(d,(62,265),'LUITEL.',FD,ACID)
    assert max(right1,right2)<811,(right1,right2)
    assert bottom2<440,bottom2
    d.line((71,458,776,458),fill=LINE,width=2)
    text_top(d,(72,474),'I BUILD SOFTWARE. I STUDY WHAT IT CHANGES.',FMAIN,IVORY)
    text_top(d,(71,510),'TEACHING   /   RESEARCH   /   ENGINEERING',FM3,SUB)
    d.line((833,98,833,502),fill=LINE,width=2)
    text_top(d,(873,107),'OBSERVATION / 001',FM2,ACID)
    text_top(d,(873,491),'EVIDENCE  >  ASSUMPTION',FM3,SUB)
    return im

BASE=frame_base()
POINTS=[
    (906,205),(1002,186),(1099,225),(1204,180),(1315,231),
    (926,330),(1042,307),(1136,353),(1260,304),(1328,381),
    (994,416),(1176,418)
]
EDGES=[
    (0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,8),(8,9),
    (1,6),(2,7),(3,8),(5,10),(6,10),(7,11),(8,11),(10,11),(2,6)
]

def mix(a,b,f):
    return tuple(round(a[j]*(1-f)+b[j]*f) for j in range(3))

def render(t):
    im=BASE.copy()
    d=ImageDraw.Draw(im)
    coords=[]
    for i,(x,y) in enumerate(POINTS):
        phase=i*.68
        amp=7+3*(i%3)
        xx=x+amp*math.sin(t*math.tau/6+phase)
        yy=y+amp*math.cos(t*math.tau/6+phase*1.4)
        coords.append((round(xx),round(yy)))
    for x in range(890,1375,44):
        for y in range(177,456,44):
            d.point((x,y),fill=GRID)
    for j,(a,b) in enumerate(EDGES):
        pulse=.5+.5*math.sin(t*math.tau/6+j*.46)
        color=mix(GRID,LINE,.30+.32*pulse)
        d.line((*coords[a],*coords[b]),fill=color,width=2)
    for a,b in ((0,1),(1,2),(2,7),(7,8),(8,9)):
        d.line((*coords[a],*coords[b]),fill=mix(LINE,ACID,.15),width=2)
    route=[0,1,2,7,8,11,10,5]
    edge_pos=((t/6)*len(route))%len(route)
    start=int(edge_pos)
    k=edge_pos-start
    a=coords[route[start]]
    b=coords[route[(start+1)%len(route)]]
    qx=a[0]+(b[0]-a[0])*k
    qy=a[1]+(b[1]-a[1])*k
    for i,(x,y) in enumerate(coords):
        active=i in route
        r=5 if active else 3
        d.ellipse((x-r,y-r,x+r,y+r),fill=ACID if i==7 else (167,174,166) if active else LINE)
    for r,light in ((25,.13),(16,.3),(7,1)):
        c=mix(BG,ACID,light)
        d.ellipse((qx-r,qy-r,qx+r,qy+r),outline=c,width=3 if r==16 else 2)
    fx,fy=coords[7]
    d.arc((fx-29,fy-29,fx+29,fy+29),start=15,end=305,fill=BURNT,width=3)
    xlo=881
    v=(math.sin(t*math.tau/6)+1)/2
    yy=int(447-32*v)
    d.line((xlo,yy,xlo+58,yy),fill=ACID,width=3)
    d.line((xlo,yy-7,xlo,yy+7),fill=ACID,width=2)
    section=(t%6)/6
    d.rectangle((872,156,1362,160),fill=GRID)
    d.rectangle((872,156,int(872+490*section),160),fill=ACID)
    return im

MW,MH=900,930
FDM=fitted_font(FONT_DISPLAY,['YOGESH','LUITEL.'],220,810)
FMM=ImageFont.truetype(FONT_MONO_BOLD,23)
FBM=ImageFont.truetype(FONT_TEXT,28)
def mobile_base():
    im=Image.new('RGB',(MW,MH),BG)
    d=ImageDraw.Draw(im)
    d.rectangle((0,0,MW,12),fill=ACID)
    d.text((49,54),'YL / 0224',font=FMM,fill=ACID)
    d.text((688,54),'NEPAL',font=FMM,fill=SUB)
    d.line((49,112,853,112),fill=LINE,width=2)
    def mtext(y,txt,color):
        b=d.textbbox((0,0),txt,font=FDM)
        assert 49+b[2]-b[0]<MW-20
        d.text((49-b[0],y-b[1]),txt,font=FDM,fill=color)
        return y+b[3]-b[1]
    b1=mtext(150,'YOGESH',IVORY)
    b2=mtext(315,'LUITEL.',ACID)
    assert b1<325 and b2<498
    d.line((49,518,854,518),fill=LINE,width=2)
    d.text((49,543),'I BUILD SOFTWARE.',font=FBM,fill=IVORY)
    d.text((49,582),'I STUDY WHAT IT CHANGES.',font=FBM,fill=IVORY)
    d.text((49,648),'OBSERVATION / 001',font=FMM,fill=ACID)
    d.line((49,694,854,694),fill=LINE,width=2)
    d.text((49,888),'TEACHING / RESEARCH / ENGINEERING',font=FMM,fill=SUB)
    return im

MBASE=mobile_base()
def render_mobile(t):
    im=MBASE.copy()
    d=ImageDraw.Draw(im)
    cc=[]
    for i,(x,y) in enumerate(POINTS):
        phase=i*.68
        xx=70+(x-900)*1.48+8*math.sin(t*math.tau/6+phase)
        yy=729+(y-180)*.54+5*math.cos(t*math.tau/6+phase*1.4)
        cc.append((round(xx),round(yy)))
    for j,(a,b) in enumerate(EDGES):
        pulse=.5+.5*math.sin(t*math.tau/6+j*.46)
        d.line((*cc[a],*cc[b]),fill=mix(GRID,LINE,.30+.32*pulse),width=2)
    for a,b in ((0,1),(1,2),(2,7),(7,8),(8,9)):
        d.line((*cc[a],*cc[b]),fill=mix(LINE,ACID,.16),width=2)
    route=[0,1,2,7,8,11,10,5]
    edge=((t/6)*len(route))%len(route)
    s=int(edge)
    k=edge-s
    a,b=cc[route[s]],cc[route[(s+1)%len(route)]]
    qx=a[0]+(b[0]-a[0])*k
    qy=a[1]+(b[1]-a[1])*k
    for i,(x,y) in enumerate(cc):
        r=5 if i in route else 3
        d.ellipse((x-r,y-r,x+r,y+r),fill=ACID if i==7 else SUB if i in route else LINE)
    for r,light in ((23,.14),(13,.35),(6,1)):
        d.ellipse((qx-r,qy-r,qx+r,qy+r),outline=mix(BG,ACID,light),width=2)
    x,y=cc[7]
    d.arc((x-20,y-20,x+20,y+20),15,310,fill=BURNT,width=3)
    d.rectangle((49,863,854,867),fill=GRID)
    d.rectangle((49,863,49+int(805*(t%6)/6),867),fill=ACID)
    return im

FRAMES=72
FPS=12
frames=[render(i/FPS) for i in range(FRAMES)]
master=frames[10].quantize(colors=88,method=Image.Quantize.FASTOCTREE)
q=[f.quantize(palette=master,dither=Image.Dither.NONE) for f in frames]
q[0].save(ASSET/'hero.gif',save_all=True,append_images=q[1:],duration=round(1000/FPS),loop=0,optimize=True,disposal=2)
frames[10].save(ASSET/'hero-still.png',optimize=True)
mf=[render_mobile(i/FPS) for i in range(FRAMES)]
mp=mf[10].quantize(colors=88,method=Image.Quantize.FASTOCTREE)
mq=[f.quantize(palette=mp,dither=Image.Dither.NONE) for f in mf]
mq[0].save(ASSET/'hero-mobile.gif',save_all=True,append_images=mq[1:],duration=round(1000/FPS),loop=0,optimize=True,disposal=2)
mf[10].save(ASSET/'hero-mobile-still.png',optimize=True)
print('Generated two animated GIFs: desktop and mobile, 72 frames each.')
