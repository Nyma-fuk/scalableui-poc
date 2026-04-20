# Productivity assistant dashboard

## Summary

Calendar, tasks, phone, and map are arranged as a parked or pre-drive assistant view.

## Product

- Product: `sdk_car_scalableui_productivity_dashboard_x86_64`
- Lunch: `sdk_car_scalableui_productivity_dashboard_x86_64-trunk_staging-userdebug`
- RRO: `CarSystemUIScalableUiHmiProductivityDashboardRRO`

## Use Cases

- calendar/task review
- fleet workflow
- communication demo

## Panels

- `calendar_panel`: Calendar, `2%,3% - 49%,48%`
- `task_panel`: Tasks, `51%,3% - 98%,48%`
- `map_mini_panel`: Map Mini, `2%,52% - 49%,97%`
- `phone_panel`: Phone, `51%,52% - 98%,97%`

## Apply This Variant Only

Run from the AAOS checkout root:

```bash
bash workdir/scalableui-poc/scripts/apply_hmi_variant.sh productivity-dashboard
lunch sdk_car_scalableui_productivity_dashboard_x86_64-trunk_staging-userdebug
```

The script applies common ScalableUI routing patches, the common demo app patch,
the product patch for this variant, and the RRO patch for this variant.

## Notes

- Use this variant mostly for parked or pre-drive evaluation.
