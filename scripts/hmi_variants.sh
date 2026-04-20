#!/bin/bash

HMI_VARIANTS=(
  "fixed-3zone|sdk_car_scalableui_fixed_3zone_x86_64"
  "map-first|sdk_car_scalableui_map_first_x86_64"
  "media-dock|sdk_car_scalableui_media_dock_x86_64"
  "productivity-dashboard|sdk_car_scalableui_productivity_dashboard_x86_64"
  "app-with-rail|sdk_car_scalableui_app_with_rail_x86_64"
  "floating-card|sdk_car_scalableui_floating_card_x86_64"
  "app-grid-hub|sdk_car_scalableui_app_grid_hub_x86_64"
  "calm-mode|sdk_car_scalableui_calm_mode_x86_64"
  "parking-mode|sdk_car_scalableui_parking_mode_x86_64"
  "developer-cockpit|sdk_car_scalableui_developer_cockpit_x86_64"
  "dual-display|sdk_car_scalableui_dual_display_x86_64"
  "showcase-modes|sdk_car_scalableui_showcase_modes_x86_64"
  "widget-workspace|sdk_car_scalableui_widget_workspace_x86_64"
)

find_hmi_product() {
  local requested="$1"
  local entry slug product
  for entry in "${HMI_VARIANTS[@]}"; do
    IFS="|" read -r slug product <<<"$entry"
    if [[ "$requested" == "$slug" || "$requested" == "$product" ]]; then
      echo "$slug|$product"
      return 0
    fi
  done
  return 1
}

print_hmi_variants() {
  local entry slug product
  for entry in "${HMI_VARIANTS[@]}"; do
    IFS="|" read -r slug product <<<"$entry"
    printf '  %-24s %s\n' "$slug" "$product"
  done
}

hmi_rro_module_for_slug() {
  case "$1" in
    fixed-3zone) echo "CarSystemUIScalableUiHmiFixed3zoneRRO" ;;
    map-first) echo "CarSystemUIScalableUiHmiMapFirstRRO" ;;
    media-dock) echo "CarSystemUIScalableUiHmiMediaDockRRO" ;;
    productivity-dashboard) echo "CarSystemUIScalableUiHmiProductivityDashboardRRO" ;;
    app-with-rail) echo "CarSystemUIScalableUiHmiAppWithRailRRO" ;;
    floating-card) echo "CarSystemUIScalableUiHmiFloatingCardRRO" ;;
    app-grid-hub) echo "CarSystemUIScalableUiHmiAppGridHubRRO" ;;
    calm-mode) echo "CarSystemUIScalableUiHmiCalmModeRRO" ;;
    parking-mode) echo "CarSystemUIScalableUiHmiParkingModeRRO" ;;
    developer-cockpit) echo "CarSystemUIScalableUiHmiDeveloperCockpitRRO" ;;
    dual-display) echo "CarSystemUIScalableUiHmiDualDisplayRRO" ;;
    showcase-modes) echo "CarSystemUIScalableUiHmiShowcaseModesRRO" ;;
    widget-workspace) echo "CarSystemUIScalableUiHmiWidgetWorkspaceRRO" ;;
    *) return 1 ;;
  esac
}
