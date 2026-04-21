# Driver and passenger display HMI Spec

## Intent

Driver and passenger panels are split by displayId for multi-display exploration.

## Build Target

- `sdk_car_scalableui_dual_display_x86_64-trunk_staging-userdebug`

## Panel Table

| Panel | Label | Component | Left | Top | Right | Bottom | Display |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `driver_map_panel` | Driver Map | `com.android.car.scalableui.hmi.map/.MapActivity` | `2%` | `3%` | `72%` | `97%` | `0` |
| `driver_media_panel` | Driver Media | `com.android.car.scalableui.hmi.media/.MediaActivity` | `74%` | `3%` | `98%` | `97%` | `0` |
| `passenger_app_panel` | Passenger App | `com.android.car.scalableui.hmi.passenger/.PassengerActivity` | `0` | `0` | `100%` | `100%` | `1` |

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
