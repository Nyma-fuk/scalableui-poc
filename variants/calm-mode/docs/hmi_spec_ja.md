# Calm mode minimal HMI Spec

## Intent

Information density is reduced to map, media mini, and small status surfaces.

## Build Target

- `sdk_car_scalableui_calm_mode_x86_64-trunk_staging-userdebug`

## Panel Table

| Panel | Label | Component | Left | Top | Right | Bottom | Display |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `map_panel` | Calm Map | `com.android.car.carlauncher/com.android.car.carlauncher.homescreen.MapTosActivity` | `4%` | `6%` | `96%` | `78%` | `0` |
| `media_mini_panel` | Media Mini | `com.android.car.scalableui.hmi.demo/.MediaPanelActivity` | `4%` | `82%` | `58%` | `96%` | `0` |
| `status_panel` | Status | `com.android.car.scalableui.hmi.demo/.StatusPanelActivity` | `62%` | `82%` | `96%` | `96%` | `0` |

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
