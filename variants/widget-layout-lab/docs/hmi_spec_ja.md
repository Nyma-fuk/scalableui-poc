# Widget layout lab cockpit Spec

## Intent

A map-first widget cockpit with a hidden right-side widget menu. The menu can launch widget demo apps into named ScalableUI panels and switch between prepared layout patterns that mirror drag-and-drop HMI exploration.

## Build Target

- `sdk_car_scalableui_widget_layout_lab_x86_64-trunk_staging-userdebug`

## Panel Table

| Panel | Label | Component | Left | Top | Right | Bottom | Display |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `lab_background_panel` | Lab Background | `decor` | `0` | `0` | `100%` | `100%` | `0` |
| `widget_a_panel` | Widget A Map | `com.android.car.scalableui.hmi.map/.MapActivity` | `4%` | `7%` | `48%` | `86%` | `0` |
| `widget_b_panel` | Widget B Calendar | `com.android.car.scalableui.hmi.calendar/.CalendarActivity` | `52%` | `7%` | `96%` | `20%` | `0` |
| `widget_c_panel` | Widget C Weather | `com.android.car.scalableui.hmi.weather/.WeatherActivity` | `52%` | `23%` | `96%` | `36%` | `0` |
| `widget_d_panel` | Widget D Media | `com.android.car.scalableui.hmi.media/.MediaActivity` | `0` | `100%` | `30%` | `130%` | `0` |
| `widget_e_panel` | Widget E Tasks | `com.android.car.scalableui.hmi.tasks/.TaskActivity` | `0` | `100%` | `30%` | `130%` | `0` |
| `widget_f_panel` | Widget F Interactive | `com.android.car.scalableui.hmi.widgets/.WidgetActivity` | `0` | `100%` | `30%` | `130%` | `0` |
| `widget_drop_zone_panel` | Widget Drop Zone | `com.android.car.scalableui.hmi.widgetdropzone/.WidgetDropZoneActivity` | `44%` | `82%` | `50%` | `92%` | `0` |
| `widget_menu_button_panel` | Widget Menu Button | `com.android.car.scalableui.hmi.widgetmenubutton/.WidgetMenuButtonActivity` | `91%` | `82%` | `97%` | `92%` | `0` |
| `widget_picker_panel` | Hidden Widget Picker | `com.android.car.scalableui.hmi.widgetmenu/.WidgetMenuActivity` | `73%` | `0` | `100%` | `100%` | `0` |

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

- The right-side Widget Layout button launches the picker and a temporary drop zone.
- Pattern buttons dispatch ScalableUI custom events through the SystemUI broadcast bridge.
- Drag source cards use Android global drag data; dropping on the drop zone applies a prepared layout pattern.
