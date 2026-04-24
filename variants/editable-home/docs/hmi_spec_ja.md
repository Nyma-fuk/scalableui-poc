# Editable multipanel home Spec

## Intent

A ScalableUI-based multipanel home keeps system bars outside the managed area, lets the user choose L1/L2/L3 layouts plus per-panel apps, and restores the saved assignment on the next Home entry.

## Build Target

- `sdk_car_scalableui_editable_home_x86_64-trunk_staging-userdebug`

## Panel Table

| Panel | Label | Component | Left | Top | Right | Bottom | Display |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `home_panel_primary` | Home Primary | `com.android.car.scalableui.hmi.map/.MapActivity, com.android.car.scalableui.hmi.media/.MediaActivity, com.android.car.scalableui.hmi.controls/.ControlsActivity, com.android.car.scalableui.hmi.calendar/.CalendarActivity, com.android.car.scalableui.hmi.settings/.SettingsActivity, com.android.car.scalableui.hmi.gball/.GBallActivity` | `4%` | `12%` | `62%` | `84%` | `0` |
| `home_panel_secondary_top` | Home Secondary Top | `com.android.car.scalableui.hmi.map/.MapActivity, com.android.car.scalableui.hmi.media/.MediaActivity, com.android.car.scalableui.hmi.controls/.ControlsActivity, com.android.car.scalableui.hmi.calendar/.CalendarActivity, com.android.car.scalableui.hmi.settings/.SettingsActivity, com.android.car.scalableui.hmi.gball/.GBallActivity` | `64%` | `12%` | `96%` | `46%` | `0` |
| `home_panel_secondary_bottom` | Home Secondary Bottom | `com.android.car.scalableui.hmi.map/.MapActivity, com.android.car.scalableui.hmi.media/.MediaActivity, com.android.car.scalableui.hmi.controls/.ControlsActivity, com.android.car.scalableui.hmi.calendar/.CalendarActivity, com.android.car.scalableui.hmi.settings/.SettingsActivity, com.android.car.scalableui.hmi.gball/.GBallActivity` | `64%` | `50%` | `96%` | `84%` | `0` |
| `home_edit_overlay` | Home Edit Overlay | `decor` | `3%` | `10%` | `97%` | `88%` | `0` |

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

- The managed Home content area is inset so top bar and nav bar remain visible.
- HomeEditActivity stores layout id and per-panel assignment in SharedPreferences.
- Duplicate assignments are rejected when the user presses Save.
- The edit overlay is a ScalableUI decor panel; the editor UI itself opens inside app_panel.
