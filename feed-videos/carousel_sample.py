"""Example carousel (Practice question format) - 1080x1350, 6 slides."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gg_engine as G
from gg_engine import T, ROW, card, stack, pill, FN, NAVY, TEAL, GOLD, CREAM, WHITE, GRAY, LIGHT, RED, PEACH, NAVY2, LINE, SOFT
from PIL import Image, ImageDraw
import os

W, H = 1080, 1350; TOTAL = 6; OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/carousel'
os.makedirs(OUT, exist_ok=True)

def paper(n, dark=False):
    if dark:
        im = Image.new('RGB', (W, H), NAVY); d = ImageDraw.Draw(im)
        d.ellipse((780, -240, 1260, 240), fill=NAVY2)
        lab, cnt = GOLD, LIGHT
    else:
        im = Image.new('RGB', (W, H), CREAM); d = ImageDraw.Draw(im)
        for y in range(230, H, 74): d.line((0, y, W, y), fill=(206, 222, 230), width=3)
        d.line((118, 0, 118, H), fill=(232, 160, 150), width=4)
        lab, cnt = TEAL, GRAY
    d.text((150 if not dark else 90, 95), 'THE GOOD GRADE', font=FN('inter', 'Bold', 32), fill=lab, anchor='lm')
    d.text((W - 90, 95), f'{n}/{TOTAL}', font=FN('inter', 'Bold', 32), fill=cnt, anchor='rm')
    return im, d

def paste(im, src, x, y): im.paste(src, (int(x), int(y)), src)

def swipe(d, text='Swipe', dark=False):
    c = GOLD if dark else TEAL; f = FN('inter', 'Bold', 36)
    x = W - 90 - d.textlength(text, font=f) - 70; y = H - 110
    d.text((x, y), text, font=f, fill=c)
    ax, ay = W - 140, y + 22
    d.line((ax, ay, ax + 46, ay), fill=c, width=6); d.polygon([(ax + 50, ay), (ax + 32, ay - 14), (ax + 32, ay + 14)], fill=c)

def circle(d, box, c, pad=16, w=9):
    pts = G.p_circle(box, pad); d.line(pts, fill=c, width=w, joint='curve')

CH = ['A.  ¼ cup', 'B.  ⅜ cup', 'C.  ½ cup', 'D.  1½ cups']
def choices(im, y, hi=None, dim=False):
    pos = [(170, y), (590, y), (170, y + 100), (590, y + 100)]; boxes = []
    for i, c in enumerate(CH):
        col = (170, 180, 190) if dim and i != hi else NAVY
        t = T(c, 'disp', 'SemiBold', 60, col); paste(im, t, *pos[i])
        boxes.append((pos[i][0], pos[i][1] + 4, pos[i][0] + t.width - 20, pos[i][1] + t.height - 8))
    return boxes

slides = []
# 1 hook
im, d = paper(1)
paste(im, pill('PRACTICE QUESTION', TEAL, WHITE, 34), 150, 190)
paste(im, T("Half a recipe.\n¾ cup of sugar.\nHow much do you need?", 'disp', 'Black', 86, NAVY, maxw=860), 140, 290)
choices(im, 790)
paste(im, T("Got your answer? Swipe to check.", 'disp', 'SemiBold', 46, GRAY, maxw=800), 150, 1060)
swipe(d); slides.append(im)

# 2 hint
im, d = paper(2)
paste(im, T("HINT", 'inter', 'Bold', 40, TEAL), 150, 230)
paste(im, T("“Half of” means", 'disp', 'Black', 92, NAVY), 140, 290)
paste(im, T("times ½.", 'disp', 'Black', 92, NAVY, hl=('times ½', GOLD)), 140, 405)
paste(im, T("So half of ¾ cup\nis the same as ½ × ¾.", 'disp', 'Medium', 54, GRAY, maxw=820), 150, 600)
paste(im, T("Last chance to change your answer.", 'hand', 'Bold', 54, TEAL, maxw=820), 150, 900)
swipe(d); slides.append(im)

# 3 work
im, d = paper(3)
paste(im, T("WORK IT OUT", 'inter', 'Bold', 40, TEAL), 150, 230)
r1, _ = ROW([{'frac': ('1', '2')}, ' × ', {'frac': ('3', '4')}], 'hand', 'Bold', 110); paste(im, r1, 150, 300)
paste(im, T("multiply straight across", 'hand', 'Bold', 50, GRAY), 160, 600)
r2, b2 = ROW(['= ', {'frac': ('1 × 3', '2 × 4')}, ' = ', {'frac': ('3', '8'), 'c': TEAL}], 'hand', 'Bold', 104); paste(im, r2, 150, 690)
bb = b2[-1]; circle(d, (bb[0] + 150, bb[1] + 690, bb[2] + 150, bb[3] + 690), TEAL, 14)
swipe(d); slides.append(im)

# 4 answer + trap
im, d = paper(4)
paste(im, T("ANSWER", 'inter', 'Bold', 40, TEAL), 150, 230)
paste(im, T("B.  ⅜ cup", 'disp', 'Black', 120, NAVY), 140, 290)
boxes = choices(im, 520, hi=1, dim=True); circle(d, boxes[1], TEAL, 18)
trap = card(stack([T("THE TRAP: D", 'inter', 'Bold', 38, RED),
                   T("Cutting the bottom number in half (4 → 2) gives 3/2 = 1½ cups. That doubles the sugar instead.", 'disp', 'SemiBold', 50, NAVY, maxw=760)], 14), 44, fill=WHITE)
paste(im, trap, 130, 790)
swipe(d); slides.append(im)

# 5 kitchen version
im, d = paper(5)
paste(im, T("IN A REAL KITCHEN", 'inter', 'Bold', 40, TEAL), 150, 230)
paste(im, T("No ⅜ cup in the drawer?", 'disp', 'Black', 86, NAVY, maxw=860), 140, 290)
r, _ = ROW(['¼ cup  +  2 tbsp'], 'hand', 'Bold', 110, TEAL); paste(im, r, 150, 560)
paste(im, T("⅛ cup is 2 tablespoons,\nand ¼ + ⅛ = ⅜.", 'disp', 'Medium', 54, GRAY, maxw=820), 150, 800)
swipe(d); slides.append(im)

# 6 CTA (try 10 free questions)
im, d = paper(6, dark=True)
paste(im, T("Want more like this?", 'disp', 'Black', 100, WHITE, maxw=880), 80, 260)
d.rounded_rectangle((90, 520, 250, 534), 7, fill=GOLD)
paste(im, T("Practice math and science on our site, at your own pace.", 'inter', 'SemiBold', 46, LIGHT, maxw=880), 80, 580)
d.rounded_rectangle((90, 860, W - 90, 980), 40, fill=GOLD)
d.text((W // 2, 920), 'Try 10 free questions: link in bio', font=FN('inter', 'Bold', 44), fill=NAVY, anchor='mm')
d.text((W // 2, H - 90), 'goodgradetutoring.com', font=FN('inter', 'SemiBold', 36), fill=LIGHT, anchor='mm')
slides.append(im)

for i, s in enumerate(slides, 1): s.save(f'{OUT}/practice_q_carousel_{i}.jpg', quality=92)
tw = 360; th = int(tw * H / W); pad = 20
sheet = Image.new('RGB', (pad + 3 * (tw + pad), pad + 2 * (th + pad)), (235, 235, 235))
for i, s in enumerate(slides): sheet.paste(s.resize((tw, th)), (pad + (i % 3) * (tw + pad), pad + (i // 3) * (th + pad)))
sheet.save(f'{OUT}/practice_q_carousel_overview.jpg', quality=90); print('ok')
