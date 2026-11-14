# The Good Grade: feed videos + carousels (7-format rotation)

Approved by Brandon on Nov 14, 2026. Starts the week of Mon Nov 16, 2026.
This is separate from the daily Question of the Day Reel (3:00 PM) and the Stories (12:15 and 4:15 PM weekdays). Neither of those changes.

## Schedule (America/New_York, 10:30 AM)
| Day | Medium | Networks |
|---|---|---|
| Mon | Carousel | Instagram + Facebook (1080x1350), TikTok photo post (1080x1920 copy) |
| Tue | Video | IG Reel, FB Reel, TikTok, YouTube Short (1080x1920 MP4 + cover) |
| Wed | Carousel | same as Mon |
| Thu | Video | same as Tue |
| Fri | Carousel | same as Mon |
| Sat | Video | same as Tue |

## Rotation
Post index i = 6*w + d. w = whole weeks from Mon 2026-11-16. d = 0 (Mon) through 5 (Sat).
FORMAT = FORMATS[i % 7]. Because there are 6 posts a week and 7 formats, each format moves between video and carousel over the weeks.

FORMATS (order matters, so the same format never posts twice in a row):
1. Quick tip: one idea, explained like talking to a parent at the kitchen table. Video ~15 s; carousel 4–5 slides.
2. Practice question: pause or "swipe when you have your answer", then walk through it. Video ~30–35 s with a 3-2-1 countdown; carousel 5–6 slides (question, hint, work, answer + trap, bonus, CTA).
3. Parent question: one real FAQ in plain words. Video ~30 s; carousel 5–6 slides.
4. Whiteboard walkthrough: marker handwriting, worked out live. Video 45–60 s; carousel 5–7 slides of handwritten steps.
5. Common mistake: open with the mistake ("most students get this wrong because…"), then fix it. Video ~30–35 s; carousel 4–6 slides.
6. SAT/ACT tip: one test trick with a real (original) example. Video 45–60 s; carousel 5–7 slides.
7. Why it clicks: a short "aha" moment. No student names, no results promised. Video 15–25 s; carousel 4–5 slides.

Never the same twice in a row (check the previous line in LOG.md): format, opening line, opener type, CTA, visual style/background, voice, music bed, thumbnail/cover style.
- Opener type: real-life example / the question / the mistake. Never "Did you know…" or "In this video…".
- CTA: CTAS[i % 4] = free cheat sheets / comment your answer / free consultation / try 10 free questions. Swap with the next one only if it truly doesn't fit the post (and still never repeat the previous post's CTA).
- Visual style by format: cards (white), notebook, soft teal, whiteboard, grid paper, test booklet (navy header), cream. Each post also varies its layout (centered vs. left, card vs. bare text, where the brand label sits).
- Videos: voice alternates af_heart / am_michael. Music bed rotates lofi → pluck → pad → keys, never the same as the previous video.
- Video lengths mix 15 / 30 / 60 s.

## Audiences and subjects (rotate inside the formats)
K–8 parents (elementary/middle math), high school (algebra, geometry, SAT/ACT), sciences (biology, chemistry, physics), college and adult learners (organic chemistry, biochemistry, calculus, study skills for STEM courses). At least one post a week for parents and one for college/adult learners. Every other week, one carousel is bilingual (Spanish first, short English line under it, "usted") for Spanish-speaking families.

## Never
No fake AI teacher or realistic fake person; no photos of real people; no faces or voices of Brandon or Odelin (they have said no for now; if they later film themselves, they supply the clip). No hype, no guaranteed results, no invented statistics, students or testimonials. Captions 0–3 hashtags (never more than 5), first-person plural ("our tutors"), written like a person.

## Files
- gg_engine.py: video engine (beats → MP4). Needs voice/ copied to /home/claude/qotd and `bash setup.sh` run once.
- video_samples.py: the 7 approved sample videos (one per format). Use as templates.
- carousel_sample.py: the approved sample carousel (Practice question). Use it as the template for all carousels.
- covers_sample.py: one cover style per format.
- LOG.md: one line per post.
