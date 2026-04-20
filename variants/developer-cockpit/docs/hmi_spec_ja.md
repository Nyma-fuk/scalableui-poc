# Diagnostics developer cockpit Spec

## Intent

Debug status, controls, app-under-test, and map/media panels are arranged for PoC validation.

## Build Target

- `sdk_car_scalableui_developer_cockpit_x86_64-trunk_staging-userdebug`

## Panel Table

| Panel | Label | Component | Left | Top | Right | Bottom | Display |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `debug_status_panel` | Debug Status | `com.android.car.scalableui.hmi.demo/.DebugPanelActivity` | `2%` | `3%` | `39%` | `48%` | `0` |
| `app_under_test_panel` | App Under Test | `com.android.car.scalableui.hmi.demo/.TaskPanelActivity` | `41%` | `3%` | `98%` | `48%` | `0` |
| `control_panel` | Controls | `com.android.car.scalableui.hmi.demo/.ControlsPanelActivity` | `2%` | `52%` | `39%` | `97%` | `0` |
| `map_media_panel` | Map Media | `com.android.car.carlauncher/com.android.car.carlauncher.homescreen.MapTosActivity` | `41%` | `52%` | `98%` | `97%` | `0` |

## Routing

- Fixed panels are assigned through `config_default_activities`.
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
