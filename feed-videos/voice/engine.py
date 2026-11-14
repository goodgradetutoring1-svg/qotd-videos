"""Good Grade Tutoring - Question of the Day video engine.
Usage: python3 engine.py spec.json out.mp4 [--preview]   (--preview writes PNG frames only)
Spec format: see SPEC_EXAMPLE.json. Screen-share look, red pen marks, voiceover, music, captions.
Spec key "humanize" (default true) -> sentence-by-sentence voice with natural pauses, even loudness,
and a light warmth/room treatment on the voice. "speed" defaults to 1.0 (natural pace)."""
import json, math, os, re, subprocess, sys, wave, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont

Q = os.environ.get('QOTD_HOME', '/home/claude/qotd'); V = Q + '/vendor/'
W, H, FPS, SR = 1080, 1920, 30, 44100
FD = '/usr/share/fonts/opentype/inter/'
_fc = {}
def F(w, s):
    k = (w, int(s))
    if k not in _fc: _fc[k] = ImageFont.truetype(FD + f'Inter-{w}.otf', int(s))
    return _fc[k]

BG = (14, 20, 38); PAGE = (255, 255, 255); INK = (17, 24, 39); GRAY = (100, 110, 128)
BLUE = (37, 99, 235); RED = (230, 57, 70); GREEN = (22, 163, 74); AMBER = (245, 158, 11)
COLORS = {'ink': INK, 'blue': BLUE, 'red': RED, 'green': GREEN, 'gray': GRAY, 'amber': (217, 119, 6)}
WX0, WY0, WX1, WY1 = 40, 270, 1040, 1600
PX = 90; CONTENT_W = 860

def ease(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
def prog(t, a, d): return ease((t - a) / d) if d > 0 else (1.0 if t >= a else 0.0)

# ======================= TTS (Kokoro via onnxruntime, espeak-ng phonemes) =======================
_sess = _voices = _vocab = None
def phonemize(text):
    out = []
    for chunk in re.findall(r"[^.,!?;:]+|[.,!?;:]", text):
        if re.fullmatch(r"[.,!?;:]", chunk): out.append(chunk); continue
        if not chunk.strip(): continue
        ipa = subprocess.run([V + 'espeak/bin/espeak-ng', '-q', '--ipa', '-v', 'en-us', chunk.strip()],
                             capture_output=True, text=True,
                             env={'ESPEAK_DATA_PATH': V + 'espeak/share/espeak-ng-data'}).stdout
        out.append((' ' if out else '') + ' '.join(ipa.split()))
    return ''.join(out)

def synth(text, voice, speed):
    global _sess, _voices, _vocab
    import onnxruntime as ort
    if _sess is None:
        _sess = ort.InferenceSession(V + 'kokoro-v1.0.onnx', providers=['CPUExecutionProvider'])
        _voices = np.load(V + 'voices-v1.0.bin')
        _vocab = json.load(open(V + 'kokoro-onnx/src/kokoro_onnx/config.json'))['vocab']
    toks = [_vocab[c] for c in phonemize(text) if c in _vocab][:510]
    tin = 'input_ids' if 'input_ids' in {i.name for i in _sess.get_inputs()} else 'tokens'
    a = _sess.run(None, {tin: np.array([[0, *toks, 0]], dtype=np.int64),
                         'style': np.asarray(_voices[voice][len(toks) - 1], dtype=np.float32),
                         'speed': np.array([speed], dtype=np.float32)})[0]
    a = np.asarray(a, dtype=np.float32).ravel()
    a = a / max(1e-6, np.abs(a).max()) * 0.9
    # resample 24k -> 44.1k with ffmpeg
    pcm = (a * 32767).astype(np.int16).tobytes()
    r = subprocess.run(['ffmpeg', '-v', 'error', '-f', 's16le', '-ar', '24000', '-ac', '1', '-i', '-',
                        '-ar', str(SR), '-f', 's16le', '-'], input=pcm, capture_output=True).stdout
    return np.frombuffer(r, np.int16).astype(np.float32) / 32768

def trim_silence(a, thr=0.012):
    idx = np.where(np.abs(a) > thr)[0]
    if len(idx) == 0: return a
    return a[max(0, idx[0] - int(.02 * SR)): idx[-1] + int(.06 * SR)]

def synth_human(text, voice, speed, rng):
    """Speak sentence by sentence with natural pauses, slight pace variation, even loudness."""
    sents = [s.strip() for s in re.findall(r'[^.!?]+[.!?]*', text) if s.strip()]
    parts = []
    for i, s in enumerate(sents):
        sp = speed * rng.uniform(.96, 1.03)
        if s.endswith('?'): sp *= .97
        a = trim_silence(synth(s, voice, sp))
        rms = np.sqrt(np.mean(a ** 2)) + 1e-9
        a = a * (0.11 / rms)                       # loudness match each sentence
        parts.append(a)
        if i < len(sents) - 1:
            gap = .42 if s.endswith(('?', '!')) else .32
            if s.lower().startswith(('so ', 'okay', 'alright', 'now')): gap += .05
            parts.append(np.zeros(int((gap + rng.uniform(-.04, .06)) * SR), np.float32))
    return np.concatenate(parts).astype(np.float32)

def warm_voice(track):
    """Gentle EQ, compression and a touch of room so the voice sounds less 'in a box'."""
    pcm = (np.clip(track, -1, 1) * 32767).astype(np.int16).tobytes()
    af = ('highpass=f=75,equalizer=f=180:t=q:w=1:g=2.5,equalizer=f=3200:t=q:w=1.4:g=-2,'
          'equalizer=f=7500:t=q:w=1:g=-1.5,acompressor=threshold=-20dB:ratio=2.2:attack=12:release=220:makeup=1.5,'
          'aecho=0.9:0.5:23|41:0.10|0.06')
    r = subprocess.run(['ffmpeg', '-v', 'error', '-f', 's16le', '-ar', str(SR), '-ac', '1', '-i', '-',
                        '-af', af, '-f', 's16le', '-'], input=pcm, capture_output=True).stdout
    out = np.frombuffer(r, np.int16).astype(np.float32) / 32768
    res = np.zeros_like(track); res[:min(len(out), len(track))] = out[:len(track)]
    return res

# ======================= drawing helpers =======================
def wrap(text, font, width):
    words, lines, cur = text.split(), [], ''
    for w_ in words:
        t = (cur + ' ' + w_).strip()
        if font.getlength(t) <= width or not cur: cur = t
        else: lines.append(cur); cur = w_
    if cur: lines.append(cur)
    return lines

def text_img(txt, font, color, pad=8):
    l, t, r, b = font.getbbox(txt)
    im = Image.new('RGBA', (int(r) + pad * 2, int(max(b, font.size * 1.2)) + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((pad, pad), txt, font=font, fill=color)
    return im

def norm_part(p):
    if isinstance(p, str): return {'text': p}
    return p

def row_img(parts, fsize, maxw):
    """parts: strings, {"text","color","bold"}, {"frac":[num,den],"color"}. Returns (img, part_boxes)."""
    for scale in [1, .92, .85, .78, .7, .62, .55]:
        fs = fsize * scale
        f, fb = F('SemiBold', fs), F('Bold', fs * 1.08)
        hasfrac = any('frac' in norm_part(p) for p in parts)
        h = int(fs * (3.0 if hasfrac else 1.7))
        im = Image.new('RGBA', (2400, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        x, cy, boxes = 6, h // 2, []
        for p in map(norm_part, parts):
            col = COLORS.get(p.get('color', 'ink'), INK)
            if 'frac' in p:
                n, dn = p['frac']; fn = fb if p.get('bold') else f
                w = max(fn.getlength(n), fn.getlength(dn)) + fs * 0.5
                d.text((x + w / 2, cy - fs * 0.15), n, font=fn, fill=col, anchor='mb')
                d.line((x, cy, x + w, cy), fill=col, width=max(3, int(fs / 12)))
                d.text((x + w / 2, cy + fs * 0.12), dn, font=fn, fill=col, anchor='mt')
                boxes.append((x, cy - fs * 1.25, x + w, cy + fs * 1.25)); x += w
            else:
                fn = fb if p.get('bold') else f
                d.text((x, cy), p['text'], font=fn, fill=col, anchor='lm')
                w = fn.getlength(p['text']); boxes.append((x, cy - fs * 0.6, x + w, cy + fs * 0.6)); x += w
        if x <= maxw or scale == .55:
            return im.crop((0, 0, int(x) + 10, h)), boxes

def ellipse_pts(cx, cy, rx, ry, turns=1.12, n=70):
    return [(cx + rx * (1 + 0.04 * math.sin(i * 0.5)) * math.cos(-0.15 + 2 * math.pi * turns * i / n - 1.9),
             cy + ry * (1 + 0.04 * math.sin(i * 0.5)) * math.sin(-0.15 + 2 * math.pi * turns * i / n - 1.9))
            for i in range(n + 1)]
def line_pts(x0, y0, x1, y1, n=20):
    return [(x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n + 3 * math.sin(i * 0.9)) for i in range(n + 1)]
def circle_box(b, pad=14):
    x0, y0, x1, y1 = b
    return ellipse_pts((x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2 + pad * .5 + 6, (y1 - y0) / 2 + pad)

def partial(pts, p):
    if p <= 0: return []
    segs = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    tot = sum(segs) * p; out = [pts[0]]
    for i, s in enumerate(segs):
        if tot >= s: out.append(pts[i + 1]); tot -= s
        else:
            a, b = pts[i], pts[i + 1]; f = tot / s if s else 0
            out.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)); break
    return out

# ======================= build =======================
def build(spec, out, preview=False):
    voice, speed = spec.get('voice', 'af_heart'), spec.get('speed', 1.0)
    humanize = spec.get('humanize', True); rng = random.Random(7)
    n_steps = len(spec['steps'])
    # ---- segments: intro, pause, steps..., answer, trap, outro ----
    segs = [{'kind': 'intro', 'say': spec['narration']['intro'], 'cap': spec['captions']['intro']},
            {'kind': 'pause', 'say': spec['narration'].get('pause', 'Pause the video, and give it a shot.'),
             'cap': [['Pause and try it first!', 'amber']]}]
    for i, st in enumerate(spec['steps']):
        segs.append({'kind': 'step', 'i': i, 'say': st['say'], 'cap': st['caption']})
    segs.append({'kind': 'answer', 'say': spec['narration']['answer'], 'cap': spec['captions']['answer']})
    if spec.get('trap'):
        segs.append({'kind': 'trap', 'say': spec['trap']['say'], 'cap': spec['trap']['caption']})
    segs.append({'kind': 'outro', 'say': spec['narration'].get('outro',
                 'See you tomorrow! Follow Good Grade Tutoring for a new question every day.'), 'cap': None})
    LEAD, TAIL = (0.4, 0.55) if humanize else (0.25, 0.35)
    t = 0.0
    for s in segs:
        s['audio'] = synth_human(s['say'], voice, speed, rng) if humanize else synth(s['say'], voice, speed)
        vd = len(s['audio']) / SR
        mins = {'intro': 5.0, 'pause': vd + LEAD + 2.2, 'answer': 3.5, 'outro': 4.5}.get(s['kind'], 4.0)
        s['t0'], s['dur'] = t, max(mins, vd + LEAD + TAIL); t += s['dur']
    TOTAL = t
    S = lambda kind, i=None: next(s for s in segs if s['kind'] == kind and (i is None or s.get('i') == i))

    # ---- base frame ----
    base = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(base)
    d.text((W // 2, 105), 'GOOD GRADE TUTORING', font=F('Bold', 30), fill=AMBER, anchor='mm')
    title = spec['title']; ft = F('ExtraBold', 62)
    while ft.getlength(title) > 1000: ft = F('ExtraBold', ft.size - 2)
    d.text((W // 2, 170), title, font=ft, fill='white', anchor='mm')
    d.text((W // 2, 228), spec['subtitle'], font=F('SemiBold', 30), fill=(148, 163, 184), anchor='mm')
    d.rounded_rectangle((WX0 + 6, WY0 + 10, WX1 + 6, WY1 + 10), 22, fill=(6, 10, 22))
    d.rounded_rectangle((WX0, WY0, WX1, WY1), 22, fill=PAGE)
    d.rounded_rectangle((WX0, WY0, WX1, WY0 + 64), 22, fill=(229, 231, 235))
    d.rectangle((WX0, WY0 + 40, WX1, WY0 + 64), fill=(229, 231, 235))
    for i, c in enumerate([(255, 95, 87), (254, 188, 46), (40, 200, 64)]):
        d.ellipse((WX0 + 26 + i * 34, WY0 + 22, WX0 + 46 + i * 34, WY0 + 42), fill=c)
    d.text((W // 2 - 40, WY0 + 32), spec.get('filename', 'Practice_Question.pdf'), font=F('Medium', 26), fill=GRAY, anchor='mm')
    d.rounded_rectangle((WX1 - 190, WY0 + 14, WX1 - 18, WY0 + 50), 18, fill=(220, 38, 38))
    d.ellipse((WX1 - 176, WY0 + 26, WX1 - 164, WY0 + 38), fill='white')
    d.text((WX1 - 98, WY0 + 32), 'Sharing', font=F('Bold', 24), fill='white', anchor='mm')

    # ---- layout with auto-shrink until it fits the window ----
    for k in [1, .94, .88, .82, .76, .7, .64]:
        els, marks_geo, y = [], {}, 352
        it = segs[0]; T0, D0 = it['t0'], it['dur']
        els.append((text_img('QUESTION', F('Bold', 26), BLUE), (PX - 8, y), T0 + .3, .4)); y += 40
        fq = F('Medium', 40 * k); qlines = wrap(spec['question'], fq, CONTENT_W)
        qline_boxes = []
        nq = len(qlines)
        for j, ln in enumerate(qlines):
            els.append((text_img(ln, fq, INK), (PX - 8, y), T0 + .5 + j * 1.6 / nq, 1.6 / nq))
            qline_boxes.append((ln, PX, y + 8, fq)); y += int(54 * k)
        disp_boxes = []
        if spec.get('display'):
            y += int(20 * k)
            for j, parts in enumerate(spec['display']):
                im, bx = row_img(parts, 50 * k, CONTENT_W - 120)
                x0 = max(PX + 40, (WX0 + WX1) // 2 - im.width // 2 - 60)
                els.append((im, (x0, y), T0 + 2.3 + j * .5, .6))
                disp_boxes.append([(b[0] + x0, b[1] + y, b[2] + x0, b[3] + y) for b in bx])
                y += im.height + int(2 * k)
        y += int(14 * k)
        fch = F('Medium', 42 * k); letters = 'ABCDE'
        chs = spec['choices']
        two_col = all(fch.getlength(f'{letters[i]}.  {c}') < 380 for i, c in enumerate(chs))
        choice_boxes = []
        for i, c in enumerate(chs):
            s = f'{letters[i]}.  {c}'
            if two_col: x, yy = (PX if i % 2 == 0 else 560), y + (i // 2) * int(62 * k)
            else: x, yy = PX, y + i * int(60 * k)
            els.append((text_img(s, fch, INK), (x - 8, yy), T0 + 3.5 + i * .3, .4))
            choice_boxes.append((x - 12, yy, x + fch.getlength(s) + 12, yy + int(60 * k)))
        y = (choice_boxes[-1][3] + int(14 * k))
        divider_y = y; y += int(18 * k)
        work_top = y
        step_rows = []
        for i, st in enumerate(spec['steps']):
            sg = S('step', i); t0, du = sg['t0'], sg['dur']
            fh = F('Bold', 38 * k)
            head = st['heading']
            while fh.getlength(head) > CONTENT_W - 70 and fh.size > 22: fh = F('Bold', fh.size - 1)
            im = Image.new('RGBA', (980, int(64 * k)), (0, 0, 0, 0)); dd = ImageDraw.Draw(im)
            r = int(25 * k); cy = int(32 * k)
            dd.ellipse((0, cy - r, 2 * r, cy + r), fill=BLUE)
            dd.text((r, cy), str(i + 1), font=F('Bold', 30 * k), fill='white', anchor='mm')
            dd.text((2 * r + 16, cy), head, font=fh, fill=INK, anchor='lm')
            els.append((im, (PX - 8, y), t0, .7)); y += int(60 * k)
            if st.get('sub'):
                fs = F('Medium', 32 * k)
                for ln in wrap(st['sub'], fs, CONTENT_W - 60):
                    els.append((text_img(ln, fs, GRAY), (PX + 50, y), t0 + .15 * du, .7)); y += int(44 * k)
            rb = None
            if st.get('row'):
                im, bx = row_img(st['row'], 46 * k, CONTENT_W - 60)
                if any('frac' in norm_part(p) for p in st['row']): y += int(10 * k)
                rx = PX + 52
                els.append((im, (rx, y - int(6 * k)), t0 + .4 * du, min(1.4, .3 * du)))
                rb = [(b[0] + rx, b[1] + y - 6 * k, b[2] + rx, b[3] + y - 6 * k) for b in bx]
                y += im.height - int(10 * k)
            step_rows.append(rb); y += int(12 * k)
        ans_y = max(y + 6, WY1 - 100)
        if ans_y + 72 <= WY1 - 14: break
    # answer banner
    letter = letters[spec['answer_index']]
    ans = Image.new('RGBA', (860, 70), (0, 0, 0, 0)); ad = ImageDraw.Draw(ans)
    ad.rounded_rectangle((0, 0, 859, 69), 16, fill=GREEN)
    atxt = f"ANSWER:  {letter}" + (f"   ({spec['answer_note']})" if spec.get('answer_note') else '')
    fa = F('ExtraBold', 40)
    while fa.getlength(atxt) > 820: fa = F('ExtraBold', fa.size - 1)
    ad.text((430, 35), atxt, font=fa, fill='white', anchor='mm')
    sa = S('answer')
    els.append((ans, (110, ans_y), sa['t0'] + 1.0, .6))

    # ---- pen marks ----
    def resolve(m):
        tg = m['target']
        if tg == 'question':
            full = ' '.join(l for l, *_ in qline_boxes); idx = full.find(m['text'])
            if idx < 0:
                print('WARNING: mark text not in question:', m['text']); return None
            end_, paths, pos = idx + len(m['text']), [], 0
            for ln, x, yy, fq_ in qline_boxes:
                a, b = max(idx, pos), min(end_, pos + len(ln))
                if a < b:
                    x0 = x + fq_.getlength(ln[:a - pos]); x1 = x + fq_.getlength(ln[:b - pos])
                    if m.get('type', 'underline') == 'underline':
                        paths.append(line_pts(x0 - 4, yy + fq_.size * 1.18, x1 + 6, yy + fq_.size * 1.15))
                    else: paths.append(circle_box((x0, yy, x1, yy + fq_.size * 1.2), 8))
                pos += len(ln) + 1
            return paths
        if tg == 'display':
            b = disp_boxes[m['line']][m['part']]
            if 'line2' in m:  # circle a vertical pair across two display lines
                b2 = disp_boxes[m['line2']][m.get('part2', m['part'])]
                b = (min(b[0], b2[0]), b[1], max(b[2], b2[2]), b2[3])
            return [circle_box(b, m.get('pad', 10))]
        if tg == 'row':
            b = step_rows[m['step']][m['part']]
            return [circle_box(b, m.get('pad', 6))]
        raise ValueError(f'bad mark {m}')
    strokes = []
    for i, st in enumerate(spec['steps']):
        sg = S('step', i); ms = st.get('marks', [])
        for j, m in enumerate(ms):
            at = m.get('at', .12 + .26 * j / max(1, len(ms)) if m['target'] != 'row' else .72)
            paths = resolve(m) or []
            du = min(1.0, .2 * sg['dur']) / max(1, len(paths))
            for q, pts in enumerate(paths):
                strokes.append((pts, sg['t0'] + at * sg['dur'] + q * du, du, RED))
    cb = choice_boxes[spec['answer_index']]
    strokes.append((circle_box(cb, 4), sa['t0'] + .1, .9, GREEN))

    # ---- captions ----
    cap_imgs = []
    fc = F('Bold', 46)
    for s in segs:
        if not s['cap']: continue
        im = Image.new('RGBA', (W, 260), (0, 0, 0, 0)); cd = ImageDraw.Draw(im)
        lines = s['cap']
        for i, (txt, col) in enumerate(lines):
            f_ = fc
            while f_.getlength(txt) > 1000: f_ = F('Bold', f_.size - 2)
            cc = {'white': 'white', 'amber': AMBER, 'green': (74, 222, 128), 'red': (248, 113, 113)}.get(col, 'white')
            cd.text((W // 2, 130 + (i - (len(lines) - 1) / 2) * 64), txt, font=f_, fill=cc, anchor='mm',
                    stroke_width=2, stroke_fill=(0, 0, 0))
        cap_imgs.append((s['t0'], s['t0'] + s['dur'], im))

    # ---- cursor path: hover over each element as it appears ----
    keys = [(0, 880, 1300)]
    for img, (x, y), s, du in sorted(els, key=lambda e: e[2]):
        keys.append((s + du * .6, x + min(img.width, 500) * .7, y + img.height * .6))
    keys.append((TOTAL, 960, 1460)); keys.sort()
    def cursor_at(t):
        for pts, s, du, _ in strokes:
            if s < t <= s + du: return partial(pts, ease((t - s) / du))[-1], True
        for (t0, x0, y0), (t1, x1, y1) in zip(keys, keys[1:]):
            if t0 <= t <= t1:
                e = ease(min(1, ease((t - t0) / max(t1 - t0, 1e-6)) * 1.6))
                return (x0 + (x1 - x0) * e, y0 + (y1 - y0) * e), False
        return keys[-1][1:], False

    def with_alpha(im, a):
        if a >= .999: return im
        r, g, b, al = im.split(); return Image.merge('RGBA', (r, g, b, al.point(lambda v: int(v * a))))

    end = Image.new('RGB', (W, H), BG); ed = ImageDraw.Draw(end)
    ed.text((W // 2, 640), 'GOOD GRADE TUTORING', font=F('Bold', 40), fill=AMBER, anchor='mm')
    ed.text((W // 2, 790), spec.get('end_line1', 'New question'), font=F('Black', 84), fill='white', anchor='mm')
    ed.text((W // 2, 895), 'every day.', font=F('Black', 84), fill='white', anchor='mm')
    ed.rounded_rectangle((240, 1010, 840, 1110), 50, fill=BLUE)
    ed.text((W // 2, 1060), 'Follow for more', font=F('ExtraBold', 46), fill='white', anchor='mm')
    ed.text((W // 2, 1210), spec.get('end_cta', 'Comment your answer below'), font=F('SemiBold', 36), fill=(203, 213, 225), anchor='mm')
    ed.text((W // 2, 1300), 'goodgradetutoring.com', font=F('Bold', 40), fill=(226, 232, 240), anchor='mm')

    sp, so = S('pause'), S('outro')
    def render(t):
        if t >= so['t0']:
            return Image.blend(base, end, prog(t, so['t0'], .6)) if t < so['t0'] + .6 else end.copy()
        fr = base.copy(); dr = ImageDraw.Draw(fr)
        dr.line((PX, divider_y, WX1 - 50, divider_y), fill=(229, 231, 235), width=3)
        if t >= sa['t0']:
            a = prog(t, sa['t0'], .4); col = tuple(int(255 + (c - 255) * a) for c in (220, 252, 231))
            dr.rounded_rectangle(cb, 12, fill=col)
        for img, (x, y), s, du in els:
            p = prog(t, s, du)
            if p <= 0: continue
            c = img.crop((0, 0, max(1, int(img.width * p)), img.height)); fr.paste(c, (int(x), int(y)), c)
        if sp['t0'] <= t < sp['t0'] + sp['dur']:
            el = t - sp['t0']; step = sp['dur'] / 3; n = 3 - int(el / step)
            if n >= 1:
                ph = (el % step) / step; cy = (work_top + WY1) // 2 - 40
                dr.text((W // 2, cy), str(n), font=F('Black', 220 + 40 * (1 - ph)),
                        fill=tuple(int(200 + 40 * ph) for _ in range(3)), anchor='mm')
                dr.text((W // 2, cy + 180), 'THINK FIRST', font=F('Bold', 34), fill=(160, 170, 185), anchor='mm')
        for pts, s, du, col in strokes:
            if t >= s:
                pp = partial(pts, prog(t, s, du))
                if len(pp) > 1: dr.line(pp, fill=col, width=7, joint='curve')
        (cx, cy), pen = cursor_at(t)
        if pen: dr.ellipse((cx - 9, cy - 9, cx + 9, cy + 9), fill=RED, outline='white', width=3)
        else:
            pts = [(0, 0), (0, 44), (11, 33), (19, 51), (27, 47), (19, 30), (34, 30)]
            dr.polygon([(cx + a, cy + b) for a, b in pts], fill='black', outline='white', width=3)
        for s, e, im in cap_imgs:
            if s <= t < e:
                a = min(prog(t, s, .25), 1 - prog(t, e - .25, .25)); ci = with_alpha(im, a); fr.paste(ci, (0, 1630), ci)
        return fr

    if preview:
        stem = os.path.splitext(out)[0]; shots = []
        for s in segs:
            shots.append(s['t0'] + s['dur'] * .92)
        ims = [render(x).resize((360, 640)) for x in shots]
        sheet = Image.new('RGB', (360 * min(5, len(ims)), 640 * math.ceil(len(ims) / 5)), BG)
        for i, im in enumerate(ims): sheet.paste(im, ((i % 5) * 360, (i // 5) * 640))
        sheet.save(stem + '_preview.png'); print('preview', stem + '_preview.png', 'total', round(TOTAL, 1)); return

    # ---- audio mix ----
    N = int(TOTAL * SR) + SR
    voice_tr = np.zeros(N, np.float32)
    for s in segs:
        i0 = int((s['t0'] + LEAD) * SR); voice_tr[i0:i0 + len(s['audio'])] += s['audio']
    if humanize: voice_tr = warm_voice(voice_tr)
    music = make_music(N, TOTAL)
    env = np.convolve(np.abs(voice_tr), np.ones(int(.12 * SR)) / int(.12 * SR), mode='same')
    duck = np.convolve(1 - .6 * np.clip(env / .05, 0, 1), np.ones(int(.2 * SR)) / int(.2 * SR), mode='same')
    music *= duck
    fi = int(.8 * SR); music[:fi] *= np.linspace(0, 1, fi)
    e_ = int(TOTAL * SR); fo = int(2 * SR); music[e_ - fo:e_] *= np.linspace(1, 0, fo); music[e_:] = 0
    sfx = np.zeros(N, np.float32)
    def put(sig, t0):
        i0 = int(t0 * SR); sfx[i0:i0 + len(sig)] += sig[:max(0, N - i0)]
    x = np.arange(int(.05 * SR)) / SR; tick = (np.sin(2 * np.pi * 1800 * x) * np.exp(-x / .008) * .25).astype(np.float32)
    x = np.arange(int(.12 * SR)) / SR; pop = (np.sin(2 * np.pi * (600 + 500 * np.exp(-x / .02)) * x) * np.exp(-x / .03) * .18).astype(np.float32)
    for j in range(3): put(tick, sp['t0'] + j * sp['dur'] / 3)
    for i in range(n_steps): put(pop, S('step', i)['t0'])
    put(note(midi(84), 1.2, .22, .003, .45) + note(midi(88), 1.2, .16, .003, .45), sa['t0'])
    put(pop, sa['t0'] + 1.0)
    mix = (voice_tr + music * .55 + sfx)[:int((TOTAL + .1) * SR)]
    mix = mix / np.abs(mix).max() * .89
    wav = os.path.splitext(out)[0] + '_mix.wav'
    w = wave.open(wav, 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.stack([mix, mix], 1) * 32767).astype(np.int16).tobytes()); w.close()

    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                           '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', wav, '-shortest',
                           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p',
                           '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    for i in range(int(TOTAL * FPS)):
        ff.stdin.write(render(i / FPS).convert('RGB').tobytes())
    ff.stdin.close(); ff.wait(); os.remove(wav)
    print('done', out, 'duration', round(TOTAL, 1))

def midi(m): return 440 * 2 ** ((m - 69) / 12)
def note(f, dur, amp, attack=.02, decay=1.2):
    x = np.arange(int(dur * SR)) / SR
    env = np.minimum(1, x / attack) * np.exp(-x / decay)
    tone = np.sin(2 * np.pi * f * x) + .35 * np.sin(4 * np.pi * f * x) * np.exp(-x / .3) + .12 * np.sin(6 * np.pi * f * x) * np.exp(-x / .15)
    return (tone * env * amp).astype(np.float32)

def make_music(N, TOTAL):
    music = np.zeros(N, np.float32); beat = 60 / 84; bar = 4 * beat
    chords = [[48, 55, 64, 71], [45, 52, 60, 67], [41, 48, 57, 64], [43, 50, 59, 62]]
    arps = [[72, 76, 79, 83], [69, 72, 76, 79], [65, 69, 72, 76], [67, 71, 74, 79]]
    def add(sig, t0):
        i0 = int(t0 * SR)
        if i0 < N: music[i0:i0 + len(sig)] += sig[:N - i0]
    k = 0
    while k * bar < TOTAL + bar:
        ch, s0 = k % 4, k * bar
        for m in chords[ch]: add(note(midi(m), bar * 1.05, .05, .25, 3.0), s0)
        for j in range(8): add(note(midi(arps[ch][[0, 1, 2, 3, 2, 1, 2, 3][j]]), beat * 1.5, .028, .005, .5), s0 + j * beat / 2)
        x = np.arange(int(.25 * SR)) / SR
        kick = (np.sin(2 * np.pi * (50 + 60 * np.exp(-x / .03)) * x) * np.exp(-x / .09) * .10).astype(np.float32)
        add(kick, s0); add(kick, s0 + 2 * beat); k += 1
    # one-pole low-pass via ffmpeg-free cumulative filter (scipy-free)
    a = .35; y = np.empty_like(music); prev = 0.0
    try:
        from scipy.signal import lfilter
        return lfilter([a], [1, a - 1], music).astype(np.float32)
    except ImportError:
        for i, v in enumerate(music): prev += a * (v - prev); y[i] = prev
        return y

if __name__ == '__main__':
    spec = json.load(open(sys.argv[1]))
    build(spec, sys.argv[2], preview='--preview' in sys.argv)
