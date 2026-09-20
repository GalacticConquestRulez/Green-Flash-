#!/bin/bash
# The RAINS page hero film, from Ephraim's own drone edit of the wall.
# out/ is not in git, so this is how the file comes back if it is ever rebuilt.
#
#   assets/source/ephraim-drop/16_9 VFX.mp4
#                                    4K60 H.264, 58 s, from "Ephraim website.zip"
#                                    (the owner, 2026-09-20). The graded cut with
#                                    the titles on it; "16_9 No FX.mp4" is the same
#                                    flight without them and is kept as source.
#   out/video/hero-rains.mp4         four beats from it, 720p30 crf 30, no audio:
#
#     0.0-4.6    the Manhattan skyline with the "Open Air Gallery" title card
#     9.2-13.7   the descent over the block to the wall
#     31.6-34.3  the finished wall: three faces, RAINS, the AMC placard
#     36.7-40.1  close, the painter on the lift
#     40.3-44.6  close on the faces as the lift pulls back
#     44.8-49.3  the pull-away over the block
#
#   Every boundary above is one of the film's own cuts (scene detection puts
#   them at 4.65, 9.12, 13.78, 31.03, 34.38, 36.55, 40.15, 44.65), so no beat
#   starts or ends mid-move. The stretches left out are the edit's graphics -
#   the paint-can flourish at 6 s, the light flare at 22 s, the rotoscoped
#   musician at 28 s and the doves at 30 s - which read as somebody else's
#   film behind a headline. 24.0 s in total.
#
#   out/video/hero-rains.webp        poster, from 10.4 s into the cut - the
#                                    finished wall. A data-saver visitor gets
#                                    the poster and nothing else (site.js drops
#                                    autoplay there), so the poster has to be
#                                    the wall rather than the skyline the clip
#                                    happens to open on.
set -e
cd "$(dirname "$0")"
mkdir -p out/video
SRC='assets/source/ephraim-drop/16_9 VFX.mp4'
OUT=out/video/hero-rains
nice -n 15 ffmpeg -v error -y -i "$SRC" -an -filter_complex \
  "[0:v]trim=0:4.6,setpts=PTS-STARTPTS[a];[0:v]trim=9.2:13.7,setpts=PTS-STARTPTS[b];[0:v]trim=31.6:34.3,setpts=PTS-STARTPTS[c];[0:v]trim=36.7:40.1,setpts=PTS-STARTPTS[d];[0:v]trim=40.3:44.6,setpts=PTS-STARTPTS[e];[0:v]trim=44.8:49.3,setpts=PTS-STARTPTS[f];[a][b][c][d][e][f]concat=n=6:v=1:a=0,scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,fps=30,format=yuv420p[v]" \
  -map "[v]" -c:v libx264 -preset slow -crf 30 -profile:v high -movflags +faststart "$OUT.mp4"
nice -n 15 ffmpeg -v error -y -ss 10.4 -i "$OUT.mp4" -frames:v 1 -c:v libwebp -quality 74 "$OUT.webp"
ls -la "$OUT".*
