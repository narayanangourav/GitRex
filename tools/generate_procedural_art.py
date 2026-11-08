"""Create GitRex's original illustrated artwork from first principles.

No downloaded images, model weights, fonts, photographs or source artwork.
All shapes, color gradients, scales, plants and shadows are drawn with Pillow
and deterministic pseudo-random numbers. Re-running produces the same assets.

License: MIT; artwork is original procedural output from this included source.
"""
from __future__ import annotations
import argparse
import math
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageChops

WIDTH, HEIGHT = 1200, 800
ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets' / 'procedural'
SEED = 351714


def spline(points, closed=True, parts=8):
    """Sample a smooth Catmull-Rom curve; endpoints are defined in source."""
    n = len(points)
    if n < 3: return points
    result = []
    count = n if closed else n-1
    for k in range(count):
        p0 = points[(k-1) % n] if closed or k else points[0]
        p1, p2 = points[k], points[(k+1)%n]
        p3 = points[(k+2)%n] if closed or k+2<n else points[-1]
        for j in range(parts):
            t = j/parts
            t2, t3 = t*t, t*t*t
            x = .5*((2*p1[0])+(-p0[0]+p2[0])*t+(2*p0[0]-5*p1[0]+4*p2[0]-p3[0])*t2+(-p0[0]+3*p1[0]-3*p2[0]+p3[0])*t3)
            y = .5*((2*p1[1])+(-p0[1]+p2[1])*t+(2*p0[1]-5*p1[1]+4*p2[1]-p3[1])*t2+(-p0[1]+3*p1[1]-3*p2[1]+p3[1])*t3)
            result.append((round(x), round(y)))
    if not closed: result.append(points[-1])
    return result


def mask_polygon(points):
    m = Image.new('L', (WIDTH,HEIGHT), 0)
    ImageDraw.Draw(m).polygon(spline(points), fill=255)
    return m


def gradient_layer(mask, upper, lower, left_to_right=False):
    base = Image.new('RGBA',(WIDTH,HEIGHT))
    d = ImageDraw.Draw(base)
    side = WIDTH if left_to_right else HEIGHT
    for pos in range(side):
        f = pos / (side-1)
        # Rich highlights toward the upper/left side, warm shadows on the lower edge.
        col = tuple(round(upper[k]*(1-f) + lower[k]*f) for k in range(3))+(255,)
        if left_to_right: d.line((pos,0,pos,HEIGHT),fill=col)
        else: d.line((0,pos,WIDTH,pos),fill=col)
    base.putalpha(mask)
    return base


def draw_shape(canvas, points, upper, lower, outline=(42,42,30), width=3):
    m=mask_polygon(points)
    canvas.alpha_composite(gradient_layer(m,upper,lower))
    p=spline(points)
    ImageDraw.Draw(canvas).line(p+[p[0]], fill=outline+(255,),width=width, joint='curve')
    return m


def stroke(canvas, pts, color, width=2, smooth=True):
    p=spline(pts,False) if smooth and len(pts)>2 else pts
    ImageDraw.Draw(canvas).line(p,fill=color,width=width,joint='curve')


def textured_scales(canvas, region, box, seed, count, radius=4):
    rng=random.Random(seed)
    layer=Image.new('RGBA',(WIDTH,HEIGHT))
    d=ImageDraw.Draw(layer)
    xmin,ymin,xmax,ymax=box
    for _ in range(count):
        x=rng.randrange(xmin,xmax); y=rng.randrange(ymin,ymax)
        if region.getpixel((x,y)) < 200: continue
        r=rng.randint(1,radius)
        if rng.random()<.68:
            col=(23,29,19,rng.randint(22,68))
            d.arc((x-r*2,y-r,x+r*2,y+r), 195,345,fill=col,width=1)
        else:
            col=(220,192,126,rng.randint(18,60))
            d.ellipse((x-r,y-r//2,x+r,y+r//2),fill=col)
    layer.putalpha(ImageChops.multiply(layer.getchannel('A'),region))
    canvas.alpha_composite(layer)


def forest():
    rng=random.Random(SEED)
    scene=Image.new('RGBA',(WIDTH,HEIGHT),(0,0,0,255))
    d=ImageDraw.Draw(scene)
    for y in range(HEIGHT):
        f=y/HEIGHT
        top=(120,145,119); lower=(36,59,41)
        col=tuple(round(top[k]*(1-f)+lower[k]*f) for k in range(3))+(255,)
        d.line((0,y,WIDTH,y), fill=col)
    # Hazy backlit canopy and distant tree trunks.
    haze=Image.new('RGBA',(WIDTH,HEIGHT),(0,0,0,0)); h=ImageDraw.Draw(haze)
    h.ellipse((560,-180,1140,500), fill=(241,224,160,95))
    h.ellipse((730,40,1200,440), fill=(252,218,141,45))
    scene=Image.alpha_composite(scene,haze.filter(ImageFilter.GaussianBlur(95)))
    bg=Image.new('RGBA',(WIDTH,HEIGHT),(0,0,0,0)); b=ImageDraw.Draw(bg)
    for i in range(38):
        x=rng.randrange(-100,WIDTH+100); thick=rng.randint(5,25)
        tone=rng.randint(26,75)
        b.line((x+rng.randint(-70,70),-50,x,710), fill=(tone,tone+19,tone+2,rng.randint(50,120)), width=thick)
        for _ in range(3):
            cx=x+rng.randint(-100,100); cy=rng.randrange(50,420)
            b.ellipse((cx-95,cy-42,cx+95,cy+42),fill=(40,85,45,rng.randint(15,70)))
    scene=Image.alpha_composite(scene,bg.filter(ImageFilter.GaussianBlur(20)))
    trunks=Image.new('RGBA',(WIDTH,HEIGHT),(0,0,0,0)); td=ImageDraw.Draw(trunks)
    for x,width in [(72,53),(248,25),(1023,37),(1170,64)]:
        td.polygon([(x-width//2,-50),(x+width//2,-50),(x+width//3,730),(x-width,730)], fill=(21,45,31,205))
        td.line((x-7,20,x-28,690),fill=(98,118,77,55),width=6)
        for j in range(5):
            y=rng.randrange(45,360)
            ex=x+rng.choice((-1,1))*rng.randrange(110,260)
            td.line(spline([(x,y+60),(x+(ex-x)*.30,y+20),(ex,y-65)],False), fill=(29,53,32,180),width=rng.randint(10,24),joint='curve')
    scene=Image.alpha_composite(scene,trunks.filter(ImageFilter.GaussianBlur(1.2)))
    foliage=Image.new('RGBA',(WIDTH,HEIGHT),(0,0,0,0)); fd=ImageDraw.Draw(foliage)
    for i in range(340):
        x=rng.randint(-100,WIDTH+100);y=rng.choice([rng.randrange(-70,145),rng.randrange(450,710)])
        rad=rng.randrange(10,47)
        fd.ellipse((x-rad,y-rad//2,x+rad,y+rad//2),fill=(rng.randrange(25,72),rng.randrange(62,118),rng.randrange(25,60),rng.randrange(22,85)))
    scene=Image.alpha_composite(scene,foliage.filter(ImageFilter.GaussianBlur(5)))
    # Floor with horizontal root patterns, moss and stones.
    ground=Image.new('RGBA',(WIDTH,HEIGHT)); gd=ImageDraw.Draw(ground)
    gd.polygon([(0,672),(125,654),(280,665),(415,669),(600,658),(780,675),(940,660),(1200,668),(1200,800),(0,800)],fill=(40,53,32,235))
    for _ in range(1350):
        x=rng.randrange(WIDTH);y=rng.randrange(675,799);r=rng.randrange(1,6)
        gd.ellipse((x-r,y-r//2,x+r,y+r//2),fill=(rng.randint(50,98),rng.randint(58,103),rng.randint(30,57),rng.randint(35,130)))
    for _ in range(45):
        x=rng.randrange(WIDTH);y=rng.randrange(680,785);rw=rng.randrange(5,30)
        gd.ellipse((x-rw,y-5,x+rw,y+9),fill=(35,41,31,190))
        gd.arc((x-rw,y-6,x+rw,y+6),180,350,fill=(115,113,83,90),width=2)
    # Ferns and grasses sit in front of the ground, behind sprite.
    for _ in range(95):
        x=rng.randrange(WIDTH);y=rng.randrange(665,775);length=rng.randrange(10,62)
        sign=rng.choice([-1,1]); end=(x+length*sign,y-length)
        gd.line((x,y,*end),fill=(53,98,50,rng.randrange(75,175)),width=2)
        for j in range(1,5):
            xx=x+(end[0]-x)*j/5;yy=y+(end[1]-y)*j/5
            gd.line((xx,yy,xx+11*sign,yy+5),fill=(80,130,65,95),width=2)
    scene=Image.alpha_composite(scene,ground)
    # Soft glow/vignette for readable UI and grounded depth.
    vignette=Image.new('RGBA',(WIDTH,HEIGHT),(0,0,0,0));vd=ImageDraw.Draw(vignette)
    vd.rectangle((0,0,WIDTH,HEIGHT),fill=(0,0,0,18))
    scene=Image.alpha_composite(scene,vignette)
    return scene.convert('RGB')


def dinosaur():
    rng=random.Random(SEED+1)
    c=Image.new('RGBA',(WIDTH,HEIGHT),(0,0,0,0))
    # Far hind limb: shaded and partially obscured by the body.
    backleg=[(666,471),(729,466),(757,504),(752,561),(734,620),(725,684),(739,713),(788,714),(821,736),(825,751),(775,749),(747,739),(710,748),(681,739),(676,716),(672,671),(668,637),(642,584),(639,530)]
    bmask=draw_shape(c,backleg,(64,75,49),(32,39,30),width=4)
    textured_scales(c,bmask,(630,465,825,750),SEED+2,900,3)
    # Tail: muscular at the base, tapering into a flexible balancing tip.
    tail=[(537,411),(466,415),(390,421),(310,448),(232,484),(164,515),(104,530),(44,549),(92,539),(166,534),(246,512),(320,500),(393,520),(475,542),(540,522)]
    tmask=draw_shape(c,tail,(103,104,69),(49,58,39),width=3)
    textured_scales(c,tmask,(50,412,538,550),SEED+3,2800,3)
    stroke(c,[(90,543),(246,501),(360,467),(473,462)],(189,162,100,85),2)
    # Main torso: broad iliac region, heavy belly, tapering shoulders.
    torso=[(443,409),(493,375),(549,355),(625,355),(700,373),(767,391),(813,421),(828,459),(806,505),(768,532),(700,547),(616,554),(535,533),(477,499),(443,460)]
    bodymask=draw_shape(c,torso,(119,117,77),(55,62,42),width=4)
    textured_scales(c,bodymask,(445,356,820,551),SEED+4,4200,5)
    # Fold structures across shoulders and flanks.
    for pts in [[(515,404),(495,443),(512,491)],[(564,387),(552,427),(565,496)],[(654,387),(666,420),(668,468)],[(727,402),(753,438),(744,492)]]:
        stroke(c,pts,(30,39,29,120),5)
        stroke(c,[(x-4,y-5) for x,y in pts],(192,165,111,55),2)
    # Thigh near camera, filled before lower leg.
    thigh=[(562,476),(613,458),(647,480),(648,526),(626,567),(607,608),(583,644),(570,673),(560,704),(581,721),(608,721),(627,739),(613,753),(581,747),(555,745),(532,755),(513,751),(501,743),(506,729),(521,704),(523,664),(526,622),(530,580),(534,541)]
    legmask=draw_shape(c,thigh,(115,111,73),(51,57,39),width=4)
    textured_scales(c,legmask,(501,460,649,756),SEED+5,1400,4)
    stroke(c,[(560,530),(578,559),(563,603),(547,648)],(31,40,26,160),5)
    stroke(c,[(586,613),(581,657),(569,689)],(163,143,92,75),3)
    # Other foot: planted claws visible from behind.
    foot=[(696,720),(744,716),(772,727),(805,724),(830,743),(822,756),(791,752),(766,746),(741,755),(712,749),(694,752),(678,742)]
    fmask=draw_shape(c,foot,(72,75,50),(37,44,33),width=3)
    # Neck is thick, connecting shoulder to skull.
    neck=[(728,420),(765,370),(811,322),(853,276),(891,246),(945,248),(969,282),(956,328),(919,376),(883,418),(825,471),(775,474)]
    nmask=draw_shape(c,neck,(117,113,79),(50,58,43),width=4)
    textured_scales(c,nmask,(731,248,970,476),SEED+6,1900,3)
    for pts in [[(794,353),(838,384),(823,431)],[(837,312),(880,340),(855,394)],[(886,285),(914,322),(887,359)]]:
        stroke(c,pts,(45,49,30,145),4)
    # Tiny forelimbs close to torso, two clawed digits each.
    for pts in [ [(806,430),(809,470),(838,485),(850,513)], [(776,435),(786,477),(809,494),(814,516)] ]:
        stroke(c,pts,(35,43,31,255),15)
        stroke(c,[(x-2,y-3) for x,y in pts],(131,122,77,190),9)
    stroke(c,[(850,513),(843,525),(849,534)],(24,28,23,245),5)
    stroke(c,[(850,513),(861,523),(861,531)],(24,28,23,245),4)
    stroke(c,[(814,516),(808,532),(814,539)],(24,28,23,245),4)
    # Distinct open mouth: lower jaw and shadowed gape drawn under upper skull.
    lowerjaw=[(940,302),(996,329),(1046,342),(1117,333),(1129,345),(1123,359),(1068,374),(1005,368),(960,351),(921,328)]
    draw_shape(c,lowerjaw,(95,85,58),(50,44,34),width=4)
    gape=[(962,275),(1025,278),(1130,289),(1117,337),(1054,344),(999,326),(944,312)]
    draw_shape(c,gape,(66,37,34),(27,20,23),outline=(35,25,21),width=2)
    # Red oral highlights and muscular tongue.
    stroke(c,[(974,310),(1033,317),(1073,324),(1106,321)],(120,64,60,200),7)
    # Upper snout / iconic T-Rex skull and pronounced brow ridge.
    skull=[(879,266),(887,226),(905,190),(942,174),(969,175),(1001,187),(1030,185),(1068,191),(1098,203),(1120,219),(1134,244),(1129,272),(1108,286),(1073,292),(1036,284),(997,276),(970,294),(945,312),(918,310),(899,290)]
    hmask=draw_shape(c,skull,(151,139,94),(74,74,49),width=4)
    textured_scales(c,hmask,(884,175,1130,312),SEED+7,2200,3)
    # Brow orbital ridges and musculature.
    stroke(c,[(921,225),(940,206),(958,200),(973,215)],(63,65,44,220),11)
    stroke(c,[(921,223),(940,203),(957,198),(973,210)],(181,166,114,200),4)
    stroke(c,[(1005,211),(1042,213),(1080,220)],(187,160,108,110),3)
    # Ear + slit pupil + light catch.
    d=ImageDraw.Draw(c)
    d.ellipse((950,221,973,244),fill=(48,42,28,255),outline=(188,166,107,255),width=3)
    d.ellipse((956,223,968,240),fill=(198,150,52,255))
    d.ellipse((960,226,964,240),fill=(22,22,14,255))
    d.ellipse((958,227,961,230),fill=(238,220,177,255))
    d.ellipse((1106,241,1116,248),fill=(30,39,30,255))
    # Fine jaw/tooth contours; teeth are individual triangles, not stickers.
    for j in range(13):
        x=985+j*10; y=int(286+5*math.sin(j*.4))
        length=11+(j%4)*2
        d.polygon([(x,y-1),(x+7,y-1),(x+5,y+length)],fill=(225,211,163,255),outline=(116,104,72,255))
    for j in range(10):
        x=998+j*11; y=int(344-6*math.sin(j*.31))
        d.polygon([(x,y+1),(x+6,y+1),(x+4,y-8-(j%3)*2)],fill=(214,198,159,245))
    stroke(c,[(954,313),(997,326),(1054,340),(1124,337)],(157,119,87,170),3)
    # Subtle darker skin spots, scars and dorsal striping, masked to existing silhouette.
    allmask=c.getchannel('A')
    overlay=Image.new('RGBA',(WIDTH,HEIGHT));od=ImageDraw.Draw(overlay)
    for i in range(1600):
        x=rng.randrange(110,1100);y=rng.randrange(195,720)
        if allmask.getpixel((x,y))<190:continue
        rr=rng.randint(1,4)
        od.ellipse((x-rr,y-rr//2,x+rr,y+rr//2),fill=(20,29,22,rng.randrange(18,90)))
    overlay.putalpha(ImageChops.multiply(overlay.getchannel('A'),allmask))
    c.alpha_composite(overlay)
    # Dorsal ridge marks and subtle highlights.
    stroke(c,[(488,391),(565,366),(640,371),(702,389),(771,410)],(206,187,130,60),4)
    stroke(c,[(465,496),(531,523),(614,545),(699,535)],(28,36,26,85),5)
    # Soft antialiased outline from high-res source drawn directly at target size.
    return c


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output-dir',default=str(ASSETS))
    args=ap.parse_args()
    output=Path(args.output_dir);output.mkdir(parents=True,exist_ok=True)
    bg=output/'forest_procedural.png'; fg=output/'trex_procedural.png'
    forest().save(bg,optimize=True)
    dinosaur().save(fg,optimize=True)
    print(f'Original procedural art generated: {fg} and {bg}')
    print(f'Seed: {SEED}; canvas: {WIDTH}x{HEIGHT}; external assets: none')

if __name__ == '__main__':main()
