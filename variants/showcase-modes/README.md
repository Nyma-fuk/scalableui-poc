# Mode-switching showcase

## Summary

A comparison layout keeps normal, calm, and app-focus concepts visible as separate regions.

## Product

- Product: `sdk_car_scalableui_showcase_modes_x86_64`
- Lunch: `sdk_car_scalableui_showcase_modes_x86_64-trunk_staging-userdebug`
- RRO: `CarSystemUIScalableUiHmiShowcaseModesRRO`

## Use Cases

- mode comparison
- stakeholder demo
- variant planning

## Panels

- `normal_map_panel`: Normal Map, `2%,3% - 49%,48%`
- `normal_context_panel`: Normal Context, `51%,3% - 98%,48%`
- `calm_preview_panel`: Calm Preview, `2%,52% - 49%,97%`
- `app_focus_preview_panel`: App Focus Preview, `51%,52% - 98%,97%`

## Apply This Variant Only

Run from the AAOS checkout root:

```bash
bash workdir/scalableui-poc/scripts/apply_hmi_variant.sh showcase-modes
lunch sdk_car_scalableui_showcase_modes_x86_64-trunk_staging-userdebug
```

The script applies common ScalableUI routing patches, the common demo app patch,
the product patch for this variant, and the RRO patch for this variant.

## Notes

- This variant is a static showcase; interactive mode buttons can be added later.
