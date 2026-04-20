# Fixed 3-zone cockpit

## Summary

Map, calendar, and radio are always visible in a stable 3-zone layout.

## Product

- Product: `sdk_car_scalableui_fixed_3zone_x86_64`
- Lunch: `sdk_car_scalableui_fixed_3zone_x86_64-trunk_staging-userdebug`
- RRO: `CarSystemUIScalableUiHmiFixed3zoneRRO`

## Use Cases

- baseline cockpit
- navigation with schedule
- radio demo

## Panels

- `map_panel`: Map, `2%,3% - 58%,97%`
- `calendar_panel`: Calendar, `60%,3% - 98%,48%`
- `radio_panel`: Radio, `60%,52% - 98%,97%`

## Apply This Variant Only

Run from the AAOS checkout root:

```bash
bash workdir/scalableui-poc/scripts/apply_hmi_variant.sh fixed-3zone
lunch sdk_car_scalableui_fixed_3zone_x86_64-trunk_staging-userdebug
```

The script applies common ScalableUI routing patches, the common demo app patch,
the product patch for this variant, and the RRO patch for this variant.

## Notes

- No special notes.
