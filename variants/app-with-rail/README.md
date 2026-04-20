# Fullscreen app with persistent rail

## Summary

A large app workspace remains available while a side rail keeps shortcuts and status visible.

## Product

- Product: `sdk_car_scalableui_app_with_rail_x86_64`
- Lunch: `sdk_car_scalableui_app_with_rail_x86_64-trunk_staging-userdebug`
- RRO: `CarSystemUIScalableUiHmiAppWithRailRRO`

## Use Cases

- tablet-like app mode
- persistent shortcuts
- fullscreen routing study

## Panels

- `rail_shortcuts_panel`: Shortcuts, `82%,3% - 98%,31%`
- `rail_media_panel`: Media Mini, `82%,35% - 98%,64%`
- `rail_status_panel`: Status, `82%,68% - 98%,97%`

## Apply This Variant Only

Run from the AAOS checkout root:

```bash
bash workdir/scalableui-poc/scripts/apply_hmi_variant.sh app-with-rail
lunch sdk_car_scalableui_app_with_rail_x86_64-trunk_staging-userdebug
```

The script applies common ScalableUI routing patches, the common demo app patch,
the product patch for this variant, and the RRO patch for this variant.

## Notes

- The DEFAULT app_panel opens in the left 80% instead of covering the rail.
