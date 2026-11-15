import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'story_template_nov2026.py')).read().split('# 1. Intro')[0])
OUT = os.path.join(HERE, '2026-11')
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

def answer(head, steps, trap_title, trap, name):
    im, d = base()
    y = block(d, 90, 430, head, F('Black', 110), NAVY, 900, 1.05)
    y += 40; top = y; yy = y + 45
    for t, c in steps:
        yy = block(d, 140, yy, t, F('Bold', 52), c, 820) + 14
    d.rounded_rectangle((90, top, 990, yy + 30), 36, outline=(223, 234, 230), width=3)
    y = yy + 70
    d.rounded_rectangle((90, y, 990, y + 330), 30, fill=(252, 236, 210))
    yy = block(d, 130, y + 35, trap_title, F('Bold', 46, False), NAVY, 820)
    block(d, 130, yy + 10, trap, F('Medium', 44, False), GRAY, 820)
    footer(d, 'Follow for more')
    save(im, name)

# Mon 12:15 question (elementary: order of operations)
question('Elementary math question', 'What is\n6 + 4 × 2?', ['A) 12', 'B) 14', 'C) 16', 'D) 20'], 'gg-2026-11-16-1215-question.jpg')

# Mon 4:15 answer
answer('Answer: B) 14',
       [('Multiply first:  4 × 2 = 8', NAVY), ('Then add:  6 + 8 = 14', TEAL)],
       'Why not D) 20?',
       'That is what you get if you add first. Always multiply before you add.',
       'gg-2026-11-16-1615-answer.jpg')

# Tue 12:15 study tip: error log
im, d = base()
y = block(d, 90, 430, 'Study tip', F('Bold', 52, False), TEAL, 900)
y = block(d, 90, y + 20, 'Keep a mistake notebook.', F('Black', 116), NAVY, 900, 1.05)
y = block(d, 90, y + 40, 'Every time you miss a problem, write down:', F('SemiBold', 50), GRAY, 880)
y += 40
for n, t in [('1', 'The problem'), ('2', 'What went wrong'), ('3', 'The correct steps')]:
    d.ellipse((90, y, 180, y + 90), fill=TEAL)
    d.text((135, y + 45), n, font=F('Black', 48), fill=WHITE, anchor='mm')
    block(d, 210, y + 18, t, F('Bold', 50), NAVY, 780)
    y += 130
d.rounded_rectangle((90, y + 30, 990, y + 180), 30, fill=SOFT)
block(d, 130, y + 65, 'Review it before every test.', F('Bold', 44, False), NAVY, 820)
footer(d, 'More tips: follow us')
save(im, 'gg-2026-11-17-1215-study-tip.jpg')

# Tue 4:15 free resource: ACT practice
im, d = base(TEAL, dark=True)
d.ellipse((760, -160, 1260, 340), fill=(110, 165, 151))
d.text((90, 290), 'THE GOOD GRADE', font=F('Bold', 34, False), fill=AMBER)
y = block(d, 90, 430, 'Free ACT practice questions', F('Black', 108), WHITE, 900, 1.05)
y = block(d, 90, y + 40, 'Printable practice question PDFs for the ACT. Free to download and use at home.', F('SemiBold', 50), (235, 245, 242), 880)
y += 60
for t in ['Printable PDFs', 'ACT practice', '100% free']:
    pill(d, 90, y, t, WHITE, NAVY, 42); y += 125
footer(d, 'Get them: link in bio')
save(im, 'gg-2026-11-17-1615-resource.jpg')

# Wed 12:15 Spanish parent tip
im, d = base(TEAL, dark=True)
y = block(d, 90, 430, 'Consejo para padres', F('Bold', 52, False), AMBER, 900)
y = block(d, 90, y + 20, 'Pídale que se lo explique.', F('Black', 108), WHITE, 900, 1.05)
y = block(d, 90, y + 40, 'Después de la tarea de matemáticas, pídale a su hijo que le explique un problema, paso a paso.', F('SemiBold', 50), (235, 245, 242), 880)
y = block(d, 90, y + 30, 'Si puede explicarlo con sus propias palabras, lo está entendiendo.', F('SemiBold', 50), (235, 245, 242), 880)
footer(d, 'Clases en español: link en la bio')
save(im, 'gg-2026-11-18-1215-espanol.jpg')

# Wed 4:15 blog spotlight (newest post)
im, d = base(AMBER)
d.rectangle((80, 280, 700, 336), fill=AMBER)
d.text((90, 290), 'NUEVO EN EL BLOG', font=F('Bold', 34, False), fill=NAVY)
y = block(d, 90, 430, '¿Qué es el GPA? Guía para padres de high school', F('Black', 96), NAVY, 900, 1.06)
y = block(d, 90, y + 40, 'Cómo se calcula el GPA y por qué importa, explicado en español.', F('SemiBold', 48), (60, 60, 60), 880)
y += 50
for t in ['Qué es el GPA', 'La escala de 4 puntos', 'Ejemplo paso a paso']:
    pill(d, 90, y, t, NAVY, WHITE, 40); y += 118
w = d.textlength('Léalo: link en la bio', font=F('Bold', 36, False)) + 80
x0 = (W - w) / 2
d.rounded_rectangle((x0, 1560, x0 + w, 1640), 40, fill=NAVY)
d.text((W // 2, 1600), 'Léalo: link en la bio', font=F('Bold', 36, False), fill=WHITE, anchor='mm')
save(im, 'gg-2026-11-18-1615-blog.jpg')

# Thu 12:15 about: when we teach
im, d = base()
y = block(d, 90, 430, 'Tutoring that fits your schedule', F('Black', 104), NAVY, 900, 1.05)
y = block(d, 90, y + 30, 'Live 1-on-1 online lessons. Hours (Eastern):', F('SemiBold', 48), GRAY, 880)
y += 40
for day, hrs in [('Mon–Fri', '8am–9pm'), ('Saturday', '10am–9pm'), ('Sunday', '10am–5pm')]:
    d.rounded_rectangle((90, y, 990, y + 104), 26, fill=WHITE, outline=(223, 234, 230), width=3)
    d.text((140, y + 52), day, font=F('Bold', 48), fill=NAVY, anchor='lm')
    d.text((940, y + 52), hrs, font=F('Bold', 48), fill=TEAL, anchor='rm')
    y += 124
block(d, 90, y + 30, 'In English, Spanish or both. No driving: learn from home.', F('SemiBold', 46), GRAY, 880)
footer(d, 'Learn more: link in bio')
save(im, 'gg-2026-11-19-1215-about.jpg')

# Thu 4:15 consultation CTA
im, d = base(NAVY, dark=True)
y = block(d, 90, 430, 'What happens in a free consultation?', F('Black', 100), WHITE, 900, 1.05)
y += 50
for n, t in [('1', 'We get to know your student'), ('2', 'We talk about goals and classes'), ('3', 'We suggest a plan that fits')]:
    d.ellipse((90, y, 180, y + 90), fill=AMBER)
    d.text((135, y + 45), n, font=F('Black', 48), fill=NAVY, anchor='mm')
    block(d, 210, y + 18, t, F('Bold', 46), WHITE, 780)
    y += 140
y = block(d, 90, y + 20, '30 minutes. Free. Book online or call/text (937) 368-7471.', F('SemiBold', 46), LIGHT, 880)
footer(d, 'Book free: link in bio')
save(im, 'gg-2026-11-19-1615-consultation.jpg')

# Fri 12:15 question (SAT/ACT-style functions)
question('SAT/ACT math question', 'If f(x) = 3x − 5,\nwhat is\nf(4) − f(2)?', ['A) 1', 'B) 2', 'C) 6', 'D) 7'], 'gg-2026-11-20-1215-question.jpg')

# Fri 4:15 answer
answer('Answer: C) 6',
       [('f(4) = 3(4) − 5 = 7', NAVY), ('f(2) = 3(2) − 5 = 1', NAVY), ('7 − 1 = 6', TEAL)],
       'Why not B) 2?',
       'That subtracts the inputs (4 − 2). Find each output first, then subtract.',
       'gg-2026-11-20-1615-answer.jpg')
