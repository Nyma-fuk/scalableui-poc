# Floating card HMI

## Summary

A full-screen map/background is combined with floating rounded cards.

## Product

- Product: `sdk_car_scalableui_floating_card_x86_64`
- Lunch: `sdk_car_scalableui_floating_card_x86_64-trunk_staging-userdebug`
- RRO: `CarSystemUIScalableUiHmiFloatingCardRRO`

## Use Cases

- modern floating UI
- map card exploration
- ambient cockpit

## Panels

- `map_background_panel`: Map Background, `0,0 - 100%,100%`
- `primary_card_panel`: Primary Card, `8%,12% - 55%,52%`
- `secondary_card_panel`: Secondary Card, `58%,58% - 94%,90%`

## Apply This Variant Only

Run from the AAOS checkout root:

```bash
bash workdir/scalableui-poc/scripts/apply_hmi_variant.sh floating-card
lunch sdk_car_scalableui_floating_card_x86_64-trunk_staging-userdebug
```

The script applies common ScalableUI routing patches, the common demo app patch,
the product patch for this variant, and the RRO patch for this variant.

## Notes

- No special notes.
