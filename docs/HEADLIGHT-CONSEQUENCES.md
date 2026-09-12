# AI Headlight Flash Consequence — Dynamic Flares

An addon for **Dynamic Flares v1.2** that makes the existing shared high-beam flare larger and more visible.

| Parameter | Dynamic Flares | Addon |
| --- | ---: | ---: |
| `flare_inner_angle` | 12 | 34 |
| `default_scale` | 0.10 | 0.28 |
| `scale_factor` | 48 | 72 |

Vehicles must use the `flare.vehicle.high_beam` hookup for this adjustment to apply. The player truck's outward-facing high-beam flare can also change. This visual adjustment does not add AI reactions, change how often traffic flashes, or introduce penalties.

## Requirements

Obtain [Dynamic Flares from its author](https://modsy.io/euro-truck-simulator-2/mods/dynamic-flares). Its definition and assets are not included in this download because the original mod prohibits redistribution.

The builder requires Python 3.10+ and a legitimately obtained **readable** `vehicle_high_beam.sii`. It also accepts an extracted Dynamic Flares directory or ordinary ZIP containing `unit/hookup/vehicle/flare/vehicle_high_beam.sii`, its two referenced bulb/scaling includes, and `model/flare/uniform_white_amplified.pmd`.

Locked/HashFS archives are unsupported. Renaming one to `.zip` does not convert it. Obtain a readable definition through an author-supported route; if you have only the definition, pass that individual file instead of its containing directory.

## Build and install

```powershell
python tools/build_addon.py headlight --source "vehicle_high_beam.sii" --output "AI_Headlight_Flash_Consequence_Dynamic_Flares.scs"
```

Choose a new output filename, then install the generated `.scs` in your ETS2 `mod` folder. Keep Dynamic Flares enabled below the addon and disable older copies of the addon. For a single-file source, the referenced assets must be supplied by the enabled original mod.

If you already have the earlier addon with the three edited values, you can rebuild its archive and manifest:

```powershell
python tools/build_addon.py headlight --repair-existing --source "AI_Headlight_Flash_Consequence_Dynamic_Flares.scs" --output "AI_Headlight_Flash_Consequence_Dynamic_Flares_Rebuilt.scs"
```

A higher-priority mod replacing the same flare path can override these changes. Models using other hookups are unaffected. The resulting appearance in driving and VR remains unverified.
