"""Two question carousels (Sat Nov 21 + Sun Nov 22, 2026). 1080x1350 + TikTok 1080x1920 copies."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gg_engine as G
from gg_engine import T, ROW, card, stack, pill, FN, NAVY, TEAL, GOLD, CREAM, WHITE, GRAY, LIGHT, RED, NAVY2
from PIL import Image, ImageDraw

W, H = 1080, 1350
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/qc'
os.makedirs(OUT, exist_ok=True)


def paper(n, total, dark=False, style='lined'):
    if dark:
        im = Image.new('RGB', (W, H), NAVY); d = ImageDraw.Draw(im)
        d.ellipse((780, -240, 1260, 240), fill=NAVY2)
        lab, cnt, lx = GOLD, LIGHT, 90
    elif style == 'grid':
        im = Image.new('RGB', (W, H), WHITE); d = ImageDraw.Draw(im)
        for x in range(0, W, 60): d.line((x, 0, x, H), fill=(226, 236, 240), width=2)
        for y in range(0, H, 60): d.line((0, y, W, y), fill=(226, 236, 240), width=2)
        lab, cnt, lx = TEAL, GRAY, 90
    else:
        im = Image.new('RGB', (W, H), CREAM); d = ImageDraw.Draw(im)
        for y in range(230, H, 74): d.line((0, y, W, y), fill=(206, 222, 230), width=3)
        d.line((118, 0, 118, H), fill=(232, 160, 150), width=4)
        lab, cnt, lx = TEAL, GRAY, 150
    d.text((lx, 95), 'THE GOOD GRADE', font=FN('inter', 'Bold', 32), fill=lab, anchor='lm')
    d.text((W - 90, 95), f'{n}/{total}', font=FN('inter', 'Bold', 32), fill=cnt, anchor='rm')
    return im, d


def paste(im, src, x, y): im.paste(src, (int(x), int(y)), src)


def swipe(d, text='Swipe'):
    f = FN('inter', 'Bold', 36)
    x = W - 90 - d.textlength(text, font=f) - 70; y = H - 110
    d.text((x, y), text, font=f, fill=TEAL)
    ax, ay = W - 140, y + 22
    d.line((ax, ay, ax + 46, ay), fill=TEAL, width=6)
    d.polygon([(ax + 50, ay), (ax + 32, ay - 14), (ax + 32, ay + 14)], fill=TEAL)


def circle(d, box, c, pad=16, w=9):
    d.line(G.p_circle(box, pad), fill=c, width=w, joint='curve')


def choices(im, ch, x0, y, hi=None, dim=False, size=60):
    pos = [(x0, y), (x0 + 420, y), (x0, y + 100), (x0 + 420, y + 100)]; boxes = []
    for i, c in enumerate(ch):
        col = (170, 180, 190) if dim and i != hi else NAVY
        t = T(c, 'disp', 'SemiBold', size, col); paste(im, t, *pos[i])
        boxes.append((pos[i][0], pos[i][1] + 4, pos[i][0] + t.width - 20, pos[i][1] + t.height - 8))
    return boxes


def cta(n, total, head, sub, button):
    im, d = paper(n, total, dark=True)
    paste(im, T(head, 'disp', 'Black', 100, WHITE, maxw=880), 80, 260)
    d.rounded_rectangle((90, 520, 250, 534), 7, fill=GOLD)
    paste(im, T(sub, 'inter', 'SemiBold', 46, LIGHT, maxw=880), 80, 580)
    d.rounded_rectangle((90, 860, W - 90, 980), 40, fill=GOLD)
    d.text((W // 2, 920), button, font=FN('inter', 'Bold', 44), fill=NAVY, anchor='mm')
    d.text((W // 2, H - 90), 'goodgradetutoring.com', font=FN('inter', 'SemiBold', 36), fill=LIGHT, anchor='mm')
    return im


def save(slides, name):
    bg_light, bg_grid = CREAM, WHITE
    for i, s in enumerate(slides, 1):
        s.save(f'{OUT}/{name}-{i}.jpg', quality=92)
        # TikTok 1080x1920 copy: slide pasted at y=285 on a matching background
        bg = s.getpixel((5, 5))
        tt = Image.new('RGB', (1080, 1920), bg); tt.paste(s, (0, 285))
        tt.save(f'{OUT}/{name}-tt-{i}.jpg', quality=92)
    return slides


# ---------------- A: rectangle (Sat Nov 21, HS algebra / SAT-ACT) ----------------
TA = 5; CHA = ['A.  13', 'B.  18', 'C.  26', 'D.  40']
A = []
im, d = paper(1, TA, style='grid')
paste(im, pill('QUESTION OF THE WEEKEND', TEAL, WHITE, 34), 90, 190)
paste(im, T("A rectangle is 3 cm longer than it is wide. Its area is 40 cm².\nWhat's the perimeter?", 'disp', 'Black', 76, NAVY, maxw=900), 90, 290)
choices(im, CHA, 130, 800)
paste(im, T("Pick one, then swipe.", 'disp', 'SemiBold', 46, GRAY, maxw=800), 90, 1070)
swipe(d); A.append(im)

im, d = paper(2, TA, style='grid')
paste(im, T("HINT", 'inter', 'Bold', 40, TEAL), 90, 230)
paste(im, T("Call the width w.", 'disp', 'Black', 88, NAVY, maxw=900), 90, 290)
paste(im, T("Then the length is w + 3,\nand width × length = 40.", 'disp', 'Medium', 56, GRAY, maxw=900), 90, 450)
paste(im, T("Which two numbers are 3 apart\nand multiply to 40?", 'hand', 'Bold', 58, TEAL, maxw=900), 90, 760)
swipe(d); A.append(im)

im, d = paper(3, TA, style='grid')
paste(im, T("WORK IT OUT", 'inter', 'Bold', 40, TEAL), 90, 230)
r1, _ = ROW(['w(w + 3) = 40'], 'hand', 'Bold', 96); paste(im, r1, 90, 300)
r2, _ = ROW(['5 × 8 = 40'], 'hand', 'Bold', 96); paste(im, r2, 90, 470)
paste(im, T("width 5, length 8", 'hand', 'Bold', 52, GRAY), 100, 640)
r3, b3 = ROW(['P = 5 + 8 + 5 + 8 = ', {'t': '26', 'c': TEAL}], 'hand', 'Bold', 84); paste(im, r3, 90, 760)
bb = b3[-1]; circle(d, (bb[0] + 90, bb[1] + 760, bb[2] + 90, bb[3] + 760), TEAL, 14)
swipe(d); A.append(im)

im, d = paper(4, TA, style='grid')
paste(im, T("ANSWER", 'inter', 'Bold', 40, TEAL), 90, 230)
paste(im, T("C.  26 cm", 'disp', 'Black', 120, NAVY), 90, 290)
bx = choices(im, CHA, 130, 520, hi=2, dim=True); circle(d, bx[2], TEAL, 18)
trap = card(stack([T("THE TRAP: A", 'inter', 'Bold', 38, RED),
                   T("5 + 8 = 13 is only half the way around. A rectangle has two widths and two lengths.", 'disp', 'SemiBold', 50, NAVY, maxw=780)], 14), 44, fill=WHITE)
paste(im, trap, 90, 790)
swipe(d); A.append(im)

A.append(cta(5, TA, "Comment if you got it!", "Then grab our free cheat sheets for algebra and geometry formulas.", "Free cheat sheets: link in bio"))
save(A, 'gg-2026-11-21-question-carousel')

# ---------------- B: physics (Sun Nov 22, HS/college physics) ----------------
TB = 5; CHB = ['A.  5 m', 'B.  20 m', 'C.  40 m', 'D.  80 m']
B = []
im, d = paper(1, TB)
paste(im, pill('PHYSICS QUESTION', TEAL, WHITE, 34), 150, 190)
paste(im, T("A car starts from rest and speeds up evenly to 20 m/s in 4 seconds.\nHow far did it go?", 'disp', 'Black', 74, NAVY, maxw=840), 140, 290)
choices(im, CHB, 170, 800)
paste(im, T("Lock in your answer. Swipe.", 'disp', 'SemiBold', 46, GRAY, maxw=800), 150, 1070)
swipe(d); B.append(im)

im, d = paper(2, TB)
paste(im, T("HINT", 'inter', 'Bold', 40, TEAL), 150, 230)
paste(im, T("It wasn't going 20 m/s the whole time.", 'disp', 'Black', 84, NAVY, maxw=840), 140, 290)
paste(im, T("It started at 0. Speeding up evenly means the average speed is halfway between.", 'disp', 'Medium', 54, GRAY, maxw=820), 150, 560)
swipe(d); B.append(im)

im, d = paper(3, TB)
paste(im, T("WORK IT OUT", 'inter', 'Bold', 40, TEAL), 150, 230)
paste(im, T("average speed", 'hand', 'Bold', 52, GRAY), 160, 300)
r1, _ = ROW(['= ', {'frac': ('0 + 20', '2')}, ' = 10 m/s'], 'hand', 'Bold', 92); paste(im, r1, 150, 370)
paste(im, T("distance = average speed × time", 'hand', 'Bold', 52, GRAY), 160, 690)
r2, b2 = ROW(['= 10 × 4 = 40 m'], 'hand', 'Bold', 92); paste(im, r2, 150, 770)
swipe(d); B.append(im)

im, d = paper(4, TB)
paste(im, T("ANSWER", 'inter', 'Bold', 40, TEAL), 150, 230)
paste(im, T("C.  40 m", 'disp', 'Black', 120, NAVY), 140, 290)
bx = choices(im, CHB, 170, 520, hi=2, dim=True); circle(d, bx[2], TEAL, 18)
trap = card(stack([T("THE TRAP: D", 'inter', 'Bold', 38, RED),
                   T("20 × 4 = 80 m uses the top speed for the whole trip. Same answer with ½at²: a = 5 m/s², ½ × 5 × 4² = 40 m.", 'disp', 'SemiBold', 48, NAVY, maxw=760)], 14), 44, fill=WHITE)
paste(im, trap, 130, 790)
swipe(d); B.append(im)

B.append(cta(5, TB, "Want more like this?", "Practice math and science on our site, at your own pace.", "Try 10 free questions: link in bio"))
save(B, 'gg-2026-11-22-question-carousel')

# overview
allS = A + B; tw = 270; th = int(tw * H / W); pad = 16
sheet = Image.new('RGB', (pad + 5 * (tw + pad), pad + 2 * (th + pad)), (235, 235, 235))
for i, s in enumerate(allS): sheet.paste(s.resize((tw, th)), (pad + (i % 5) * (tw + pad), pad + (i // 5) * (th + pad)))
sheet.save(f'{OUT}/question-carousels-preview.jpg', quality=90); print('ok')
