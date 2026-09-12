# AI Headlight Flash Consequence — investigation and local builder

**This addon adjusts an existing flare. It does not create an AI response, change how frequently traffic flashes, or add fines or other consequences.** Vehicles must already use the shared `flare.vehicle.high_beam` hookup. The player truck's outward-facing high-beam flare can change too.

## Why the original was not working

The inspected ETS2 1.60 log rejected the original addon's manifest and description as incompatible ZIP entries. The addon was discovered but was not active in that session, while Dynamic Flares v1.2 was active.

Two defects were found:

1. The archive marked files as Unix entries but stored only permission bits, without a regular-file type. This is the leading explanation for the ZIP-entry rejection; it has not been isolated in a new runtime test. The builder now writes ordinary DOS ZIP entries with complete sizes/CRC values and no data descriptors.
2. The manifest's anonymous unit-name component was 23 characters long. SCS unit-name components have a 12-character limit. Generated manifests use the short `.package_name` form shown in the official example. [SCS unit documentation](https://modding.scssoft.com/wiki/Documentation/Engine/Units), [SCS Mod Manager documentation](https://modding.scssoft.com/wiki/Documentation/Engine/Mod_manager).

Packaging repair should address those defects, but it cannot add missing gameplay logic. The original contains only metadata and one flare definition. Its intended parameter changes are:

| Parameter | Dynamic Flares v1.2 baseline | Addon |
| --- | ---: | ---: |
| `flare_inner_angle` | 12 | 34 |
| `default_scale` | 0.10 | 0.28 |
| `scale_factor` | 48 | 72 |

The builder preserves the supplied definition's other content. The resulting visibility and any road-light interaction remain untested in driving; this is an experimental visual tweak.

## Why this release contains a builder

The old addon copied its remaining definition from Dynamic Flares. That mod's supplied terms prohibit redistribution, so neither the copied definition nor Dynamic Flares models/includes are distributed here. Obtain [Dynamic Flares from its author](https://modsy.io/euro-truck-simulator-2/mods/dynamic-flares).

You need a legitimately obtained **readable** `vehicle_high_beam.sii`, an extracted Dynamic Flares directory, or an ordinary ZIP containing that definition at `unit/hookup/vehicle/flare/vehicle_high_beam.sii`. For a ZIP/directory source, the builder also requires its two referenced bulb/scaling include files beside the definition and `model/flare/uniform_white_amplified.pmd`. If you have only the definition, pass that individual file instead. Python 3.10+ is required.

```powershell
python tools/build_addon.py headlight --source "vehicle_high_beam.sii" --output "Headlight_Flash_Consequence.scs"
```

The installed Dynamic Flares archive inspected for this collection uses HashFS and cannot be read by this builder. Changing its extension to `.zip` will not help. This tool does not unlock archives; obtain a readable definition through an author-supported route. For a single `.sii` input, referenced models/includes cannot be verified locally and must be provided by the enabled original mod.

If you already have the old personal addon, its existing three edited values can instead be repackaged explicitly:

```powershell
python tools/build_addon.py headlight --repair-existing --source "AI_Headlight_Flash_Consequence_Dynamic_Flares.scs" --output "Headlight_Flash_Consequence_Repaired.scs"
```

The old addon is not a release asset. Repair mode rebuilds its metadata and ZIP container around the supplied definition. It does not make the original dependency redistributable.

Keep Dynamic Flares enabled below the generated addon. Disable the old addon. A higher-priority mod replacing the same flare path can override these changes, and traffic models using other hookups will not be affected.
