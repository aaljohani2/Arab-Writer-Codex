#!/usr/bin/env python3
from pathlib import Path
import json,re,sys
ROOT=Path(__file__).resolve().parents[1]
errors=[]
try: m=json.loads((ROOT/'.codex-plugin/plugin.json').read_text(encoding='utf-8'))
except Exception as e: m={}; errors.append(f'invalid plugin.json: {e}')
version=(ROOT/'VERSION').read_text().strip() if (ROOT/'VERSION').exists() else ''
for k in ('name','version','description','skills'):
    if not m.get(k): errors.append(f'missing plugin field {k}')
if m.get('version')!=version: errors.append('plugin version must match VERSION')
if m.get('name')!='arab-writer-codex': errors.append('unexpected plugin name')
skills=m.get('skills','')
if skills.startswith('./'):
    if not (ROOT/skills[2:]).exists(): errors.append(f'plugin skills path not found: {skills}')
else: errors.append('plugin skills path must be relative and start ./')

# Keep installation docs aligned with the repository configured in the manifest.
repo_url=m.get('repository','').rstrip('/')
expected_install=f'{repo_url}/tree/main/.agents/skills/arab-writer'
for rel in ('README.md','docs/INSTALL.md'):
    doc_path=ROOT/rel
    if not doc_path.is_file():
        errors.append(f'missing installation documentation: {rel}')
        continue
    if expected_install not in doc_path.read_text(encoding='utf-8'):
        errors.append(f'{rel} must include the canonical skill installation URL')
if repo_url.startswith('https://github.com/'):
    repo_slug=re.escape(repo_url.rsplit('/',1)[-1])
    same_project_links=re.compile(r'https://github[.]com/[^/\s)]+/'+repo_slug+r'(?=/|[\s)\]\x60]|$)')
    for doc_path in [ROOT/'README.md',*sorted((ROOT/'docs').glob('*.md'))]:
        if not doc_path.is_file(): continue
        for found in same_project_links.findall(doc_path.read_text(encoding='utf-8')):
            if found!=repo_url:
                errors.append(f'{doc_path.relative_to(ROOT)}: outdated repository link {found}')
else:
    errors.append('plugin repository must be a github.com HTTPS URL')
if errors:
    print('FAILED'); [print('- '+e) for e in errors]; sys.exit(1)
print(f'OK: plugin manifest v{version} is valid.')
