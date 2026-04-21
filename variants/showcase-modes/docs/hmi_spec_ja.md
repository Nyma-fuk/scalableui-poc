# Mode-switching showcase Spec

## Intent

A comparison layout keeps normal, calm, and app-focus concepts visible as separate regions.

## Build Target

- `sdk_car_scalableui_showcase_modes_x86_64-trunk_staging-userdebug`

## Panel Table

| Panel | Label | Component | Left | Top | Right | Bottom | Display |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `normal_map_panel` | Normal Map | `com.android.car.scalableui.hmi.map/.MapActivity` | `2%` | `3%` | `49%` | `48%` | `0` |
| `normal_context_panel` | Normal Context | `com.android.calendar/.AllInOneActivity` | `51%` | `3%` | `98%` | `48%` | `0` |
| `calm_preview_panel` | Calm Preview | `com.android.car.scalableui.hmi.calm/.CalmActivity` | `2%` | `52%` | `49%` | `97%` | `0` |
| `app_focus_preview_panel` | App Focus Preview | `com.android.car.scalableui.hmi.tasks/.TaskActivity` | `51%` | `52%` | `98%` | `97%` | `0` |

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
