"""Deterministic naturalistic 2-D compositing and animated GIF creation."""
from __future__ import annotations

import html
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from .model import derive

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
ASSETS = PACKAGE_ROOT/'assets'


def font(size:int, bold=False):
    candidates = (
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        'C:/Windows/Fonts/segoeuib.ttf' if bold else 'C:/Windows/Fonts/segoeui.ttf',
        'C:/Windows/Fonts/arialbd.ttf' if bold else 'C:/Windows/Fonts/arial.ttf',
    )
    for c in candidates:
        try:
            return ImageFont.truetype(c,size)
        except OSError:
            pass
    return ImageFont.load_default()


def _draw_pill(draw, xy, value, color, fontsize=17):
    x,y=xy
    f=font(fontsize,bold=True)
    width=round(draw.textlength(value,font=f))+26
    draw.rounded_rectangle((x,y,x+width,y+fontsize+20),radius=10,fill=(19,30,27,215))
    draw.text((x+13,y+8),value,font=f,fill=color)
    return width


def _scene(background, sprite, state, t, size):
    w,h=size
    mode=state.behavior
    phase=2*math.pi*t
    bounce=(1.8 if mode=='walk' else 1.1 if mode=='idle' else 2.5)*abs(math.sin(phase))
    offset_x=(6 if mode=='walk' else 2)*math.sin(phase)
    breathe=(0.0035 if mode!='roar' else 0.007)*math.sin(phase)
    scale=state.scale*(1+breathe)
    # Scale the same original procedurally illustrated dinosaur.
    sw,sh=max(1,int(w*scale)),max(1,int(h*scale))
    dinosaur=sprite.resize((sw,sh),Image.Resampling.LANCZOS)
    x=round(w*.5-sw*.5+offset_x)
    y=round(h*.948-sh*.948-bounce)
    image=background.copy()
    # Grounding shadow moves with the feet.
    shadow=Image.new('RGBA',(w,h),(0,0,0,0))
    d=ImageDraw.Draw(shadow)
    rx=round(w*.23*scale); ry=round(h*.025*scale)
    cx=round(w*.55+offset_x); cy=round(h*.944)
    d.ellipse((cx-rx,cy-ry,cx+rx,cy+ry),fill=(0,0,0,125))
    shadow=shadow.filter(ImageFilter.GaussianBlur(max(2,int(w*.012))))
    image.alpha_composite(shadow)
    image.alpha_composite(dinosaur,(x,y))
    return image


def _ui(image, state, footer=True, demo=False):
    w,h=image.size
    overlay=Image.new('RGBA',(w,h),(0,0,0,0))
    d=ImageDraw.Draw(overlay)
    d.rounded_rectangle((15,15,min(w-15,round(w*.61)),87),radius=13,fill=(12,24,20,198))
    accent=state.language_color
    try:
        Image.new('RGB',(1,1),accent)
    except ValueError:
        accent='#dca969'
    d.text((34,27),'GitRex',font=font(29,True),fill='#fff1dc')
    d.text((34,62),'YOUR ACTIVITY. YOUR T-REX.',font=font(12,True),fill='#b6c4b1')
    if w>=660:
        d.text((200,33),'@'+state.login,font=font(15,True),fill='#f3dfbf')
    if footer:
        footer_height=76
        d.rounded_rectangle((15,h-footer_height-13,w-15,h-13),radius=12,fill=(12,24,20,210))
        labels=[f'{state.contributions:,} contributions',f'Level {state.level} / 5',state.stage]
        x=27
        if w < 640:
            labels=[f'{state.contributions:,} contributions',state.stage]
        for i,value in enumerate(labels):
            text_size=13 if w<640 else 16
            x+=_draw_pill(d,(x,h-footer_height-1),value,'#fff3df' if i!=len(labels)-1 else accent,text_size)+8
    if demo:
        d.rounded_rectangle((w-139,18,w-18,50),radius=8,fill=(113,62,27,225))
        d.text((w-123,26),'DEMO DATA',font=font(14,True),fill='#fff5df')
    return Image.alpha_composite(image,overlay)


def render(snapshot:dict, output_dir:Path, width=720, frames=12, demo=False) -> dict:
    if not 360<=width<=1400:
        raise ValueError('Width must be between 360 and 1400')
    if not 4<=frames<=30:
        raise ValueError('Frames must be between 4 and 30')
    state=derive(snapshot)
    output_dir=Path(output_dir)
    output_dir.mkdir(parents=True,exist_ok=True)
    h=round(width*2/3)
    size=(width,h)
    background=Image.open(ASSETS/'forest_original.png').convert('RGBA').resize(size,Image.Resampling.LANCZOS)
    sprite=Image.open(ASSETS/'trex_original.png').convert('RGBA').resize(size,Image.Resampling.LANCZOS)
    # RGB compositing avoids color leakage from transparent pixels.
    composed=[]
    for index in range(frames):
        scene=_scene(background,sprite,state,index/frames,size)
        scene=_ui(scene,state,demo=demo)
        composed.append(scene.convert('RGB'))
    png_path=output_dir/'trex.png'
    gif_path=output_dir/'trex.gif'
    html_path=output_dir/'preview.html'
    summary_path=output_dir/'summary.json'
    composed[0].save(png_path,optimize=True)
    # Use a shared image palette for smooth playback and smaller assets.
    palette=composed[0].quantize(colors=96,method=Image.Quantize.MEDIANCUT)
    indexed=[]
    for f in composed:
        indexed.append(f.quantize(palette=palette,dither=Image.Dither.NONE))
    indexed[0].save(gif_path,save_all=True,append_images=indexed[1:],
                    duration=max(50,round(1600/frames)),loop=0,optimize=True,disposal=2)
    safe_login=html.escape(state.login,quote=True)
    html_path.write_text('''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GitRex Preview</title><style>body{background:#0b1412;color:#f5e7d0;
font:16px system-ui;margin:0;padding:30px;text-align:center}img{width:min(100%,900px);
border-radius:15px;box-shadow:0 15px 55px #0009}p{color:#afc2b4}</style></head>
<body><h1>GitRex</h1><p>@'''+safe_login+''' · contribution-driven T-Rex'''+(' · <strong>DEMO DATA</strong>' if demo else '')+'''</p>
<img src="trex.gif" alt="Animated T-Rex powered by GitHub contributions">
<p>Rendered from original procedural GitRex artwork. This preview works offline.</p>
</body></html>''',encoding='utf-8')
    summary_path.write_text(json.dumps({'schema_version':1, 'mode':'demo' if demo else 'live-or-imported', **state.to_dict()},indent=2)+'\n',encoding='utf-8')
    return {'gif':str(gif_path),'png':str(png_path),'preview':str(html_path),
            'summary':str(summary_path),'size_bytes':gif_path.stat().st_size,
            'state':state.to_dict()}
