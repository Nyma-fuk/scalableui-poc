# Driver and passenger display HMI

## Summary

Driver and passenger panels are split by displayId for multi-display exploration.

## Product

- Product: `sdk_car_scalableui_dual_display_x86_64`
- Lunch: `sdk_car_scalableui_dual_display_x86_64-trunk_staging-userdebug`
- RRO: `CarSystemUIScalableUiHmiDualDisplayRRO`

## Use Cases

- multi-display planning
- driver/passenger separation
- target display study

## Panels

- `driver_map_panel`: Driver Map, `2%,3% - 72%,97%`
- `driver_media_panel`: Driver Media, `74%,3% - 98%,97%`
- `passenger_app_panel`: Passenger App, `0,0 - 100%,100%`

## Apply This Variant Only

Run from the AAOS checkout root:

```bash
bash workdir/scalableui-poc/scripts/apply_hmi_variant.sh dual-display
lunch sdk_car_scalableui_dual_display_x86_64-trunk_staging-userdebug
```

The script applies common ScalableUI routing patches, the common demo app patch,
the product patch for this variant, and the RRO patch for this variant.

## Notes

- Requires a multi-display emulator or target to validate displayId=1 behavior.
