#!/usr/bin/env bash
# Applies the prerendering-related nginx changes to a LIVE config that certbot
# has already modified, without clobbering its SSL settings.
#
# Copying deploy/nginx/green-flash-advertising.conf over the live file would
# delete certbot's ssl_certificate lines and the HTTP->HTTPS redirect, taking
# the site back to plain HTTP. This patches in place instead.
#
# Safe to re-run: each change is skipped if already present. Backs up first and
# rolls back automatically if nginx rejects the result.
#
# Usage (on the droplet, as root):
#   bash /root/greenflash-src/deploy/patch-nginx.sh
set -euo pipefail

CONF="${GF_NGINX_CONF:-/etc/nginx/sites-available/greenflash}"
BACKUP="${CONF}.bak.$(date +%Y%m%d%H%M%S)"

[ -f "$CONF" ] || { echo "ERROR: $CONF not found."; exit 1; }

cp "$CONF" "$BACKUP"
echo "Backed up to $BACKUP"

python3 - "$CONF" <<'PY'
import re, sys

path = sys.argv[1]
src = open(path).read()
original = src
changes = []

SECURITY = """        add_header X-Content-Type-Options "nosniff" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
        add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;
        add_header Cache-Control "no-cache" always;"""

NEW_ROOT_LOCATION = """    location / {
        try_files $uri $uri/index.html =404;

%s
    }""" % SECURITY

# 1. Replace the whole `location / { ... }` block: resolve prerendered
#    directories, 404 on genuine misses, and carry the headers explicitly
#    (nginx drops inherited add_header once a block defines its own).
root_loc = re.compile(r"[ \t]*location / \{.*?\n[ \t]*\}", re.S)
m = root_loc.search(src)
if m and "try_files $uri $uri/index.html =404;" not in m.group(0):
    src = src[:m.start()] + NEW_ROOT_LOCATION + src[m.end():]
    changes.append("location / now resolves prerendered dirs, 404s on misses, keeps headers")
elif m:
    changes.append("= location / already updated")

# 2. Drop the dead `location = /index.html` block. It only ever matched a
#    literal /index.html request, never "/", so its no-cache never applied.
dead = re.compile(r"\n[ \t]*#[^\n]*cache[^\n]*\n[ \t]*location = /index\.html \{.*?\n[ \t]*\}\n", re.S | re.I)
if dead.search(src):
    src = dead.sub("\n", src)
    changes.append("removed dead `location = /index.html` block")
else:
    dead2 = re.compile(r"\n[ \t]*location = /index\.html \{.*?\n[ \t]*\}\n", re.S)
    if dead2.search(src):
        src = dead2.sub("\n", src)
        changes.append("removed dead `location = /index.html` block")

# 3. Serve the prerendered 404 page for genuine misses.
if "error_page 404 /404.html;" not in src:
    block = """
    error_page 404 /404.html;
    location = /404.html {
        internal;
        add_header Cache-Control "no-cache" always;
    }
"""
    idx = src.find("index index.html;")
    if idx == -1:
        print("  ! could not find an anchor for error_page; skipping", file=sys.stderr)
    else:
        eol = src.index("\n", idx) + 1
        src = src[:eol] + block + src[eol:]
        changes.append("error_page 404 -> /404.html")
else:
    changes.append("= error_page already present")

if src != original:
    open(path, "w").write(src)

for c in changes:
    print("  " + ("" if c.startswith("=") else "+ ") + c)
if src == original:
    print("  (no textual changes)")
PY

if nginx -t 2>&1; then
  systemctl reload nginx
  echo
  echo "nginx config valid and reloaded."
else
  cp "$BACKUP" "$CONF"
  echo
  echo "nginx REJECTED the config — rolled back. Site unchanged."
  exit 1
fi
