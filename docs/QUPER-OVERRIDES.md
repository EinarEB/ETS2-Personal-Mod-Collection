# Quper Overrides

An addon for [Realistic Economy ETS2 by Quper](https://steamcommunity.com/sharedfiles/filedetails/?id=3318908089) that sets hired-driver truck and trailer integrity-wear thresholds to **0.8**.

| Setting | Value |
| --- | ---: |
| Hired-driver truck integrity-wear threshold | 0.8 |
| Hired-driver trailer integrity-wear threshold | 0.8 |
| Maximum driving time | 1,440 minutes / 24 hours |
| Sleeping time | 480 minutes / 8 hours |

The driving and sleeping values match Quper 1.60.4. The addon adds the two hired-driver thresholds to its economy definition and preserves unrelated economy settings.

**Used-truck generation is unchanged.** This addon contains no used-vehicle configuration and does not alter dealer stock, generated mileage, wear, or pricing. Existing vehicles are not repaired, and normal wear and repair costs still apply.

## Build and install

Obtain Quper's original mod from its author. With Python 3.10+, supply either its readable ZIP/.scs archive or an extracted directory containing `def/economy_data.sii`:

```powershell
python tools/build_addon.py quper --source "Quper-extracted" --output "Quper_Overrides.scs"
```

Choose a new output filename, then install the generated `.scs` in your ETS2 `mod` folder. Enable it directly above Quper and disable older Quper override addons. There is one configuration.

The builder expects the Quper 1.60.4 economy layout. Missing, duplicate, or unexpected settings cause it to stop. A future Quper update may require a matching addon update.
