#!/usr/bin/env bash
# Builds the site and syncs it to /var/www/greenflash on your Droplet.
# Usage: ./deploy/deploy.sh user@your-droplet-ip
set -euo pipefail

TARGET="${1:?Usage: deploy.sh user@your-droplet-ip}"
REMOTE_ROOT="/var/www/greenflash"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"
npm ci
npm run build

rsync -az --delete dist/ "${TARGET}:${REMOTE_ROOT}/"
echo "Deployed to ${TARGET}:${REMOTE_ROOT}"
