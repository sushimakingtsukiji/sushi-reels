"""Animated caption overlays ("text_style": "kinetic", 2026-11-12, reel 004).

Each beat gets its own PNG sequence (30 fps, RGBA 1080x1920) that build_reel.py overlays
on the beat's clips. Per beat:
  "anim": "pop"    words pop in one by one (scale bounce)
          "marker" line fades in, then an orange marker sweeps behind the **keyword**
          "slide"  lines slide in from the left, staggered
          "stamp"  big text drops in from slightly larger size (for hooks / endings)
  "chapter": "01  SUIT UP"  small pill top-left that slides in
  "y": centre of the text block (default 1180)
Global extras (spec "kinetic": {...}): "badge" text pill top-right, "progress": orange bar
along the top showing how far through the story we are.
**word** = accent colour (orange), or marker background for "marker".
"""
import math, os, re
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
F_BIG = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
F_SMALL = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
WHITE, ORANGE, NAVY, CREAM, RED = (255, 255, 255), (255, 140, 26), (27, 42, 74), (255, 246, 232), (215, 38, 61)

_fonts = {}
def font(path, size):
    k = (path, size)
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(path, size)
    return _fonts[k]

def ease_out(x):
    x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3

def back_out(x):
    x = max(0.0, min(1.0, x)); c1 = 1.9; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

def parse(line):
    return [(p, i % 2 == 1) for i, p in enumerate(re.split(r"\*\*", line)) if p]

def word_img(word, size, color, shadow=True):
    f = font(F_BIG, size)
    l, t, r, b = f.getbbox(word)
    pad = 24
    im = Image.new("RGBA", (r - l + pad * 2, b - t + pad * 2), (0, 0, 0, 0))
    if shadow:
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((pad - l + 3, pad - t + 6), word, font=f, fill=(0, 0, 0, 170))
        sh = sh.filter(ImageFilter.GaussianBlur(7))
        im.alpha_composite(sh)
    d = ImageDraw.Draw(im)
    d.text((pad - l, pad - t), word, font=f, fill=color, stroke_width=max(2, size // 40), stroke_fill=(40, 25, 10))
    return im, pad

def layout(text, size):
    """-> list of lines; each line = list of (word, is_hl). Words keep trailing spaces."""
    out = []
    for line in text.split("\n"):
        words = []
        for p, hl in parse(line):
            for w in re.findall(r"\S+\s*", p):
                words.append((w, hl))
        out.append(words)
    return out

def chapter_pill(canvas, label, t):
    if not label:
        return
    k = ease_out(t / 0.35)
    f = font(F_SMALL, 40)
    num, _, rest = label.partition(" ")
    nw = ImageDraw.Draw(canvas).textlength(num, font=f)
    rw = ImageDraw.Draw(canvas).textlength(" " + rest.strip(), font=f)
    w, h = int(nw + rw + 56), 70
    pill = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(pill)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=h // 2, fill=CREAM + (240,))
    d.text((28, 12), num, font=f, fill=RED)
    d.text((28 + nw, 12), " " + rest.strip(), font=f, fill=NAVY)
    pill.putalpha(pill.getchannel("A").point(lambda a: int(a * k)))
    canvas.alpha_composite(pill, (int(60 - 160 * (1 - k)), 250))

def badge(canvas, text):
    if not text:
        return
    f = font(F_SMALL, 34)
    w = int(ImageDraw.Draw(canvas).textlength(text, font=f)) + 48
    h = 60
    b = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(b)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=h // 2, fill=(0, 0, 0, 110))
    d.text((24, 10), text, font=f, fill=WHITE)
    canvas.alpha_composite(b, (W - w - 60, 255))

def progress(canvas, frac):
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle([60, 210, W - 60, 220], radius=5, fill=(255, 255, 255, 90))
    x = 60 + int((W - 120) * max(0.0, min(1.0, frac)))
    if x > 66:
        d.rounded_rectangle([60, 210, x, 220], radius=5, fill=ORANGE + (255,))

def render_text(canvas, beat, t):
    anim = beat.get("anim", "pop")
    size = beat.get("size", 96)
    cy = beat.get("y", 1180)
    lines = layout(beat["text"], size)
    lh = int(size * 1.22)
    top = cy - lh * len(lines) // 2
    stagger = 0.11 if anim == "pop" else 0.13
    idx = 0
    for li, words in enumerate(lines):
        imgs = []
        for w, hl in words:
            col = ORANGE if (hl and anim != "marker") else WHITE
            imgs.append(word_img(w.rstrip(), size, col) + (w, hl))
        space = font(F_BIG, size).getlength(" ")
        widths = [im.width - 2 * pad for im, pad, w, hl in imgs]
        total = sum(widths) + space * (len(imgs) - 1)
        x = (W - total) / 2
        y = top + li * lh
        if anim == "marker":
            # marker bar behind highlighted words, sweeping after the line is in
            mk = ease_out((t - 0.25 - 0.1 * li) / 0.3)
            xx = x
            for (im, pad, w, hl), wd in zip(imgs, widths):
                if hl and mk > 0:
                    m = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                    ImageDraw.Draw(m).rounded_rectangle(
                        [xx - 14, y + size * 0.12, xx - 14 + (wd + 28) * mk, y + size * 1.12],
                        radius=12, fill=ORANGE + (235,))
                    canvas.alpha_composite(m)
                xx += wd + space
        for (im, pad, w, hl), wd in zip(imgs, widths):
            if anim == "pop":
                k = (t - idx * stagger) / 0.22
                if k > 0:
                    s = max(0.01, back_out(k))
                    a = ease_out(k * 1.5)
                    im2 = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
                    im2.putalpha(im2.getchannel("A").point(lambda v: int(v * a)))
                    cx, cyy = x + wd / 2, y + size * 0.6
                    canvas.alpha_composite(im2, (int(cx - im2.width / 2), int(cyy - im2.height / 2)))
            elif anim == "slide":
                k = ease_out((t - li * stagger) / 0.3)
                if k > 0:
                    im2 = im.copy(); im2.putalpha(im2.getchannel("A").point(lambda v: int(v * k)))
                    canvas.alpha_composite(im2, (int(x - pad - 140 * (1 - k)), int(y - pad)))
            elif anim == "stamp":
                k = ease_out(t / 0.28)
                s = 1.35 - 0.35 * k
                im2 = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
                im2.putalpha(im2.getchannel("A").point(lambda v: int(v * min(1, k * 1.4))))
                cx, cyy = W / 2 + (x + wd / 2 - W / 2) * s, cy + (y + size * 0.6 - cy) * s
                canvas.alpha_composite(im2, (int(cx - im2.width / 2), int(cyy - im2.height / 2)))
            else:  # marker: whole line fades in
                k = ease_out((t - 0.1 * li) / 0.2)
                if k > 0:
                    im2 = im.copy(); im2.putalpha(im2.getchannel("A").point(lambda v: int(v * k)))
                    canvas.alpha_composite(im2, (int(x - pad), int(y - pad)))
            x += wd + space
            idx += 1

def render_beat(beat, beat_start, beat_dur, body_dur, glob, outdir):
    os.makedirs(outdir, exist_ok=True)
    n = int(math.ceil(beat_dur * FPS)) + 2
    for i in range(n):
        t = i / FPS
        c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        if glob.get("progress"):
            progress(c, (beat_start + t) / body_dur)
        badge(c, glob.get("badge"))
        chapter_pill(c, beat.get("chapter"), t)
        render_text(c, beat, t)
        c.save(os.path.join(outdir, f"{i:04d}.png"), compress_level=1)
    return os.path.join(outdir, "%04d.png")
