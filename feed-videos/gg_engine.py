"""The Good Grade - uploaded feed video engine (7-format rotation).
Not used for Question of the Day or Stories.
A video = list of beats. Each beat: narration ('say'), elements that appear during it, optional 'clear'.
Voice: Kokoro (same humanized pipeline as the QOTD engine). Styles: cards, notebook, soft, whiteboard, grid, test, cream.
"""
import sys, os, math, random, re, wave, subprocess
sys.path.insert(0, '/home/claude/qotd')
import engine as E
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS, SR = 1080, 1920, 30, 44100
NAVY = (27, 51, 75); TEAL = (86, 143, 129); GOLD = (248, 176, 69); CREAM = (250, 247, 241)
WHITE = (255, 255, 255); SOFT = (238, 245, 243); GRAY = (70, 86, 104); LIGHT = (200, 214, 226)
RED = (205, 62, 58); PEACH = (252, 236, 210); NAVY2 = (36, 66, 95); LINE = (223, 234, 230)
FONTS = {'disp': '/usr/share/fonts/opentype/inter/InterDisplay-{w}.otf',
         'inter': '/usr/share/fonts/opentype/inter/Inter-{w}.otf',
         'hand': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts', 'Kalam-{w}.ttf'),
         'serif': '/usr/share/fonts/truetype/dejavu/DejaVuSerif{w}.ttf'}
_fc = {}
def FN(fam, w, size):
    if fam == 'serif': w = '' if w in ('Regular', '') else '-Bold'
    if fam == 'hand': w = 'Bold' if w in ('Bold', 'ExtraBold', 'Black') else 'Regular'
    k = (fam, w, int(size))
    if k not in _fc: _fc[k] = ImageFont.truetype(FONTS[fam].format(w=w), int(size))
    return _fc[k]

def ease(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)

# ------------------------------------------------------------------ text / rows
def wrap(text, font, maxw):
    out = []
    for para in text.split('\n'):
        cur = ''
        for w_ in para.split(' '):
            t = (cur + ' ' + w_).strip()
            if font.getlength(t) <= maxw or not cur: cur = t
            else: out.append(cur); cur = w_
        out.append(cur)
    return out

def T(text, fam='disp', w='Bold', size=60, color=NAVY, maxw=900, align='left', lh=1.18, hl=None):
    """Multi-line text image. hl=(substring, color): highlighter bar behind that phrase."""
    f = FN(fam, w, size); lines = wrap(text, f, maxw)
    lw = [f.getlength(l) for l in lines]; bw = int(max(lw)) + 30
    step = int(size * lh); bh = step * len(lines) + int(size * .35)
    im = Image.new('RGBA', (bw, bh), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        x = {'left': 10, 'center': (bw - lw[i]) / 2, 'right': bw - lw[i] - 10}[align]
        y = i * step + 4
        if hl and hl[0] in l:
            a = l.index(hl[0]); x0 = x + f.getlength(l[:a]); x1 = x0 + f.getlength(hl[0])
            d.rounded_rectangle((x0 - 10, y + size * .38, x1 + 10, y + size * 1.08), 8, fill=hl[1])
        d.text((x, y), l, font=f, fill=color)
    return im

def P(p):
    return {'t': p} if isinstance(p, str) else p

def ROW(parts, fam='hand', w='Bold', size=100, color=NAVY):
    """parts: 'text' | {'t','c','b'} | {'sub'} | {'sup'} | {'frac':(n,d),'c'} | {'gap':px}. Returns (img, boxes)."""
    f = FN(fam, w, size); fs = FN(fam, w, size * .58)
    hasfrac = any('frac' in P(p) for p in parts)
    h = int(size * (2.6 if hasfrac else 1.6)); cy = h // 2
    im = Image.new('RGBA', (3000, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    x = 8; boxes = []
    for p in map(P, parts):
        c = p.get('c', color)
        if 'arrow' in p:
            aw = p['arrow']; lw_ = max(5, int(size / 16))
            d.line((x + 14, cy + 4, x + aw - 18, cy), fill=c, width=lw_)
            d.line((x + aw - 44, cy - 24, x + aw - 16, cy, x + aw - 42, cy + 26), fill=c, width=lw_, joint='curve')
            boxes.append((x, cy - size * .5, x + aw, cy + size * .5)); x += aw; continue
        if 'gap' in p:
            boxes.append((x, cy - size * .6, x + p['gap'], cy + size * .6)); x += p['gap']; continue
        if 'frac' in p:
            n, dn = p['frac']; wd = max(f.getlength(n), f.getlength(dn)) + size * .35
            d.text((x + wd / 2, cy - size * .08), n, font=f, fill=c, anchor='mb')
            d.line((x, cy, x + wd, cy), fill=c, width=max(4, int(size / 14)))
            d.text((x + wd / 2, cy + size * .05), dn, font=f, fill=c, anchor='mt')
            boxes.append((x, cy - size * 1.15, x + wd, cy + size * 1.15)); x += wd + size * .1; continue
        if 'sub' in p:
            d.text((x, cy + size * .18), p['sub'], font=fs, fill=c, anchor='lm')
            wd = fs.getlength(p['sub']); boxes.append((x, cy - size * .1, x + wd, cy + size * .5)); x += wd; continue
        if 'sup' in p:
            d.text((x, cy - size * .38), p['sup'], font=fs, fill=c, anchor='lm')
            wd = fs.getlength(p['sup']); boxes.append((x, cy - size * .7, x + wd, cy)); x += wd; continue
        ff = FN(p.get('fam', fam), 'Black' if p.get('b') else p.get('w', w), size)
        d.text((x, cy), p['t'], font=ff, fill=c, anchor='lm')
        wd = ff.getlength(p['t']); boxes.append((x, cy - size * .62, x + wd, cy + size * .62)); x += wd
    return im.crop((0, 0, int(x) + 12, h)), boxes

def card(img, pad=50, fill=WHITE, radius=36, outline=LINE, shadow=(0, 0, 0, 28), minw=0):
    w = max(img.width + 2 * pad, minw); h = img.height + 2 * pad
    out = Image.new('RGBA', (w + 14, h + 18), (0, 0, 0, 0)); d = ImageDraw.Draw(out)
    if shadow: d.rounded_rectangle((8, 14, w + 6, h + 14), radius, fill=shadow)
    d.rounded_rectangle((0, 0, w, h), radius, fill=fill, outline=outline, width=3 if outline else 0)
    out.paste(img, ((w - img.width) // 2 if minw else pad, pad), img)
    return out

def stack(imgs, gap=20, align='left'):
    w = max(i.width for i in imgs); h = sum(i.height for i in imgs) + gap * (len(imgs) - 1)
    out = Image.new('RGBA', (w, h), (0, 0, 0, 0)); y = 0
    for i in imgs:
        x = {'left': 0, 'center': (w - i.width) // 2}[align]; out.paste(i, (x, y), i); y += i.height + gap
    return out

def pill(text, bg=GOLD, fg=NAVY, size=34, fam='inter'):
    f = FN(fam, 'Bold', size); w = int(f.getlength(text)) + 56; h = size + 30
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), h // 2, fill=bg)
    d.text((w // 2, h // 2), text, font=f, fill=fg, anchor='mm'); return im

# ------------------------------------------------------------------ strokes
def wobble(pts, amt=2.0, seed=1):
    r = random.Random(seed); return [(x + r.uniform(-amt, amt), y + r.uniform(-amt, amt)) for x, y in pts]
def p_circle(box, pad=16, seed=3):
    x0, y0, x1, y1 = box; return wobble(E.ellipse_pts((x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2 + pad, (y1 - y0) / 2 + pad * .7), 1.5, seed)
def p_line(x0, y0, x1, y1, n=24): return E.line_pts(x0, y0, x1, y1, n)
def p_box(box, pad=18):
    x0, y0, x1, y1 = box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad
    return wobble([(x0, y0)] + [(x0 + (x1 - x0) * i / 20, y0) for i in range(1, 21)] + [(x1, y0 + (y1 - y0) * i / 10) for i in range(1, 11)]
                  + [(x1 - (x1 - x0) * i / 20, y1) for i in range(1, 21)] + [(x0, y1 - (y1 - y0) * i / 10) for i in range(1, 11)], 1.5)
def p_check(cx, cy, s=40): return [(cx - s, cy), (cx - s * .55, cy + s * .2), (cx - s * .2, cy + s * .55), (cx + s * .35, cy - s * .25), (cx + s, cy - s * .9)]
def p_x(cx, cy, s=60): return [[(cx - s, cy - s), (cx + s, cy + s)], [(cx + s, cy - s), (cx - s, cy + s)]]
def p_strike(box): x0, y0, x1, y1 = box; return p_line(x0 - 6, (y0 + y1) / 2 + 8, x1 + 6, (y0 + y1) / 2 - 8, 10)

# ------------------------------------------------------------------ backgrounds
def background(style):
    im = Image.new('RGB', (W, H), WHITE); d = ImageDraw.Draw(im)
    lab = FN('inter', 'Bold', 30)
    if style == 'cards':
        d.rectangle((0, 0, W, 16), fill=GOLD)
        d.text((W // 2, 120), 'THE GOOD GRADE', font=lab, fill=TEAL, anchor='mm')
    elif style == 'notebook':
        im.paste(CREAM, (0, 0, W, H))
        for y in range(300, H, 74): d.line((0, y, W, y), fill=(206, 222, 230), width=3)
        d.line((128, 0, 128, H), fill=(232, 160, 150), width=4)
        d.text((W - 70, 120), 'THE GOOD GRADE', font=lab, fill=TEAL, anchor='rm')
    elif style == 'soft':
        im.paste(SOFT, (0, 0, W, H))
        d.ellipse((760, -260, 1300, 280), fill=(222, 236, 232)); d.ellipse((-260, 1600, 260, 2120), fill=PEACH)
        d.text((80, 120), 'THE GOOD GRADE', font=lab, fill=TEAL, anchor='lm')
        d.rounded_rectangle((80, 150, 180, 158), 4, fill=GOLD)
    elif style == 'whiteboard':
        im.paste((236, 238, 240), (0, 0, W, H))
        d.rounded_rectangle((28, 230, W - 28, 1560), 18, fill=(150, 156, 164))
        d.rounded_rectangle((40, 242, W - 40, 1548), 12, fill=(252, 252, 250))
        d.rounded_rectangle((120, 1550, 960, 1585), 8, fill=(170, 176, 184))
        for i, c in enumerate([NAVY, TEAL, RED]): d.rounded_rectangle((200 + i * 150, 1530, 320 + i * 150, 1556), 10, fill=c)
        d.text((W // 2, 140), 'THE GOOD GRADE', font=lab, fill=NAVY, anchor='mm')
    elif style == 'grid':
        for x in range(0, W, 54): d.line((x, 0, x, H), fill=(232, 238, 242), width=2)
        for y in range(0, H, 54): d.line((0, y, W, y), fill=(232, 238, 242), width=2)
        d.rectangle((0, 0, 18, H), fill=TEAL)
        d.text((80, 120), 'THE GOOD GRADE', font=lab, fill=NAVY, anchor='lm')
    elif style == 'test':
        im.paste(CREAM, (0, 0, W, H))
        d.rectangle((0, 0, W, 300), fill=NAVY)
        d.text((80, 110), 'THE GOOD GRADE', font=lab, fill=GOLD, anchor='lm')
        d.text((80, 200), 'SAT / ACT TIP', font=FN('disp', 'Black', 76), fill=WHITE, anchor='lm')
        d.rounded_rectangle((80, 252, 240, 264), 6, fill=GOLD)
    elif style == 'cream':
        im.paste(CREAM, (0, 0, W, H))
        d.rectangle((0, H - 18, W, H), fill=NAVY)
        d.text((W - 80, 120), 'THE GOOD GRADE', font=lab, fill=NAVY, anchor='rm')
        d.rounded_rectangle((W - 180, 150, W - 80, 158), 4, fill=GOLD)
    return im

# ------------------------------------------------------------------ end cards (4 CTA designs)
def end_card(kind, line1, line2):
    im = Image.new('RGB', (W, H), WHITE); d = ImageDraw.Draw(im)
    big = FN('disp', 'Black', 92); mid = FN('inter', 'SemiBold', 42); site = FN('inter', 'Bold', 40)
    def lines(y, txt, f, fill):
        for l in wrap(txt, f, 900): d.text((W // 2, y), l, font=f, fill=fill, anchor='mm'); y += int(f.size * 1.15)
        return y
    if kind == 'consult':
        im.paste(NAVY, (0, 0, W, H)); d.ellipse((700, -300, 1300, 300), fill=NAVY2)
        d.text((W // 2, 520), 'THE GOOD GRADE', font=FN('inter', 'Bold', 36), fill=GOLD, anchor='mm')
        y = lines(720, line1, big, WHITE); y = lines(y + 40, line2, mid, LIGHT)
        d.rounded_rectangle((160, y + 70, 920, y + 190), 60, fill=GOLD)
        d.text((W // 2, y + 130), 'Book a free consultation', font=FN('inter', 'Bold', 44), fill=NAVY, anchor='mm')
        d.text((W // 2, y + 290), 'goodgradetutoring.com', font=site, fill=LIGHT, anchor='mm')
    elif kind == 'questions':
        d.text((W // 2, 480), 'THE GOOD GRADE', font=FN('inter', 'Bold', 36), fill=TEAL, anchor='mm')
        for i in range(10):
            cx = 190 + (i % 5) * 175; cy = 650 + (i // 5) * 175
            d.ellipse((cx - 62, cy - 62, cx + 62, cy + 62), fill=TEAL if i < 7 else SOFT)
            d.text((cx, cy), str(i + 1), font=FN('disp', 'Black', 56), fill=WHITE if i < 7 else TEAL, anchor='mm')
        y = lines(1060, line1, big, NAVY); y = lines(y + 30, line2, mid, GRAY)
        d.text((W // 2, y + 80), 'Link in bio  ·  goodgradetutoring.com', font=FN('inter', 'Bold', 38), fill=TEAL, anchor='mm')
    elif kind == 'cheatsheet':
        im.paste(CREAM, (0, 0, W, H))
        d.rounded_rectangle((330, 380, 770, 900), 26, fill=(230, 224, 210))
        d.rounded_rectangle((310, 360, 750, 880), 26, fill=WHITE, outline=LINE, width=4)
        d.rectangle((310, 360, 750, 440), fill=GOLD); d.rounded_rectangle((310, 360, 750, 400), 26, fill=GOLD)
        d.text((530, 404), 'CHEAT SHEET', font=FN('inter', 'Black', 40), fill=NAVY, anchor='mm')
        for i in range(6): d.rounded_rectangle((360, 490 + i * 62, 360 + [320, 260, 300, 220, 310, 240][i], 510 + i * 62), 10, fill=LINE if i % 2 else SOFT)
        y = lines(1040, line1, big, NAVY); y = lines(y + 30, line2, mid, GRAY)
        d.rounded_rectangle((250, y + 60, 830, y + 160), 50, fill=NAVY)
        d.text((W // 2, y + 110), 'Free  ·  link in bio', font=FN('inter', 'Bold', 42), fill=WHITE, anchor='mm')
    elif kind == 'comment':
        im.paste(SOFT, (0, 0, W, H))
        d.rounded_rectangle((120, 520, 960, 980), 60, fill=WHITE, outline=TEAL, width=6)
        d.polygon([(260, 975), (240, 1110), (380, 975)], fill=WHITE); d.line([(262, 979), (240, 1110), (378, 979)], fill=TEAL, width=6)
        yy = 750 - (len(wrap(line1, FN('disp', 'Black', 80), 760)) - 1) * 46
        for l in wrap(line1, FN('disp', 'Black', 80), 760):
            d.text((W // 2, yy), l, font=FN('disp', 'Black', 80), fill=NAVY, anchor='mm'); yy += 92
        y = lines(1220, line2, mid, GRAY)
        d.text((W // 2, y + 80), 'THE GOOD GRADE', font=FN('inter', 'Bold', 36), fill=TEAL, anchor='mm')
    return im

# ------------------------------------------------------------------ music beds
def bed(N, total, style, seed=1):
    m = np.zeros(N, np.float32)
    def add(sig, t0):
        i0 = int(t0 * SR)
        if i0 < N: m[i0:i0 + len(sig)] += sig[:N - i0]
    if style == 'lofi':
        return E.make_music(N, total) * .9
    if style == 'pluck':        # bright, bouncy
        bpm = 104; beat = 60 / bpm; chords = [[60, 64, 67], [57, 60, 64], [65, 69, 72], [67, 71, 74]]
        k = 0
        while k * beat < total + 2:
            ch = chords[(k // 8) % 4]
            add(E.note(E.midi(ch[k % 3] + 12), beat * 1.2, .035, .003, .18), k * beat)
            if k % 2 == 0: add(E.note(E.midi(ch[0] - 12), beat * 2, .05, .01, .5), k * beat)
            k += 1
        return m
    if style == 'pad':          # calm, warm
        bar = 2.8; chords = [[50, 57, 62, 66], [47, 54, 59, 62], [43, 50, 55, 59], [45, 52, 57, 61]]
        k = 0
        while k * bar < total + bar:
            for n_ in chords[k % 4]: add(E.note(E.midi(n_), bar * 1.4, .045, .9, 2.5), k * bar)
            add(E.note(E.midi(chords[k % 4][2] + 12), bar * .8, .02, .02, .7), k * bar + bar / 2)
            k += 1
        return m
    if style == 'keys':         # soft piano, slower
        bpm = 72; beat = 60 / bpm; prog = [[53, 57, 60, 64], [55, 59, 62, 65], [52, 55, 59, 64], [57, 60, 64, 67]]
        k = 0
        while k * beat * 4 < total + 4:
            ch = prog[k % 4]
            for j, n_ in enumerate(ch): add(E.note(E.midi(n_ + 12), beat * 2, .03, .006, .9), k * beat * 4 + j * beat * .5)
            add(E.note(E.midi(ch[0] - 12), beat * 4, .05, .02, 1.6), k * beat * 4)
            k += 1
        return m
    return m

# ------------------------------------------------------------------ voice with sentence timing
def speak(text, voice, rng):
    sents = [s.strip() for s in re.findall(r'[^.!?]+[.!?]*', text) if s.strip()]
    parts, timing, t = [], [], 0.0
    for i, s in enumerate(sents):
        a = E.trim_silence(E.synth(s, voice, rng.uniform(.97, 1.03) * (.97 if s.endswith('?') else 1)))
        a = a * (0.11 / (np.sqrt(np.mean(a ** 2)) + 1e-9))
        timing.append((t, t + len(a) / SR, s)); parts.append(a); t += len(a) / SR
        if i < len(sents) - 1:
            g = (.42 if s.endswith(('?', '!')) else .3) + rng.uniform(-.03, .05)
            parts.append(np.zeros(int(g * SR), np.float32)); t += g
    return np.concatenate(parts).astype(np.float32), timing

# ------------------------------------------------------------------ build
def build(v, out, preview=False):
    rng = random.Random(v.get('seed', 5)); voice = v.get('voice', 'af_heart')
    LEAD, TAIL = .35, .5
    t = 0.0; els = []
    for bi, b in enumerate(v['beats']):
        if b.get('say'):
            b['audio'], tm = speak(b['say'], voice, rng)
        else:
            b['audio'], tm = np.zeros(1, np.float32), []
        vd = len(b['audio']) / SR
        b['t0'] = t; b['dur'] = max(b.get('min', 0), vd + LEAD + TAIL + b.get('extra', 0))
        b['subs'] = [(t + LEAD + a, t + LEAD + e_, b.get('show', {}).get(s, s)) for a, e_, s in tm]
        if b.get('clear'):
            for e in els:
                if not e.get('keep') and e['end'] > t: e['end'] = t + .3
        for e in b.get('els', []):
            e = dict(e); e['t'] = t + e.get('at', 0) * b['dur'] if e.get('at', 0) <= 1 else t + e['at']
            if 'atv' in e: e['t'] = t + LEAD + e['atv'] * vd       # fraction of the spoken part
            if bi == 0 and e.get('atv', 1) == 0: e['t'] = 0.0; e['d'] = min(e['d'], .2)   # hook visible from frame 1
            e.setdefault('d', .45); e.setdefault('end', 1e9); e['bi'] = bi
            if e.get('anim') == 'wipe' and 'd' not in b.get('els', [{}])[0]: pass
            els.append(e)
        t += b['dur']
    TOTAL = t
    bg = background(v['style'])
    for i, e in enumerate(els): e['id'] = i

    def put(fr, e, tt):
        p = (tt - e['t']) / e['d'] if e['d'] > 0 else 1
        if p <= 0 or tt >= e['end']: return
        p = min(1.0, p); ep = ease(p)
        fade_out = 1.0
        if e['end'] < 1e8 and tt > e['end'] - .3: fade_out = max(0, (e['end'] - tt) / .3)
        k = e.get('anim', 'up')
        if k == 'stroke' or k == 'strokes':
            paths = e['pts'] if k == 'strokes' else [e['pts']]
            dr = ImageDraw.Draw(fr, 'RGBA'); n = len(paths)
            for j, pts in enumerate(paths):
                pj = min(1, max(0, p * n - j))
                pp = E.partial(pts, pj)
                if len(pp) > 1:
                    c = e.get('c', RED); dr.line(pp, fill=(*c, int(255 * fade_out)), width=e.get('w', 8), joint='curve')
            return
        if k == 'countdown':
            dr = ImageDraw.Draw(fr); cx, cy, R = e['cx'], e['cy'], 120
            el = tt - e['t']; n = e.get('n', 3); left = n - el
            if left <= 0 or fade_out < 1: return
            dr.ellipse((cx - R, cy - R, cx + R, cy + R), outline=LINE, width=18)
            dr.arc((cx - R, cy - R, cx + R, cy + R), -90, -90 + 360 * (left / n), fill=TEAL, width=18)
            dr.text((cx, cy), str(math.ceil(left)), font=FN('disp', 'Black', 120), fill=NAVY, anchor='mm')
            dr.text((cx, cy + R + 60), e.get('label', 'Pause and try it'), font=FN('inter', 'Bold', 40), fill=GRAY, anchor='mm')
            return
        img = e['img']; x, y = e['x'], e['y']
        if e.get('anchor') == 'c': x = (W - img.width) // 2 if x is None else x - img.width // 2
        a = fade_out
        if k == 'wipe':
            c = img.crop((0, 0, max(1, int(img.width * p)), img.height))
            if a < 1: c = alpha(c, a)
            fr.paste(c, (int(x), int(y)), c)
            if e.get('pen') and p < 1:
                dr = ImageDraw.Draw(fr); px, py = x + img.width * p, y + img.height * .55
                dr.polygon([(px, py), (px + 16, py - 10), (px + 70, py - 90), (px + 92, py - 72), (px + 30, py + 8)], fill=e.get('penc', NAVY))
                dr.polygon([(px, py), (px + 16, py - 10), (px + 30, py + 8)], fill=(40, 40, 40))
            return
        if k == 'pop':
            s = .8 + .2 * ep + .06 * math.sin(math.pi * ep)
            im2 = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s)))) if p < 1 else img
            im2 = alpha(im2, min(1, p * 2) * a)
            fr.paste(im2, (int(x + (img.width - im2.width) / 2), int(y + (img.height - im2.height) / 2)), im2); return
        if k == 'fade':
            im2 = alpha(img, ep * a); fr.paste(im2, (int(x), int(y)), im2); return
        if k == 'left':
            im2 = alpha(img, ep * a); fr.paste(im2, (int(x - (1 - ep) * 60), int(y)), im2); return
        im2 = alpha(img, ep * a); fr.paste(im2, (int(x), int(y + (1 - ep) * 40)), im2)   # 'up'

    def alpha(im, a):
        if a >= .999: return im
        r, g, b, al = im.split(); return Image.merge('RGBA', (r, g, b, al.point(lambda q: int(q * a))))

    for e in els:
        if e.get('kind') == 'end':
            e['img'] = end_card(*e['card']).convert('RGBA'); e['x'] = 0; e['y'] = 0; e['anim'] = 'fade'; e['keep'] = True
    cache = {'key': None, 'img': None}
    subs = [s for b in v['beats'] for s in b['subs']] if v.get('subs') else []
    end_t = min([e['t'] for e in els if e.get('kind') == 'end'] or [1e9])

    def render(tt):
        settled = tuple(e['id'] for e in els if e.get('anim') != 'countdown' and tt >= e['t'] + e['d'] and tt < e['end'] - .3)
        if settled != cache['key']:
            base = bg.copy()
            for e in els:
                if e['id'] in settled: put(base, e, e['t'] + e['d'] + 1e-3)
            cache['key'] = settled; cache['img'] = base
        fr = cache['img'].copy()
        for e in els:
            if e['id'] not in settled: put(fr, e, tt)
        if subs and tt < end_t:
            for a, b_, s in subs:
                if a - .1 <= tt < b_ + .25:
                    f = FN('inter', 'Bold', 44); ls = wrap(s, f, 920)[:3]
                    dr = ImageDraw.Draw(fr, 'RGBA'); y0 = v.get('sub_y', 1660)
                    hh = len(ls) * 58 + 30; dr.rounded_rectangle((60, y0 - 15, W - 60, y0 + hh - 15), 28, fill=(*NAVY, 225))
                    for i, l in enumerate(ls): dr.text((W // 2, y0 + 14 + i * 58), l, font=f, fill=WHITE if i else WHITE, anchor='mt')
                    break
        return fr

    stem = os.path.splitext(out)[0]
    if preview:
        shots = [b['t0'] + b['dur'] * .95 for b in v['beats']] + v.get('extra_shots', [])
        ims = [render(x).convert('RGB').resize((432, 768)) for x in sorted(shots)]
        cols = min(4, len(ims)); rows = math.ceil(len(ims) / cols)
        sheet = Image.new('RGB', (432 * cols, 768 * rows), (40, 40, 40))
        for i, im in enumerate(ims): sheet.paste(im, ((i % cols) * 432, (i // cols) * 768))
        sheet.save(stem + '_preview.jpg', quality=88); print('preview', stem, round(TOTAL, 1)); return TOTAL

    # audio
    N = int((TOTAL + 1) * SR); vt = np.zeros(N, np.float32)
    for b in v['beats']:
        i0 = int((b['t0'] + LEAD) * SR); vt[i0:i0 + len(b['audio'])] += b['audio']
    vt = E.warm_voice(vt)
    mu = bed(N, TOTAL, v.get('music', 'lofi'))
    mu = mu / (np.abs(mu).max() + 1e-9) * .22
    env = np.convolve(np.abs(vt), np.ones(int(.12 * SR)) / int(.12 * SR), mode='same')
    mu *= np.convolve(1 - .6 * np.clip(env / .05, 0, 1), np.ones(int(.2 * SR)) / int(.2 * SR), mode='same')
    fi = int(.6 * SR); mu[:fi] *= np.linspace(0, 1, fi)
    e_ = int(TOTAL * SR); fo = int(1.5 * SR); mu[e_ - fo:e_] *= np.linspace(1, 0, fo); mu[e_:] = 0
    sfx = np.zeros(N, np.float32)
    def sput(sig, t0):
        i0 = int(t0 * SR); sfx[i0:i0 + len(sig)] += sig[:max(0, N - i0)]
    x = np.arange(int(.05 * SR)) / SR; tick = (np.sin(2 * np.pi * 1800 * x) * np.exp(-x / .008) * .2).astype(np.float32)
    x = np.arange(int(.12 * SR)) / SR; pop = (np.sin(2 * np.pi * (600 + 500 * np.exp(-x / .02)) * x) * np.exp(-x / .03) * .12).astype(np.float32)
    for e in els:
        if e.get('anim') == 'countdown':
            for j in range(e.get('n', 3)): sput(tick, e['t'] + j)
        if e.get('sfx') == 'pop': sput(pop, e['t'])
        if e.get('sfx') == 'chime': sput(E.note(E.midi(84), 1.2, .2, .003, .45) + E.note(E.midi(88), 1.2, .15, .003, .45), e['t'])
    mix = (vt + mu + sfx)[:int((TOTAL + .05) * SR)]
    mix = mix / np.abs(mix).max() * .89
    wav = stem + '_mix.wav'
    w = wave.open(wav, 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.stack([mix, mix], 1) * 32767).astype(np.int16).tobytes()); w.close()
    tmp = stem + '_tmp.mp4'
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                           '-i', '-', '-i', wav, '-shortest', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p',
                           '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', tmp], stdin=subprocess.PIPE)
    for i in range(int(TOTAL * FPS)):
        ff.stdin.write(render(i / FPS).convert('RGB').tobytes())
    ff.stdin.close(); rc = ff.wait(); os.remove(wav)
    if rc == 0: os.replace(tmp, out)
    print('done', out, round(TOTAL, 1)); return TOTAL
