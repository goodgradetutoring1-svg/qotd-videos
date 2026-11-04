from PIL import Image, ImageDraw, ImageFont
import os

OUT = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920
NAVY = (27, 51, 75); TEAL = (86, 143, 129); AMBER = (248, 176, 69)
CREAM = (250, 247, 241); WHITE = (255, 255, 255); SOFT = (238, 245, 243); GRAY = (70, 86, 104)
FD = '/usr/share/fonts/opentype/inter/'

def F(weight, size, display=True):
    return ImageFont.truetype(FD + ('InterDisplay-' if display else 'Inter-') + weight + '.otf', size)

def wrap(d, text, font, maxw):
    lines = []
    for para in text.split('\n'):
        words, cur = para.split(' '), ''
        for w in words:
            t = (cur + ' ' + w).strip()
            if d.textlength(t, font=font) <= maxw:
                cur = t
            else:
                lines.append(cur); cur = w
        lines.append(cur)
    return lines

def block(d, x, y, text, font, fill, maxw, gap=1.18, align='left'):
    lh = int(font.size * gap)
    for line in wrap(d, text, font, maxw):
        if align == 'center':
            d.text((W // 2, y), line, font=font, fill=fill, anchor='ma')
        else:
            d.text((x, y), line, font=font, fill=fill)
        y += lh
    return y

def base(bg=CREAM, dark=False):
    im = Image.new('RGB', (W, H), bg)
    d = ImageDraw.Draw(im)
    # decorative soft circles
    d.ellipse((760, -160, 1260, 340), fill=(TEAL if dark else SOFT))
    d.ellipse((-200, 1600, 240, 2040), fill=((36, 66, 95) if dark else (252, 236, 210)))
    # brand label (kept below top safe zone)
    d.text((90, 290), 'THE GOOD GRADE', font=F('Bold', 34, False), fill=(AMBER if dark else TEAL))
    d.rounded_rectangle((90, 340, 190, 350), 5, fill=AMBER)
    return im, d

def footer(d, text='goodgradetutoring.com', dark=False):
    w = d.textlength(text, font=F('Bold', 36, False)) + 80
    x0 = (W - w) / 2
    d.rounded_rectangle((x0, 1560, x0 + w, 1640), 40, fill=AMBER)
    d.text((W // 2, 1600), text, font=F('Bold', 36, False), fill=NAVY, anchor='mm')

def pill(d, x, y, text, bg, fg, size=34):
    f = F('Bold', size, False)
    w = d.textlength(text, font=f) + 56
    d.rounded_rectangle((x, y, x + w, y + size + 34), (size + 34) // 2, fill=bg)
    d.text((x + 28, y + 17), text, font=f, fill=fg)
    return x + w

def save(im, name):
    p = os.path.join(OUT, name)
    im.save(p, 'JPEG', quality=90, optimize=True)
    print(p)

# 1. Intro
im, d = base()
y = block(d, 90, 430, 'Hi! We\'re\nThe Good Grade', F('Black', 104), NAVY, 900, 1.08)
y = block(d, 90, y + 40, 'A husband-and-wife tutoring team: Odelin teaches math, Brandon teaches science.', F('SemiBold', 48), GRAY, 880)
y += 50
for t, c in [('Live 1-on-1 online', TEAL), ('K–12 + early college', NAVY), ('English or Spanish', AMBER)]:
    pill(d, 90, y, t, c, WHITE if c != AMBER else NAVY, 40); y += 120
footer(d, 'Free consultation: link in bio')
save(im, 'story-1-intro.jpg')

# 2. Quick question
im, d = base(NAVY, dark=True)
y = block(d, 90, 430, 'Quick question', F('Bold', 52, False), AMBER, 900)
y = block(d, 90, y + 20, 'What is 25% of 80?', F('Black', 120), WHITE, 900, 1.05)
y += 60
opts = ['A) 15', 'B) 20', 'C) 25', 'D) 32']
for o in opts:
    d.rounded_rectangle((90, y, 990, y + 120), 26, fill=(36, 66, 95))
    d.text((140, y + 60), o, font=F('Bold', 54), fill=WHITE, anchor='lm')
    y += 150
block(d, 90, y + 30, 'Answer in the next story', F('SemiBold', 44, False), (200, 214, 226), 900)
save(im, 'story-2-question.jpg')

# 3. Answer
im, d = base()
y = block(d, 90, 430, 'Answer: B) 20', F('Black', 110), NAVY, 900, 1.05)
y += 50
d.rounded_rectangle((90, y, 990, y + 520), 36, fill=WHITE, outline=(223, 234, 230), width=3)
yy = block(d, 140, y + 50, '25% is the same as 1/4.', F('Bold', 52), NAVY, 800)
yy = block(d, 140, yy + 20, 'So 25% of 80 = 80 ÷ 4 = 20.', F('Bold', 52), TEAL, 800)
block(d, 140, yy + 30, 'Quick trick: 50% is half, 25% is half of that.', F('Medium', 44, False), GRAY, 800)
block(d, 90, y + 600, 'New Question of the Day every afternoon on our page.', F('SemiBold', 46), GRAY, 880)
footer(d, 'Follow for more')
save(im, 'story-3-answer.jpg')

# 4. Hablamos espanol
im, d = base(TEAL, dark=True)
y = block(d, 90, 430, 'Hablamos español', F('Black', 112), WHITE, 900, 1.05)
y = block(d, 90, y + 40, 'Clases de matemáticas y ciencias en vivo, uno a uno, en español, en inglés o en los dos idiomas.', F('SemiBold', 50), (235, 245, 242), 890)
y = block(d, 90, y + 40, 'Los padres pueden hablar con nosotros en español.', F('SemiBold', 50), (235, 245, 242), 890)
footer(d, 'Consulta gratis: link en la bio')
save(im, 'story-4-espanol.jpg')

# 5. Free resources
im, d = base()
y = block(d, 90, 430, 'Free cheat sheets', F('Black', 108), NAVY, 900, 1.05)
y = block(d, 90, y + 30, 'Printable PDFs for students, 100% free:', F('SemiBold', 48), GRAY, 880)
y += 40
items = ['Basic Math', 'Algebra Essentials', 'Pre-Calculus', 'Calculus', 'SAT Math Formulas', 'Chemistry', 'Biology', 'Physics']
x, col = 90, 0
for i, t in enumerate(items):
    c = [TEAL, NAVY, AMBER][i % 3]
    nx = pill(d, x, y, t, c, WHITE if c != AMBER else NAVY, 38)
    if nx > 700 or col == 1:
        x, y, col = 90, y + 112, 0
    else:
        x, col = nx + 20, col + 1
footer(d, 'Grab them: link in bio')
save(im, 'story-5-resources.jpg')

# 6. Book a consultation
im, d = base(NAVY, dark=True)
y = block(d, 90, 430, 'Free 30-minute consultation', F('Black', 104), WHITE, 900, 1.05)
y = block(d, 90, y + 40, 'Tell us about your student\'s grade, subject and goals. We\'ll recommend a plan. No pressure.', F('SemiBold', 48), (200, 214, 226), 880)
y += 60
for t in ['Pick a time online in seconds', 'Or call/text (937) 368-7471']:
    d.rounded_rectangle((90, y, 990, y + 110), 26, fill=(36, 66, 95))
    d.text((140, y + 55), t, font=F('Bold', 46, False), fill=WHITE, anchor='lm')
    y += 140
footer(d, 'Book now: link in bio')
save(im, 'story-6-consultation.jpg')

# 7. ACT tip
im, d = base()
y = block(d, 90, 430, 'ACT Math tip', F('Bold', 52, False), TEAL, 900)
y = block(d, 90, y + 20, '45 questions.\n50 minutes.', F('Black', 120), NAVY, 900, 1.05)
y = block(d, 90, y + 40, 'That\'s a little over a minute each. If a question is eating your time, mark it, move on, and come back.', F('SemiBold', 50), GRAY, 880)
d.rounded_rectangle((90, y + 50, 990, y + 200), 30, fill=SOFT)
block(d, 130, y + 85, 'Free ACT practice questions on our site.', F('Bold', 44, False), NAVY, 820)
footer(d, 'Link in bio')
save(im, 'story-7-act-tip.jpg')

# 8. Blog
im, d = base(AMBER)
d.rectangle((80, 280, 700, 336), fill=AMBER)
d.text((90, 290), 'NEW ON THE BLOG', font=F('Bold', 34, False), fill=NAVY)
y = block(d, 90, 430, 'How to help your child with fractions at home', F('Black', 100), NAVY, 900, 1.06)
y = block(d, 90, y + 40, 'Simple visual tricks, worked examples, and the mistakes to watch for in grades 3–5.', F('SemiBold', 48), (60, 60, 60), 880)
# fraction strips
y += 60
d.rounded_rectangle((90, y, 990, y + 80), 16, fill=NAVY); d.text((540, y + 40), '1', font=F('Bold', 40), fill=WHITE, anchor='mm')
y += 100
for k, c in [(2, TEAL), (4, WHITE)]:
    w = 900 / k
    for i in range(k):
        x0 = 90 + i * w
        d.rounded_rectangle((x0 + 4, y, x0 + w - 4, y + 80), 16, fill=c if i == 0 else None, outline=NAVY, width=4)
    d.text((90 + w / 2, y + 40), f'1/{k}', font=F('Bold', 38), fill=WHITE if k == 2 else NAVY, anchor='mm')
    y += 100
im2 = im; d2 = ImageDraw.Draw(im2)
w = d2.textlength('Read it: goodgradetutoring.com/blog', font=F('Bold', 36, False)) + 80
x0 = (W - w) / 2
d2.rounded_rectangle((x0, 1560, x0 + w, 1640), 40, fill=NAVY)
d2.text((W // 2, 1600), 'Read it: goodgradetutoring.com/blog', font=F('Bold', 36, False), fill=WHITE, anchor='mm')
save(im2, 'story-8-blog.jpg')
