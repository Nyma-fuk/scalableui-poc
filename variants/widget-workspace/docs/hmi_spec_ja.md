# Widget workspace cockpit Spec

## Intent

A compact Panel Control button reveals a hidden runtime menu. Users choose a destination panel, then choose which demo app should appear in that panel.

## Build Target

- `sdk_car_scalableui_widget_workspace_x86_64-trunk_staging-userdebug`

## Panel Table

| Panel | Label | Component | Left | Top | Right | Bottom | Display |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `panel_menu_button` | Panel Control Button | `com.android.car.scalableui.hmi.panelmenubutton/.PanelMenuButtonActivity` | `2%` | `3%` | `11%` | `12%` | `0` |
| `panel_menu` | Hidden Panel Menu | `com.android.car.scalableui.hmi.panelmenu/.PanelMenuActivity` | `2%` | `14%` | `34%` | `88%` | `0` |
| `workspace_panel` | Interactive Workspace | `com.android.car.scalableui.hmi.widgets/.WidgetActivity` | `13%` | `3%` | `98%` | `68%` | `0` |
| `widget_controls_panel` | Widget Controls | `com.android.car.scalableui.hmi.controls/.ControlsActivity` | `13%` | `72%` | `55%` | `97%` | `0` |
| `workspace_status_panel` | Workspace Status | `com.android.car.scalableui.hmi.status/.StatusActivity` | `57%` | `72%` | `98%` | `97%` | `0` |

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

## Variant Notes

- Panel Control opens the hidden menu only when the user asks for it.
- Panel Menu adds a target panel extra so SystemUI can route the selected app to the requested panel.
- All Apps launches are kept separate and should open in the fullscreen app_panel.
