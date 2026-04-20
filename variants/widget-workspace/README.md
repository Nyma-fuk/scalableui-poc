# Widget workspace cockpit

## Summary

An interactive left menu launches map, G Ball, widget, media, and task apps into one ScalableUI workspace panel so users can swap the panel content at runtime.

## Product

- Product: `sdk_car_scalableui_widget_workspace_x86_64`
- Lunch: `sdk_car_scalableui_widget_workspace_x86_64-trunk_staging-userdebug`
- RRO: `CarSystemUIScalableUiHmiWidgetWorkspaceRRO`

## Use Cases

- runtime panel app swapping
- widget interaction demo
- map and G Ball sample validation

## Panels

- `panel_menu`: Panel Menu, `2%,3% - 22%,97%`
- `workspace_panel`: Interactive Workspace, `24%,3% - 98%,68%`
- `widget_controls_panel`: Widget Controls, `24%,72% - 60%,97%`
- `workspace_status_panel`: Workspace Status, `62%,72% - 98%,97%`

## Apply This Variant Only

Run from the AAOS checkout root:

```bash
bash workdir/scalableui-poc/scripts/apply_hmi_variant.sh widget-workspace
lunch sdk_car_scalableui_widget_workspace_x86_64-trunk_staging-userdebug
```

The script applies common ScalableUI routing patches, the common demo app patch,
the product patch for this variant, and the RRO patch for this variant.

## Notes

- workspace_panel uses a role string-array so multiple apps can be routed to one panel.
- Panel Menu starts the selected component; ScalableUI routes it into workspace_panel.
