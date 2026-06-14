from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
import random
random.seed(11)
W,H=1200,630

# ---------- 1. sky gradient: soot black (top) -> ember (low horizon) ----------
def lerp(a,b,t): return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))
stops=[(0.00,(7,6,6)),(0.40,(20,14,11)),(0.62,(46,24,15)),(0.78,(120,52,24)),(0.88,(196,98,42)),(0.96,(228,138,66)),(1.0,(150,64,30))]
def gcol(p):
    for i in range(len(stops)-1):
        p0,c0=stops[i]; p1,c1=stops[i+1]
        if p<=p1:
            t=(p-p0)/(p1-p0) if p1>p0 else 0; return lerp(c0,c1,t)
    return stops[-1][1]
img=Image.new("RGB",(W,H)); d=ImageDraw.Draw(img)
for y in range(H): d.line([(0,y),(W,y)],fill=gcol(y/H))

# ---------- 2. furnace glow (soft, behind the figures) ----------
glow=Image.new("RGB",(W,H),(0,0,0)); gd=ImageDraw.Draw(glow)
gd.ellipse([W*0.16,H*0.40,W*0.99,H*0.90],fill=(255,166,82))
gd.ellipse([W*0.40,H*0.48,W*0.84,H*0.82],fill=(255,206,140))
gd.ellipse([W*0.52,H*0.54,W*0.74,H*0.76],fill=(255,228,176))
glow=glow.filter(ImageFilter.GaussianBlur(70))
img=ImageChops.screen(img,glow)
d=ImageDraw.Draw(img)  # re-bind: screen() returned a NEW image

# ---------- 3. smoke plumes (blurred, rising) ----------
smoke=Image.new("RGBA",(W,H),(0,0,0,0)); smd=ImageDraw.Draw(smoke)
for (x,w,col) in [(150,70,(40,28,22,120)),(330,90,(54,34,24,120)),(560,80,(40,28,22,110)),(900,100,(60,40,28,120)),(1060,70,(40,28,22,110))]:
    for k in range(7):
        yy=H*0.50-k*46; ww=w+k*14
        smd.ellipse([x-ww//2,yy-34,x+ww//2,yy+34],fill=col)
smoke=smoke.filter(ImageFilter.GaussianBlur(26))
img.paste(smoke,(0,0),smoke)

# ---------- 4. industrial skyline (chimneys + sheds), pure black, lit windows ----------
BK=(6,5,4)
hz=int(H*0.62)
d.rectangle([0,hz,W,H],fill=BK)  # ground mass
# factory sheds (sawtooth roofs)
for (x,w,h) in [(60,150,70),(250,120,55),(840,170,80),(1030,140,60)]:
    d.rectangle([x,hz-h,x+w,hz],fill=BK)
    for i in range(0,w,28): d.polygon([(x+i,hz-h),(x+i+14,hz-h-16),(x+i+28,hz-h)],fill=BK)
# chimneys
for (x,top,w) in [(120,250,26),(186,210,22),(300,300,20),(905,265,30),(1075,235,24)]:
    d.rectangle([x,top,x+w,hz],fill=BK); d.rectangle([x-4,top,x+w+4,top+10],fill=BK)
# lit windows (tiny ember dots)
for (x,y) in [(70,430),(90,430),(110,430),(870,420),(890,420),(1040,440),(1060,440)]:
    d.rectangle([x,y,x+7,y+9],fill=(226,150,70))

# ---------- 5. the walking gang: flat-cap silhouettes, backlit ----------
def man(x,feet,h,col=BK):
    s=h/250.0; top=feet-h; sw=50*s; hip=42*s
    d.polygon([(x-sw/2,top+46*s),(x+sw/2,top+46*s),(x+hip/2+9*s,feet),(x-hip/2-9*s,feet)],fill=col)  # coat
    d.ellipse([x-sw/2,top+30*s,x+sw/2,top+64*s],fill=col)                                            # shoulders
    hr=15*s
    d.ellipse([x-hr,top+8*s,x+hr,top+40*s],fill=col)                                                 # head
    cw=hr*2.4
    d.ellipse([x-cw/2,top,x+cw/2,top+17*s],fill=col)                                                 # flat cap
    pk=1 if x<W/2 else -1
    d.polygon([(x+pk*cw*0.35,top+8*s),(x+pk*cw*0.85,top+11*s),(x+pk*cw*0.35,top+17*s)],fill=col)     # peak
# back row (smaller, hazier) then front row (bigger)
for (x,f,h) in [(470,556,168),(700,550,158),(585,544,138)]: man(x,f,h)
for (x,f,h) in [(345,604,256),(545,616,288),(745,606,262),(910,594,228)]: man(x,f,h)
# rising embers
for i in range(36):
    ex=random.randint(120,1080); ey=random.randint(300,560); r=random.choice([1,1,2])
    d.ellipse([ex,ey,ex+r,ey+r],fill=(255,190,110))

# ---------- 5b. wet-street reflection of the furnace glow ----------
refl=Image.new("RGB",(W,H),(0,0,0)); rd=ImageDraw.Draw(refl)
rd.ellipse([W*0.30,H*0.66,W*0.86,H*1.06],fill=(84,38,16))
for sx in range(340,930,24):
    rd.line([(sx,hz),(sx+random.randint(-12,12),H)],fill=(66,30,14),width=3)
refl=refl.filter(ImageFilter.GaussianBlur(28))
img=ImageChops.screen(img,refl); d=ImageDraw.Draw(img)
# ---------- 6. vignette ----------
vig=Image.new("L",(W,H),96); vd=ImageDraw.Draw(vig)
vd.ellipse([int(W*0.04),int(-H*0.10),int(W*0.96),int(H*1.18)],fill=255)
vig=vig.filter(ImageFilter.GaussianBlur(140))
img=ImageChops.multiply(img,Image.merge("RGB",(vig,vig,vig)))

# ---------- 7. film grain ----------
noise=Image.effect_noise((W,H),26).convert("RGB")
img=Image.blend(img,ImageChops.overlay(img,noise),0.05)

# ---------- 8. typography ----------
d=ImageDraw.Draw(img,"RGBA")
def font(paths,sz):
    for p in paths:
        try: return ImageFont.truetype(p,sz)
        except Exception: pass
    return ImageFont.load_default()
serif=["/System/Library/Fonts/Supplemental/Songti.ttc","/System/Library/Fonts/STSong.ttf","/System/Library/Fonts/PingFang.ttc"]
sans=["/System/Library/Fonts/PingFang.ttc","/System/Library/Fonts/Hiragino Sans GB.ttc"]
mono=["/System/Library/Fonts/Menlo.ttc","/System/Library/Fonts/Courier.ttc"]
f_t=font(serif,98); f_s=font(sans,34); f_e=font(mono,23); f_k=font(sans,22)
# thin editorial frame
d.rectangle([34,34,W-34,H-34],outline=(214,196,160,90),width=2)
d.rectangle([42,42,W-42,H-42],outline=(214,196,160,40),width=1)
# kicker
d.text((70,86),"CASE FILE · 案卷",font=f_k,fill=(202,166,74,255))
d.line([(70,120),(330,120)],fill=(214,69,47,220),width=3)
# title (with soft shadow for legibility over smoke)
d.text((68,138),"浴血黑帮 · 卷宗",font=f_t,fill=(10,7,5,180))
d.text((66,136),"浴血黑帮 · 卷宗",font=f_t,fill=(245,236,218,255))
# subtitle
d.text((70,252),"谢尔比家二十年 · 六季全剧情",font=f_s,fill=(214,182,120,255))
d.text((72,300),"Peaky Blinders Dossier   ·   1919–1934   ·   S1–S6",font=f_e,fill=(190,172,138,235))

img.save("/Users/cry/Desktop/peaky-dossier/og.png",quality=92)
print("saved",img.size)
