# Parking and charging dashboard

## Summary

Parking and charging use cases get a dense dashboard with energy, media, settings, and shortcuts.

## Product

- Product: `sdk_car_scalableui_parking_mode_x86_64`
- Lunch: `sdk_car_scalableui_parking_mode_x86_64-trunk_staging-userdebug`
- RRO: `CarSystemUIScalableUiHmiParkingModeRRO`

## Use Cases

- charging dashboard
- parked app mode
- energy/status demo

## Panels

- `energy_panel`: Energy, `2%,3% - 49%,48%`
- `media_panel`: Media, `51%,3% - 98%,48%`
- `settings_panel`: Settings, `2%,52% - 49%,97%`
- `shortcuts_panel`: Shortcuts, `51%,52% - 98%,97%`

## Apply This Variant Only

Run from the AAOS checkout root:

```bash
bash workdir/scalableui-poc/scripts/apply_hmi_variant.sh parking-mode
lunch sdk_car_scalableui_parking_mode_x86_64-trunk_staging-userdebug
```

The script applies common ScalableUI routing patches, the common demo app patch,
the product patch for this variant, and the RRO patch for this variant.

## Notes

- Vehicle parked/charging event wiring is not included; this is a build-time HMI variant.
