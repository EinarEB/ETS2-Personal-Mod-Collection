"""Package only the reviewed public files; no game installation is accessed."""
import argparse
import hashlib
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ASSETS = {'regional-gps': 'Regional_GPS_Minimal_1.6.1.scs',
          'vr-rain': 'VR_Rain_Streaks_Subtle_0.10.1.scs'}

def archive(path, files):
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_STORED, allowZip64=False) as z:
        for name, content in sorted(files.items()):
            assert re.fullmatch(r'[A-Za-z0-9_./-]+', name) and '..' not in name.split('/')
            info = zipfile.ZipInfo(name, (2026, 9, 12, 0, 0, 0))
            info.create_system = 0
            info.external_attr = 0x20
            z.writestr(info, content)
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        assert set(z.namelist()) == set(files)
        assert not z.comment
        for info in z.infolist():
            assert info.create_system == 0 and info.external_attr == 0x20
            assert info.flag_bits == 0 and not info.extra and not info.comment
            assert z.read(info) == files[info.filename]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'dist')
    output = parser.parse_args().output.resolve()
    # Do not let the build outputs overwrite source trees.
    if output == ROOT or any(p == output or p in output.parents for p in (ROOT/'mods', ROOT/'tools', ROOT/'docs', ROOT/'tests')):
        raise ValueError('Choose a separate output directory')
    output.mkdir(parents=True, exist_ok=True)
    names = []
    for slug, name in ASSETS.items():
        folder = ROOT / 'mods' / slug
        files = {p.relative_to(folder).as_posix(): p.read_bytes() for p in folder.rglob('*') if p.is_file()}
        assert files['manifest.sii'].decode().count('mod_package : .package_name') == 1
        archive(output / name, files)
        names.append(name)
    builder_files = {p: (ROOT / p).read_bytes() for p in (
        'tools/build_addon.py', 'docs/HEADLIGHT-CONSEQUENCES.md', 'docs/QUPER-OVERRIDES.md',
        'docs/INSTALLATION.md', 'THIRD-PARTY-NOTICES.md')}
    builder_files['README.md'] = (
        '# ETS2 Personal Addon Builders\n\n'
        'Python 3.10+; no extra packages. Read docs/QUPER-OVERRIDES.md or '
        'docs/HEADLIGHT-CONSEQUENCES.md before building. Upstream mods are not bundled.\n\n'
        'Run `python tools/build_addon.py --help` from this folder. '
        'Choose a fresh output filename, then install the result manually.\n'
    ).encode()
    name = 'ETS2_Personal_Addon_Builders_v1.0.1.zip'
    archive(output / name, builder_files)
    names.append(name)
    sums = ''.join(hashlib.sha256((output / name).read_bytes()).hexdigest() + '  ' + name + '\n' for name in sorted(names))
    (output / 'SHA256SUMS.txt').write_text(sums, encoding='ascii')
    print(sums, end='')

if __name__ == '__main__':
    main()
