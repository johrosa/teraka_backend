#!/usr/bin/env python3
import glob
import os

root = os.getcwd()
mds = sorted([os.path.relpath(p, root) for p in glob.glob('*.md')])
refs = {md: 0 for md in mds}

for md in mds:
    txt = open(md, 'r', encoding='utf-8', errors='ignore').read()
    for target in mds:
        if target == md:
            continue
        if target in txt:
            refs[target] += 1

# Keep these as essential docs
keep = {'00_RESUME_FINAL.md', 'CHECKLIST_COMPLETE.md', 'INDEX.md', 'START_HERE.md', 'README.md', 'HOME_PAGE.md', 'DEPLOYMENT_CHECKLIST.md'}

print("File Reference Count:")
for md in mds:
    print(f"{md}: {refs[md]} refs")

print("\n--- Candidates for deletion (0 refs, not essential) ---")
candidates = []
for md, c in refs.items():
    if c == 0 and md not in keep:
        candidates.append(md)
        print(md)

print(f"\nTotal candidates: {len(candidates)}")
