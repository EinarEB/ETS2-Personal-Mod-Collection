# ETS2 Personal Mod Collection

Small personal tweaks for **Euro Truck Simulator 2 1.60**: a wider GPS view, gentler rain streaks, economy preferences, and more visible high-beam flares.

**[Download the release](https://github.com/EinarEB/ETS2-Personal-Mod-Collection/releases/tag/v1.0.0)** · [All releases](https://github.com/EinarEB/ETS2-Personal-Mod-Collection/releases) · [Installation](docs/INSTALLATION.md)

The first release is a **preview**. Archives, manifests, privacy, and builder behavior have been checked offline. These repaired packages have not had a new in-game or driving test. See [validation and changes](docs/VALIDATION.md).

| Mod | What it does | Download format |
| --- | --- | --- |
| [Regional GPS Minimal](docs/REGIONAL-GPS.md) | A wide, uncluttered overhead GPS view with readable roads, city labels, and truck marker. | Ready-to-use `.scs` |
| [VR Rain Streaks Subtle](docs/VR-RAIN.md) | Sets the falling-rain streak material to a subdued RGB value of 0.10. | Ready-to-use `.scs` |
| [Quper Overrides / Fleet Guard](docs/QUPER-OVERRIDES.md) | Longer driving/rest intervals, relaxed hired-driver wear thresholds, and an optional used-truck wear preset. | Local builder; requires your copy of Quper's economy mod |
| [AI Headlight Flash Consequence](docs/HEADLIGHT-CONSEQUENCES.md) | Enlarges the existing shared high-beam flare. It does not add AI reactions or penalties. | Local builder; requires a readable definition from your copy of Dynamic Flares |

The builders are distributed instead of copies of the upstream Quper and Dynamic Flares definitions. They write a new `.scs` file to a location you choose. They do not install mods, launch the game, edit saves, or change Steam settings. The headlight builder cannot read locked/HashFS archives; its documentation explains the available inputs.

## Getting started

1. Download the desired `.scs` files or `ETS2_Personal_Addon_Builders_v1.0.0.zip` from [v1.0.0](https://github.com/EinarEB/ETS2-Personal-Mod-Collection/releases/tag/v1.0.0). GitHub's automatic source archive contains source files, not the ready-built mods.
2. For a builder-based addon, follow its linked instructions first. Python 3.10 or newer is required; no third-party Python packages are needed.
3. With ETS2 closed, copy the chosen `.scs` files into your ETS2 user folder's `mod` directory.
4. Activate them in Mod Manager, disable older versions of the same tweak, and follow the documented load order.

Use only the tweaks you want. They are separate mods, not an all-or-nothing overhaul. Dependencies must be obtained from their original authors.

## Source and rebuilding

`mods/` contains the two directly distributed mods. `tools/build_addon.py` contains the dependency-based builders. `tools/build_release.py` creates the distributable archives with consistent ZIP metadata.

```powershell
python -m unittest discover -s tests -v
python tools/build_release.py --output dist
```

Personal names were removed from mod metadata and filenames. The machine-specific build report and installed-DLC inventory were omitted. No profiles, saves, logs, credentials, or local installation paths are distributed. Public GitHub account attribution remains on this repository. See [credits and upstream content](THIRD-PARTY-NOTICES.md).
