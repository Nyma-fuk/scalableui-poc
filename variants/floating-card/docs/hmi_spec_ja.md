# Floating card HMI Spec

## Intent

A full-screen map/background is combined with floating rounded cards.

## Build Target

- `sdk_car_scalableui_floating_card_x86_64-trunk_staging-userdebug`

## Panel Table

| Panel | Label | Component | Left | Top | Right | Bottom | Display |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `map_background_panel` | Map Background | `com.android.car.scalableui.hmi.map/.MapActivity` | `0` | `0` | `100%` | `100%` | `0` |
| `primary_card_panel` | Primary Card | `com.android.calendar/.AllInOneActivity` | `8%` | `12%` | `55%` | `52%` | `0` |
| `secondary_card_panel` | Secondary Card | `com.android.car.scalableui.hmi.media/.MediaActivity` | `58%` | `58%` | `94%` | `90%` | `0` |

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
