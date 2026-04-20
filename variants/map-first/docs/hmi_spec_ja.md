# Map-first navigation cockpit Spec

## Intent

The map owns most of the display while a narrow right rail shows glanceable context.

## Build Target

- `sdk_car_scalableui_map_first_x86_64-trunk_staging-userdebug`

## Panel Table

| Panel | Label | Component | Left | Top | Right | Bottom | Display |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `map_panel` | Wide Map | `com.android.car.scalableui.hmi.demo/.MapPanelActivity` | `2%` | `3%` | `72%` | `97%` | `0` |
| `event_panel` | Next Event | `com.android.calendar/.AllInOneActivity` | `74%` | `3%` | `98%` | `31%` | `0` |
| `media_mini_panel` | Media Mini | `com.android.car.scalableui.hmi.demo/.MediaPanelActivity` | `74%` | `35%` | `98%` | `64%` | `0` |
| `status_panel` | Vehicle Status | `com.android.car.scalableui.hmi.demo/.StatusPanelActivity` | `74%` | `68%` | `98%` | `97%` | `0` |

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
