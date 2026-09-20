#!/bin/bash
# "The wall going up" - the portrait reel on the RAINS page, beside the story.
# out/ is not in git, so this is how the file comes back if it is ever rebuilt.
#
#   assets/source/ephraim-drop/9_16 Progress Visual_.mp4
#                                    2160x3840 60fps H.264, 34 s, from
#                                    "Ephraim website.zip" (the owner, 2026-09-20)
#   out/video/rains-progress.mp4     the reel whole, 720x1280 30fps crf 30, no
#                                    audio. It is Ephraim's own edit and it
#                                    already has the arc the section wants -
#                                    the RAINS artwork card, the wall going up
#                                    from the lift over the block, and the
#                                    Open Air Gallery card it ends on - so it
#                                    is re-encoded rather than re-cut. 2160 is
#                                    exactly three times 720, so the scale is
#                                    a clean third and nothing is cropped.
#   out/video/rains-progress.webp    poster, from 12 s in: the lift at the
#                                    wall, which is what the section is about.
set -e
cd "$(dirname "$0")"
mkdir -p out/video
SRC='assets/source/ephraim-drop/9_16 Progress Visual_.mp4'
OUT=out/video/rains-progress
nice -n 15 ffmpeg -v error -y -i "$SRC" -an \
  -vf "scale=720:1280,fps=30,format=yuv420p" \
  -c:v libx264 -preset slow -crf 30 -profile:v high -movflags +faststart "$OUT.mp4"
nice -n 15 ffmpeg -v error -y -ss 12 -i "$OUT.mp4" -frames:v 1 -c:v libwebp -quality 74 "$OUT.webp"
ls -la "$OUT".*
