#!/bin/bash
# Regenerates the Home hero clip from Ephraim's Johnnie Walker footage.
# out/ is not in git, so this is how the file comes back if it is ever rebuilt.
#
#   assets/source/johnnie-walker.mov   4K HEVC, 43 s, uploaded by the owner
#                                      2026-09-19 (was "Johnny Walker .MOV")
#   out/video/hero-johnnie-walker.mp4  three beats from it, 720p30 crf 30, no
#                                      audio: the drone reveal of the wall
#                                      (2–12 s), Ephraim on the lift painting
#                                      it (15–21 s), the aerial down the block
#                                      (29–37 s). The source's own cuts sit at
#                                      ~14 s and ~27 s, so these are clean.
#   out/video/hero-johnnie-walker.webp poster, from 3 s in
set -e
cd "$(dirname "$0")"
mkdir -p out/video
SRC=assets/source/johnnie-walker.mov
OUT=out/video/hero-johnnie-walker
ffmpeg -v error -y -i "$SRC" -an -filter_complex \
  "[0:v]trim=2:12,setpts=PTS-STARTPTS[a];[0:v]trim=15:21,setpts=PTS-STARTPTS[b];[0:v]trim=29:37,setpts=PTS-STARTPTS[c];[a][b][c]concat=n=3:v=1:a=0,scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,fps=30,format=yuv420p[v]" \
  -map "[v]" -c:v libx264 -preset slow -crf 30 -profile:v high -movflags +faststart "$OUT.mp4"
ffmpeg -v error -y -ss 3 -i "$OUT.mp4" -frames:v 1 -c:v libwebp -quality 74 "$OUT.webp"
ls -la "$OUT".*
