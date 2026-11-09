import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'story_template_nov2026.py')).read().split('# 1. Intro')[0])
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '2026-11')
LIGHT = (200, 214, 226)

def save(im, name):
    p = os.path.join(OUT, name)
    im.save(p, 'JPEG', quality=90, optimize=True)
    print(p)

def question(label, q, opts, name):
    im, d = base(NAVY, dark=True)
    y = block(d, 90, 430, label, F('Bold', 52, False), AMBER, 900)
    y = block(d, 90, y + 20, q, F('Black', 104), WHITE, 900, 1.06)
    y += 50
    for o in opts:
        d.rounded_rectangle((90, y, 990, y + 112), 26, fill=(36, 66, 95))
        d.text((140, y + 56), o, font=F('Bold', 54), fill=WHITE, anchor='lm')
        y += 138
    block(d, 90, y + 20, 'Answer at 4:15 today', F('SemiBold', 44, False), LIGHT, 900)
    save(im, name)

def answer(head, steps, trap_title, trap, name, foot='Follow for more'):
    im, d = base()
    y = block(d, 90, 430, head, F('Black', 108), NAVY, 900, 1.05)
    y += 40
    top = y
    yy = y + 45
    for i, (t, c) in enumerate(steps):
        yy = block(d, 140, yy, t, F('Bold', 50), c, 800) + 12
    d.rounded_rectangle((90, top, 990, yy + 30), 36, outline=(223, 234, 230), width=3)
    y = yy + 70
    d.rounded_rectangle((90, y, 990, y + 300), 30, fill=(252, 236, 210))
    yy = block(d, 130, y + 35, trap_title, F('Bold', 44, False), NAVY, 820)
    block(d, 130, yy + 10, trap, F('Medium', 42, False), GRAY, 820)
    footer(d, foot)
    return im, d

# Mon 12:15 question (algebra)
question('Algebra question', 'Solve:\n2(x + 3) = 14', ['A) 4', 'B) 5.5', 'C) 7', 'D) 8'], 'gg-2026-11-09-1215-question.jpg')

# Mon 4:15 answer
im, d = base()
y = block(d, 90, 430, 'Answer: A) 4', F('Black', 110), NAVY, 900, 1.05)
y += 40; top = y; yy = y + 45
for t, c in [('2(x + 3) = 14', NAVY), ('Divide by 2:  x + 3 = 7', NAVY), ('Subtract 3:  x = 4', TEAL)]:
    yy = block(d, 140, yy, t, F('Bold', 52), c, 820) + 14
d.rounded_rectangle((90, top, 990, yy + 30), 36, outline=(223, 234, 230), width=3)
y = yy + 70
d.rounded_rectangle((90, y, 990, y + 330), 30, fill=(252, 236, 210))
yy = block(d, 130, y + 35, 'Why not B) 5.5?', F('Bold', 46, False), NAVY, 820)
block(d, 130, yy + 10, 'That comes from writing 2x + 3 = 14. The 2 multiplies BOTH x and 3.', F('Medium', 44, False), GRAY, 820)
footer(d, 'Follow for more')
save(im, 'gg-2026-11-09-1615-answer.jpg')

# Tue 12:15 SAT tip
im, d = base()
y = block(d, 90, 430, 'Digital SAT Math tip', F('Bold', 52, False), TEAL, 900)
y = block(d, 90, y + 20, '44 questions.\n70 minutes.', F('Black', 120), NAVY, 900, 1.05)
y = block(d, 90, y + 40, 'A calculator is allowed the whole time. Use it to check your work: plug your answer back into the problem.', F('SemiBold', 50), GRAY, 880)
d.rounded_rectangle((90, y + 50, 990, y + 200), 30, fill=SOFT)
block(d, 130, y + 85, 'Mental math first, calculator to confirm.', F('Bold', 44, False), NAVY, 820)
footer(d, 'More tips: follow us')
save(im, 'gg-2026-11-10-1215-test-tip.jpg')

# Tue 4:15 free resource
im, d = base(TEAL, dark=True)
d.ellipse((760, -160, 1260, 340), fill=(110, 165, 151))
d.text((90, 290), 'THE GOOD GRADE', font=F('Bold', 34, False), fill=AMBER)
y = block(d, 90, 430, 'Free SAT Math practice', F('Black', 108), WHITE, 900, 1.05)
y = block(d, 90, y + 40, 'Free practice question PDFs for Digital SAT Math. Print them and practice at home.', F('SemiBold', 50), (235, 245, 242), 880)
y += 60
for t in ['Printable PDFs', 'Digital SAT Math', '100% free']:
    pill(d, 90, y, t, WHITE, NAVY, 42); y += 125
footer(d, 'Get them: link in bio')
save(im, 'gg-2026-11-10-1615-resource.jpg')

# Wed 12:15 Spanish vocab card
im, d = base()
y = block(d, 90, 430, 'Vocabulario de matemáticas', F('Black', 100), NAVY, 900, 1.06)
y = block(d, 90, y + 30, 'Inglés  /  Español', F('Bold', 44, False), TEAL, 880)
y += 30
for en, es in [('sum', 'suma'), ('difference', 'diferencia'), ('product', 'producto'), ('quotient', 'cociente'), ('equation', 'ecuación')]:
    d.rounded_rectangle((90, y, 990, y + 104), 26, fill=WHITE, outline=(223, 234, 230), width=3)
    d.text((140, y + 52), en, font=F('Bold', 48), fill=NAVY, anchor='lm')
    d.text((940, y + 52), es, font=F('Bold', 48), fill=TEAL, anchor='rm')
    y += 124
footer(d, 'Clases en español: link en la bio')
save(im, 'gg-2026-11-11-1215-espanol.jpg')

# Wed 4:15 blog spotlight
im, d = base(AMBER)
d.rectangle((80, 280, 700, 336), fill=AMBER)
d.text((90, 290), 'NUEVO EN EL BLOG', font=F('Bold', 34, False), fill=NAVY)
y = block(d, 90, 430, 'Sistema escolar en Estados Unidos: guía para padres', F('Black', 96), NAVY, 900, 1.06)
y = block(d, 90, y + 40, 'Una guía sencilla en español sobre cómo funciona la escuela aquí.', F('SemiBold', 48), (60, 60, 60), 880)
y += 50
for t in ['Grados', 'Middle y high school', 'Calificaciones con letras', 'Créditos en Ohio']:
    pill(d, 90, y, t, NAVY, WHITE, 40); y += 118
w = d.textlength('Léalo: link en la bio', font=F('Bold', 36, False)) + 80
x0 = (W - w) / 2
d.rounded_rectangle((x0, 1560, x0 + w, 1640), 40, fill=NAVY)
d.text((W // 2, 1600), 'Léalo: link en la bio', font=F('Bold', 36, False), fill=WHITE, anchor='mm')
save(im, 'gg-2026-11-11-1615-blog.jpg')

# Thu 12:15 how sessions work
im, d = base()
y = block(d, 90, 430, 'How our sessions work', F('Black', 104), NAVY, 900, 1.05)
y += 50
for n, t in [('1', 'Free 30-minute consultation'), ('2', 'Live 1-on-1 lessons online'), ('3', 'A summary after every session'), ('4', 'In English, Spanish or both')]:
    d.ellipse((90, y, 180, y + 90), fill=TEAL)
    d.text((135, y + 45), n, font=F('Black', 48), fill=WHITE, anchor='mm')
    block(d, 210, y + 18, t, F('Bold', 48), NAVY, 780)
    y += 150
block(d, 90, y + 20, 'K–12 and early college. Math with Odelin, science with Brandon.', F('SemiBold', 46), GRAY, 880)
footer(d, 'Learn more: link in bio')
save(im, 'gg-2026-11-12-1215-about.jpg')

# Thu 4:15 consultation CTA
im, d = base(NAVY, dark=True)
y = block(d, 90, 430, 'Not sure where to start?', F('Black', 108), WHITE, 900, 1.05)
y = block(d, 90, y + 40, 'Book a free 30-minute consultation. We\'ll talk about your student and suggest a plan.', F('SemiBold', 50), LIGHT, 880)
y += 60
for t in ['Book at goodgradetutoring.com', 'Call/text (937) 368-7471']:
    d.rounded_rectangle((90, y, 990, y + 110), 26, fill=(36, 66, 95))
    d.text((140, y + 55), t, font=F('Bold', 46, False), fill=WHITE, anchor='lm')
    y += 140
footer(d, 'Free consultation: link in bio')
save(im, 'gg-2026-11-12-1615-consultation.jpg')

# Fri 12:15 chemistry question
question('Chemistry question', 'How many atoms are in one H₂SO₄ molecule?', ['A) 3', 'B) 6', 'C) 7', 'D) 8'], 'gg-2026-11-13-1215-question.jpg')

# Fri 4:15 answer
im, d = base()
y = block(d, 90, 430, 'Answer: C) 7', F('Black', 110), NAVY, 900, 1.05)
y += 40; top = y; yy = y + 45
for t, c in [('H₂ = 2 hydrogen', NAVY), ('S = 1 sulfur', NAVY), ('O₄ = 4 oxygen', NAVY), ('2 + 1 + 4 = 7 atoms', TEAL)]:
    yy = block(d, 140, yy, t, F('Bold', 52), c, 820) + 14
d.rounded_rectangle((90, top, 990, yy + 30), 36, outline=(223, 234, 230), width=3)
y = yy + 70
d.rounded_rectangle((90, y, 990, y + 330), 30, fill=(252, 236, 210))
yy = block(d, 130, y + 35, 'Why not A) 3?', F('Bold', 46, False), NAVY, 820)
block(d, 130, yy + 10, '3 is the number of elements (H, S, O). The subscripts tell you how many atoms.', F('Medium', 44, False), GRAY, 820)
footer(d, 'Follow for more')
save(im, 'gg-2026-11-13-1615-answer.jpg')
