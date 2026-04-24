# Fixed 3-zone cockpit Spec

## Intent

Map, calendar, and radio are always visible in a stable 3-zone layout.

## Build Target

- `sdk_car_scalableui_fixed_3zone_x86_64-trunk_staging-userdebug`

## Panel Table

| Panel | Label | Component | Left | Top | Right | Bottom | Display |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `map_panel` | Map | `com.android.car.scalableui.hmi.map/.MapActivity` | `2%` | `3%` | `58%` | `97%` | `0` |
| `calendar_panel` | Calendar | `com.android.calendar/.AllInOneActivity` | `60%` | `3%` | `98%` | `48%` | `0` |
| `radio_panel` | Radio | `com.android.car.radio/.RadioActivity` | `60%` | `52%` | `98%` | `97%` | `0` |

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

- No special notes.
