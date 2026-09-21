#!/bin/bash
# "The wall going up" - the portrait reel on the RAINS page, beside the story.
# out/ is not in git, so this is how the file comes back if it is ever rebuilt.
#
#   assets/source/ephraim-drop/9_16 Progress Visual_.mp4
#                                    2160x3840 60fps H.264, 34 s, from
#                                    "Ephraim website.zip" (the owner, 2026-09-20)
#
#   The reel is kept whole rather than re-cut: it is Ephraim's own edit and it
#   already has the arc the section wants - the RAINS artwork card, the wall
#   going up from the lift over the block, and the Open Air Gallery card it
#   ends on.
#
#   out/video/rains-progress.mp4       2160x3840 60fps at source size and rate,
#                                      H.264 high@5.2, crf 23 capped at 12
#                                      Mbit, no audio, faststart. A build
#                                      intermediate only: the poster below is
#                                      cut from it and nothing on the site
#                                      names it, so it is not kept in
#                                      out/video and never shipped (2026-09-21).
#   out/video/rains-progress-1080.mp4  1080x1920, crf 24 - the ONLY file the
#                                      page names, at every width. The frame is
#                                      300px wide on a desktop and narrower on a
#                                      phone, so there is nothing a big screen
#                                      could usefully swap in: progress_band()
#                                      carries no data-hi and calls
#                                      clip_sources(..., hi=False).
#   out/video/rains-progress.webp      poster, full size, from 12 s in: the
#                                      lift at the wall, which is what the
#                                      section is about.
set -e
cd "$(dirname "$0")"
mkdir -p out/video
SRC='assets/source/ephraim-drop/9_16 Progress Visual_.mp4'
OUT=out/video/rains-progress

enc() {   # enc <width> <height> <crf> <dest>
  nice -n 15 ffmpeg -v error -y -i "$SRC" -an \
    -vf "scale=$1:$2:force_original_aspect_ratio=increase,crop=$1:$2,fps=60,format=yuv420p" \
    -c:v libx264 -preset slow -crf "$3" -maxrate 12M -bufsize 24M \
    -profile:v high -level 5.2 -movflags +faststart "$4"
}
enc 2160 3840 23 "$OUT.mp4"
enc 1080 1920 24 "$OUT-1080.mp4"
nice -n 15 ffmpeg -v error -y -ss 12 -i "$OUT.mp4" -frames:v 1 -c:v libwebp -quality 76 "$OUT.webp"
# The master has done its job once the poster is out of it. Keeping it would put
# thirty megabytes nothing on the site can fetch into every rsync of out/video/.
rm -f "$OUT.mp4"
ls -la "$OUT-1080.mp4" "$OUT.webp"
