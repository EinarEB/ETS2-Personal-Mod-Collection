# ETS2 Personal Mod Collection

Small tweaks for **Euro Truck Simulator 2 1.60**: a wider GPS view, subtler rain streaks, hired-driver wear tolerance, and more visible high-beam flares.

**[Download](https://github.com/EinarEB/ETS2-Personal-Mod-Collection/releases/tag/v1.0.1)** · [Installation](docs/INSTALLATION.md) · [Compatibility](docs/VALIDATION.md)

| Mod | What it does | Download |
| --- | --- | --- |
| [Regional GPS Minimal](docs/REGIONAL-GPS.md) | A wide, uncluttered overhead GPS view with readable roads, city labels, and truck marker. | Ready-to-use `.scs` |
| [VR Rain Streaks Subtle](docs/VR-RAIN.md) | Makes falling rain streaks more subdued with a material RGB value of 0.10. | Ready-to-use `.scs` |
| [Quper Overrides](docs/QUPER-OVERRIDES.md) | Sets hired-driver truck and trailer integrity-wear thresholds to 0.8. Used-truck generation is unchanged. | Builder for your copy of Quper's economy mod |
| [AI Headlight Flash Consequence — Dynamic Flares](docs/HEADLIGHT-CONSEQUENCES.md) | Makes the existing shared high-beam flare larger and more visible. | Builder for your copy of Dynamic Flares |

Each mod can be used separately. Quper Overrides and the Dynamic Flares addon require their original mods; the included builders create the matching `.scs` files locally.

## Installation

1. Download the desired `.scs` files or `ETS2_Personal_Addon_Builders_v1.0.1.zip` from the [release](https://github.com/EinarEB/ETS2-Personal-Mod-Collection/releases/tag/v1.0.1).
2. For Quper or Dynamic Flares, follow the linked mod guide to build the addon. Python 3.10+ is required.
3. With ETS2 closed, copy the chosen `.scs` files into your ETS2 user folder's `mod` directory.
4. Enable them in Mod Manager, disable older copies of the same addon, and follow the documented load order.

These packages are currently a preview for ETS2 1.60; in-game compatibility and appearance have not yet been revalidated.

## Source

`mods/` contains the GPS and rain definitions. `tools/build_addon.py` builds the Quper and Dynamic Flares addons; `tools/build_release.py` packages the downloads.

```powershell
python -m unittest discover -s tests
python tools/build_release.py --output dist
```

[Credits](THIRD-PARTY-NOTICES.md)
