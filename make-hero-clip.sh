#!/bin/bash
# Regenerates the Home hero clip from Ephraim's Johnnie Walker footage.
# out/ is not in git, so this is how the file comes back if it is ever rebuilt.
#
#   assets/source/johnnie-walker.mov   3840x2160 HEVC, 43 s, uploaded by the
#                                      owner 2026-09-19 (was "Johnny Walker .MOV")
#
#   Three beats, 24 s in total, at the source's own 3840x2160:
#
#     2-12   the drone reveal of the wall
#     15-21  Ephraim on the lift painting it
#     29-37  the aerial down the block
#
#   The source's own cuts sit at ~14 s and ~27 s, so these are clean.
#
#   The source reports 23.9965 fps, not the 30 this script used to force. That
#   force was resampling a 24 fps drone pan up to 30 - two frames duplicated in
#   every five, and a move that judders - so it is gone: the cut is 24 fps, the
#   rate the camera shot at, which is also what the Flower City hero does.
#
#   out/video/hero-johnnie-walker.mp4       3840x2160 24fps, H.264 high@5.2,
#                                           crf 23 capped at 12 Mbit, no audio.
#   out/video/hero-johnnie-walker-1080.mp4  the same cut at 1920x1080, crf 24.
#                                           The server HTML names this one; a
#                                           phone with no script and a reduced-
#                                           motion visitor never fetch the big
#                                           file, and site.js swaps it in above
#                                           900px before the element loads.
#   out/video/hero-johnnie-walker.webp      poster, 4K, from 3 s in.
set -e
cd "$(dirname "$0")"
mkdir -p out/video
SRC=assets/source/johnnie-walker.mov
OUT=out/video/hero-johnnie-walker
CUTS="[0:v]trim=2:12,setpts=PTS-STARTPTS[a];[0:v]trim=15:21,setpts=PTS-STARTPTS[b];[0:v]trim=29:37,setpts=PTS-STARTPTS[c];[a][b][c]concat=n=3:v=1:a=0"

# Both renditions come from the master. A 1080 made by shrinking the 4K encode
# inherits its artefacts and then adds its own.
enc() {   # enc <width> <height> <crf> <dest>
  nice -n 15 ffmpeg -v error -y -i "$SRC" -an -filter_complex \
    "$CUTS,scale=$1:$2:force_original_aspect_ratio=increase,crop=$1:$2,fps=24,format=yuv420p[v]" \
    -map "[v]" -c:v libx264 -preset slow -crf "$3" -maxrate 12M -bufsize 24M \
    -profile:v high -level 5.2 -movflags +faststart "$4"
}
enc 3840 2160 23 "$OUT.mp4"
enc 1920 1080 24 "$OUT-1080.mp4"
nice -n 15 ffmpeg -v error -y -ss 3 -i "$OUT.mp4" -frames:v 1 -c:v libwebp -quality 76 "$OUT.webp"
ls -la "$OUT".mp4 "$OUT-1080.mp4" "$OUT.webp"
