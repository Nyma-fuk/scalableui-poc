# Widget workspace cockpit Spec

## Intent

An interactive left menu launches map, G Ball, widget, media, and task apps into one ScalableUI workspace panel so users can swap the panel content at runtime.

## Build Target

- `sdk_car_scalableui_widget_workspace_x86_64-trunk_staging-userdebug`

## Panel Table

| Panel | Label | Component | Left | Top | Right | Bottom | Display |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `panel_menu` | Panel Menu | `com.android.car.scalableui.hmi.panelmenu/.PanelMenuActivity` | `2%` | `3%` | `22%` | `97%` | `0` |
| `workspace_panel` | Interactive Workspace | `com.android.car.scalableui.hmi.widgets/.WidgetActivity, com.android.car.scalableui.hmi.map/.MapActivity, com.android.car.scalableui.hmi.gball/.GBallActivity, com.android.car.scalableui.hmi.media/.MediaActivity, com.android.car.scalableui.hmi.tasks/.TaskActivity` | `24%` | `3%` | `98%` | `68%` | `0` |
| `widget_controls_panel` | Widget Controls | `com.android.car.scalableui.hmi.controls/.ControlsActivity` | `24%` | `72%` | `60%` | `97%` | `0` |
| `workspace_status_panel` | Workspace Status | `com.android.car.scalableui.hmi.status/.StatusActivity` | `62%` | `72%` | `98%` | `97%` | `0` |

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
