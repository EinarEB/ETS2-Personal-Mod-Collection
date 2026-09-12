#!/usr/bin/env python3
"""Build personal ETS2 overrides from the user's own readable dependency files.

Python 3.10+; standard library only. No game installation or extraction is done.
"""

from __future__ import annotations

import argparse
from contextlib import ExitStack
from decimal import Decimal
import io
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import zipfile


VERSION = "1.0.1"
MAX_DEFINITION_BYTES = 1024 * 1024
MAX_ENTRIES = 100000
HEADLIGHT_PATH = "unit/hookup/vehicle/flare/vehicle_high_beam.sii"
ECONOMY_PATH = "def/economy_data.sii"
USED_PATH = "def/used_vehicle_config.sii"
EXPECTED_INCLUDES = (
    "vehicle_bulb_type_incandescent.sui",
    "vehicle_lights_scaling_distance_beam.sui",
)
EXPECTED_MODEL = "/model/flare/uniform_white_amplified.pmd"
HEADLIGHT_VALUES = {
    "flare_inner_angle": ("12", "34"),
    "default_scale": ("0.10", "0.28"),
    "scale_factor": ("48", "72"),
}
NUMBER = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"


class BuildError(ValueError):
    """The supplied input cannot safely produce the requested override."""


def shared_open(path: Path):
    """Open read-only, allowing other Windows processes to read/write/delete."""
    if os.name != "nt":
        return path.open("rb")
    import ctypes
    from ctypes import wintypes
    import msvcrt

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    create = kernel.CreateFileW
    create.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                       ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD,
                       wintypes.HANDLE]
    create.restype = wintypes.HANDLE
    handle = create(str(path), 0x80000000, 7, None, 3, 0x80, None)
    if handle == wintypes.HANDLE(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        fd = msvcrt.open_osfhandle(handle, os.O_RDONLY | os.O_BINARY)
    except BaseException:
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel.CloseHandle(handle)
        raise
    return os.fdopen(fd, "rb")


def check_no_links(path: Path) -> None:
    for part in (path, *path.parents):
        try:
            metadata = part.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(metadata.st_mode) or (
                getattr(metadata, "st_file_attributes", 0) & 0x400):
            raise BuildError("Symbolic links and Windows reparse points are not supported.")


def safe_member(name: str) -> str:
    """Validate archive names without ever extracting them."""
    if not name or name.startswith("/") or "\\" in name or ":" in name:
        raise BuildError("Unsafe archive/reference path.")
    parts = name.split("/")
    reserved = {"con", "prn", "aux", "nul", *(
        f"{prefix}{number}" for prefix in ("com", "lpt") for number in range(1, 10))}
    for part in parts:
        if (not part or part in (".", "..") or part.endswith((" ", "."))
                or any(ord(char) < 32 for char in part)
                or any(char in part for char in '<>"|?*')
                or part.split(".")[0].casefold() in reserved):
            raise BuildError("Unsafe archive/reference path.")
    return name


class Source:
    """Bounded, read-only view of a ZIP, directory, or single headlight file."""

    def __init__(self, path: Path, *, allow_single: bool = False):
        self.path = Path(os.path.abspath(path))
        self.stack = ExitStack()
        self.entries = {}
        self.names = set()
        self.archive = None
        self.single = False
        check_no_links(self.path)
        try:
            if self.path.is_dir():
                self._directory(self.path)
            elif allow_single and self.path.name == "vehicle_high_beam.sii":
                self.single = True
                self._add(HEADLIGHT_PATH, self.path, self.path.stat().st_size)
            else:
                stream = self.stack.enter_context(shared_open(self.path))
                signature = stream.read(4)
                stream.seek(0)
                if signature == b"SCS#":
                    raise BuildError("HashFS/protected SCS input is unsupported. Supply a legitimately "
                                     "obtained readable definition, ZIP, or extracted directory; "
                                     "this tool does not unpack or unlock HashFS.")
                try:
                    self.archive = self.stack.enter_context(zipfile.ZipFile(stream))
                except zipfile.BadZipFile as exc:
                    raise BuildError("Source must be a readable ZIP .scs or an extracted directory.") from exc
                for info in self.archive.infolist():
                    if info.flag_bits & 1:
                        raise BuildError("Encrypted ZIP entries are unsupported.")
                    if "\x00" in info.orig_filename:
                        raise BuildError("Unsafe archive path.")
                    mode = info.external_attr >> 16
                    filetype = stat.S_IFMT(mode)
                    if info.create_system == 3 and filetype not in (0, stat.S_IFREG, stat.S_IFDIR):
                        raise BuildError("ZIP links and special files are unsupported.")
                    self._add(info.orig_filename.removesuffix("/"), info, info.file_size,
                              directory=info.is_dir())
                for name in self.entries:
                    for parent in PurePosixPath(name).parents:
                        if str(parent).casefold() in self.entries:
                            raise BuildError("Archive has a file/directory path collision.")
        except BaseException:
            self.stack.close()
            raise

    def _add(self, name, entry, size, *, directory=False):
        name = safe_member(name)
        key = name.casefold()
        if key in self.names:
            raise BuildError("Duplicate or case-ambiguous source paths.")
        self.names.add(key)
        if len(self.names) > MAX_ENTRIES:
            raise BuildError("Source has too many entries.")
        if not directory:
            if name.lower().endswith((".sii", ".sui")) and size > MAX_DEFINITION_BYTES:
                raise BuildError("Source contains an oversized definition.")
            self.entries[key] = entry

    def _directory(self, current):
        with os.scandir(current) as scan:
            for entry in scan:
                metadata = entry.stat(follow_symlinks=False)
                if entry.is_symlink() or getattr(metadata, "st_file_attributes", 0) & 0x400:
                    raise BuildError("Source directories may not contain links or reparse points.")
                path = Path(entry.path)
                name = path.relative_to(self.path).as_posix()
                is_dir = stat.S_ISDIR(metadata.st_mode)
                if not is_dir and not stat.S_ISREG(metadata.st_mode):
                    raise BuildError("Source contains a special file.")
                self._add(name, path, metadata.st_size, directory=is_dir)
                if is_dir:
                    self._directory(path)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return self.stack.__exit__(*args)

    def has(self, name):
        return safe_member(name).casefold() in self.entries

    def read(self, name):
        entry = self.entries.get(safe_member(name).casefold())
        if entry is None:
            raise BuildError(f"Missing required source file: {name}")
        if self.archive is not None:
            stream = self.archive.open(entry)
        else:
            check_no_links(entry)
            stream = shared_open(entry)
        with stream:
            data = stream.read(MAX_DEFINITION_BYTES + 1)
        if len(data) > MAX_DEFINITION_BYTES:
            raise BuildError("Required definition exceeds the size limit.")
        try:
            text = data.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise BuildError("Definitions must be UTF-8 text.") from exc
        if "\x00" in text:
            raise BuildError("Definition contains NUL bytes.")
        return text


def uncomment(text):
    """Mask comments while retaining character offsets and quoted references."""
    pattern = r'"(?:\\.|[^"\\])*"|/\*[\s\S]*?\*/|//[^\r\n]*|\#[^\r\n]*'
    return re.sub(pattern, lambda match: match[0] if match[0].startswith('"') else
                  re.sub(r"[^\r\n]", " ", match[0]), text)


def require_unit(text, kind, identifier):
    code = re.sub(r'"(?:\\.|[^"\\])*"', lambda match: " " * len(match[0]), uncomment(text))
    if not re.match(r"\s*SiiNunit\s*\{", code):
        raise BuildError("Definition is not a SiiNunit file.")
    headers = re.findall(r"(?m)^\s*" + re.escape(kind) + r"\s*:\s*([^\s{]+)\s*\{", code)
    if headers != [identifier]:
        raise BuildError(f"Expected exactly one {kind}: {identifier} unit.")
    shape = (r"\s*SiiNunit\s*\{\s*" + re.escape(kind) + r"\s*:\s*"
             + re.escape(identifier) + r"\s*\{[^{}]*\}\s*\}\s*")
    if not re.fullmatch(shape, code):
        raise BuildError("Expected one complete definition unit with balanced braces.")


def insert_missing_values(text, kind, identifier, values):
    """Add optional scalar fields to the verified unit, never outside its braces."""
    require_unit(text, kind, identifier)
    code = uncomment(text)
    missing = {}
    present = {}
    for key, value in values.items():
        occurrences = re.findall(r"(?m)^[ \t]*" + re.escape(key) + r"[ \t]*:", code)
        if occurrences:
            present[key] = value
        else:
            missing[key] = value
    text = replace_values(text, present)
    if not missing:
        return text
    code = re.sub(r'"(?:\\.|[^"\\])*"', lambda match: " " * len(match[0]), uncomment(text))
    header = re.search(re.escape(kind) + r"\s*:\s*" + re.escape(identifier) + r"\s*\{", code)
    start = header.end() - 1
    depth = 0
    end = None
    for offset in range(start, len(code)):
        if code[offset] == "{":
            depth += 1
        elif code[offset] == "}":
            depth -= 1
            if depth == 0:
                end = offset
                break
    if end is None:
        raise BuildError("Unbalanced economy unit braces.")
    line_start = text.rfind("\n", 0, end) + 1
    insert_at = line_start if not text[line_start:end].strip() else end
    newline = "\r\n" if "\r\n" in text else "\n"
    fields = "".join(f"\t\t{key}: {value}{newline}" for key, value in missing.items())
    if insert_at and text[insert_at - 1] not in "\r\n":
        fields = newline + fields
    return text[:insert_at] + fields + text[insert_at:]


def replace_values(text, replacements, expected=None):
    """Replace only unique numeric tokens; comments/other bytes stay intact."""
    code = uncomment(text)
    changes = []
    for key, replacement in replacements.items():
        definitions = list(re.finditer(r"(?m)^[ \t]*" + re.escape(key) + r"[ \t]*:", code))
        matches = list(re.finditer(r"(?m)^[ \t]*" + re.escape(key)
                                  + r"[ \t]*:[ \t]*(" + NUMBER + r")[ \t\r]*$", code))
        if len(definitions) != 1 or len(matches) != 1:
            raise BuildError(f"Expected one numeric value for {key}; missing or ambiguous input.")
        match = matches[0]
        if expected is not None and Decimal(match[1]) != Decimal(expected[key]):
            raise BuildError(f"Unexpected baseline for {key}; the source version does not match.")
        changes.append((match.start(1), match.end(1), replacement))
    for start, end, replacement in sorted(changes, reverse=True):
        text = text[:start] + replacement + text[end:]
    return text


def reference_path(current, reference):
    if reference.startswith("/"):
        return safe_member(reference[1:])
    safe_member(reference)
    return safe_member((PurePosixPath(current).parent / reference).as_posix())


def validate_headlight_references(source, text, *, require_files):
    code = uncomment(text)
    includes = re.findall(r'(?m)^[ \t]*@include[ \t]+"([^"\r\n]+)"[ \t\r]*$', code)
    models = re.findall(r'(?m)^[ \t]*model[ \t]*:[ \t]*"([^"\r\n]+)"[ \t\r]*$', code)
    if sorted(includes) != sorted(EXPECTED_INCLUDES) or models != [EXPECTED_MODEL]:
        raise BuildError("Unexpected or missing Dynamic Flares include/model references.")
    references = [reference_path(HEADLIGHT_PATH, name) for name in (*includes, *models)]
    if require_files:
        for name in references:
            if not source.has(name):
                raise BuildError(f"Missing referenced dependency file: {name}")


def metadata(title, description):
    manifest = ("SiiNunit\n{\nmod_package : .package_name\n{\n"
                f'    package_version: "{VERSION}"\n'
                f'    display_name: "{title}"\n'
                '    author: "ETS2 Personal Mod Collection"\n'
                '    description_file: "description.txt"\n'
                '    compatible_versions[]: "1.60.*"\n'
                '}\n}\n')
    return {"manifest.sii": manifest, "description.txt": description + "\n"}


def headlight(source, *, repair_existing=False):
    text = source.read(HEADLIGHT_PATH)
    require_unit(text, "flare_vehicle", "flare.vehicle.high_beam")
    light_types = re.findall(r"(?m)^[ \t]*light_type[ \t]*:[ \t]*([^\r\n]*)\r?$", uncomment(text))
    if len(light_types) != 1 or light_types[0].strip() != "high_beam":
        raise BuildError("Expected exactly one light_type: high_beam field.")
    validate_headlight_references(source, text,
                                 require_files=not source.single and not repair_existing)
    replacements = {key: value[1] for key, value in HEADLIGHT_VALUES.items()}
    expected = {key: value[1 if repair_existing else 0] for key, value in HEADLIGHT_VALUES.items()}
    patched = replace_values(text, replacements, expected)
    if repair_existing:
        patched = text  # Validate but preserve all numeric spellings in existing repairs.
    result = metadata("Headlight Flash Visibility Addon",
                      "Enlarges the existing high-beam flash flare visual. Requires Dynamic Flares "
                      "v1.2 enabled below this addon. This contains no AI behavior logic and does "
                      "not make drivers flash or react to headlights. Driving/VR quality is unverified.")
    result[HEADLIGHT_PATH] = patched
    return result


def quper(source, *, preset="fleetguard"):
    if preset not in ("fleetguard", "100percent"):
        raise BuildError("Unknown Quper preset.")
    economy = source.read(ECONOMY_PATH)
    require_unit(economy, "economy_data", "economy.data.storage")
    threshold = "0.8" if preset == "fleetguard" else "0.9999"
    times = {"maximum_driving_time": "1440", "sleeping_time": "480"}
    thresholds = {"driver_undrivable_truck_integrity_wear": threshold,
                  "driver_undrivable_trailer_integrity_wear": threshold}
    result = metadata(f"Quper Overrides - {preset}",
                      "Requires the matching Quper source mod enabled below this addon. "
                      "Sets driving time to 1440 minutes and sleep to 480 minutes. "
                      + ("Sets hired-driver integrity-wear thresholds to 0.8 and used-truck "
                         "component wear ranges to zero. Existing trucks are not repaired."
                         if preset == "fleetguard" else
                         "Sets hired-driver integrity-wear thresholds to 0.9999; this is just "
                         "below 100 percent, not exactly 100 percent. No used-truck override."))
    economy = replace_values(economy, times, times)
    result[ECONOMY_PATH] = insert_missing_values(economy, "economy_data", "economy.data.storage", thresholds)
    if preset == "fleetguard":
        used = source.read(USED_PATH)
        require_unit(used, "used_vehicle_assortment_config", ".config")
        expected = {f"truck_{component}_{wear}_{bound}":
                    ("0.4" if wear == "wear_unfixable" and bound == "max" else "0.0")
                    for component in ("chassis", "wheels", "engine", "transmission", "cabin")
                    for wear in ("wear", "wear_unfixable") for bound in ("min", "max")}
        # Validate every relevant range, but preserve existing zero spellings.
        replace_values(used, expected, expected)
        maxima = {key: "0.0" for key, value in expected.items() if value == "0.4"}
        result[USED_PATH] = replace_values(used, maxima)
    return result


def write_new_archive(output, files):
    data = io.BytesIO()
    with zipfile.ZipFile(data, "w", compression=zipfile.ZIP_STORED, allowZip64=False) as archive:
        for name, content in sorted(files.items()):
            info = zipfile.ZipInfo(safe_member(name), (2026, 9, 12, 0, 0, 0))
            info.create_system = 0
            info.external_attr = 0x20
            info.compress_type = zipfile.ZIP_STORED
            archive.writestr(info, content.encode("utf-8"))
    # All validation and ZIP construction finish before a new output is created.
    check_no_links(output)
    with output.open("xb") as stream:
        stream.write(data.getvalue())


def build(command, source_path, output_path, *, preset="fleetguard", repair_existing=False):
    source_path = Path(os.path.abspath(source_path))
    output_path = Path(os.path.abspath(output_path))
    check_no_links(source_path)
    check_no_links(output_path)
    if output_path.suffix.lower() != ".scs":
        raise BuildError("Output must be a new .scs file.")
    if output_path.exists():
        raise BuildError("Refusing to overwrite an existing output.")
    if not output_path.parent.is_dir():
        raise BuildError("Output parent directory must already exist.")
    if source_path.is_dir() and output_path.is_relative_to(source_path):
        raise BuildError("Output may not be inside the source directory.")
    if source_path == output_path:
        raise BuildError("Source and output must be different paths.")
    if command not in ("headlight", "quper"):
        raise BuildError("Unknown command.")
    if repair_existing and command != "headlight":
        raise BuildError("Repair mode is only available for headlight.")
    with Source(source_path, allow_single=command == "headlight") as source:
        files = (headlight(source, repair_existing=repair_existing) if command == "headlight"
                 else quper(source, preset=preset))
    write_new_archive(output_path, files)
    return output_path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("headlight", "quper"):
        sub = commands.add_parser(command)
        sub.add_argument("--source", required=True, type=Path,
                         help="Your readable source ZIP .scs or extracted directory; headlight "
                              "also accepts a single vehicle_high_beam.sii")
        sub.add_argument("--output", required=True, type=Path, help="New .scs file; never overwritten")
        if command == "headlight":
            sub.add_argument("--repair-existing", action="store_true",
                             help="Repackage an existing 34 / 0.28 / 72 addon; dependency assets "
                                  "are supplied separately by Dynamic Flares")
        else:
            sub.add_argument("--preset", choices=("fleetguard", "100percent"), default="fleetguard")
    args = parser.parse_args(argv)
    try:
        output = build(args.command, args.source, args.output,
                       preset=getattr(args, "preset", "fleetguard"),
                       repair_existing=getattr(args, "repair_existing", False))
    except (BuildError, OSError, zipfile.BadZipFile, NotImplementedError, RuntimeError) as exc:
        parser.exit(2, f"Build failed: {exc}\n")
    print(f"Created {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
