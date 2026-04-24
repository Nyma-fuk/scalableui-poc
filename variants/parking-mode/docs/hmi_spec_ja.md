# Parking and charging dashboard Spec

## Intent

Parking and charging use cases get a dense dashboard with energy, media, settings, and shortcuts.

## Build Target

- `sdk_car_scalableui_parking_mode_x86_64-trunk_staging-userdebug`

## Panel Table

| Panel | Label | Component | Left | Top | Right | Bottom | Display |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `energy_panel` | Energy | `com.android.car.scalableui.hmi.energy/.EnergyActivity` | `2%` | `3%` | `49%` | `48%` | `0` |
| `media_panel` | Media | `com.android.car.scalableui.hmi.media/.MediaActivity` | `51%` | `3%` | `98%` | `48%` | `0` |
| `settings_panel` | Settings | `com.android.car.scalableui.hmi.settings/.SettingsActivity` | `2%` | `52%` | `49%` | `97%` | `0` |
| `shortcuts_panel` | Shortcuts | `com.android.car.scalableui.hmi.shortcuts/.ShortcutsActivity` | `51%` | `52%` | `98%` | `97%` | `0` |

## Routing

- Fixed panels are assigned through `config_default_activities`.
- Panels with multiple component names use a ScalableUI role string-array so
  user-launched apps can be routed into the same panel.
- `panel_app_grid` opens as the All apps overlay.
- `app_panel` is the `DEFAULT` launch-root fallback for generic apps.
- The common Launcher/SystemUI patches keep the All apps launch behavior aligned
  with the base PoC.

## Validation Checklist

1. Apply the variant patches.
2. Build the lunch target.
3. Confirm every fixed panel opens.
4. Open All apps and launch a non-fixed app.
5. Press Home and confirm overlays close.

## Variant Notes

- Vehicle parked/charging event wiring is not included; this is a build-time HMI variant.
