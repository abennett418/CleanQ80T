"""Sign CleanQ80T with the owner's locally configured official Samsung profile."""
from pathlib import Path
import json
import subprocess
import uuid
import xml.etree.ElementTree as XML
import zipfile
from font_assets import write_widget_archive

ROOT = Path(__file__).resolve().parents[1]
config_path = ROOT / '.local/signing.json'
if not config_path.is_file():
    raise SystemExit('Configure .local/signing.json with sdk_path, profiles_path and profile. See docs/development.md.')
config = json.loads(config_path.read_text())
cli = Path(config['sdk_path']) / 'tools/ide/bin/tizen'
profiles = Path(config['profiles_path'])
profile_name = config['profile']
if not cli.is_file() or not profiles.is_file() or not profile_name:
    raise SystemExit('Configured SDK or signing profile is missing.')
profile_tree = XML.parse(profiles)
selected = next((p for p in profile_tree.getroot().findall('profile') if p.get('name') == profile_name), None)
if selected is None:
    raise SystemExit('Configured profile is not present in profiles_path.')
for item in selected.findall('profileitem'):
    key = item.get('key')
    if key and not Path(key).is_file():
        raise SystemExit('A configured certificate file is missing.')

# Keep SDK paths and existing certificate profiles intact. Password handling is
# owned by Samsung's certificate store; never copy passwords into command args.
result = subprocess.run([str(cli), 'cli-config', 'default.profiles.path=' + str(profiles)],
                        capture_output=True, timeout=30)
if result.returncode:
    raise SystemExit('SDK signing profile configuration failed.')
dist = ROOT / 'dist'
dist.mkdir(exist_ok=True)
unsigned = dist / 'CleanQ80T-unsigned.wgt'
write_widget_archive(unsigned, include_private=False)
# A fresh output directory prevents an old signed widget from passing validation.
signed_dir = dist / 'signed' / uuid.uuid4().hex
signed_dir.mkdir(parents=True)
command = [str(cli), 'package', '-t', 'wgt', '-s', profile_name,
           '-o', str(signed_dir), '--', str(unsigned)]
try:
    result = subprocess.run(command, stdin=subprocess.DEVNULL, capture_output=True, timeout=60)
except subprocess.TimeoutExpired:
    raise SystemExit('SDK signing timed out; no TV contacted.')
if result.returncode:
    raise SystemExit('SDK signing failed. Check the local profile in Certificate Manager; no TV contacted.')
signed = signed_dir / unsigned.name
if not signed.is_file():
    raise SystemExit('SDK did not create the expected signed widget.')
with zipfile.ZipFile(signed) as package:
    if package.testzip() or not {'author-signature.xml', 'signature1.xml'}.issubset(package.namelist()):
        raise SystemExit('Signed widget is corrupt or missing signatures.')
    if package.read('config.xml') != (ROOT / 'app/config.xml').read_bytes():
        raise SystemExit('Signed manifest differs from the current app.')
target = dist / 'CleanQ80T.wgt'
target.write_bytes(signed.read_bytes())
print('Signed widget created: ' + str(target))
print('No TV contacted; installation and launch are separate steps.')
