#!/usr/bin/env python3
"""Fetch all unread entries from a Folo feed with pagination, save titles+descriptions+IDs."""

import subprocess
import json
import sys

FEED_ID = "204012564879785984"

def run_folo(args):
    cmd = ["npx", "--yes", "folocli@latest"] + args
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return json.loads(result.stdout)

all_entries = []
cursor = None

while True:
    cmd_args = ["timeline", "--feed", FEED_ID, "--unread-only"]
    if cursor:
        cmd_args += ["--cursor", cursor]
    
    resp = run_folo(cmd_args)
    data = resp.get("data", {})
    entries = data.get("entries", [])
    
    if not entries:
        break
    
    all_entries.extend(entries)
    print(f"Fetched {len(entries)} entries (total: {len(all_entries)})", file=sys.stderr)
    
    if not data.get("hasNext"):
        break
    cursor = data.get("nextCursor")

# Remove duplicates by entry ID
seen = set()
unique = []
for e in all_entries:
    eid = e["entries"]["id"]
    if eid not in seen:
        seen.add(eid)
        unique.append(e)

print(f"\n=== {len(unique)} unique unread entries ===\n")

for i, e in enumerate(unique):
    ent = e["entries"]
    print(f"[{i+1}] ID: {ent['id']}")
    print(f"    Title: {ent['title']}")
    print(f"    Desc:  {ent.get('description', 'N/A')[:200]}")
    print(f"    Date:  {ent.get('publishedAt', 'N/A')}")
    print(f"    Cats:  {', '.join(ent.get('categories', []))}")
    print()
