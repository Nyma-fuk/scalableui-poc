# Media dock cockpit Spec

## Intent

Media controls are emphasized with a large bottom dock and compact navigation.

## Build Target

- `sdk_car_scalableui_media_dock_x86_64-trunk_staging-userdebug`

## Panel Table

| Panel | Label | Component | Left | Top | Right | Bottom | Display |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `map_mini_panel` | Map Mini | `com.android.car.carlauncher/com.android.car.carlauncher.homescreen.MapTosActivity` | `2%` | `3%` | `38%` | `44%` | `0` |
| `now_playing_panel` | Now Playing | `com.android.car.scalableui.hmi.demo/.MediaPanelActivity` | `40%` | `3%` | `98%` | `44%` | `0` |
| `media_dock_panel` | Media Dock | `com.android.car.scalableui.hmi.demo/.ControlsPanelActivity` | `2%` | `48%` | `98%` | `97%` | `0` |

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
