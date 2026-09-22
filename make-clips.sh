#!/bin/bash
# Mendoza Marketing films - after /root/openairgallery-src/make-rains-clip.sh
# and make-films.sh. out/ is not in git, so this is how every mp4 and poster
# comes back from assets/ on a clean checkout.
#
# THE SOURCES (assets/source/, gitignored; assets/_sources.json maps them back
# to the owner's drop of 2026-09-22):
#
#   assets/source/drone/*.mov   six DJI clips from one real-estate shoot on a
#                               lakefront house, 23 June 2026. All 3840x2160,
#                               HEVC 10-bit (yuv420p10le), 59.94 fps, ~72-84
#                               Mbit, no audio, 39-161 MB. Each file carries a
#                               SECOND video stream - the DJI cover thumbnail -
#                               so every filter below reads [n:v:0] explicitly
#                               rather than letting ffmpeg choose.
#   assets/source/kelly/*.mov   three vertical ad creatives Drew cut for
#                               Kelly's Country Store, 2160x3840 HEVC + AAC.
#
# WHAT IS BUILT
#
#   out/video/hero-drone.mp4        the home hero, 3840x2160 30fps
#   out/video/hero-drone-1080.mp4   its 1920x1080 companion
#   out/video/hero-drone.webp       poster, 4K
#   out/video/drone-1..6.mp4        the whole shoot for the /drones rail,
#   out/video/drone-1..6.webp       1920x1080 30fps, with posters
#   out/video/reel-santa.mp4        the three Kelly's reels, 1080x1920,
#   out/video/reel-pretzels.mp4     WITH SOUND - they are ad creatives and the
#   out/video/reel-rice-krispies.mp4  sound is part of the work
#   out/video/reel-*.webp           their posters
#
# THE HERO CUT - which clips, and why
#
#   Six clips were watched at 0/25/50/75/95%. Two of them (0024, 0027) are
#   INTERIOR flights - a living room and a sunroom - beautiful, but a hero
#   behind "Content. Websites. Drones." has to say drone in its first second,
#   and an interior does not. Of the four exteriors, 0037 and 0036(2) are the
#   only two that are a single unbroken move on the house:
#
#     A  0036(2)  10.8 s  an elevated orbit: the drone comes down and around
#                         the roof with the pool and the lake in frame. This is
#                         the shot that could not have been taken any other
#                         way, so the film opens on it and the poster is a
#                         frame from it.
#     B  0037     10.1 s  a low push-in from the seawall across the lawn: a big
#                         tree wipes off the left of frame and the house is
#                         revealed, growing to fill the width. It ends on the
#                         calm full front elevation, which is where a headline
#                         can sit and where the loop restarts.
#
#   Neither is 12-15 s on its own (the longest exterior take is 13.4 s), so the
#   hero is those two beats cut together, the aerial then the reveal:
#
#     0.0 - 5.4   0036(2) trimmed 0.2 -> 5.6   the orbit, pool and lake in frame
#     5.4 - 14.6  0037    trimmed 0.8 -> 10.0  the reveal, ending full-frontal
#
#   14.6 s in total. The 0.2 s and 0.8 s handles drop the gimbal settling at
#   each file's head; the outs stop short of each file's last frames.
#
#   The poster is taken at 0.9 s into the cut - inside beat A, house, pool and
#   lake all in view. A data-saver visitor gets the poster and nothing else
#   (site.js drops autoplay there), so the poster has to be the aerial the film
#   opens on rather than a frame the visitor never reaches.
#
#   Both renditions are encoded from the sources, never one from the other: a
#   1080 made by shrinking the 4K encode inherits its artefacts and adds its
#   own. The companion is capped harder on purpose (crf 26, 5 Mbit) - it is the
#   file every phone, every no-script and every reduced-motion visitor is
#   offered, and site.js swaps in the 4K file above 900 px before the element
#   loads.
#
#   59.94 fps -> 30 fps is an exact 2:1 decimation of the source, so nothing
#   judders; 10-bit -> yuv420p is forced because no browser decodes 10-bit
#   H.264.
#
# THE RAIL - order and in/out points
#
#   The six clips are renumbered so the rail reads the way a property tour
#   does, outside in, instead of in DJI filename order:
#
#     drone-1  0036(2)  0.1 -> 10.6  the aerial orbit (pool, lake, roof)
#     drone-2  0037     0.2 -> 9.95  the push-in reveal from the seawall
#     drone-3  0036(1)  0.2 -> 9.2   up the lawn and in to the window wall
#     drone-4  0036     0.2 -> 13.2  the pass along the garden front
#     drone-5  0027     0.2 -> 17.3  inside: the sunroom, then the dining room
#     drone-6  0024     0.15 -> 4.2  inside: the living room and the water view
#
#   Every clip is used whole apart from the handles at each end - the shoot is
#   the point of the rail - and the longest is 17.1 s, inside the 20 s cap.
#
# THE REELS
#
#   HEVC 2160x3840 -> H.264 1080x1920, exactly half, whole, with the audio
#   transcoded to AAC 128k. SantaAd is 59.94 fps and is decimated to 30; the
#   two short ones are 48 fps and are left at 48 rather than resampled unevenly
#   (they are 2.5 s and the files are tiny either way).
#
#     reel-santa          20.3 s  the Santa event ad, captions burnt in
#     reel-pretzels        2.5 s  a box of chocolate pretzels being packed
#     reel-rice-krispies   2.3 s  sprinkles going on the bars
#
#   Posters: Santa at 12.0 s (Santa in the chair, no caption mid-animation),
#   pretzels at 2.2 s (the full box), rice krispies at 1.1 s (the finished bars).
#
# Everything runs under nice -n 15: this box builds sites while it encodes.
set -e
cd "$(dirname "$(readlink -f "$0")")"
mkdir -p out/video

D=assets/source/drone
K=assets/source/kelly

C_0024="$D/dji_fly_20260623_101038_0024_1782698976416_video.mov"
C_0027="$D/dji_fly_20260623_101538_0027_1782699062790_video.mov"
C_0036="$D/dji_fly_20260623_110026_0036_1782699367808_video.mov"
C_0036_1="$D/dji_fly_20260623_110026_0036_1782699367808_video(1).mov"
C_0036_2="$D/dji_fly_20260623_110026_0036_1782699367808_video(2).mov"
C_0037="$D/dji_fly_20260623_110414_0037_1782699383394_video.mov"

for f in "$C_0024" "$C_0027" "$C_0036" "$C_0036_1" "$C_0036_2" "$C_0037" \
         "$K/santa.mov" "$K/pretzels.mov" "$K/rice-krispies.mov"; do
  [ -f "$f" ] || { echo "make-clips.sh: missing $f" >&2; exit 1; }
done

# ---------------------------------------------------------------- the hero ---
HERO=out/video/hero-drone
CUT="[0:v:0]trim=0.2:5.6,setpts=PTS-STARTPTS[a];[1:v:0]trim=0.8:10.0,setpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=1:a=0[c]"

# hero_enc <width> <height> <crf> <maxrate> <bufsize> <dest>
hero_enc() {
  nice -n 15 ffmpeg -v error -y -i "$C_0036_2" -i "$C_0037" -an \
    -filter_complex "$CUT;[c]scale=$1:$2:force_original_aspect_ratio=increase,crop=$1:$2,fps=30,format=yuv420p[v]" \
    -map "[v]" -c:v libx264 -preset slow -crf "$3" -maxrate "$4" -bufsize "$5" \
    -profile:v high -level 5.2 -movflags +faststart "$6"
}
hero_enc 3840 2160 23 12M 24M "$HERO.mp4"
hero_enc 1920 1080 26 5M 10M "$HERO-1080.mp4"
nice -n 15 ffmpeg -v error -y -ss 0.9 -i "$HERO.mp4" -frames:v 1 \
  -c:v libwebp -quality 76 -compression_level 6 "$HERO.webp"

# ---------------------------------------------------------------- the rail ---
# rail <n> <src> <in> <out> <poster-second-into-the-cut>
rail() {
  local n=$1 src=$2 ss=$3 to=$4 pt=$5
  nice -n 15 ffmpeg -v error -y -i "$src" -an \
    -filter_complex "[0:v:0]trim=$ss:$to,setpts=PTS-STARTPTS,scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30,format=yuv420p[v]" \
    -map "[v]" -c:v libx264 -preset slow -crf 24 -maxrate 8M -bufsize 16M \
    -profile:v high -level 4.2 -movflags +faststart "out/video/drone-$n.mp4"
  # The rail posters are the cards themselves and six of them load at once, so
  # they are 1280 wide rather than the film's 1920: ~200 KB each instead of
  # ~400 KB, for a card that is never displayed above 700 px.
  nice -n 15 ffmpeg -v error -y -ss "$pt" -i "out/video/drone-$n.mp4" -frames:v 1 \
    -vf "scale=1280:-2" -c:v libwebp -quality 74 -compression_level 6 \
    "out/video/drone-$n.webp"
}
rail 1 "$C_0036_2" 0.1  10.6 0.9   # aerial orbit: house, pool, lake
rail 2 "$C_0037"   0.2  9.95 8.9   # the reveal, house full-frontal
rail 3 "$C_0036_1" 0.2  9.2  2.2   # the lawn, the house across it
rail 4 "$C_0036"   0.2  13.2 0.2   # the garden front, lake at the left
rail 5 "$C_0027"   0.2  17.3 0.3   # the sunroom, lake through the glass
rail 6 "$C_0024"   0.15 4.2  0.9   # the living room and the water view

# --------------------------------------------------------------- the reels ---
# reel <name> <src> <fps|keep> <poster-second>
reel() {
  local name=$1 src=$2 fps=$3 pt=$4 chain
  chain="scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
  [ "$fps" = keep ] || chain="$chain,fps=$fps"
  chain="$chain,format=yuv420p"
  nice -n 15 ffmpeg -v error -y -i "$src" \
    -filter_complex "[0:v:0]$chain[v]" -map "[v]" -map 0:a:0 \
    -c:v libx264 -preset slow -crf 24 -maxrate 6M -bufsize 12M \
    -profile:v high -level 4.2 -c:a aac -b:a 128k -ac 2 \
    -movflags +faststart "out/video/reel-$name.mp4"
  nice -n 15 ffmpeg -v error -y -ss "$pt" -i "out/video/reel-$name.mp4" -frames:v 1 \
    -c:v libwebp -quality 76 -compression_level 6 "out/video/reel-$name.webp"
}
reel santa         "$K/santa.mov"         30   12.0
reel pretzels      "$K/pretzels.mov"      keep 2.2
reel rice-krispies "$K/rice-krispies.mov" keep 1.1

ls -la out/video/
echo FILMS DONE
