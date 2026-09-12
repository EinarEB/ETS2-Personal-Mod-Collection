# Installation

Download individual assets from the release. `.scs` files go directly into the `mod` directory inside your ETS2 user folder; do not unpack them. On a typical Windows installation this is `Documents/Euro Truck Simulator 2/mod`, though redirected Documents folders can differ. Close ETS2 before changing installed mods.

Enable the selected mods in Mod Manager. Higher priority means higher in the list:

| Addon | Place above | Also required |
| --- | --- | --- |
| Regional GPS Minimal | Other mods that replace `def/map_data.sii` or the same city definitions | ETS2 1.60; compatible official map content |
| VR Rain Streaks Subtle | Other mods replacing `material/environment/rain.mat` | ETS2 1.60 |
| Quper Overrides | Realistic Economy ETS2 by Quper | The Quper version used to build the addon |
| Headlight Flash Consequence | Dynamic Flares and other overrides of the high-beam flare definition | Dynamic Flares v1.2 remains enabled |

Disable old copies of the same addon. Only one Quper preset should be active at a time. Restart ETS2 after changing the active collection.

Load order cannot combine different edits to the same file. A higher-priority definition replaces the lower-priority definition. Custom maps, GPS/Route Advisor mods, lighting overhauls, and economy changes may need a dedicated compatibility patch.

To remove an addon, deactivate it and remove its `.scs` with the game closed. Changes to offers or vehicles already stored in a save can persist after an economy addon is removed; these mods do not rewrite existing save data.

## Builders

Extract `ETS2_Personal_Addon_Builders_v1.0.0.zip` into a working folder. Open a terminal there and follow [Quper](QUPER-OVERRIDES.md) or [headlight](HEADLIGHT-CONSEQUENCES.md) instructions. Choose a new output filename in that working folder, inspect the result, then copy it into the game's mod directory yourself.

The builders accept only readable source formats. They do not download dependencies, bypass archive protection, or bundle the original authors' mods.

## Checksums

Compare a downloaded asset with the matching line in `SHA256SUMS.txt`:

```powershell
Get-FileHash -Algorithm SHA256 .\Regional_GPS_Minimal_1.6.1.scs
```
