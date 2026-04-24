# Widget workspace cockpit

## Summary

A compact Panel Control button reveals a hidden runtime menu. Users choose a destination panel, then choose which demo app should appear in that panel.

## Product

- Product: `sdk_car_scalableui_widget_workspace_x86_64`
- Lunch: `sdk_car_scalableui_widget_workspace_x86_64-trunk_staging-userdebug`
- RRO: `CarSystemUIScalableUiHmiWidgetWorkspaceRRO`

## Use Cases

- user-selected panel app swapping
- hidden runtime HMI control menu
- widget interaction demo
- map and G Ball sample validation

## Panels

- `panel_menu_button`: Panel Control Button, `2%,3% - 11%,12%`
- `panel_menu`: Hidden Panel Menu, `2%,14% - 34%,88%`
- `workspace_panel`: Interactive Workspace, `13%,3% - 98%,68%`
- `widget_controls_panel`: Widget Controls, `13%,72% - 55%,97%`
- `workspace_status_panel`: Workspace Status, `57%,72% - 98%,97%`

## Apply This Variant Only

Run from the AAOS checkout root:

```bash
bash workdir/scalableui-poc/scripts/apply_hmi_variant.sh widget-workspace
lunch sdk_car_scalableui_widget_workspace_x86_64-trunk_staging-userdebug
```

The script applies common ScalableUI routing patches, the common demo app patch,
the product patch for this variant, and the RRO patch for this variant.

## Notes

- Panel Control opens the hidden menu only when the user asks for it.
- Panel Menu adds a target panel extra so SystemUI can route the selected app to the requested panel.
- All Apps launches are kept separate and should open in the fullscreen app_panel.
