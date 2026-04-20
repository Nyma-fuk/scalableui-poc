# HMI Variant Suite

This directory contains generated patch packs for all HMI ideas described in
the wiki page `HMI_Pattern_Ideas_ja.md`.

## Variants

| Variant | Product | HMI |
| --- | --- | --- |
| `fixed-3zone` | `sdk_car_scalableui_fixed_3zone_x86_64` | Fixed 3-zone cockpit |
| `map-first` | `sdk_car_scalableui_map_first_x86_64` | Map-first navigation cockpit |
| `media-dock` | `sdk_car_scalableui_media_dock_x86_64` | Media dock cockpit |
| `productivity-dashboard` | `sdk_car_scalableui_productivity_dashboard_x86_64` | Productivity assistant dashboard |
| `app-with-rail` | `sdk_car_scalableui_app_with_rail_x86_64` | Fullscreen app with persistent rail |
| `floating-card` | `sdk_car_scalableui_floating_card_x86_64` | Floating card HMI |
| `app-grid-hub` | `sdk_car_scalableui_app_grid_hub_x86_64` | App grid hub |
| `calm-mode` | `sdk_car_scalableui_calm_mode_x86_64` | Calm mode minimal HMI |
| `parking-mode` | `sdk_car_scalableui_parking_mode_x86_64` | Parking and charging dashboard |
| `developer-cockpit` | `sdk_car_scalableui_developer_cockpit_x86_64` | Diagnostics developer cockpit |
| `dual-display` | `sdk_car_scalableui_dual_display_x86_64` | Driver and passenger display HMI |
| `showcase-modes` | `sdk_car_scalableui_showcase_modes_x86_64` | Mode-switching showcase |

## Apply All Variants

Run from the AAOS checkout root:

```bash
bash workdir/scalableui-poc/scripts/apply_hmi_suite.sh
```

After applying the suite, choose a product at build time:

```bash
lunch sdk_car_scalableui_map_first_x86_64-trunk_staging-userdebug
```

## Apply One Variant

```bash
bash workdir/scalableui-poc/scripts/apply_hmi_variant.sh map-first
lunch sdk_car_scalableui_map_first_x86_64-trunk_staging-userdebug
```

The suite is better when you want every HMI available in one checkout. The
single-variant script is better when you want a smaller patch surface.
