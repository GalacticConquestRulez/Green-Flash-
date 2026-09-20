#!/bin/bash
# The Flower City Arts Center page hero film - Max's film of the Rochester wall.
# out/ is not in git, so this is how the file comes back if it is ever rebuilt.
#
#   assets/source/ephraim-drop/flower-city-arts-center.mov
#                                    4K24 H.264, 60 s, from "Ephraim website.zip"
#                                    (the owner, 2026-09-20). Film by Max -
#                                    @omgmaxgod, which is what its own title
#                                    card says and what the page credits.
#   out/video/hero-flower-city.mp4   four beats from it, 720p24 crf 30, no audio:
#
#     21.3-25.0  the finished mural, the painters still on it
#     6.0-11.1   the underpass wall with the lifts at work on it
#     50.4-57.4  the community group in front of the wall
#     0.3-5.0    the title card, FLOWER CITY ARTS CENTER / SHOT BY @OMGMAXGOD
#
#   The film's own order puts its title card first, over an aerial of the
#   interchange, and that is right for a film and wrong for a page hero: it
#   would give the top of a mural page four and a half seconds of highway
#   before the wall arrived, every twenty seconds, for ever. So the wall goes
#   first and the card is where the loop turns over - the credit is still on
#   screen for as long as it was, and the poster and the first frame are now
#   the same picture.
#
#   The boundaries are the film's own cuts (11.17, 21.21, 25, 50.29, 57.42),
#   and the third beat keeps the cut at 54.46 inside it because both sides of
#   it are the same group in front of the same wall. Left out: the MAXGOD
#   branded segment at 34-36 s and the second building at 38-45 s, which is
#   not this wall. 20.5 s in total.
#
#   24 fps is the source's own rate and it is kept: forcing a drone pan from
#   24 to 30 duplicates two frames in every five and the move judders.
#
#   out/video/hero-flower-city.webp  poster, from 1.5 s into the cut - the
#                                    finished mural, which is now also where
#                                    the clip starts, so a data-saver visitor
#                                    and a playing one see the same frame.
set -e
cd "$(dirname "$0")"
mkdir -p out/video
SRC='assets/source/ephraim-drop/flower-city-arts-center.mov'
OUT=out/video/hero-flower-city
nice -n 15 ffmpeg -v error -y -i "$SRC" -an -filter_complex \
  "[0:v]trim=21.3:25.0,setpts=PTS-STARTPTS[a];[0:v]trim=6.0:11.1,setpts=PTS-STARTPTS[b];[0:v]trim=50.4:57.4,setpts=PTS-STARTPTS[c];[0:v]trim=0.3:5.0,setpts=PTS-STARTPTS[d];[a][b][c][d]concat=n=4:v=1:a=0,scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,format=yuv420p[v]" \
  -map "[v]" -c:v libx264 -preset slow -crf 30 -profile:v high -movflags +faststart "$OUT.mp4"
nice -n 15 ffmpeg -v error -y -ss 1.5 -i "$OUT.mp4" -frames:v 1 -c:v libwebp -quality 74 "$OUT.webp"
ls -la "$OUT".*
