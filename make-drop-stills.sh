#!/bin/bash
# Still frames for the four walls in Ephraim's drop of 2026-09-25.
#
# Four of the films in that drop are the only record we have of four walls -
# nobody sent photographs of them - so the gallery on each project page is cut
# out of the film itself, exactly the way the Flower City Arts Center gallery
# was cut out of Max's film in the drop before this one
# (docs/ephraim-drop-2026-09-20.md, step 5).
#
# Frames are pulled at the camera's own size - 3840x2160 for the two landscape
# films, 2160x3840 for the two portrait ones - and written as near-lossless
# JPEG into assets/, where ./process.sh turns each one into the four WebP
# renditions build.py's pic() asks for. Nothing is cropped and nothing is
# scaled here: the still is the frame.
#
# The timecodes were chosen by eye off a contact sheet of each film. They are
# the wall from the street, the painter on the lift, the detail close enough to
# see the brush, and the block the wall stands on. A frame with a title card,
# a legal card or a camera move through it is never used: a still that is
# obviously a frame grab reads as a mistake, and one that carries somebody
# else's typography reads as theirs.
#
# assets/ is gitignored, like every other image on this site, so this script is
# the record: running it on a clean clone puts the same twenty frames back.
set -e
cd "$(dirname "$0")"
D=assets/source/drop-2026-09-25
A=assets

still() {   # still <source> <seconds> <name>
  nice -n 15 ffmpeg -v error -y -ss "$2" -i "$D/$1" -frames:v 1 -q:v 2 "$A/$3.jpg"
}

# A$AP Rocky x Ray-Ban, Grand Street - the wall from the block, the roundel,
# the painter at the face, and the street it stands over.
still asap-rocky-ray-ban.mov 32.64 asap-rocky-ray-ban-new-york-hero
still asap-rocky-ray-ban.mov  5.76 asap-rocky-ray-ban-new-york-1
still asap-rocky-ray-ban.mov  9.60 asap-rocky-ray-ban-new-york-2
still asap-rocky-ray-ban.mov 28.80 asap-rocky-ray-ban-new-york-3
still asap-rocky-ray-ban.mov 44.16 asap-rocky-ray-ban-new-york-4

# Moncler, Grand Street - the finished wall, the eye being painted, the street
# sign that names the corner, and the MONCLER GENIUS handstyle on the brick.
still moncler.mov 37.88 moncler-new-york-hero
still moncler.mov 11.53 moncler-new-york-1
still moncler.mov 18.12 moncler-new-york-2
still moncler.mov 28.00 moncler-new-york-3
still moncler.mov 31.29 moncler-new-york-4

# Fords Gin - shot portrait, so these frames are 2160x3840 and the page frames
# them portrait rather than stretching them into a landscape well.
still fords-gin.mov 29.19 fords-gin-new-york-hero
still fords-gin.mov  6.95 fords-gin-new-york-1
still fords-gin.mov  9.73 fords-gin-new-york-2
still fords-gin.mov 12.51 fords-gin-new-york-3
still fords-gin.mov 23.63 fords-gin-new-york-4

# Christian Louboutin x Shun Sudo - portrait as well.
still louboutin-shun-sudo.mov 10.54 louboutin-shun-sudo-new-york-hero
still louboutin-shun-sudo.mov  4.06 louboutin-shun-sudo-new-york-1
still louboutin-shun-sudo.mov  5.68 louboutin-shun-sudo-new-york-2
still louboutin-shun-sudo.mov 12.17 louboutin-shun-sudo-new-york-3
still louboutin-shun-sudo.mov 18.66 louboutin-shun-sudo-new-york-4

ls -la "$A"/asap-rocky-ray-ban-new-york-*.jpg "$A"/moncler-new-york-*.jpg \
       "$A"/fords-gin-new-york-*.jpg "$A"/louboutin-shun-sudo-new-york-*.jpg
echo STILLS DONE
