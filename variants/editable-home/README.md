# Editable multipanel home

## Summary

A ScalableUI-based multipanel home keeps system bars outside the managed area, lets the user choose L1/L2/L3 layouts plus per-panel apps, and restores the saved assignment on the next Home entry.

## Product

- Product: `sdk_car_scalableui_editable_home_x86_64`
- Lunch: `sdk_car_scalableui_editable_home_x86_64-trunk_staging-userdebug`
- RRO: `CarSystemUIScalableUiHmiEditableHomeRRO`

## Use Cases

- multipanel home host evaluation
- layout preset switching with persistence
- user-selected panel app assignment
- system-bar-safe content area validation

## Panels

- `home_panel_primary`: Home Primary, `4%,12% - 62%,84%`
- `home_panel_secondary_top`: Home Secondary Top, `64%,12% - 96%,46%`
- `home_panel_secondary_bottom`: Home Secondary Bottom, `64%,50% - 96%,84%`
- `home_edit_overlay`: Home Edit Overlay, `3%,10% - 97%,88%`

## Apply This Variant Only

Run from the AAOS checkout root:

```bash
bash workdir/scalableui-poc/scripts/apply_hmi_variant.sh editable-home
lunch sdk_car_scalableui_editable_home_x86_64-trunk_staging-userdebug
```

The script applies common ScalableUI routing patches, the common demo app patch,
the product patch for this variant, and the RRO patch for this variant.

## Notes

- The managed Home content area is inset so top bar and nav bar remain visible.
- HomeEditActivity stores layout id and per-panel assignment in SharedPreferences.
- Duplicate assignments are rejected when the user presses Save.
- The edit overlay is a ScalableUI decor panel; the editor UI itself opens inside app_panel.
