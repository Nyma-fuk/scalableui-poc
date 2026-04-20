# App grid hub

## Summary

All apps is treated as the central hub and launched apps are routed to fullscreen.

## Product

- Product: `sdk_car_scalableui_app_grid_hub_x86_64`
- Lunch: `sdk_car_scalableui_app_grid_hub_x86_64-trunk_staging-userdebug`
- RRO: `CarSystemUIScalableUiHmiAppGridHubRRO`

## Use Cases

- demo launcher
- many app trials
- fullscreen app launching

## Panels

- `home_status_panel`: Home Status, `2%,3% - 98%,18%`
- `media_mini_panel`: Media Mini, `2%,82% - 98%,97%`

## Apply This Variant Only

Run from the AAOS checkout root:

```bash
bash workdir/scalableui-poc/scripts/apply_hmi_variant.sh app-grid-hub
lunch sdk_car_scalableui_app_grid_hub_x86_64-trunk_staging-userdebug
```

The script applies common ScalableUI routing patches, the common demo app patch,
the product patch for this variant, and the RRO patch for this variant.

## Notes

- panel_app_grid defaults to opened for this hub-like variant.
