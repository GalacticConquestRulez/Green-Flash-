#!/usr/bin/env python3
"""Pull placeholder photography from Ephraim's live Wix site into assets/.

Read wix-sources.json, and for every URL in it ask Wix for a much larger
rendition of the *same* image. The rule that makes this safe:

    keep the media id, the ~mv2.<ext> and the trailing filename byte-for-byte;
    rewrite ONLY the transform segment between /v1/ and that filename.

A /v1/crop/x_,y_,w_,h_/ prefix is kept as well - that crop is the client's own
framing of the shot and we have no business overriding it.

Never construct a bare https://static.wixstatic.com/media/<id> URL. Wix answers
403 to those; the full rendered path is the only thing it serves.

Files land as assets/<slug>-hero.<ext>, assets/<slug>-1.<ext>, ... and every
fetch is recorded in assets/_sources.json so the swap to Ephraim's originals is
auditable. Both directories are gitignored: this is a cache, not source.

    python3 fetch-wix.py                  # fetch everything missing
    python3 fetch-wix.py --only gucci-new-york upendo-los-angeles
    python3 fetch-wix.py --force          # refetch even if the file is there

See docs/images.md for the swap procedure.
"""

import argparse
import hashlib
import io
import json
import os
import re
import sys
import time
from datetime import datetime, timezone

import requests
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCES = os.path.join(HERE, "wix-sources.json")
ASSETS = os.path.join(HERE, "assets")
LEDGER = os.path.join(ASSETS, "_sources.json")

# Step down until Wix gives us something substantial. Wix never upscales, so a
# w_3000 request against a 1242px original simply returns 1242px - the step
# down is for the URLs Wix refuses outright at the top size.
WIDTHS = (3000, 2400, 1600)
MIN_BYTES = 60 * 1024
PAUSE = 0.5

REFERER = "https://www.openairgallery.art/"
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)

EXT_BY_TYPE = {
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/avif": "avif",
}

# https://static.wixstatic.com/media/<media-id>/v1/<transform chain>/<filename>
URL_RE = re.compile(
    r"^(https://static\.wixstatic\.com/media/[^/]+/v1/)(.+)/([^/]+)$"
)
CROP_RE = re.compile(r"^(crop/[^/]+)/(.+)$")


def retarget(url, width):
    """Rewrite only the transform segment, asking for a `width`-bounded fit.

    fit with w == h bounds the longest side and preserves the aspect ratio;
    enc_auto gets us real JPEG/PNG bytes rather than the AVIF the page renders.
    """
    m = URL_RE.match(url)
    if not m:
        raise ValueError("not a rendered Wix media URL: %s" % url)
    prefix, chain, filename = m.groups()

    crop = ""
    cm = CROP_RE.match(chain)
    if cm:
        crop = cm.group(1) + "/"  # the client's framing survives untouched

    out = "%s%sfit/w_%d,h_%d,q_90,enc_auto/%s" % (prefix, crop, width, width, filename)

    # Belt and braces: a bare /media/<id> URL is a 403, and dropping the
    # trailing filename is the easiest way to accidentally build one.
    assert "/v1/" in out and out.rsplit("/", 1)[-1] == filename, out
    assert out.startswith(prefix), out
    return out


def fetch(session, url, label):
    """Try each width in turn. Return the first response over MIN_BYTES, else
    the largest 200 we saw (a genuinely small original must not fail the run)."""
    best = None
    for width in WIDTHS:
        target = retarget(url, width)
        try:
            r = session.get(target, timeout=60)
        except requests.RequestException as exc:
            print("    w_%-5d ERROR %s" % (width, exc))
            time.sleep(PAUSE)
            continue

        body = r.content if r.status_code == 200 else b""
        print("    w_%-5d %s %8d bytes  %s"
              % (width, r.status_code, len(body), r.headers.get("Content-Type", "-")))
        time.sleep(PAUSE)

        if r.status_code != 200 or not body:
            continue
        cand = (width, body, r.headers.get("Content-Type", ""))
        if len(body) > MIN_BYTES:
            return cand
        if best is None or len(body) > len(best[1]):
            best = cand

    if best is not None:
        print("    !! nothing over %d KB for %s; keeping the largest (%d bytes)"
              % (MIN_BYTES // 1024, label, len(best[1])))
    return best


def save(name, url, cand, native, ledger):
    width, body, ctype = cand
    mime = ctype.split(";")[0].strip().lower()
    ext = EXT_BY_TYPE.get(mime)
    if ext is None:
        print("    !! unexpected Content-Type %r for %s; saving as .jpg" % (ctype, name))
        ext = "jpg"
    elif ext not in ("jpg", "png"):
        print("    !! %s came back as %s - process.sh only globs jpg/jpeg/png, so "
              "this one will be ignored. Check the Accept header." % (name, mime))
    path = os.path.join(ASSETS, "%s.%s" % (name, ext))

    try:
        pixels = list(Image.open(io.BytesIO(body)).size)
    except Exception as exc:                      # noqa: BLE001 - never fatal
        print("    !! could not read pixel size (%s)" % exc)
        pixels = None

    with open(path, "wb") as fh:
        fh.write(body)

    ledger[name] = {
        "file": os.path.basename(path),
        "requested_url": retarget(url, width),
        "rendered_url": url,
        "step_width": width,
        "bytes": len(body),
        "pixels": pixels,
        "native": native,
        "content_type": ctype,
        "sha256": hashlib.sha256(body).hexdigest(),
        "fetched": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "origin": "static.wixstatic.com (openairgallery.art) - PLACEHOLDER",
    }
    print("    -> %s  %s  %d bytes"
          % (os.path.basename(path), "x".join(map(str, pixels)) if pixels else "?", len(body)))
    return pixels


def existing(name):
    for ext in ("jpg", "jpeg", "png", "webp", "avif"):
        path = os.path.join(ASSETS, "%s.%s" % (name, ext))
        if os.path.exists(path):
            return path
    return None


def jobs_from(doc, only):
    """(name, url, native) for everything we are meant to pull."""
    out = []
    for slug, p in doc["projects"].items():
        if only and slug not in only:
            continue
        if p.get("hero"):
            out.append(("%s-hero" % slug, p["hero"], p.get("native")))
        natives = p.get("gallery_native") or []
        for i, url in enumerate(p.get("gallery") or [], start=1):
            native = natives[i - 1] if i - 1 < len(natives) else None
            out.append(("%s-%d" % (slug, i), url, native))
    for name, e in doc.get("extras", {}).items():
        if only and name not in only:
            continue
        out.append((name, e["url"], e.get("native")))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--only", nargs="+", metavar="NAME",
                    help="project slugs and/or extras keys to fetch")
    ap.add_argument("--force", action="store_true",
                    help="refetch even when the file already exists")
    args = ap.parse_args()

    doc = json.load(open(SOURCES, encoding="utf-8"))
    os.makedirs(ASSETS, exist_ok=True)

    ledger = {}
    if os.path.exists(LEDGER):
        ledger = json.load(open(LEDGER, encoding="utf-8"))
    ledger.setdefault("_meta", {})
    ledger["_meta"].update({
        "what": "Provenance for every file in assets/. Each row says exactly which "
                "Wix URL it came from, at what size, and when.",
        "status": "PLACEHOLDERS pulled from Ephraim's own live Wix site. When his "
                  "originals arrive, drop them into assets/ under the same names, "
                  "delete their rows here, and re-run process.sh. See docs/images.md.",
        "referer": REFERER,
        "last_run": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    })

    session = requests.Session()
    session.headers.update({
        "User-Agent": UA,
        "Referer": REFERER,
        # Load-bearing. enc_auto means "whatever this client accepts", so an
        # ordinary browser Accept gets us AVIF or WebP bytes wearing a .jpg
        # name. Asking only for JPEG/PNG makes Wix re-encode to the real thing,
        # which is also all process.sh globs for.
        "Accept": "image/jpeg,image/png,image/*;q=0.8,*/*;q=0.5",
        "Accept-Language": "en-US,en;q=0.9",
    })

    jobs = jobs_from(doc, set(args.only) if args.only else None)
    got = skipped = failed = 0

    for name, url, native in jobs:
        have = existing(name)
        if have and not args.force:
            print("%-28s skip (%s already here)" % (name, os.path.basename(have)))
            skipped += 1
            continue
        print("%-28s %s" % (name, "native %sx%s" % tuple(native) if native else ""))
        cand = fetch(session, url, name)
        if cand is None:
            print("    !! FAILED - no usable response")
            failed += 1
            continue
        save(name, url, cand, native, ledger)
        got += 1

    with open(LEDGER, "w", encoding="utf-8") as fh:
        json.dump(ledger, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print("\nfetched %d, skipped %d, failed %d -> %s" % (got, skipped, failed, LEDGER))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
