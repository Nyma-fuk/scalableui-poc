# Widget layout lab cockpit

## Summary

A map-first widget cockpit with a hidden right-side widget menu. The menu can launch widget demo apps into named ScalableUI panels and switch between prepared layout patterns that mirror drag-and-drop HMI exploration.

## Product

- Product: `sdk_car_scalableui_widget_layout_lab_x86_64`
- Lunch: `sdk_car_scalableui_widget_layout_lab_x86_64-trunk_staging-userdebug`
- RRO: `CarSystemUIScalableUiHmiWidgetLayoutLabRRO`

## Use Cases

- map plus calendar and weather first screen
- right-side widget picker overlay
- predefined widget placement pattern switching
- drag-and-drop style widget evaluation

## Panels

- `lab_background_panel`: Lab Background, `0,0 - 100%,100%`
- `widget_a_panel`: Widget A Map, `4%,7% - 48%,86%`
- `widget_b_panel`: Widget B Calendar, `52%,7% - 96%,20%`
- `widget_c_panel`: Widget C Weather, `52%,23% - 96%,36%`
- `widget_d_panel`: Widget D Media, `0,100% - 30%,130%`
- `widget_e_panel`: Widget E Tasks, `0,100% - 30%,130%`
- `widget_f_panel`: Widget F Interactive, `0,100% - 30%,130%`
- `widget_drop_zone_panel`: Widget Drop Zone, `44%,82% - 50%,92%`
- `widget_menu_button_panel`: Widget Menu Button, `91%,82% - 97%,92%`
- `widget_picker_panel`: Hidden Widget Picker, `73%,0 - 100%,100%`

## Apply This Variant Only

Run from the AAOS checkout root:

```bash
bash workdir/scalableui-poc/scripts/apply_hmi_variant.sh widget-layout-lab
lunch sdk_car_scalableui_widget_layout_lab_x86_64-trunk_staging-userdebug
```

The script applies common ScalableUI routing patches, the common demo app patch,
the product patch for this variant, and the RRO patch for this variant.

## Notes

- The right-side Widget Layout button launches the picker and a temporary drop zone.
- Pattern buttons dispatch ScalableUI custom events through the SystemUI broadcast bridge.
- Drag source cards use Android global drag data; dropping on the drop zone applies a prepared layout pattern.
