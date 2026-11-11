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


# ---- 2026-11-12 second round: three more caption designs (no top bar / badge) ----
F_REG = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
F_XB = "/usr/share/fonts/opentype/inter/InterDisplay-ExtraBold.otf"


def _plain(text):
    return text.replace("**", "")


def render_type(canvas, beat, t):
    """Typewriter: letters appear one by one on a dark translucent box (lower third),
    keyword in warm yellow. Feels like a story being told."""
    size = beat.get("size", 64)
    f = font(F_XB, size)
    cy = beat.get("y", 1300)
    lines = beat["text"].split("\n")
    total = sum(len(_plain(l)) for l in lines)
    shown = int(min(total, max(0, t) / 0.035))
    lh = int(size * 1.3)
    d0 = ImageDraw.Draw(canvas)
    maxw = max(d0.textlength(_plain(l), font=f) for l in lines)
    bw, bh = maxw + 70, lh * len(lines) + 40
    k = ease_out(t / 0.18)
    box = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(box).rounded_rectangle([(W - bw) / 2, cy - bh / 2, (W + bw) / 2, cy + bh / 2],
                                          radius=26, fill=(15, 15, 20, int(150 * k)))
    canvas.alpha_composite(box)
    d = ImageDraw.Draw(canvas)
    y = cy - bh / 2 + 20
    n = 0
    for line in lines:
        x = (W - d.textlength(_plain(line), font=f)) / 2
        for p, hl in parse(line):
            for ch in p:
                if n < shown:
                    d.text((x, y), ch, font=f, fill=(255, 205, 64) if hl else WHITE)
                x += d.textlength(ch, font=f)
                n += 1
        y += lh
    # blinking cursor while typing
    if shown < total or int(t * 3) % 2 == 0:
        pass


def render_sticker(canvas, beat, t, idx):
    """Sticker: each line is a slightly tilted paper sticker (cream / brand red) that pops in.
    Playful, scrapbook feel. Tilt alternates per line and per beat."""
    size = beat.get("size", 78)
    f = font(F_BIG, size)
    cy = beat.get("y", 1200)
    lines = beat["text"].split("\n")
    lh = int(size * 1.55)
    top = cy - lh * len(lines) / 2
    for li, line in enumerate(lines):
        k = (t - li * 0.12) / 0.25
        if k <= 0:
            continue
        hl_line = "**" in line
        bg = RED if hl_line else CREAM
        fg = WHITE if hl_line else NAVY
        txt = _plain(line)
        tw = ImageDraw.Draw(canvas).textlength(txt, font=f)
        l, tt, r, b = f.getbbox(txt)
        pw, ph = int(tw + 64), int(b - tt + 44)
        st = Image.new("RGBA", (pw + 40, ph + 40), (0, 0, 0, 0))
        sh = Image.new("RGBA", st.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([24, 28, 24 + pw, 28 + ph], radius=14, fill=(0, 0, 0, 90))
        st.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
        dd = ImageDraw.Draw(st)
        dd.rounded_rectangle([20, 20, 20 + pw, 20 + ph], radius=14, fill=bg + (255,))
        dd.text((20 + 32 - l, 20 + 22 - tt), txt, font=f, fill=fg)
        ang = (3.5 if (li + idx) % 2 == 0 else -3.0)
        s = max(0.01, back_out(k))
        st = st.rotate(ang, resample=Image.BICUBIC, expand=True)
        st = st.resize((max(1, int(st.width * s)), max(1, int(st.height * s))), Image.LANCZOS)
        st.putalpha(st.getchannel("A").point(lambda v: int(v * min(1, k * 2))))
        xoff = (-40 if (li + idx) % 2 == 0 else 40) if len(lines) > 1 else 0
        canvas.alpha_composite(st, (int(W / 2 + xoff - st.width / 2), int(top + li * lh + lh / 2 - st.height / 2)))


def render_big(canvas, beat, t):
    """Big word: one huge keyword across the screen that wipes in from the left (outlined
    white), with a small line of context above it. Editorial / magazine feel."""
    cy = beat.get("y", 1180)
    lines = beat["text"].split("\n")
    small = _plain(lines[0]) if len(lines) > 1 else ""
    bigw = _plain(lines[-1]).upper()
    size = beat.get("size", 150)
    f = font(F_BIG, size)
    while ImageDraw.Draw(canvas).textlength(bigw, font=f) > W - 100 and size > 60:
        size -= 6; f = font(F_BIG, size)
    l, tt, r, b = f.getbbox(bigw)
    im = Image.new("RGBA", (r - l + 60, b - tt + 60), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((30 - l + 4, 30 - tt + 8), bigw, font=f, fill=(0, 0, 0, 150))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
    ImageDraw.Draw(im).text((30 - l, 30 - tt), bigw, font=f, fill=WHITE,
                            stroke_width=max(3, size // 30), stroke_fill=(30, 30, 30))
    k = ease_out((t - 0.12) / 0.35)
    if k > 0:
        mask = Image.new("L", im.size, 0)
        ImageDraw.Draw(mask).rectangle([0, 0, int(im.width * k), im.height], fill=255)
        a = Image.composite(im.getchannel("A"), Image.new("L", im.size, 0), mask)
        im.putalpha(a)
        canvas.alpha_composite(im, (int((W - im.width) / 2), int(cy - im.height / 2)))
    if small:
        fs = font(F_XB, 56)
        ks = ease_out(t / 0.25)
        tw = ImageDraw.Draw(canvas).textlength(small, font=fs)
        lab = Image.new("RGBA", (int(tw + 50), 86), (0, 0, 0, 0))
        ImageDraw.Draw(lab).rounded_rectangle([0, 0, lab.width - 1, 85], radius=43, fill=(255, 196, 0, 255))
        ImageDraw.Draw(lab).text((25, 10), small, font=fs, fill=(25, 25, 25))
        lab.putalpha(lab.getchannel("A").point(lambda v: int(v * ks)))
        canvas.alpha_composite(lab, (int((W - lab.width) / 2), int(cy - im.height / 2 - 70 - 30 * (1 - ks))))


_beat_counter = [0]
_render_text_orig = render_text


def render_text(canvas, beat, t):  # noqa: F811  (dispatch incl. new designs)
    a = beat.get("anim", "pop")
    if a == "type":
        return render_type(canvas, beat, t)
    if a == "sticker":
        return render_sticker(canvas, beat, t, beat.get("_idx", 0))
    if a == "big":
        return render_big(canvas, beat, t)
    return _render_text_orig(canvas, beat, t)


# ---- "native": the TikTok / Reels in-app caption look (2026-11-12, reel 004 final round) ----
EMOJI_FONT = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
_emoji_cache = {}


def emoji_img(ch, px):
    k = (ch, px)
    if k not in _emoji_cache:
        f = ImageFont.truetype(EMOJI_FONT, 109)
        im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True)
        im = im.crop(im.getbbox())
        s = px / im.height
        _emoji_cache[k] = im.resize((max(1, int(im.width * s)), px), Image.LANCZOS)
    return _emoji_cache[k]


def render_native(canvas, beat, t):
    """White rounded bubble(s) with black bold text -- the caption style viewers already know
    from TikTok/Instagram, so it reads instantly. **keyword** in warm orange, optional
    "emoji" after the last line. Pops in (slight overshoot) at the start of the beat."""
    size = beat.get("size", 66)
    f = font(F_XB, size)
    cy = beat.get("y", 1230)
    lines = beat["text"].split("\n")
    emo = beat.get("emoji")
    d0 = ImageDraw.Draw(canvas)
    asc, desc = f.getmetrics()
    lh = asc + desc + 26
    widths = [d0.textlength(_plain(l), font=f) for l in lines]
    ew = int(size * 1.05) + 14 if emo else 0
    widths[-1] += ew
    bw, bh = int(max(widths) + 80), lh * len(lines) + 30
    blk = Image.new("RGBA", (bw + 40, bh + 40), (0, 0, 0, 0))
    sh = Image.new("RGBA", blk.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(blk)
    y = 20 + 15
    for li, (line, w) in enumerate(zip(lines, widths)):
        x0 = (blk.width - w) / 2 - 30
        ImageDraw.Draw(sh).rounded_rectangle([x0 + 2, y - 13 + 6, x0 + w + 62, y + lh - 13 + 6 + (13 if li < len(lines) - 1 else 0)],
                                             radius=22, fill=(0, 0, 0, 60))
        d.rounded_rectangle([x0, y - 13, x0 + w + 60, y + lh - 13 + (13 if li < len(lines) - 1 else 0)],
                            radius=22, fill=(255, 255, 255, 250))
        y += lh
    blk = Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)), blk)
    d = ImageDraw.Draw(blk)
    y = 20 + 15
    for li, (line, w) in enumerate(zip(lines, widths)):
        x = (blk.width - w) / 2
        for p, hl in parse(line):
            d.text((x, y), p, font=f, fill=(234, 88, 12) if hl else (17, 17, 17))
            x += d.textlength(p, font=f)
        if emo and li == len(lines) - 1:
            e = emoji_img(emo, int(size * 1.05))
            blk.alpha_composite(e, (int(x + 14), int(y + (asc + desc - e.height) / 2 + 2)))
        y += lh
    k = (t) / 0.2
    s = max(0.01, back_out(k)) * 0.15 + 0.85 if k < 1 else 1.0
    a = ease_out(k * 1.6)
    if s != 1.0:
        blk = blk.resize((max(1, int(blk.width * s)), max(1, int(blk.height * s))), Image.LANCZOS)
    blk.putalpha(blk.getchannel("A").point(lambda v: int(v * a)))
    canvas.alpha_composite(blk, (int((W - blk.width) / 2), int(cy - blk.height / 2)))


_render_text_v2 = render_text


def render_text(canvas, beat, t):  # noqa: F811
    if beat.get("anim") == "native":
        return render_native(canvas, beat, t)
    return _render_text_v2(canvas, beat, t)
