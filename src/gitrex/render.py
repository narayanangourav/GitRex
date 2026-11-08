"""Deterministic naturalistic 2-D compositing and animated GIF creation."""
from __future__ import annotations

import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from .model import LEVELS, RexState, derive

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


def _scene(background, sprite, state: RexState, t, size):
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
    y=round(h*.86-sh*.948-bounce)
    image=background.copy()
    # Grounding shadow moves with the feet.
    shadow=Image.new('RGBA',(w,h),(0,0,0,0))
    d=ImageDraw.Draw(shadow)
    rx=round(w*.23*scale); ry=round(h*.025*scale)
    cx=round(w*.55+offset_x); cy=round(h*.856)
    d.ellipse((cx-rx,cy-ry,cx+rx,cy+ry),fill=(0,0,0,125))
    shadow=shadow.filter(ImageFilter.GaussianBlur(max(2,int(w*.012))))
    image.alpha_composite(shadow)
    image.alpha_composite(dinosaur,(x,y))
    return image


def _draw_roadmap(draw, state: RexState, width: int, height: int) -> None:
    ratio = width / 1200
    panel_height = round(184 * max(0.72, ratio))
    panel_top = height - panel_height - 14
    panel_left = 15
    panel_right = width - 15
    draw.rounded_rectangle(
        (panel_left, panel_top, panel_right, height - 14),
        radius=15,
        fill=(12, 24, 20, 224),
    )

    current = LEVELS[state.level]
    next_level = LEVELS[state.level + 1] if state.level + 1 < len(LEVELS) else None
    compact = width < 1100
    heading_font = font(max(10, round(18 * ratio)), bold=True)
    status_font = font(max(8, round(18 * ratio)), bold=True)
    heading_y = panel_top + (8 if compact else 13)
    draw.text((panel_left + 22, heading_y), 'EVOLUTION PATH', font=heading_font, fill='#d8c7a4')
    current_label = f'CURRENT · LEVEL {state.level}  {current.name.upper()}'
    next_label = f'NEXT → LEVEL {state.level + 1}  {next_level.name.upper()}' if next_level else 'NEXT · MAX LEVEL REACHED'
    status_text = f'{current_label}    {next_label}'
    if compact:
        status_y = panel_top + 24
        status_width = draw.textlength(status_text, font=status_font)
        if status_width > panel_right - panel_left - 32:
            status_font = font(max(7, round(15 * ratio)), bold=True)
            status_width = draw.textlength(status_text, font=status_font)
        draw.text(((width - status_width) / 2, status_y), status_text, font=status_font, fill='#fff1dc')
        node_offset = 50
        level_offset = 63
        stage_offset = 78
        description_offset = 95
        status_offset = 116
    else:
        status_width = draw.textlength(status_text, font=status_font)
        draw.text((panel_right - 22 - status_width, heading_y), status_text, font=status_font, fill='#fff1dc')
        node_offset = 59
        level_offset = 75
        stage_offset = 95
        description_offset = 121
        status_offset = 145

    center_inset = max(28, round(width * 0.075))
    first_center = panel_left + center_inset
    last_center = panel_right - center_inset
    centers = [round(first_center + (last_center - first_center) * index / (len(LEVELS) - 1)) for index in range(len(LEVELS))]
    node_y = panel_top + node_offset
    spacing = centers[1] - centers[0]
    for index in range(len(centers) - 1):
        segment_color = '#86a97a' if index < state.level else '#58675c'
        draw.line((centers[index], node_y, centers[index + 1], node_y), fill=segment_color, width=4)

    for index, (center, level) in enumerate(zip(centers, LEVELS)):
        if index < state.level:
            status = 'COMPLETE'
            color = '#a7c29a'
        elif index == state.level:
            status = 'CURRENT'
            color = '#f0bd72'
        elif index == state.level + 1:
            status = 'NEXT'
            color = '#e1d0ad'
        else:
            status = 'FUTURE'
            color = '#9aa89d'

        if index == state.level:
            highlight_half_width = min(98, round(spacing * 0.45))
            draw.rounded_rectangle(
                (center - highlight_half_width, panel_top + (38 if compact else 43), center + highlight_half_width, height - 24),
                radius=10,
                fill=(217, 160, 87, 32),
                outline=(240, 189, 114, 140),
                width=1,
            )
        radius = 9 if index == state.level else 7
        draw.ellipse((center - radius, node_y - radius, center + radius, node_y + radius), fill=color)

        level_label = f'LEVEL {index}'
        level_font = font(max(9, round(15 * ratio)), bold=True)
        stage_font = font(max(10, round(20 * ratio)), bold=True)
        description_font_size = max(8, round(14 * ratio))
        description_font = font(description_font_size)
        status_font_small = font(max(7, round(13 * ratio)), bold=True)
        draw.text((center - draw.textlength(level_label, font=level_font) / 2, panel_top + level_offset), level_label, font=level_font, fill='#d3dfd1')
        draw.text((center - draw.textlength(level.name, font=stage_font) / 2, panel_top + stage_offset), level.name, font=stage_font, fill='#fff1dc' if index == state.level else color)
        description_words = level.description.split()
        description_lines: list[str] = []
        current_line = ''
        description_width = max(45, spacing - 8)
        for word in description_words:
            candidate = f'{current_line} {word}'.strip()
            if current_line and draw.textlength(candidate, font=description_font) > description_width:
                description_lines.append(current_line)
                current_line = word
            else:
                current_line = candidate
        if current_line:
            description_lines.append(current_line)
        for line_number, line in enumerate(description_lines[:2]):
            draw.text(
                (center - draw.textlength(line, font=description_font) / 2, panel_top + description_offset + line_number * (description_font_size + 1)),
                line,
                font=description_font,
                fill='#c1cdc2',
            )
        draw.text((center - draw.textlength(status, font=status_font_small) / 2, panel_top + status_offset), status, font=status_font_small, fill=color)


def _ui(image, state: RexState, footer=True, demo=False):
    w,h=image.size
    overlay=Image.new('RGBA',(w,h),(0,0,0,0))
    d=ImageDraw.Draw(overlay)
    d.rounded_rectangle((15,15,min(w-15,round(w*.43)),96),radius=13,fill=(12,24,20,198))
    title_font_size = max(22, round(w * 0.028))
    subtitle_font_size = max(10, round(w * 0.0125))
    if w < 700:
        d.text((36,20),'LEVEL EVOLUTION',font=font(subtitle_font_size,True),fill='#b6c4b1')
        d.text((34,39),'GitRex',font=font(title_font_size,True),fill='#fff1dc')
    else:
        d.text((34,22),'GitRex',font=font(title_font_size,True),fill='#fff1dc')
        d.text((36,round(w * 0.056)),'LEVEL EVOLUTION',font=font(subtitle_font_size,True),fill='#b6c4b1')
    if footer:
        _draw_roadmap(d, state, w, h)
    if demo:
        d.rounded_rectangle((w-139,18,w-18,50),radius=8,fill=(113,62,27,225))
        d.text((w-123,26),'DEMO DATA',font=font(14,True),fill='#fff5df')
    return Image.alpha_composite(image,overlay)


def render(snapshot:dict, output_dir:Path, width=1200, frames=12, demo=False) -> dict:
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
    current_level = LEVELS[state.level]
    next_level = LEVELS[state.level+1] if state.level + 1 < len(LEVELS) else None
    public_levels = [
        {
            'level': index,
            'stage': level.name,
            'description': level.description,
            'status': ('complete' if index < state.level else 'current' if index == state.level else 'next' if index == state.level + 1 else 'future'),
        }
        for index, level in enumerate(LEVELS)
    ]
    safe_state = {
        'current': {'level': state.level, 'stage': current_level.name, 'description': current_level.description},
        'next': ({'level': state.level + 1, 'stage': next_level.name, 'description': next_level.description} if next_level else None),
        'levels': public_levels,
    }
    html_path.write_text('''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GitRex Preview</title><style>body{background:#0b1412;color:#f5e7d0;
font:16px system-ui;margin:0;padding:30px;text-align:center}img{width:min(100%,1400px);
border-radius:15px;box-shadow:0 15px 55px #0009}p{color:#afc2b4}</style></head>
<body><h1>GitRex</h1><p>Level-by-level T-Rex evolution'''+(' · <strong>DEMO DATA</strong>' if demo else '')+'''</p>
<img src="trex.gif" alt="GitRex level progression from Hatchling to Apex Rex">
<p>See the current level, completed stages, and next evolution.</p>
</body></html>''',encoding='utf-8')
    summary_path.write_text(json.dumps({'schema_version':2, **safe_state},indent=2)+'\n',encoding='utf-8')
    return {'gif':str(gif_path),'png':str(png_path),'preview':str(html_path),
            'summary':str(summary_path),'size_bytes':gif_path.stat().st_size,
            'state':safe_state['current']}
