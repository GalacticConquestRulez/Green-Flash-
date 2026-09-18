# Open Air Gallery — openairgallery.art (Ephraim, owner and painter)

A Green Flash client site. Read this before any design or build here; add to it as the owner
gives rules and the client gives notes. Build and verify in a preview first
(preview.greenflashusa.com/p/openairgallery/), one idea per commit, then promote.

## What the client is
Open Air Gallery is a **muralist and large-image company** led by Ephraim — not a painting
gallery. National brand murals plus civil-rights portraits:
Gucci, New York (81' × 80') · Crown Royal × Trail Blazers, Portland (85' × 90') · Uber,
San Francisco (62' × 23') · Victoria's Secret, Austin (36' × 8') · Vitamin Water, New York
(9' × 20') · Sprite (11' × 16') · Moncler · Red Bull · Monkey 47 · Ford Mustang (23' × 36') ·
Showtime, Boston (18' × 9') · Upendo, Los Angeles (18' × 18') · I Am A Man, Chicago (15' × 32')
· **I Am Speaking: John Lewis, Rochester (53' × 50') · Malcolm X, Rochester (53' × 50')**.
Services on the current site: murals, banners, art, graffiti removal, a shop, a "book a free
consultation" call to action; contact hello@openairgallery.art; Instagram @openairmurals.

## The site being replaced (surveyed 2026-09-18)
Wix (nameservers ns6/ns7.wixdns.net; three Wix IPs). Home / Work / About / Contact / Shop /
Graffiti Removal; **Media and Shop return 404**. Home: a tiny-planet NYC hero, four numbered
mural slides that lazy-load blurred, a broken black shape mid-page, a headline colliding with a
mint watermark, blurred "latest projects" images, an FAQ about payment/shipping/warranty.
Accent: mint green on white; dark nav. 45 media files across Home/Work/About. The work is far
better than the site presenting it — that is the whole brief in one sentence.

## Open questions (answer before designing)
- Scope: replace the whole Wix site on our stack, same sections, or a narrower first cut?
- Ephraim's own notes and any reference sites he likes — the reference is the spec.
- Domain: who holds the Wix/registrar login; move DNS to us or point A records at the droplet.
- Are Shop and Graffiti Removal real offerings to keep, or drop them?
- Original high-resolution mural photos — from Ephraim, or pulled from Wix at native size?
- Company-first (Open Air Gallery) or artist-first (Ephraim) in voice and structure?
- Timeline.

## Decisions (2026-09-18, confirmed by the owner)
1. **Scope:** full replacement, five pages — Home · Work (page per project) · About (Ephraim,
   team, process) · Services (murals, banners, graffiti removal) · Contact (consultation).
   Media and Shop dropped (both 404 today).
2. **References:** show a mockup first, then ask. The reference is the work itself:
   photo-first, full-bleed, **dimensions as the hook** ("81′ × 80′" set large on every
   project), dark canvas so the murals are the only colour, his mint kept as the one accent.
   One kinesthetic touch: a human figure dragged beside each mural for scale.
3. **Domain:** no transfer — Ephraim's Wix login, an A record to the droplet + `www` CNAME,
   certbot. Preview at preview.greenflashusa.com/p/openairgallery/ until approved.
4. **Graffiti removal stays** (Services page); **Shop goes** (Phase 2 if he sells prints).
5. **Photos:** originals from Ephraim (shared folder, people in frame for scale); the mockup
   uses the Wix copies meanwhile.
6. **Voice:** company brand (Open Air Gallery), artist-led story (Ephraim named in the hero,
   his page, his process).
7. **Timeline:** plan + mockup in a day; build 2–3 days; Ephraim reviews on preview; live
   within two weeks, gated only by photos and the Wix login.
First step on "go": one-page plan, HTML mockup of Home + the Gucci project page, screenshot to
Ephraim before any production code.

## Confirmed on 2026-09-18 (supersedes the proposals above where they differ)
- **Six pages, no shop:** Home · Work (page per project) · About · Services (murals, banners)
  · **Graffiti Removal (its own page — "make sure it looks awesome")** · Contact.
- **Design:** dark canvas, dimensions as the hook, mint `#71EEB8` (sampled from his site) as the
  single accent. Company brand, artist-led story.
- **Hosting:** preview at preview.greenflashusa.com/p/<slug>/, then **live on a Green Flash
  subdomain (openair.greenflashusa.com) while Wix keeps serving openairgallery.art.** Nothing
  touches Wix or the real domain until Ephraim switches DNS himself, later.
- **Home page references graffiti removal the way Max's site advertises Green Flash** — a
  distinct band (`gr_band()`, modelled on DGM's `gf_band()`), placed after the process.
- **The graffiti-removal signature is an animation of a graffitied brick wall being cleaned to
  sparkling new** — "Wash" in the motion vocabulary (Roll · Scale · Cure · Wash). Drawn wall by
  default; his real before/after photos if he sends them.
- The full build plan is `PLAN.md` in this repo (copied from the approved plan). Opus subagents
  implement one step each from it; the lead session reviews each commit.
- `research/wix/` holds the saved Wix pages and a full-page screenshot from the audit
  (untracked) — the source for `wix-sources.json` and for quoting his own copy.
