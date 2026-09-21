#!/bin/bash
# The two films whole, behind the play button on their project pages.
# out/ is not in git, so this is how the files come back if they are rebuilt.
#
# The hero clips are cuts with no sound, built to sit behind a headline. These
# are the films themselves - Ephraim's fifty-eight second edit of the RAINS
# job and Max's minute on the Flower City wall - at the bitrate and the size
# they were delivered in, with their audio, because a visitor who presses play
# on "watch the film" has asked for the film and not for a version of it.
#
#   assets/source/ephraim-drop/16_9 VFX.mp4         4K60 H.264 + AAC, 58 s
#   assets/source/ephraim-drop/flower-city-arts-center.mov
#                                                   4K24 H.264 + AAC, 60 s
#
# Both are already H.264 and AAC, so nothing is re-encoded: the streams are
# copied and the index is moved to the front (+faststart) so a browser can
# start playing from the first range request instead of fetching to the end
# of a three hundred megabyte file to find the moov atom. Only the video and
# audio streams are mapped, and -write_tmcd 0 keeps the muxer from writing a
# timecode track of its own out of the .mov's - nothing plays it and every
# browser skips it.
#
# THE RAINS SOURCE IS DAMAGED. "16_9 VFX.mp4" as it came out of the zip has a
# corrupt packet at dts 3020000 - 50.35 s, frame 3021 of 3507 - and every
# reader stops there, ffmpeg and ffprobe alike (-err_detect ignore_err does
# not get past it; the NAL length in the file is wrong, so there is nothing
# after it to resynchronise on). So the film here is 50.35 s of the 58.45 s
# Ephraim cut: it loses the tail of the closing pull-away and nothing else.
# The hero cut is unaffected - its last beat ends at 49.3 s, before the
# damage. "16_9 No FX.mp4" reads end to end and is whole, but it is the same
# flight *without* the grade and the title card, so it is not a substitute for
# the film this page is offering. **Ask Ephraim to send 16_9 VFX.mp4 again**
# and re-run this script; the duration below is how you check it arrived.
#
# They are big, and that is the point of the button: the element is
# preload="none" and nothing is fetched until somebody clicks. nginx serves
# /assets/video/ with the mp4 module and Accept-Ranges, so what is fetched is
# the part being watched.
#
#   out/video/film-rains.mp4         the RAINS edit, whole, with sound
#   out/video/film-rains.webp        poster, 1920 wide: the finished wall
#   out/video/film-flower-city.mp4   Max's film, whole, with sound
#   out/video/film-flower-city.webp  poster, 1920 wide: the finished mural
set -e
cd "$(dirname "$0")"
mkdir -p out/video
R='assets/source/ephraim-drop/16_9 VFX.mp4'
F='assets/source/ephraim-drop/flower-city-arts-center.mov'

# -shortest so the file ends where the picture does: the RAINS audio track
# survives a second past the last readable frame, and a film that ends on a
# frozen frame looks like our mistake rather than the file's.
nice -n 15 ffmpeg -v warning -y -i "$R" -map 0:v:0 -map 0:a:0 -c copy -shortest \
  -write_tmcd 0 -movflags +faststart out/video/film-rains.mp4
nice -n 15 ffmpeg -v warning -y -i "$F" -map 0:v:0 -map 0:a:0 -c copy \
  -write_tmcd 0 -movflags +faststart out/video/film-flower-city.mp4

# The posters are the same two frames the heroes are postered on, so the page
# does not show a visitor two different "this is the wall" stills.
nice -n 15 ffmpeg -v error -y -ss 32.8 -i "$R" -frames:v 1 -vf "scale=1920:-2" \
  -c:v libwebp -quality 76 out/video/film-rains.webp
nice -n 15 ffmpeg -v error -y -ss 22.0 -i "$F" -frames:v 1 -vf "scale=1920:-2" \
  -c:v libwebp -quality 76 out/video/film-flower-city.webp

ls -la out/video/film-*
