# Media dock cockpit Spec

## Intent

Media controls are emphasized with a large bottom dock and compact navigation.

## Build Target

- `sdk_car_scalableui_media_dock_x86_64-trunk_staging-userdebug`

## Panel Table

| Panel | Label | Component | Left | Top | Right | Bottom | Display |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `map_mini_panel` | Map Mini | `com.android.car.scalableui.hmi.map/.MapActivity` | `2%` | `3%` | `38%` | `44%` | `0` |
| `now_playing_panel` | Now Playing | `com.android.car.scalableui.hmi.media/.MediaActivity` | `40%` | `3%` | `98%` | `44%` | `0` |
| `media_dock_panel` | Media Dock | `com.android.car.scalableui.hmi.controls/.ControlsActivity` | `2%` | `48%` | `98%` | `97%` | `0` |

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
