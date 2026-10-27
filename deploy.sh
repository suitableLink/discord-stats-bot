#!/usr/bin/env bash
set -euo pipefail
cd /opt/discord-bots/stats
# Deploy exactly the checked-in main branch, without overwriting local modifications.
git fetch origin main
git checkout main
git pull --ff-only origin main
if [[ ! -x .venv/bin/python ]]; then python3 -m venv .venv; fi
.venv/bin/python -m pip install -r requirements.txt
sudo -n systemctl restart discord-stats
sudo -n systemctl --no-pager status discord-stats
