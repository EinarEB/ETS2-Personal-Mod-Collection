# Regional GPS Minimal 1.6.1

A wider overhead navigation view with fewer map symbols and visible regional roads, city labels, and player marker. This packages the existing v1.6 tuning with a corrected manifest and archive metadata.

| Setting | Value |
| --- | ---: |
| First overhead GPS zoom | 1,500 |
| Far overhead GPS zoom | 13,500 |
| Far overhead player marker | 1,620 |
| Far overhead road width factor | 10.0 |
| Far overhead generic icon size | 4.8 × 4.8 |
| Far overhead base city icon size | 1.8 × 1.8 |
| Far overhead map item mask | `0x1403` |
| Fourth city label/pin scale | 42% of each source city's original value |

The first two perspective GPS views and full world-map modes keep their source settings. Relative to v1.5, v1.6 increases the far-view generic icons and player marker by 20%, and the city multiplier from 0.35 to 0.42. The base city-icon size stays 1.8.

The release includes `def/map_data.sii` and **152 city definition overrides** generated for an ETS2 1.60 official-map snapshot. It is a fixed snapshot, not an automatic patcher: it cannot discover additional DLC or adapt to a new map version at installation time. Cities absent from the snapshot retain whatever scale their winning definition provides. Custom maps may conflict because complete city definitions are replaced. Rebuild against the appropriate definitions after relevant game/map changes.

Load above GPS, Route Advisor, map-data, and city-definition overrides. Disable earlier Regional GPS Minimal versions. The old machine-specific build report and outdated preview icon have been removed.
