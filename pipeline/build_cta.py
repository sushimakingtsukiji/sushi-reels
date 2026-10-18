"""Build the reusable booking CTA clip (website part only) from the screen recording.

Usage: python3 build_cta.py <screen_recording.mp4> <out.mp4>
"""
import subprocess, sys, os, tempfile
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SRC, OUT = sys.argv[1], sys.argv[2]
W, H = 1080, 1920
BG = (241, 239, 234)          # site background cream
NAVY = (26, 50, 67)           # site button navy
RED = (200, 16, 46)           # logo red
FONT = "/usr/share/fonts/opentype/inter/Inter-Black.otf"

# screen recording geometry (1180x2556): drop status bar + in-app URL bar
CROP_Y, CROP_H = 220, 2336
SCALE_H = 1340
SCALE_W = round(1180 * SCALE_H / CROP_H) // 2 * 2
SX, SY = (W - SCALE_W) // 2, 330
k = SCALE_H / CROP_H
BTN_CX, BTN_CY = SX + 590 * k, SY + 2226 * k      # BOOK NOW (sticky bar) centre

# source segments (seconds in the recording)
HERO = (4.5, 5.6)
SCROLL = (5.6, 8.25)
SCROLL_SPEED = 2.2
TAP = 8.25
TAP_HOLD = 1.4
BOOKING = (8.5, 10.8)

tmp = tempfile.mkdtemp(dir=os.environ.get("TMPDIR"))
p = lambda n: os.path.join(tmp, n)


def text_layer(lines, name):
    """lines: list of [(text, colour), ...] per line. Centered in top band."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    size = 84
    f = ImageFont.truetype(FONT, size)
    total_h = len(lines) * (size + 18)
    y = (SY - total_h) // 2 + 6
    for line in lines:
        widths = [d.textlength(t, font=f) for t, _ in line]
        x = (W - sum(widths)) / 2
        for (t, c), w in zip(line, widths):
            d.text((x, y), t, font=f, fill=c)
            x += w
        y += size + 18
    im.save(p(name))


# background with soft shadow + rounded mask for the phone screen
bg = Image.new("RGB", (W, H), BG)
sh = Image.new("L", (W, H), 0)
ImageDraw.Draw(sh).rounded_rectangle((SX + 6, SY + 18, SX + SCALE_W + 6, SY + SCALE_H + 18), 48, fill=110)
sh = sh.filter(ImageFilter.GaussianBlur(28))
bg.paste(Image.new("RGB", (W, H), (120, 115, 105)), (0, 0), sh)
bg.save(p("bg.png"))
mask = Image.new("L", (SCALE_W, SCALE_H), 0)
ImageDraw.Draw(mask).rounded_rectangle((0, 0, SCALE_W - 1, SCALE_H - 1), 44, fill=255)
mask.save(p("mask.png"))

text_layer([[("Tap the ", NAVY), ("link", RED)], [("in our bio", NAVY)]], "t1.png")
text_layer([[("Hit ", NAVY), ("BOOK NOW", RED)]], "t2.png")
text_layer([[("Pick your date", NAVY)], [("See you in ", NAVY), ("Tsukiji!", RED)]], "t3.png")

# red ring + arrow for the tap moment
ring = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(ring)
rw, rh = SCALE_W * 0.98, 118
d.ellipse((BTN_CX - rw / 2, BTN_CY - rh / 2, BTN_CX + rw / 2, BTN_CY + rh / 2), outline=RED, width=12)
ay0, ay1 = BTN_CY + rh / 2 + 14, H - 70
d.rectangle((BTN_CX - 16, ay0 + 60, BTN_CX + 16, ay1), fill=RED)
d.polygon([(BTN_CX, ay0), (BTN_CX - 58, ay0 + 80), (BTN_CX + 58, ay0 + 80)], fill=RED)
ring.save(p("ring.png"))

hero_d = HERO[1] - HERO[0]
scroll_d = (SCROLL[1] - SCROLL[0]) / SCROLL_SPEED
book_d = BOOKING[1] - BOOKING[0]
t1_end = hero_d + scroll_d
t2_end = t1_end + TAP_HOLD
total = t2_end + book_d

screen = f"crop=1180:{CROP_H}:0:{CROP_Y},scale={SCALE_W}:{SCALE_H},fps=30,format=rgba"
# hero frames still show the expanded in-app browser bar (ends ~y310): crop a little tighter there
HW = round(1180 * (CROP_H - 90) / CROP_H) // 2 * 2
screen_hero = f"crop={HW}:{CROP_H - 90}:{(1180 - HW) // 2}:310,scale={SCALE_W}:{SCALE_H},fps=30,format=rgba"
fc = (
    f"[0:v]trim={HERO[0]}:{HERO[1]},setpts=PTS-STARTPTS,{screen_hero}[a];"
    f"[0:v]trim={SCROLL[0]}:{SCROLL[1]},setpts=(PTS-STARTPTS)/{SCROLL_SPEED},{screen}[b];"
    f"[0:v]trim={TAP}:{TAP + 0.05},setpts=PTS-STARTPTS,{screen},tpad=stop_mode=clone:stop_duration={TAP_HOLD},trim=0:{TAP_HOLD}[c];"
    f"[0:v]trim={BOOKING[0]}:{BOOKING[1]},setpts=PTS-STARTPTS,{screen}[d];"
    f"[a][b][c][d]concat=n=4:v=1:a=0,setsar=1[scr];"
    f"[2:v]fps=30,format=gray,trim=0:{total},setpts=PTS-STARTPTS[m];"
    f"[scr][m]alphamerge[scrm];"
    f"[1:v]fps=30,trim=0:{total},setpts=PTS-STARTPTS[bg];"
    f"[bg][scrm]overlay={SX}:{SY}:shortest=1[v1];"
    f"[v1][3:v]overlay=0:0:enable='lt(t,{t1_end})'[v2];"
    f"[v2][4:v]overlay=0:0:enable='between(t,{t1_end},{t2_end})'[v3];"
    f"[v3][5:v]overlay=0:0:enable='gte(t,{t2_end})'[v4];"
    f"[v4][6:v]overlay=0:0:enable='between(t,{t1_end + 0.15},{t2_end})',format=yuv420p[v]"
)
cmd = ["ffmpeg", "-v", "error", "-y", "-i", SRC]
for n in ["bg.png", "mask.png", "t1.png", "t2.png", "t3.png", "ring.png"]:
    cmd += ["-loop", "1", "-i", p(n)]
# narration: one phrase per on-screen step, trimmed to speech and placed at each step's start
# (speech regions measured with silencedetect; regenerate with pipeline/tts.py if the script changes)
NARR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "narration")
phrases = [("p1.wav", 0.28, 1.70, 0.20),            # "Tap the link in our bio."
           ("p2.wav", 0.33, 1.12, t1_end + 0.10),   # "Hit Book Now!"
           ("p3.wav", 0.28, 2.25, t2_end + 0.10)]   # "Pick your date, and see you in Tsukiji!"
acmd = ["ffmpeg", "-v", "error", "-y"]
for f, *_ in phrases:
    acmd += ["-i", os.path.join(NARR, f)]
afc = ""
for i, (_, a, b, at) in enumerate(phrases):
    afc += (f"[{i}:a]atrim={a}:{b},asetpts=PTS-STARTPTS,aresample=48000,"
            f"afade=t=in:d=0.03,afade=t=out:st={b - a - 0.05}:d=0.05,adelay={int(at * 1000)}:all=1[n{i}];")
afc += f"[n0][n1][n2]amix=inputs=3:normalize=0,pan=stereo|c0=c0|c1=c0,apad=whole_dur={total:.3f}[aout]"
subprocess.run(acmd + ["-filter_complex", afc, "-map", "[aout]", p("narr.wav")], check=True)
cmd += ["-i", p("narr.wav"),
        "-filter_complex", fc, "-map", "[v]", "-map", "7:a",
        "-t", f"{total:.3f}", "-r", "30", "-c:v", "libx264", "-crf", "18", "-preset", "medium",
        "-c:a", "aac", "-b:a", "128k", OUT]
subprocess.run(cmd, check=True)
print(f"done: {OUT} ({total:.2f}s)")
