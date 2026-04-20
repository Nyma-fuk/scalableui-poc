# Calm mode minimal HMI

## Summary

Information density is reduced to map, media mini, and small status surfaces.

## Product

- Product: `sdk_car_scalableui_calm_mode_x86_64`
- Lunch: `sdk_car_scalableui_calm_mode_x86_64-trunk_staging-userdebug`
- RRO: `CarSystemUIScalableUiHmiCalmModeRRO`

## Use Cases

- low distraction demo
- focus mode
- normal vs calm comparison

## Panels

- `map_panel`: Calm Map, `4%,6% - 96%,78%`
- `media_mini_panel`: Media Mini, `4%,82% - 58%,96%`
- `status_panel`: Status, `62%,82% - 96%,96%`

## Apply This Variant Only

Run from the AAOS checkout root:

```bash
bash workdir/scalableui-poc/scripts/apply_hmi_variant.sh calm-mode
lunch sdk_car_scalableui_calm_mode_x86_64-trunk_staging-userdebug
```

The script applies common ScalableUI routing patches, the common demo app patch,
the product patch for this variant, and the RRO patch for this variant.

## Notes

- No special notes.
