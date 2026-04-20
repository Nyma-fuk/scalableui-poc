# Productivity assistant dashboard Spec

## Intent

Calendar, tasks, phone, and map are arranged as a parked or pre-drive assistant view.

## Build Target

- `sdk_car_scalableui_productivity_dashboard_x86_64-trunk_staging-userdebug`

## Panel Table

| Panel | Label | Component | Left | Top | Right | Bottom | Display |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `calendar_panel` | Calendar | `com.android.calendar/.AllInOneActivity` | `2%` | `3%` | `49%` | `48%` | `0` |
| `task_panel` | Tasks | `com.android.car.scalableui.hmi.demo/.TaskPanelActivity` | `51%` | `3%` | `98%` | `48%` | `0` |
| `map_mini_panel` | Map Mini | `com.android.car.scalableui.hmi.demo/.MapPanelActivity` | `2%` | `52%` | `49%` | `97%` | `0` |
| `phone_panel` | Phone | `com.android.car.scalableui.hmi.demo/.PhonePanelActivity` | `51%` | `52%` | `98%` | `97%` | `0` |

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
