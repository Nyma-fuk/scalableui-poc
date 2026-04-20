# Diagnostics developer cockpit

## Summary

Debug status, controls, app-under-test, and map/media panels are arranged for PoC validation.

## Product

- Product: `sdk_car_scalableui_developer_cockpit_x86_64`
- Lunch: `sdk_car_scalableui_developer_cockpit_x86_64-trunk_staging-userdebug`
- RRO: `CarSystemUIScalableUiHmiDeveloperCockpitRRO`

## Use Cases

- developer testbench
- demo operation
- diagnostics visualization

## Panels

- `debug_status_panel`: Debug Status, `2%,3% - 39%,48%`
- `app_under_test_panel`: App Under Test, `41%,3% - 98%,48%`
- `control_panel`: Controls, `2%,52% - 39%,97%`
- `map_media_panel`: Map Media, `41%,52% - 98%,97%`

## Apply This Variant Only

Run from the AAOS checkout root:

```bash
bash workdir/scalableui-poc/scripts/apply_hmi_variant.sh developer-cockpit
lunch sdk_car_scalableui_developer_cockpit_x86_64-trunk_staging-userdebug
```

The script applies common ScalableUI routing patches, the common demo app patch,
the product patch for this variant, and the RRO patch for this variant.

## Notes

- No special notes.
