"""
Script to add to_field='uuid_xxx', blank=True, null=True to OneToOneField/ForeignKey
definitions in core/models.py when db_column='uuid_xxx' and to_field is missing.
Creates a timestamped backup before editing.
Usage: python scripts\fix_uuid_relations.py
"""
import re
import shutil
import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODELS = ROOT / 'core' / 'models.py'

if not MODELS.exists():
    print(f"models.py not found at {MODELS}")
    raise SystemExit(1)

ts = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
backup = MODELS.with_suffix(f'.py.bak.{ts}')
shutil.copy2(MODELS, backup)
print(f'Backup created: {backup}')

text = MODELS.read_text(encoding='utf-8')

# Match OneToOneField(...) or ForeignKey(...), non-greedy capture of args
pattern = re.compile(r"\b(?P<ftype>OneToOneField|ForeignKey)\s*\((?P<args>.*?)\)", re.S)

changed = []

def repl(m):
    ftype = m.group('ftype')
    args = m.group('args')
    # If to_field already present, skip
    if re.search(r"\bto_field\s*=", args):
        return m.group(0)
    # Find db_column='uuid_...'
    dbm = re.search(r"db_column\s*=\s*['\"](?P<col>uuid_[^'\"]+)['\"]", args)
    if not dbm:
        return m.group(0)
    col = dbm.group('col')
    # Prepare insertion text
    insertion = f", to_field='{col}', blank=True, null=True"
    new_args = args.rstrip()
    # If args ends with a trailing comma + spaces, keep as is and just append
    if new_args.endswith(','):
        new_args = new_args + " to_field='{col}', blank=True, null=True".format(col=col)
    else:
        new_args = new_args + insertion
    changed.append((ftype, col))
    return f"{ftype}({new_args})"

new_text = pattern.sub(repl, text)

if new_text == text:
    print('No changes necessary.')
else:
    MODELS.write_text(new_text, encoding='utf-8')
    print(f'Modified {MODELS}; fields updated:')
    for ftype, col in changed:
        print(f' - {ftype} with db_column={col}')
    print('Please review changes and run your tests. A backup was saved.')
