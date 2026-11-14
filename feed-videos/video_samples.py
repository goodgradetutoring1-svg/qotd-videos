"""Seven sample videos, one per format. python3 videos.py <n|all> [--preview]"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gg_engine import *

def el(img, x, y, anim='up', atv=0.0, d=.45, **kw):
    e = dict(img=img, x=x, y=y, anim=anim, atv=atv, d=d); e.update(kw); return e
def center(img, y, **kw): return el(img, (W - img.width) // 2, y, **kw)
def stroke(pts, c=RED, atv=0.0, d=.6, w=8, **kw):
    e = dict(anim='stroke', pts=pts, c=c, atv=atv, d=d, w=w); e.update(kw); return e
def strokes(paths, c=RED, atv=0.0, d=.6, w=9, **kw):
    e = dict(anim='strokes', pts=paths, c=c, atv=atv, d=d, w=w); e.update(kw); return e
def off(b, x, y): return (b[0] + x, b[1] + y, b[2] + x, b[3] + y)
def end(kind, l1, l2, atv=1.0): return dict(kind='end', card=(kind, l1, l2), atv=atv, d=.6)

# ---------------------------------------------------------------- 1. Quick tip (15 s, on-screen text)
def v1():
    b3a = T("Can explain it", 'disp', 'Black', 84, TEAL); b3b = T("They've got it.", 'disp', 'SemiBold', 58, NAVY)
    b3c = T("Can't explain it", 'disp', 'Black', 84, NAVY); b3d = T("Now you know where to help.", 'disp', 'SemiBold', 58, NAVY, maxw=760)
    return dict(name='1_quick_tip', style='cards', music='pluck', voice='af_heart', beats=[
        dict(say="Your kid finishes their math homework and says, I get it.", els=[
            center(T("Your kid, after homework:", 'disp', 'SemiBold', 54, GRAY), 700, atv=0, d=.3),
            center(T("“I get it.”", 'disp', 'Black', 160, NAVY), 800, anim='pop', atv=.6, sfx='pop')]),
        dict(say="Here's a quick check. Ask them to teach you one problem.", clear=True, els=[
            center(T("QUICK CHECK", 'inter', 'Bold', 44, TEAL), 600),
            center(T("Ask them to\nteach you\none problem.", 'disp', 'Black', 124, NAVY, align='center', hl=('teach you', GOLD)), 690, atv=.3)]),
        dict(say="If they can explain it, they've got it. If not, now you know where to help.", clear=True, els=[
            el(b3a, 190, 600, anim='left'), el(b3b, 190, 710, anim='left', atv=.15),
            stroke(p_check(120, 660, 42), TEAL, atv=.15, d=.4, w=12),
            el(b3c, 190, 930, anim='left', atv=.55), el(b3d, 190, 1040, anim='left', atv=.65),
            el(pill('!', GOLD, NAVY, 54), 82, 950, anim='pop', atv=.55)]),
        dict(say="Grab our free cheat sheets. Link in bio.", clear=True, els=[
            end('cheatsheet', 'Free cheat sheets', 'Short, printable study help for home.', atv=0)]),
    ])

# ---------------------------------------------------------------- 2. Practice question (30 s, worked on screen)
def v2():
    q = card(stack([T("HALF A RECIPE", 'inter', 'Bold', 38, TEAL),
                    T("A recipe needs ¾ cup of sugar. You're making half the recipe. How much sugar do you need?", 'disp', 'Bold', 58, NAVY, maxw=760)], 12), 46)
    ch = ['A.  ¼ cup', 'B.  ⅜ cup', 'C.  ½ cup', 'D.  1½ cups']
    cpos = [(190, 860), (600, 860), (190, 960), (600, 960)]
    cims = [T(c, 'disp', 'SemiBold', 60, NAVY) for c in ch]
    r1, b1 = ROW([{'frac': ('1', '2')}, ' × ', {'frac': ('3', '4')}], 'hand', 'Bold', 100)
    r2, b2 = ROW(['= ', {'frac': ('1 × 3', '2 × 4')}, ' = ', {'frac': ('3', '8'), 'c': TEAL}], 'hand', 'Bold', 96)
    R1 = (190, 1080); R2 = (190, 1300)
    cb = cims[1]; boxB = (cpos[1][0], cpos[1][1] + 4, cpos[1][0] + cb.width - 20, cpos[1][1] + cb.height - 8)
    return dict(name='2_practice_question', style='notebook', music='lofi', voice='am_michael', subs=True, sub_y=1650, beats=[
        dict(say="You're making half a recipe that calls for three fourths of a cup of sugar. How much sugar do you need?", els=[
            el(q, 160, 290, atv=0, d=.35)] + [el(cims[i], *cpos[i], atv=.62 + .08 * i, d=.3) for i in range(4)]),
        dict(say="Pause here, and give it a try.", extra=3.2, els=[
            dict(anim='countdown', cx=W // 2, cy=1240, n=3, atv=1.0, d=3.0, label='Pause and try it')]),
        dict(say="Okay. Half of something means times one half.", els=[
            el(r1, *R1, anim='wipe', atv=.45, d=1.0, pen=True)]),
        dict(say="Multiply straight across. One times three is three. Two times four is eight.", els=[
            el(r2, *R2, anim='wipe', atv=.15, d=2.4, pen=True)]),
        dict(say="So you need three eighths of a cup. The answer is B.", els=[
            stroke(p_circle(off(b2[-1], *R2), 14), TEAL, atv=.1, d=.6, w=9),
            stroke(p_circle(boxB, 18), TEAL, atv=.65, d=.6, w=9, sfx='chime')]),
        dict(say="Bonus round. How would you measure three eighths of a cup with regular measuring cups? Comment your answer.", clear=True, els=[
            end('comment', 'How would you measure ⅜ cup?', 'Comment your answer below.', atv=0)]),
    ])

# ---------------------------------------------------------------- 3. Parent question (30 s, on-screen text)
def v3():
    bubble = card(T("How do I know if my kid needs a tutor… or just more time?", 'disp', 'ExtraBold', 78, NAVY, maxw=820), 50)
    def sign(n, txt):
        im = Image.new('RGBA', (920, 140), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, 919, 139), 34, fill=WHITE, outline=LINE, width=3)
        d.ellipse((30, 30, 110, 110), fill=GOLD); d.text((70, 70), str(n), font=FN('disp', 'Black', 46), fill=NAVY, anchor='mm')
        d.text((140, 70), txt, font=FN('disp', 'Bold', 50), fill=NAVY, anchor='lm'); return im
    return dict(name='3_parent_question', style='soft', music='pad', voice='af_heart', beats=[
        dict(say="Here's one we hear from parents a lot. How do I know if my kid needs a tutor, or just more time?", els=[
            el(pill('PARENT QUESTION', GOLD, NAVY, 36), 80, 520, atv=0, d=.3),
            el(bubble, 70, 640, anim='pop', atv=.3, sfx='pop')]),
        dict(say="Honestly? Start with their teacher. They see your kid in class every day.", clear=True, els=[
            el(T("FIRST", 'inter', 'Bold', 40, TEAL), 80, 420),
            el(T("Talk to the teacher.", 'disp', 'Black', 92, NAVY, maxw=920), 70, 480, atv=.15),
            el(T("They see your kid in class every day.", 'disp', 'Medium', 52, GRAY, maxw=900), 80, 600, atv=.5)]),
        dict(say="Then watch for a few signs. Grades slipping for more than a few weeks. Homework turning into a fight most nights. Or hearing, I'm just bad at math.", els=[
            el(T("THEN, WATCH FOR", 'inter', 'Bold', 40, TEAL), 80, 800),
            el(sign(1, 'Grades slipping for weeks'), 80, 870, anim='left', atv=.2),
            el(sign(2, 'Homework fights most nights'), 80, 1035, anim='left', atv=.48),
            el(sign(3, '“I’m just bad at math.”'), 80, 1200, anim='left', atv=.76)]),
        dict(say="If you're seeing those, that's usually when some one on one help makes sense.", els=[
            el(T("Seeing those? That's when 1-on-1 help makes sense.", 'disp', 'Bold', 60, NAVY, maxw=900, hl=('1-on-1 help', GOLD)), 80, 1420, atv=.1)]),
        dict(say="Still not sure? Book a free consultation, and our tutors will talk it through with you.", clear=True, els=[
            end('consult', 'Not sure yet?', 'Talk it through with our tutors. No pressure.', atv=0)]),
    ])

# ---------------------------------------------------------------- 4. Whiteboard walkthrough (50 s, voiceover + whiteboard)
def v4():
    hs = 120
    eq, eb = ROW([{'gap': 72}, 'H', {'sub': '2'}, ' + ', 'O', {'sub': '2'}, {'arrow': 150}, {'gap': 72}, 'H', {'sub': '2'}, 'O'], 'hand', 'Bold', hs)
    EX, EY = (W - eq.width) // 2, 340
    g1, g2 = off(eb[0], EX, EY), off(eb[7], EX, EY)
    two = ROW([{'t': '2', 'c': RED}], 'hand', 'Bold', hs)[0]
    def tally(lbl, n, c=NAVY): return ROW([lbl + ':  ', {'t': n, 'c': c}], 'hand', 'Bold', 74)
    L, R = 150, 650
    (lh, lhb), (lo, lob) = tally('H', '2'), tally('O', '2')
    (rh, rhb), (ro, rob) = tally('H', '2'), tally('O', '1')
    Y1, Y2 = 640, 760
    lab = lambda s: T(s, 'hand', 'Bold', 52, GRAY)
    def num_at(row_boxes, x, y): return off(row_boxes[1], x, y)
    def fix(box, n, c, atv):   # strike old number, write new one beside it
        im = T(n, 'hand', 'Bold', 74, c)
        return [stroke(p_strike(box), RED, atv=atv, d=.35, w=7),
                el(im, int(box[2]) + 18, int(box[1]) - 18, anim='wipe', atv=atv + .08, d=.35, pen=True)]
    note = T("Only change the BIG numbers in front!", 'hand', 'Bold', 62, TEAL, maxw=880)
    return dict(name='4_whiteboard_walkthrough', style='whiteboard', music='keys', voice='am_michael', subs=True, sub_y=1640, beats=[
        dict(say="Can you balance this one? Hydrogen plus oxygen makes water.", els=[
            el(eq, EX, EY, anim='wipe', atv=.05, d=2.2, pen=True)]),
        dict(say="First, count the atoms on each side. On the left, two hydrogens and two oxygens. On the right, two hydrogens, but only one oxygen.", els=[
            el(lab('left'), L, 560, anim='fade', atv=.18), el(lab('right'), R, 560, anim='fade', atv=.55),
            stroke(p_line(560, 580, 560, 860, 8), (150, 156, 164), atv=.1, d=.4, w=5),
            el(lh, L, Y1, anim='wipe', atv=.3, d=.4, pen=True), el(lo, L, Y2, anim='wipe', atv=.42, d=.4, pen=True),
            el(rh, R, Y1, anim='wipe', atv=.66, d=.4, pen=True), el(ro, R, Y2, anim='wipe', atv=.82, d=.4, pen=True),
            stroke(p_circle(off(rob[1], R, Y2), 14), RED, atv=.94, d=.5)]),
        dict(say="We can't change the small numbers. That would make a different chemical. So we add big numbers in front.", els=[
            el(note, 110, 950, anim='wipe', atv=.55, d=1.6, pen=True, penc=TEAL)]),
        dict(say="Put a two in front of the water. Now there are two oxygens on the right. But that makes four hydrogens.", els=[
            el(two, int(g2[0]) + 6, EY, anim='wipe', atv=.08, d=.4, pen=True, penc=RED)]
            + fix(num_at(rob, R, Y2), '2', TEAL, .42) + fix(num_at(rhb, R, Y1), '4', RED, .78)),
        dict(say="So put a two in front of the hydrogen on the left. Now it's four hydrogens and two oxygens on both sides.", els=[
            el(two, int(g1[0]) + 6, EY, anim='wipe', atv=.08, d=.4, pen=True, penc=RED)]
            + fix(num_at(lhb, L, Y1), '4', TEAL, .45) + [
            stroke(p_check(L + 300, Y2 + 140, 34), TEAL, atv=.85, d=.35, w=10),
            stroke(p_check(R + 300, Y2 + 140, 34), TEAL, atv=.92, d=.35, w=10)]),
        dict(say="Balanced! Two H two, plus O two, makes two H two O.", show={"Two H two, plus O two, makes two H two O.": "2H₂ + O₂ → 2H₂O"}, els=[
            stroke(p_box((EX + 10, EY + 30, EX + eq.width - 10, EY + eq.height - 30), 22), TEAL, atv=.1, d=1.0, w=9, sfx='chime')]),
        dict(say="Want more practice like this? Try ten free questions on our site. Link in bio.", clear=True, els=[
            end('questions', 'Try 10 free questions', 'Practice at your own pace.', atv=0)]),
    ])

# ---------------------------------------------------------------- 5. Common mistake (30 s, on-screen text)
def v5():
    s = 104
    wrong, wb = ROW(['(x + 3)', {'sup': '2'}, ' = x', {'sup': '2'}, ' + 9'], 'disp', 'Bold', s)
    r2, _ = ROW(['(x + 3)', {'sup': '2'}, ' = (x + 3)(x + 3)'], 'disp', 'Bold', 84)
    r3, _ = ROW(['= x', {'sup': '2'}, ' + 3x + 3x + 9'], 'disp', 'Bold', 84)
    r4, b4 = ROW(['= x', {'sup': '2'}, ' + ', {'t': '6x', 'c': TEAL}, ' + 9'], 'disp', 'Bold', 84)
    WX, WY = 80, 480; X2 = 80
    chk = card(stack([T("CHECK WITH x = 1", 'inter', 'Bold', 38, TEAL),
                      T("(1 + 3)² = 16", 'disp', 'Bold', 60, NAVY),
                      T("1 + 6 + 9 = 16", 'disp', 'Bold', 60, NAVY),
                      T("the wrong way: 1 + 9 = 10", 'disp', 'SemiBold', 50, RED)], 10), 44)
    CX, CY = 80, 1340
    return dict(name='5_common_mistake', style='grid', music='pluck', voice='af_heart', beats=[
        dict(say="x plus three, squared, is x squared plus nine. Right? Nope.", els=[
            el(pill('COMMON MISTAKE', RED, WHITE, 36), 80, 360, atv=0, d=.3),
            el(wrong, WX, WY, atv=0, d=.35),
            strokes(p_x(WX + wrong.width + 90, WY + wrong.height / 2, 60), RED, atv=.86, d=.4, w=14, sfx='pop')]),
        dict(say="Most students get this wrong because they square each piece separately. But squared means times itself.", els=[
            el(T("Squared means times itself:", 'inter', 'SemiBold', 46, GRAY), X2, 760, atv=.6),
            el(r2, X2, 820, atv=.72)]),
        dict(say="Multiply it out. x times x, x times three, three times x, and three times three.", els=[
            el(r3, X2 + 20, 980, anim='wipe', atv=.2, d=2.6)]),
        dict(say="That's x squared, plus six x, plus nine. That middle term is the one people forget.", els=[
            el(r4, X2 + 20, 1140, atv=0),
            stroke(p_circle(off(b4[3], X2 + 20, 1140), 14), GOLD, atv=.55, d=.6, w=10)]),
        dict(say="Quick check. Let x be one. Four squared is sixteen, and one plus six plus nine is also sixteen.", els=[
            el(chk, CX, CY, atv=.15),
            stroke(p_check(CX + 560, CY + 180, 30), TEAL, atv=.45, d=.3, w=10),
            stroke(p_check(CX + 560, CY + 266, 30), TEAL, atv=.85, d=.3, w=10)]),
        dict(say="Save this one, and grab our free cheat sheets. Link in bio.", clear=True, els=[
            end('cheatsheet', 'Save this one', 'Free, printable cheat sheets. Link in bio.', atv=0)]),
    ])

# ---------------------------------------------------------------- 6. SAT/ACT tip (60 s, test page + worked)
def v6():
    qc = card(T("If x + 2x² = 21, which of the following could be the value of x?", 'serif', 'Regular', 50, (30, 30, 30), maxw=820), 46, outline=(210, 205, 195))
    QX, QY = 70, 350
    chs = ['A)  2', 'B)  3', 'C)  4', 'D)  5']; cp = [(150, 660), (560, 660), (150, 750), (560, 750)]
    cims = [T(c, 'serif', 'Regular', 56, (30, 30, 30)) for c in chs]
    w1, _ = ROW(['C) 4:   4 + 2(16) = 36'], 'hand', 'Bold', 76, NAVY)
    w2, _ = ROW(['B) 3:   3 + 2(9) = 21'], 'hand', 'Bold', 76, NAVY)
    boxB = (cp[1][0], cp[1][1] + 6, cp[1][0] + cims[1].width - 20, cp[1][1] + cims[1].height - 10)
    return dict(name='6_sat_act_tip', style='test', music='lofi', voice='am_michael', subs=True, sub_y=1690, beats=[
        dict(say="Got an SAT question where every answer is a number? Don't solve it. Test it.", els=[
            center(T("Don't solve it.", 'disp', 'Black', 120, NAVY), 640, atv=.45),
            center(T("Test it.", 'disp', 'Black', 120, TEAL), 790, anim='pop', atv=.8, sfx='pop')]),
        dict(say="Here's a real example. x plus two x squared equals twenty one. Which of these could be x?", clear=True, els=[
            el(qc, QX, QY, atv=.1)] + [el(cims[i], *cp[i], atv=.7 + .06 * i, d=.3) for i in range(4)]),
        dict(say="You could set it equal to zero and factor. Or, just plug in the choices. Start in the middle.", els=[
            el(T("Plug in. Start in the middle.", 'disp', 'ExtraBold', 66, TEAL), 80, 880, atv=.62)]),
        dict(say="Try C, four. Four plus two times sixteen is thirty six. Way too big.", els=[
            el(w1, 90, 1010, anim='wipe', atv=.15, d=2.2, pen=True),
            el(T("too big", 'hand', 'Bold', 64, RED), 760, 1120, anim='wipe', atv=.85, d=.4, pen=True, penc=RED)]),
        dict(say="So go smaller. Try B, three. Three plus two times nine is twenty one. That's it.", els=[
            el(w2, 90, 1220, anim='wipe', atv=.3, d=2.0, pen=True),
            stroke(p_check(900, 1300, 36), TEAL, atv=.88, d=.35, w=11, sfx='chime')]),
        dict(say="The answer is B. No factoring needed.", els=[
            stroke(p_circle(boxB, 18), TEAL, atv=.1, d=.6, w=9)]),
        dict(say="Use this when the choices are numbers and the question asks for one value. Starting in the middle tells you whether to go up or down.", clear=True, els=[
            el(T("WHEN TO USE IT", 'inter', 'Bold', 42, TEAL), 80, 380),
            el(T("The choices are numbers, and it asks for one value.", 'disp', 'Black', 76, NAVY, maxw=900), 70, 450, atv=.1),
            el(card(T("Start in the middle → then go up or down.", 'disp', 'Bold', 58, NAVY, maxw=820), 44, fill=PEACH, outline=None), 70, 860, atv=.55)]),
        dict(say="Want to try it yourself? Do ten free practice questions on our site. Link in bio.", clear=True, els=[
            end('questions', 'Try 10 free questions', 'Put the plug-in trick to work.', atv=0)]),
    ])

# ---------------------------------------------------------------- 7. Why it clicks (20 s, on-screen text)
def v7():
    rows = [('3', '−6'), ('2', '−4'), ('1', '−2'), ('0', '0')]
    rims = [ROW([f'{a} × (−2) = ', {'t': r, 'c': NAVY}], 'disp', 'Bold', 88, GRAY)[0] for a, r in rows]
    last, lb = ROW(['−1 × (−2) =  ', {'t': '2', 'c': TEAL, 'b': True}], 'disp', 'Bold', 88, NAVY)
    X0, Y0, DY = 110, 860, 128
    plus = lambda: pill('+2', GOLD, NAVY, 38)
    return dict(name='7_why_it_clicks', style='cream', music='pad', voice='af_heart', beats=[
        dict(say="Ever been told a negative times a negative is positive, just memorize it? Here's why.", els=[
            el(T("Negative × negative = positive.", 'disp', 'Black', 92, NAVY, maxw=920), 70, 420, atv=0, d=.3),
            el(T("But why?", 'disp', 'Black', 92, TEAL), 70, 640, anim='pop', atv=.8, sfx='pop')]),
        dict(say="Three times negative two is negative six. Then negative four. Then negative two. Then zero.", els=[
            el(rims[i], X0, Y0 + i * DY, anim='left', atv=a) for i, a in enumerate([.05, .45, .65, .85])] + [
            el(plus(), 830, Y0 + 70 + i * DY, anim='pop', atv=.93) for i in range(3)]),
        dict(say="Each step goes up by two. So negative one times negative two? Positive two.", els=[
            el(plus(), 830, Y0 + 70 + 3 * DY, anim='pop', atv=.15),
            el(last, X0, Y0 + 4 * DY + 10, anim='pop', atv=.6, sfx='chime'),
            stroke(p_circle(off(lb[1], X0, Y0 + 4 * DY + 10), 16), TEAL, atv=.85, d=.5, w=9)]),
        dict(say="What's a math rule you were told to just memorize? Comment it below.", clear=True, els=[
            end('comment', 'What rule were you told to just memorize?', 'Comment it below.', atv=0)]),
    ])

VIDEOS = [v1, v2, v3, v4, v5, v6, v7]

if __name__ == '__main__':
    which = sys.argv[1]; prev = '--preview' in sys.argv
    os.makedirs('/tmp/fv_out', exist_ok=True)
    idx = range(7) if which == 'all' else [int(which) - 1]
    for i in idx:
        v = VIDEOS[i]()
        build(v, f"/tmp/fv_out/{v['name']}.mp4", preview=prev)
