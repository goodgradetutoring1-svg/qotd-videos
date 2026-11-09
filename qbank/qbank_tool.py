"""Good Grade Qbank daily-batch tool.
  python3 qbank_tool.py check <batch.py>   -> validates, balances answer letters, writes batch.json + carrier PNG
batch.py defines: TOPIC, CHAPTERS, AUTHOR ('Odelin' math/test prep, 'Brandon' science; staff-only field), optional EXISTING (list of existing stems to avoid), NOTES, NEXT, and Q = [(chapter, difficulty, stem, [(correct_text, why), (wrong, why) x3], explanation, check_value_or_None), ...]
"""
import sys, re, json, html, gzip, zlib, struct, random, hashlib, secrets, difflib, datetime, importlib.util, os
from fractions import Fraction

ROTATION = ['math-3','math-4','math-5','science-3','science-4','science-5','biology','chemistry','sat-math','act-math',
            'math-k','math-1','math-2','math-6','math-7','math-8','math-9','math-10','math-11','math-12',
            'science-k','science-1','science-2','physics','organic-chemistry','biochemistry','anatomy-physiology',
            'act-english','act-reading','act-science','sat-rw']
BANNED = ['guarantee', 'Odelin', 'Brandon', 'UWorld']
HERE = os.getcwd()

def words(s): return len([w for w in re.sub(r'<[^>]+>', ' ', s).split() if re.search(r'[A-Za-z]{2,}', w) or w.lower() in ('a', 'i')])
def sentences(s): return len([x for x in re.split(r'(?<=[.!?])\s+', s.strip()) if words(x) >= 3])
def norm(s): return re.sub(r'[^a-z0-9 ]', '', re.sub(r'<[^>]+>', ' ', s.lower())).split()
def num(s):
    t = s.replace(',', '').replace('$', '').replace('°', '').strip()
    if ':' in t or '(' in t: return None
    m = re.match(r'(\d+) (\d+/\d+)(?![\d.])|(-?\d+/[1-9]\d*)(?![\d.])|(-?\d+(?:\.\d+)?)(?![\d/])', t)
    if not m or m.start() != 0: return None
    if m.group(1): return Fraction(m.group(1)) + Fraction(m.group(2))
    return Fraction(m.group(3) or m.group(4))

def cmd_check(path):
    spec = importlib.util.spec_from_file_location('b', path); b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
    chapters = list(b.CHAPTERS); n = len(b.Q); errs = []
    if b.TOPIC not in ROTATION: errs.append(f'unknown topic slug {b.TOPIC}')
    if getattr(b, 'AUTHOR', '') not in ('Odelin', 'Brandon'): errs.append("set AUTHOR = 'Odelin' (math and test prep) or 'Brandon' (science)")
    # 75 is the standard daily batch (Brandon, Nov 9, 2026); 30 is the fallback if the site refuses a 75-question import.
    MIX = {75: (22, 31, 22), 30: (9, 12, 9)}
    if n not in MIX: errs.append(f'batch must have exactly 75 questions (or 30 for the fallback upload) (has {n})')
    want = MIX.get(n, (0, 0, 0))
    got = tuple(sum(1 for q in b.Q if q[1] == d) for d in ('easy', 'medium', 'hard'))
    if got != want: errs.append(f'difficulty mix must be {want} easy/medium/hard, got {got}')
    cc = {c: 0 for c in chapters}
    for q in b.Q:
        if q[0] in cc: cc[q[0]] += 1
    lo = max(1, n // len(chapters) - 1) if n >= len(chapters) else 0
    for c, k in cc.items():
        if n >= len(chapters) and k < lo: errs.append(f'subtopic "{c}" has {k} questions; spread the batch evenly (at least {lo} each)')
    seen = [norm(s.split(' | ', 1)[-1]) for s in getattr(b, 'EXISTING', [])]
    for i, (ch, d, stem, choices, expl, check) in enumerate(b.Q, 1):
        tag = f'Q{i}'
        if ch not in chapters: errs.append(f'{tag} subtopic "{ch}" is not one of: {chapters}')
        if d not in ('easy', 'medium', 'hard'): errs.append(f'{tag} bad difficulty {d}')
        if len(choices) != 4: errs.append(f'{tag} needs exactly 4 choices'); continue
        texts = [c for c, _ in choices]
        if len({t.strip().lower() for t in texts}) != 4 or len({re.sub(r'[^a-z0-9]', '', t.lower()) for t in texts}) != 4:
            errs.append(f'{tag} two choices are the same once symbols are removed (the importer rejects this)')
        for c, w in choices:
            if words(c) > 12: errs.append(f'{tag} choice too long (keep choices short): {c}')
            if words(w) < 7 or len(w) < 45: errs.append(f'{tag} per-choice explanation too short (7+ real words, 45+ chars): {w}')
        if sentences(expl) < 2 or len(expl) < 125: errs.append(f'{tag} explanation needs 2+ full sentences and 125+ characters ({len(expl)})')
        for bw in BANNED:
            for part in [stem, expl] + [x for c in choices for x in c]:
                if bw.lower() in part.lower(): errs.append(f'{tag} contains banned word "{bw}"'); break
        if check is not None:
            v = num(texts[0])
            if v is None or Fraction(str(check)).limit_denominator(10000) != v: errs.append(f'{tag} ANSWER CHECK FAILED: computed {check}, correct choice says {texts[0]}')
        ns = norm(stem)
        for s in seen:
            if difflib.SequenceMatcher(None, ns, s).ratio() > 0.85: errs.append(f'{tag} near-duplicate of another question: {" ".join(s)[:80]}'); break
        seen.append(ns)
    if errs:
        print('NOT READY — fix these and run check again:'); [print(' -', e) for e in errs]; sys.exit(1)
    # Balance correct-answer letters (~25% each). Number choices stay sorted (low-high or high-low) when possible.
    rng = random.Random(hashlib.md5(path.encode()).hexdigest()); LC = [0, 0, 0, 0]; plans = [None] * n
    items = []
    for i, q in enumerate(b.Q):
        ch = [{'t': c, 'w': w, 'ok': k == 0} for k, (c, w) in enumerate(q[3])]
        ns = [num(x['t']) for x in ch]
        items.append((i, ch, ns, all(v is not None for v in ns) and len(set(ns)) == 4))
    for i, ch, ns, numeric in items:
        if numeric:
            asc = [x for _, x in sorted(zip(ns, ch), key=lambda p: p[0])]
            pa = next(k for k, x in enumerate(asc) if x['ok']); pd = 3 - pa
            use = asc[::-1] if (LC[pd] < LC[pa] or (LC[pd] == LC[pa] and rng.random() < .5)) else asc
            plans[i] = use; LC[next(k for k, x in enumerate(use) if x['ok'])] += 1
    for i, ch, ns, numeric in items:
        if not numeric:
            tgt = rng.choice([p for p in range(4) if LC[p] == min(LC)])
            wrong = [x for x in ch if not x['ok']]; rng.shuffle(wrong)
            plans[i] = wrong[:tgt] + [x for x in ch if x['ok']] + wrong[tgt:]; LC[tgt] += 1
    def mono(a):
        v = [num(x['t']) for x in a]
        return all(v[k] < v[k + 1] for k in range(len(v) - 1)) or all(v[k] > v[k + 1] for k in range(len(v) - 1))
    for _ in range(60):
        if max(LC) - min(LC) <= 1: break
        hi, lo_ = LC.index(max(LC)), LC.index(min(LC))
        cand = next((i for i, ch, ns, numeric in items if numeric and next(k for k, x in enumerate(plans[i]) if x['ok']) == hi and not getattr(plans[i], 'mixed', False)), None)
        if cand is None: break
        ok = next(x for x in plans[cand] if x['ok']); w = [x for x in plans[cand] if not x['ok']]
        perms = [[w[a], w[b_], w[c]] for a, b_, c in ((0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0))]
        perms = [p for p in perms if not mono(p)] or perms
        order = perms[0][:lo_] + [ok] + perms[0][lo_:]
        class L(list): mixed = True
        plans[cand] = L(order); LC[hi] -= 1; LC[lo_] += 1
    rows = []
    for i, q in enumerate(b.Q):
        row = {'topic': b.TOPIC, 'chapter': q[0], 'difficulty': q[1], 'qtype': 'mc', 'stem': q[2]}
        for k, x in enumerate(plans[i]):
            row['choice_' + 'ABCD'[k]] = x['t']; row['why_' + 'ABCD'[k]] = x['w']
            if x['ok']: row['correct'] = 'ABCD'[k]
        row.update({'explanation': q[4], 'written_on': datetime.date.today().isoformat(), 'status': 'active'})
        if getattr(b, 'AUTHOR', '') in ('Odelin', 'Brandon'): row['author'] = b.AUTHOR
        rows.append(row)
    today = datetime.date.today().isoformat()
    payload = {'batch_id': f'{today}-{b.TOPIC}', 'topic': b.TOPIC, 'rows': rows,
               'notes': list(getattr(b, 'NOTES', [])), 'next': getattr(b, 'NEXT', '')}
    json.dump(payload, open('batch.json', 'w'), ensure_ascii=False, indent=1)
    data = gzip.compress(json.dumps(payload, ensure_ascii=False).encode(), 9)
    def chunk(t, d): return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    raw = b''.join(b'\x00' + b'\xff\xff\xff' * 8 for _ in range(8))
    png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 8, 8, 8, 2, 0, 0, 0)) + chunk(b'ggQb', data) + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b'')
    name = f'ggqb-{today}-{secrets.token_hex(5)}.png'; open(name, 'wb').write(png)
    print('READY', n, 'questions | difficulty', got, '| letters', dict(zip('ABCD', LC)), '| subtopics', cc)
    print('CARRIER', name, hashlib.sha256(png).hexdigest(), len(png), 'bytes')

if __name__ == '__main__':
    {'check': cmd_check}[sys.argv[1]](sys.argv[2])
