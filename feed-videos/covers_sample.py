import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gg_engine import *
C = [('1_quick_tip', 'cards', 'QUICK TIP', '“I get it.”\nTry this check.', NAVY, GOLD, NAVY),
     ('2_practice_question', 'notebook', 'PRACTICE QUESTION', 'Half of ¾ cup?', NAVY, TEAL, WHITE),
     ('3_parent_question', 'soft', 'PARENT QUESTION', 'Tutor… or just more time?', NAVY, GOLD, NAVY),
     ('4_whiteboard_walkthrough', 'whiteboard', 'WHITEBOARD', 'Balance\nH₂ + O₂ → H₂O', NAVY, RED, WHITE),
     ('5_common_mistake', 'grid', 'COMMON MISTAKE', '(x + 3)² ≠ x² + 9', NAVY, RED, WHITE),
     ('6_sat_act_tip', 'test', 'SAT / ACT', "Don't solve it.\nTest it.", NAVY, TEAL, WHITE),
     ('7_why_it_clicks', 'cream', 'WHY IT CLICKS', 'Why does\n− × − = + ?', NAVY, GOLD, NAVY)]
os.makedirs('/tmp/covers', exist_ok=True)
for name, style, tag, title, tc, pbg, pfg in C:
    im = background(style).convert('RGBA')
    t = T(title, 'disp', 'Black', 120, tc, maxw=900, align='center')
    p = pill(tag, pbg, pfg, 40)
    y = (H - t.height) // 2 - 40
    im.alpha_composite(p, ((W - p.width) // 2, y - p.height - 50)); im.alpha_composite(t, ((W - t.width) // 2, y))
    im.convert('RGB').save(f'/tmp/covers/{name}_cover.jpg', quality=92)
