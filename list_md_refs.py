import os
from pathlib import Path
from collections import defaultdict
root = Path('.')
md_files = sorted(p.relative_to(root) for p in root.rglob('*.md') if 'node_modules' not in p.parts)
for rel in md_files:
    name = rel.name
    cmd = f"rg --fixed-strings --files-with-matches {name}"
    # use os.popen with shell True
    stream = os.popen(f"rg --fixed-strings --files-with-matches {name}").read().strip().splitlines()
    refs = [r for r in stream if r and Path(r) != rel]
    print(f"{rel}\t{len(refs)}")
