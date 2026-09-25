#!/bin/bash
# The films in Ephraim's drop of 2026-09-25, for out/video/.
# out/ is not in git, so this is how every one of them comes back.
#
# See docs/ephraim-drop-2026-09-25.md for what each film is. The sources are
# in assets/source/drop-2026-09-25/ (gitignored, like the drop before it), and
# the copy_* file is the one used wherever the owner sent two of a film.
#
# NOTHING HERE IS CUT. The drop before this one built each page hero out of
# three beats trimmed from a longer film (make-rains-clip.sh). These are not:
# the rule for this drop is that a film is played whole or not at all. So the
# muted loop behind a headline is the entire film, and the play button beside
# it is that same film with its sound. No trim, no concat, no crop, and no
# scale on any master.
#
# ONE FILE PER FILM, plus the phone's copy of it and a poster:
#
#   film-<name>.mp4       the whole film at the camera's own size and rate,
#                         WITH ITS SOUND. H.264, crf 23, capped at 12 Mbit
#                         with a 24M buffer - the house numbers, out of
#                         make-hero-clip.sh.
#   film-<name>-1080.mp4  the same film with its SHORT side brought down to
#                         1080 - 1920x1080 off a landscape master, 1080x1920
#                         off a portrait one, and a near-square screen
#                         recording stays near-square. crf 26, capped at
#                         5 Mbit with a 10M buffer (CLAUDE.md, 2026-09-21).
#                         THE SERVER HTML NAMES THIS ONE: a phone, a
#                         no-script visitor and a reduced-motion visitor must
#                         never be asked for the 4K file, and build.py's PICK
#                         swaps the master in above 900px while the parser is
#                         still standing there.
#   film-<name>.webp      the poster, 1920 on its long side - the same frame
#                         the wall's still gallery leads with
#                         (make-drop-stills.sh), so a page never shows two
#                         different "this is the wall" pictures.
#
# WHY ONE FILE AND NOT TWO. make-films.sh, from the drop before this, keeps
# two: a silent crf-23 cut for the loop and a straight remux of the delivered
# master for the play button, "at the bitrate it was delivered in". That was
# free there because those sources were already H.264, and it is why
# film-rains.mp4 is 317 MB. Four of this drop's films are HEVC and have to be
# re-encoded whatever we do, and the four that are not are 50-77 Mbit camera
# masters - handing a visitor 380 MB for a thirty-nine second wall is not a
# feature. So each film is encoded once, at its own size and rate, with its
# sound kept, and that one file is both the muted loop and the film the button
# unmutes. Native resolution and frame rate are untouched, the phone gets the
# lighter copy and nobody else does, and the whole film is there - which is
# the whole of the owner's rule. The delivered masters stay in
# assets/source/drop-2026-09-25/.
#
# PRESET. The scripts before this one use -preset slow. Measured on this box,
# slow runs at about 1 frame a second on 4K and this drop is some twelve
# thousand frames of it; -preset fast measured 4.2 fps on the same clip and
# came out 0.9% larger than -preset medium. crf is what fixes the picture and
# it is unchanged, so the trade is a few per cent of file for a job that
# finishes in an hour instead of four.
#
# FRAME RATE. Every encode is -fps_mode passthrough: the source timestamps are
# kept exactly as they are. Three of these are variable-rate phone recordings
# flagged at 60 or 120 fps, and forcing one to a constant rate would be the
# last drop's judder bug all over again (CLAUDE.md, "The heroes play at the
# size the cameras shot them").
set -e
cd "$(dirname "$0")"
mkdir -p out/video
D=assets/source/drop-2026-09-25
O=out/video

# The 1080 companion keeps the film's own shape: the SHORT side goes to 1080
# and the long side follows it, so nothing is letterboxed into somebody else's
# rectangle and nothing is cropped to fit one.
small() {   # small <source> -> "WxH" with the short side at 1080
  local wh w h
  wh=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height \
        -of csv=p=0:s=x "$1")
  w=${wh%x*}; h=${wh#*x}
  python3 -c "
w,h=$w,$h
s=1080/min(w,h)
print(f'{round(w*s/2)*2}x{round(h*s/2)*2}')"
}

poster() {  # poster <source> <seconds> <dest.webp>
  nice -n 15 ffmpeg -v error -y -ss "$2" -i "$1" -frames:v 1 \
    -vf "scale='if(gt(iw,ih),1920,-2)':'if(gt(iw,ih),-2,1920)'" \
    -c:v libwebp -quality 76 "$3"
}

native() {  # native <source> <dest.mp4>
  nice -n 15 ffmpeg -v warning -y -i "$1" -map 0:v:0 -map 0:a:0 -c:a copy \
    -c:v libx264 -preset fast -crf 23 -maxrate 12M -bufsize 24M \
    -profile:v high -level 5.2 -pix_fmt yuv420p -fps_mode passthrough \
    -movflags +faststart "$2"
}

# level defaults to 4.2, which is right for 1080 at an ordinary rate. The two
# reels get 5.1: they are variable-rate screen recordings whose container is
# flagged 60 and 120 fps, and x264 sizes the level off that flag rather than
# off the ~37 frames a second actually in them - at 4.2 it writes a stream
# whose declared level its own macroblock rate exceeds, which is the kind of
# thing a hardware decoder is entitled to refuse. Nothing else changes; the
# picture is the same file at the same crf.
companion() {  # companion <source> <dest.mp4> [level]
  local size
  size=$(small "$1")
  nice -n 15 ffmpeg -v warning -y -i "$1" -map 0:v:0 -map 0:a:0 -c:a copy \
    -vf "scale=${size%x*}:${size#*x}" \
    -c:v libx264 -preset medium -crf 26 -maxrate 5M -bufsize 10M \
    -profile:v high -level "${3:-4.2}" -pix_fmt yuv420p -fps_mode passthrough \
    -movflags +faststart "$2"
}

film() {    # film <source> <name> <poster seconds>
  native    "$D/$1" "$O/$2.mp4"
  companion "$D/$1" "$O/$2-1080.mp4"
  poster    "$D/$1" "$3" "$O/$2.webp"
}

# ------------------------------------------------------------- the four walls
# Each of these is a project page's hero, looping and muted, and the film
# under it with its sound. Two were shot portrait and the page frames them
# portrait rather than stretching them into a landscape well.
film asap-rocky-ray-ban.mov   film-asap-rocky-ray-ban   32.64
film moncler.mov              film-moncler              37.88
film fords-gin.mov            film-fords-gin            29.19
film louboutin-shun-sudo.mov  film-louboutin-shun-sudo  10.54

# --------------------------------------------------------------- the showreel
# The capabilities film: Home leads with it, under the hero.
film capabilities.mp4         film-capabilities         57.00

# ------------------------------------------------------------- the studio film
# Four minutes and six seconds, 4K30. This one never loops - it is behind a
# play button on Home and on About and nowhere else - so its poster is the one
# frame that has to carry it on its own: the Moncler wall standing over Grand
# Street, which is a wall in the city, which is what the film is about.
film open-air-gallery-film.mov film-open-air-gallery    43.00

# ------------------------------------------------------------------ the reels
# Two screen recordings off his phone. The phone's own UI - the timer, the
# speaker glyph, the letterbox - is baked into the picture and stays there:
# cropping it out would be a re-cut, and the strip frames them as phones so it
# reads as what it is.
#
# ONE FILE EACH AND NO MASTER BESIDE IT, for the same reason the progress reel
# has none (CLAUDE.md, 2026-09-21): the frame is a few hundred pixels wide at
# every width, so a 2244-pixel rendition is bytes no screen can ever show, and
# a file nothing can fetch should not be built, shipped or synced.
reel() {    # reel <source> <name> <poster seconds>
  companion "$D/$1" "$O/$2-1080.mp4" 5.1
  poster    "$D/$1" "$3" "$O/$2.webp"
}
reel reel-block-therapy.mov  reel-block-therapy  23.72
reel reel-keep-it-oscar.mov  reel-keep-it-oscar  57.00

ls -la "$O"/film-asap* "$O"/film-moncler* "$O"/film-fords* "$O"/film-loub* \
       "$O"/film-capab* "$O"/film-open-air* "$O"/reel-*
echo DROP FILMS DONE
