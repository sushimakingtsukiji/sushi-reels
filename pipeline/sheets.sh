#!/bin/bash
# Labeled 5-frame strip per clip (skips clips already done), stacked 5 per sheet.
# Usage: sheets.sh <footage_dir> <out_dir> [sheet_prefix]
SRC="$1"; S="$2"; PRE="${3:-sheet}"
mkdir -p "$S"; NEW=()
for f in "$SRC"/*.MOV "$SRC"/*.mov; do
  [ -e "$f" ] || continue
  n=$(basename "$f" | sed 's/^[0-9a-f]\{8\}-//; s/\.[^.]*$//')
  [ -f "$S/$n.jpg" ] && continue
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")
  printf "%s %.1f | " "$n" "$d"
  ffmpeg -v error -y -i "$f" -vf "fps=5/$d,scale=180:-1,drawtext=fontfile=/usr/share/fonts/opentype/inter/Inter-Black.otf:text='$n':x=4:y=4:fontsize=16:fontcolor=yellow:box=1:boxcolor=black,tile=5x1" -frames:v 1 "$S/$n.jpg"
  NEW+=("$n.jpg")
done
echo
cd "$S" && python3 - "$PRE" "${NEW[@]}" <<'PY'
import sys
from PIL import Image
pre, fs = sys.argv[1], sorted(sys.argv[2:])
for i in range(0, len(fs), 5):
    ims = [Image.open(f) for f in fs[i:i+5]]
    o = Image.new('RGB', (max(im.width for im in ims), sum(im.height for im in ims))); y = 0
    for im in ims: o.paste(im, (0, y)); y += im.height
    o.save(f'{pre}{i//5}.jpg')
print(fs)
PY
