# App grid hub Spec

## Intent

All apps is treated as the central hub and launched apps are routed to fullscreen.

## Build Target

- `sdk_car_scalableui_app_grid_hub_x86_64-trunk_staging-userdebug`

## Panel Table

| Panel | Label | Component | Left | Top | Right | Bottom | Display |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `home_status_panel` | Home Status | `com.android.car.scalableui.hmi.demo/.StatusPanelActivity` | `2%` | `3%` | `98%` | `18%` | `0` |
| `media_mini_panel` | Media Mini | `com.android.car.scalableui.hmi.demo/.MediaPanelActivity` | `2%` | `82%` | `98%` | `97%` | `0` |

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
