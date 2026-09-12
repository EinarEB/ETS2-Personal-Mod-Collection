# Quper Overrides / Fleet Guard

A personal preference layer for [Realistic Economy ETS2 by Quper](https://steamcommunity.com/sharedfiles/filedetails/?id=3318908089), originally based on version 1.60.4. Obtain the original mod from its author. Its full economy definitions are not included here.

The release provides a local builder with two alternatives:

| Setting | `fleetguard` | `100percent` |
| --- | ---: | ---: |
| Maximum driving time | 1,440 minutes / 24 hours | 1,440 minutes / 24 hours |
| Sleeping time | 480 minutes / 8 hours | 480 minutes / 8 hours |
| Hired-driver truck integrity-wear threshold | 0.8 | 0.9999 |
| Hired-driver trailer integrity-wear threshold | 0.8 | 0.9999 |
| Used-truck generation override | Included | None |

`fleetguard` represents the v1.1 preset. Direct comparison with Quper 1.60.4 shows just five used-vehicle changes: `truck_{cabin,chassis,engine,transmission,wheels}_wear_unfixable_max` goes from **0.4 to 0.0**. The corresponding minimums and all ordinary component wear minimums/maximums were already zero upstream. Other used-vehicle settings are preserved. The older description's claim that permanent wear was unchanged does not accurately describe this edit; the release documents the literal fields without promising a final dealer rating or repair bill.

Driving 1,440 minutes and sleeping 480 minutes also already match Quper 1.60.4. The economy-file changes add the two hired-driver integrity-wear thresholds. Keeping the fatigue values explicit preserves this preset's intended configuration.

`100percent` represents the later v1.2 alternative. The historical name is retained as a command option, but the actual threshold is **99.99%**, not exactly 100%. It leaves used-truck generation entirely to the underlying mod. Use one preset at a time.

## Build

Python 3.10+ is required. Supply either a normal ZIP/.scs archive or an extracted mod directory with `def/economy_data.sii`. Fleet Guard also requires `def/used_vehicle_config.sii`.

```powershell
python tools/build_addon.py quper --source "Quper-extracted" --output "Quper_FleetGuard.scs"
python tools/build_addon.py quper --source "Quper-extracted" --preset 100percent --output "Quper_99.99_Wear.scs"
```

Use a fresh output path. Activate the generated addon directly above Quper and disable older Quper override addons. The builder preserves the supplied version's unrelated values; this is not proof that every future Quper version is compatible. Missing or ambiguous required settings cause the builder to stop.

Existing trucks and dealer offers already stored in a save retain their saved values. Newly generated offers use the active definitions; replacement timing comes from the supplied underlying mod. This addon does not remove wear accumulation from normal driving or guarantee that hired drivers will never incur repairs.
