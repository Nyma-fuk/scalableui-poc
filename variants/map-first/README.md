# Map-first navigation cockpit

## Summary

The map owns most of the display while a narrow right rail shows glanceable context.

## Product

- Product: `sdk_car_scalableui_map_first_x86_64`
- Lunch: `sdk_car_scalableui_map_first_x86_64-trunk_staging-userdebug`
- RRO: `CarSystemUIScalableUiHmiMapFirstRRO`

## Use Cases

- wide navigation
- ETA/status rail
- route guidance demo

## Panels

- `map_panel`: Wide Map, `2%,3% - 72%,97%`
- `event_panel`: Next Event, `74%,3% - 98%,31%`
- `media_mini_panel`: Media Mini, `74%,35% - 98%,64%`
- `status_panel`: Vehicle Status, `74%,68% - 98%,97%`

## Apply This Variant Only

Run from the AAOS checkout root:

```bash
bash workdir/scalableui-poc/scripts/apply_hmi_variant.sh map-first
lunch sdk_car_scalableui_map_first_x86_64-trunk_staging-userdebug
```

The script applies common ScalableUI routing patches, the common demo app patch,
the product patch for this variant, and the RRO patch for this variant.

## Notes

- No special notes.
