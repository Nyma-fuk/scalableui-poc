# Fullscreen app with persistent rail Spec

## Intent

A large app workspace remains available while a side rail keeps shortcuts and status visible.

## Build Target

- `sdk_car_scalableui_app_with_rail_x86_64-trunk_staging-userdebug`

## Panel Table

| Panel | Label | Component | Left | Top | Right | Bottom | Display |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `rail_shortcuts_panel` | Shortcuts | `com.android.car.scalableui.hmi.shortcuts/.ShortcutsActivity` | `82%` | `3%` | `98%` | `31%` | `0` |
| `rail_media_panel` | Media Mini | `com.android.car.scalableui.hmi.media/.MediaActivity` | `82%` | `35%` | `98%` | `64%` | `0` |
| `rail_status_panel` | Status | `com.android.car.scalableui.hmi.status/.StatusActivity` | `82%` | `68%` | `98%` | `97%` | `0` |

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
