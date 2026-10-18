"""Build a reel from an edit list (JSON) + the shared booking CTA.

Usage: python3 build_reel.py <edit.json> <out.mp4>

edit.json:
{
  "cta": "/home/claude/assets/cta_booking.mp4",
  "beats": [
    {"text": "POV: You made\\nyour own **sushi**", "size": 92,
     "clips": [{"src": "IMG_8475_3", "in": 1.0, "dur": 1.6}, ...]},
    ...
  ]
}
Text: "\\n" = line break, **word** = yellow highlight.
"""
import json, os, re, subprocess, sys, glob, tempfile
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)                      # sushi-reels checkout
FOOTAGE_DIRS = [d for d in [os.environ.get("FOOTAGE_DIR"), "/home/claude/sushi-footage/footage"] + glob.glob("/root/.claude/uploads/*") if d]
W, H = 1080, 1920
FONT = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
WHITE, YELLOW, BLACK = (255, 255, 255), (255, 214, 0), (0, 0, 0)
TEXT_CENTER_Y = 1180
ORIG_GAIN = 1.0              # room sound / guest voices
BGM_DIR = os.path.join(REPO, "assets", "bgm")
BGM_GAIN = 0.35              # music under the clips
BGM_GAIN_CTA = 0.2           # music under the narration          # centre-low; keeps clear of the bottom UI zone (~last 380px)

spec = json.load(open(sys.argv[1]))
OUT = sys.argv[2]
tmp = tempfile.mkdtemp(dir=os.environ.get("TMPDIR"))


def find_src(name):
    # footage lives in FOOTAGE_DIR (clone of the private sushi-footage repo) as <name>.mov,
    # or in chat uploads as <uuid>-<name>.mov
    for d in FOOTAGE_DIRS:
        hits = [f for f in glob.glob(f"{d}/{name}.*") + glob.glob(f"{d}/*-{name}.*")
                if f.lower().endswith(".mov")]
        if hits:
            return hits[0]
    sys.exit(f"source not found: {name} (looked in {FOOTAGE_DIRS})")


def text_png(text, size, path):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, size)
    lines = text.split("\n")
    lh = int(size * 1.18)
    y = TEXT_CENTER_Y - lh * len(lines) // 2
    stroke = max(6, size // 11)
    for line in lines:
        parts = [(p, i % 2 == 1) for i, p in enumerate(re.split(r"\*\*", line)) if p]
        widths = [d.textlength(p, font=f) for p, _ in parts]
        x = (W - sum(widths)) / 2
        for (p, hl), w in zip(parts, widths):
            d.text((x, y), p, font=f, fill=YELLOW if hl else WHITE,
                   stroke_width=stroke, stroke_fill=BLACK)
            x += w
        y += lh
    im.save(path)


segs = []
n = 0
for bi, beat in enumerate(spec["beats"]):
    tp = os.path.join(tmp, f"text{bi}.png")
    text_png(beat["text"], beat.get("size", 84), tp)
    for c in beat["clips"]:
        out = os.path.join(tmp, f"seg{n:02d}.mp4")
        vf = (f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
              f"fps=30,eq=saturation=1.08:contrast=1.03,setsar=1[v];[v][1:v]overlay=0:0,format=yuv420p[o];"
              # real room sound: clean rumble, even out level between clips, soft edges at the cuts
              f"[0:a]aresample=48000,highpass=f=90,dynaudnorm=f=150:g=15:p=0.7,volume={ORIG_GAIN * c.get('vol', 1.0)},"
              f"afade=t=in:d=0.04,afade=t=out:st={max(0, c['dur'] - 0.06)}:d=0.06,apad[a]")
        subprocess.run([
            "ffmpeg", "-v", "error", "-y", "-ss", str(c["in"]), "-t", str(c["dur"]),
            "-i", find_src(c["src"]), "-loop", "1", "-i", tp,
            "-filter_complex", vf, "-map", "[o]", "-map", "[a]", "-t", str(c["dur"]),
            "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-r", "30",
            "-c:a", "aac", "-b:a", "128k", "-ar", "48000", out], check=True)
        segs.append(out)
        n += 1

if spec.get("cta"):
    segs.append(spec["cta"] if os.path.isabs(spec["cta"]) else os.path.join(REPO, spec["cta"]))

clips_dur = sum(c["dur"] for b in spec["beats"] for c in b["clips"])
lst = os.path.join(tmp, "list.txt")
with open(lst, "w") as fh:
    fh.writelines(f"file '{s}'\n" for s in segs)
joined = os.path.join(tmp, "joined.mp4")
# re-encode on concat so every part (incl. CTA) shares timestamps cleanly
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst,
                "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-r", "30", "-pix_fmt", "yuv420p",
                "-c:a", "pcm_s16le", joined.replace(".mp4", ".mov")], check=True)
joined = joined.replace(".mp4", ".mov")
total = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                       "-of", "csv=p=0", joined]))

bgm = os.path.join(tmp, "bgm.wav")
if spec.get("bgm_file"):
    # track from the BGM library (assets/bgm): loop if short, start offset, level-match, fade out at the end
    src = spec["bgm_file"] if os.path.isabs(spec["bgm_file"]) else os.path.join(BGM_DIR, spec["bgm_file"])
    st = spec.get("bgm_start", 0)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-stream_loop", "-1", "-ss", str(st), "-i", src,
                    "-af", f"atrim=0:{total:.3f},loudnorm=I=-16:TP=-2,aresample=48000,"
                           f"afade=t=in:d=0.3,afade=t=out:st={total - 1.5:.3f}:d=1.5",
                    "-ac", "2", bgm], check=True)
    seed = os.path.basename(src)
else:
    # fallback: original BGM generated for this video (seed -> same track on rebuild)
    seed = spec.get("bgm_seed", 1)
    subprocess.run(["python3", os.path.join(HERE, "music.py"), f"{total:.2f}", str(seed), bgm]
                   + ([str(spec["bgm_bpm"])] if spec.get("bgm_bpm") else []), check=True)
# BGM sits under the voices; drops further during the narrated CTA
mix = (f"[1:a]volume='if(lt(t,{clips_dur:.2f}),{BGM_GAIN},{BGM_GAIN_CTA})':eval=frame[m];"
       f"[0:a][m]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", joined, "-i", bgm, "-filter_complex", mix,
                "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                "-movflags", "+faststart", OUT], check=True)
dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                     "-of", "csv=p=0", OUT]))
print(f"done: {OUT} ({dur:.2f}s, {n} clips, bgm {seed})")
