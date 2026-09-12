"""Synthetic fixtures: no dependency definitions or assets are distributed."""

import importlib.util
import os
from pathlib import Path
import stat
import struct
import subprocess
import sys
import tempfile
import unittest
import warnings
import zipfile


MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "build_addon.py"
SPEC = importlib.util.spec_from_file_location("build_addon", MODULE_PATH)
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


def fixture_unit(kind, identifier, fields):
    return f"SiiNunit\r\n{{\r\n{kind} : {identifier}\r\n{{\r\n{fields}\r\n}}\r\n}}\r\n"


def headlight_text(repaired=False):
    values = {key: value[1 if repaired else 0] for key, value in builder.HEADLIGHT_VALUES.items()}
    fields = "\r\n".join(f"\t{key}: {value}  # synthetic comment" for key, value in values.items())
    fields += "\r\n\tlight_type: high_beam"
    fields += '\r\n\tmodel: "' + builder.EXPECTED_MODEL + '"\r\n'
    fields += "\r\n".join('@include "' + name + '"' for name in builder.EXPECTED_INCLUDES)
    fields += "\r\n\tkeep_me: 123\r\n\t# default_scale: 99"
    return fixture_unit("flare_vehicle", "flare.vehicle.high_beam", fields)


def headlight_files(repaired=False):
    files = {builder.HEADLIGHT_PATH: headlight_text(repaired)}
    parent = str(Path(builder.HEADLIGHT_PATH).parent).replace("\\", "/")
    files.update({parent + "/" + name: "# synthetic include\n" for name in builder.EXPECTED_INCLUDES})
    files[builder.EXPECTED_MODEL[1:]] = "synthetic model placeholder"
    return files


def quper_files():
    economy = "maximum_driving_time: 1440 # keep comment\nsleeping_time: 480\nuntouched: 42"
    used = "\n".join(f"truck_{part}_{wear}_{bound}: " +
                     ("0.4" if wear == "wear_unfixable" and bound == "max" else "0.0") for part in (
        "chassis", "wheels", "engine", "transmission", "cabin")
        for wear in ("wear", "wear_unfixable") for bound in ("min", "max"))
    used += "\ntruck_wear_unfixable_limit_values[]: 0.15\ntruck_count_min: 12"
    return {builder.ECONOMY_PATH: fixture_unit("economy_data", "economy.data.storage", economy),
            builder.USED_PATH: fixture_unit("used_vehicle_assortment_config", ".config", used)}


class BuilderTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "source.scs"
        self.output = self.root / "output.scs"

    def zip_source(self, files):
        with zipfile.ZipFile(self.source, "w") as archive:
            for name, content in files.items():
                info = zipfile.ZipInfo(name)
                info.filename = name  # Keep deliberately unsafe fixture names on Windows too.
                archive.writestr(info, content.encode("utf-8") if isinstance(content, str) else content)
        return self.source

    def build(self, command="headlight", **kwargs):
        return builder.build(command, self.source, self.output, **kwargs)

    def output_files(self):
        with zipfile.ZipFile(self.output) as archive:
            return {name: archive.read(name).decode("utf-8") for name in archive.namelist()}

    def assert_rejected(self, files, message=None, command="headlight", **kwargs):
        self.zip_source(files)
        with self.assertRaisesRegex(builder.BuildError, message or ".*"):
            self.build(command, **kwargs)
        self.assertFalse(self.output.exists())

    def test_headlight_only_three_numeric_tokens_change(self):
        files = headlight_files()
        self.zip_source(files)
        original_archive = self.source.read_bytes()
        self.build()
        actual = self.output_files()
        expected = files[builder.HEADLIGHT_PATH]
        for key, (old, new) in builder.HEADLIGHT_VALUES.items():
            expected = expected.replace(f"{key}: {old}", f"{key}: {new}")
        self.assertEqual(actual[builder.HEADLIGHT_PATH], expected)
        self.assertEqual(set(actual), {"manifest.sii", "description.txt", builder.HEADLIGHT_PATH})
        self.assertEqual(self.source.read_bytes(), original_archive)
        self.assertIn("no AI behavior logic", actual["description.txt"])

    def test_regular_deterministic_stored_zip(self):
        self.zip_source(headlight_files())
        self.build()
        second = self.root / "second.scs"
        builder.build("headlight", self.source, second)
        self.assertEqual(self.output.read_bytes(), second.read_bytes())
        with zipfile.ZipFile(self.output) as archive:
            self.assertIsNone(archive.testzip())
            for info in archive.infolist():
                self.assertEqual(info.create_system, 0)
                self.assertEqual(info.external_attr, 0x20)
                self.assertEqual(info.compress_type, zipfile.ZIP_STORED)
                self.assertEqual(info.date_time, (2026, 9, 12, 0, 0, 0))
                self.assertEqual(info.flag_bits & 8, 0)
                self.assertFalse(archive.read(info).startswith(b"\xef\xbb\xbf"))
                raw = self.output.read_bytes()
                local_flags = struct.unpack_from("<H", raw, info.header_offset + 6)[0]
                self.assertEqual(local_flags & 8, 0)
        self.assertIn('package_version: "1.0.1"', self.output_files()["manifest.sii"])
        self.assertIn("mod_package : .package_name", self.output_files()["manifest.sii"])

    def test_fleetguard_preserves_other_fields_and_comments(self):
        files = quper_files()
        self.zip_source(files)
        self.build("quper")
        actual = self.output_files()
        inserted = ("\t\tdriver_undrivable_truck_integrity_wear: 0.8\r\n"
                    "\t\tdriver_undrivable_trailer_integrity_wear: 0.8\r\n")
        expected_economy = files[builder.ECONOMY_PATH].replace("}\r\n}\r\n", inserted + "}\r\n}\r\n")
        self.assertEqual(actual[builder.ECONOMY_PATH], expected_economy)
        self.assertEqual(actual[builder.USED_PATH], files[builder.USED_PATH].replace(": 0.4", ": 0.0"))

    def test_existing_thresholds_replaced_and_duplicate_rejected(self):
        files = quper_files()
        files[builder.ECONOMY_PATH] = files[builder.ECONOMY_PATH].replace(
            "untouched: 42", "untouched: 42\ndriver_undrivable_truck_integrity_wear: 0.5")
        self.zip_source(files)
        self.build("quper")
        actual = self.output_files()[builder.ECONOMY_PATH]
        self.assertEqual(actual.count("driver_undrivable_truck_integrity_wear:"), 1)
        self.assertIn("driver_undrivable_truck_integrity_wear: 0.8", actual)
        self.output.unlink()
        files[builder.ECONOMY_PATH] = files[builder.ECONOMY_PATH].replace(
            "untouched: 42", "driver_undrivable_truck_integrity_wear: 0.4")
        self.assert_rejected(files, "one numeric value", command="quper")

    def test_unknown_used_wear_baseline_rejected(self):
        files = quper_files()
        files[builder.USED_PATH] = files[builder.USED_PATH].replace(
            "truck_cabin_wear_min: 0.0", "truck_cabin_wear_min: 0.1")
        self.assert_rejected(files, "baseline", command="quper")

    def test_100percent_does_not_require_or_bundle_used_override(self):
        files = quper_files()
        del files[builder.USED_PATH]
        self.zip_source(files)
        self.build("quper", preset="100percent")
        actual = self.output_files()
        self.assertNotIn(builder.USED_PATH, actual)
        self.assertEqual(actual[builder.ECONOMY_PATH].count(": 0.9999"), 2)

    def test_missing_dependency_asset_rejected(self):
        files = headlight_files()
        del files[builder.EXPECTED_MODEL[1:]]
        self.assert_rejected(files, "Missing referenced")

    def test_missing_and_duplicate_parameter_rejected(self):
        for change in (lambda text: text.replace("default_scale:", "other_scale:"),
                       lambda text: text.replace("keep_me: 123", "default_scale: 0.10"),
                       lambda text: text.replace("default_scale: 0.10", "default_scale: nan")):
            with self.subTest(change=change):
                files = headlight_files()
                files[builder.HEADLIGHT_PATH] = change(files[builder.HEADLIGHT_PATH])
                self.assert_rejected(files, "one numeric value")

    def test_mismatched_baseline_and_unit_rejected(self):
        for old, new, message in (("scale_factor: 48", "scale_factor: 49", "baseline"),
                                  ("flare.vehicle.high_beam", "flare.vehicle.other", "unit")):
            files = headlight_files()
            files[builder.HEADLIGHT_PATH] = files[builder.HEADLIGHT_PATH].replace(old, new)
            self.assert_rejected(files, message)

    def test_light_type_must_be_present_correct_and_unique(self):
        for replacement in ("", "light_type: low_beam", "light_type: high_beam\r\nlight_type: high_beam"):
            with self.subTest(replacement=replacement):
                files = headlight_files()
                files[builder.HEADLIGHT_PATH] = files[builder.HEADLIGHT_PATH].replace(
                    "light_type: high_beam", replacement)
                self.assert_rejected(files, "light_type: high_beam")

    def test_incomplete_or_extra_unit_rejected(self):
        for transform in (lambda text: text.rstrip()[:-1],
                          lambda text: text.replace("keep_me: 123", "unexpected : .unit { value: 1 }")):
            files = headlight_files()
            files[builder.HEADLIGHT_PATH] = transform(files[builder.HEADLIGHT_PATH])
            self.assert_rejected(files, "complete definition unit")

    def test_wrong_or_unsafe_reference_rejected(self):
        for replacement in ("../outside.sui", "different.sui"):
            files = headlight_files()
            files[builder.HEADLIGHT_PATH] = files[builder.HEADLIGHT_PATH].replace(
                builder.EXPECTED_INCLUDES[0], replacement)
            self.assert_rejected(files, "references")

    def test_comments_do_not_supply_missing_fields(self):
        files = headlight_files()
        files[builder.HEADLIGHT_PATH] = files[builder.HEADLIGHT_PATH].replace(
            "\tdefault_scale:", "\t// default_scale:")
        self.assert_rejected(files, "one numeric value")

    def test_missing_quper_field_rejected(self):
        files = quper_files()
        files[builder.USED_PATH] = files[builder.USED_PATH].replace(
            "truck_cabin_wear_unfixable_max:", "other:")
        self.assert_rejected(files, "one numeric value", command="quper")

    def test_output_never_overwritten(self):
        self.zip_source(headlight_files())
        self.output.write_bytes(b"existing personal content")
        with self.assertRaisesRegex(builder.BuildError, "overwrite"):
            self.build()
        self.assertEqual(self.output.read_bytes(), b"existing personal content")

    def test_source_archive_cannot_be_output(self):
        self.zip_source(headlight_files())
        original = self.source.read_bytes()
        with self.assertRaises(builder.BuildError):
            builder.build("headlight", self.source, self.source)
        self.assertEqual(self.source.read_bytes(), original)

    def test_directory_source_works_and_cannot_receive_output(self):
        directory = self.root / "source_dir"
        directory.mkdir()
        for name, content in headlight_files().items():
            target = directory / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content.encode("utf-8"))
        builder.build("headlight", directory, self.output)
        with self.assertRaisesRegex(builder.BuildError, "inside the source"):
            builder.build("headlight", directory, directory / "addon.scs")
        self.assertFalse((directory / "addon.scs").exists())

    def test_unsafe_archive_paths_rejected_even_when_unused(self):
        for name in ("../escape.sii", "/absolute.sii", "C:/absolute.sii", "a\\b.sii",
                     "a/../b.sii", "a//b.sii", "a./b.sii", "CON.sii"):
            with self.subTest(name=name):
                files = headlight_files()
                files[name] = "unused"
                self.assert_rejected(files, "Unsafe")

    def test_case_duplicate_paths_rejected(self):
        files = headlight_files()
        files[builder.HEADLIGHT_PATH.upper()] = files[builder.HEADLIGHT_PATH]
        self.assert_rejected(files, "case-ambiguous")

    def test_exact_duplicate_paths_rejected(self):
        self.zip_source(headlight_files())
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with zipfile.ZipFile(self.source, "a") as archive:
                archive.writestr(builder.HEADLIGHT_PATH, headlight_text())
        with self.assertRaisesRegex(builder.BuildError, "Duplicate"):
            self.build()

    def test_archive_file_directory_collision_rejected(self):
        files = headlight_files()
        files["unit"] = "collision"
        self.assert_rejected(files, "collision")

    def test_oversized_unrelated_definition_rejected(self):
        files = headlight_files()
        files["def/unused.sii"] = b"x" * (builder.MAX_DEFINITION_BYTES + 1)
        self.assert_rejected(files, "oversized")

    def test_encrypted_entry_rejected_before_read(self):
        self.zip_source(headlight_files())
        data = bytearray(self.source.read_bytes())
        central = data.index(b"PK\x01\x02")
        flags = struct.unpack_from("<H", data, central + 8)[0]
        struct.pack_into("<H", data, central + 8, flags | 1)
        self.source.write_bytes(data)
        with self.assertRaisesRegex(builder.BuildError, "Encrypted"):
            self.build()

    def test_zip_symlink_rejected(self):
        self.zip_source(headlight_files())
        with zipfile.ZipFile(self.source, "a") as archive:
            info = zipfile.ZipInfo("unused_link")
            info.create_system = 3
            info.external_attr = (stat.S_IFLNK | 0o777) << 16
            archive.writestr(info, "../outside")
        with self.assertRaisesRegex(builder.BuildError, "links"):
            self.build()

    def test_single_readable_definition_supported(self):
        self.source = self.root / "vehicle_high_beam.sii"
        original = b"\xef\xbb\xbf" + headlight_text().encode("utf-8")
        self.source.write_bytes(original)
        self.build()
        self.assertEqual(self.source.read_bytes(), original)
        self.assertIn("default_scale: 0.28", self.output_files()[builder.HEADLIGHT_PATH])

    def test_repair_existing_preserves_body_and_omits_source_metadata(self):
        content = headlight_text(repaired=True).replace("0.28", "0.280")
        self.zip_source({builder.HEADLIGHT_PATH: content, "manifest.sii": "personal metadata",
                         "private.txt": "personal information"})
        self.build(repair_existing=True)
        actual = self.output_files()
        self.assertEqual(actual[builder.HEADLIGHT_PATH], content)
        self.assertNotIn("personal metadata", actual["manifest.sii"])
        self.assertNotIn("private.txt", actual)

    def test_repair_mode_rejects_unpatched_baseline(self):
        self.assert_rejected(headlight_files(), "baseline", repair_existing=True)

    def test_hashfs_is_reported_without_output(self):
        self.source.write_bytes(b"SCS#synthetic unsupported format")
        with self.assertRaisesRegex(builder.BuildError, "HashFS/protected"):
            self.build()
        self.assertFalse(self.output.exists())

    def test_invalid_encoding_rejected(self):
        files = headlight_files()
        files[builder.HEADLIGHT_PATH] = b"\xff\xfe\x00"
        self.assert_rejected(files, "UTF-8")

    def test_cli_requires_explicit_source_and_output(self):
        result = subprocess.run([sys.executable, str(MODULE_PATH), "headlight"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("--source", result.stderr)
        self.assertIn("--output", result.stderr)

    @unittest.skipUnless(os.name == "nt", "Windows sharing semantics")
    def test_source_handle_does_not_deny_writes_or_rename(self):
        self.source.write_bytes(b"synthetic source")
        renamed = self.root / "renamed.scs"
        with builder.shared_open(self.source) as stream:
            with self.source.open("r+b") as writer:
                writer.write(b"updated")
            self.source.rename(renamed)
            self.assertTrue(stream.read().startswith(b"updated"))
        self.assertTrue(renamed.exists())


if __name__ == "__main__":
    unittest.main()
