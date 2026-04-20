# Media dock cockpit

## Summary

Media controls are emphasized with a large bottom dock and compact navigation.

## Product

- Product: `sdk_car_scalableui_media_dock_x86_64`
- Lunch: `sdk_car_scalableui_media_dock_x86_64-trunk_staging-userdebug`
- RRO: `CarSystemUIScalableUiHmiMediaDockRRO`

## Use Cases

- audio-first demo
- radio/media comparison
- bottom dock exploration

## Panels

- `map_mini_panel`: Map Mini, `2%,3% - 38%,44%`
- `now_playing_panel`: Now Playing, `40%,3% - 98%,44%`
- `media_dock_panel`: Media Dock, `2%,48% - 98%,97%`

## Apply This Variant Only

Run from the AAOS checkout root:

```bash
bash workdir/scalableui-poc/scripts/apply_hmi_variant.sh media-dock
lunch sdk_car_scalableui_media_dock_x86_64-trunk_staging-userdebug
```

The script applies common ScalableUI routing patches, the common demo app patch,
the product patch for this variant, and the RRO patch for this variant.

## Notes

- No special notes.
