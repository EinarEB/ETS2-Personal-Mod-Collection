# Validation and release changes

## Initial collection release — 2026-09-12

This is an offline-reviewed preview. No new game, GPU, headset, or driving test was performed. Correct archive structure and passing builder tests do not prove visual or gameplay quality.

- Rebuilt distributed `.scs` files with conventional DOS ZIP metadata, stored compression, explicit CRC/sizes, fixed timestamps, and no extra fields or comments.
- Replaced long manifest unit identifiers with `.package_name` and neutral collection authorship. Package compatibility is restricted to ETS2 1.60.
- Retained Regional GPS v1.6 gameplay values and all 152 supplied city overrides; removed machine-specific build information and the outdated icon.
- Retained rain-material RGB 0.10 and its game texture reference.
- Distributed parameter builders for Quper and Dynamic Flares instead of their copied definitions.
- Documented the headlight loading defects separately from its limited visual behavior.
- Compared both historical Quper presets directly with upstream 1.60.4. Documented the five changed `wear_unfixable_max` fields and added driver thresholds, correcting the older wear-preservation description. No promised repair-cost outcome.
- Checked archive CRCs, local/central ZIP headers, expected file inventories, neutral manifests, and absence of source build reports and personal paths.
- Builder tests use synthetic input to check selective edits, invalid/ambiguous data, source/output safeguards, and archive structure.
- Both Quper presets were also built from the readable upstream 1.60.4 source, and the supplied old personal headlight addon was rebuilt in repair mode. These private outputs were checked offline and were not installed or distributed.

## Privacy scope

Published files were assembled from an explicit source selection. Original archives, installed-DLC inventory, build timestamps, personal names in mod metadata, original builder executables, logs, profiles, saves, machine paths, and credentials are excluded. Public GitHub account attribution and ordinary in-game place names are retained. The GPS content itself necessarily shows which cities the static mod supports; no full machine or DLC inventory report is included.

## Remaining checks

In a separately agreed game-testing session, verify that all selected manifests appear without errors, the winning definitions match the chosen load order, GPS views work with the active map, rain is comfortable in VR, and an existing headlight flash visibly changes in real driving. Verify Quper behavior using newly generated dealer stock; existing saved offers are not a valid test of new definitions.
