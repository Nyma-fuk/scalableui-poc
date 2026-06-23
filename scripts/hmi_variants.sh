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
  "editable-home|sdk_car_scalableui_editable_home_x86_64"
  "widget-layout-lab|sdk_car_scalableui_widget_layout_lab_x86_64"
  "dynamic-workspace|sdk_car_scalableui_dynamic_workspace_x86_64"
  "declarative-multipanel|sdk_car_scalableui_declarative_multipanel_x86_64"
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
    editable-home) echo "CarSystemUIScalableUiHmiEditableHomeRRO" ;;
    widget-layout-lab) echo "CarSystemUIScalableUiHmiWidgetLayoutLabRRO" ;;
    dynamic-workspace) echo "CarSystemUIScalableUiHmiDynamicWorkspaceRRO" ;;
    declarative-multipanel) echo "CarSystemUIScalableUiDeclarativeMultipanelRRO" ;;
    *) return 1 ;;
  esac
}

hmi_variant_uses_common_runtime_patches() {
  case "$1" in
    declarative-multipanel) return 1 ;;
    *) return 0 ;;
  esac
}

hmi_demo_app_modules() {
  printf '%s\n' \
    ScalableUiHmiFrameworkConfigRRO \
    ScalableUiHmiHomeDemoApp \
    ScalableUiHmiMapDemoApp \
    ScalableUiHmiGBallDemoApp \
    ScalableUiHmiWidgetsDemoApp \
    ScalableUiHmiCalendarDemoApp \
    ScalableUiHmiWeatherDemoApp \
    ScalableUiHmiWidgetMenuDemoApp \
    ScalableUiHmiWidgetMenuButtonDemoApp \
    ScalableUiHmiWidgetDropZoneDemoApp \
    ScalableUiHmiPanelMenuDemoApp \
    ScalableUiHmiPanelMenuButtonDemoApp \
    ScalableUiHmiTasksDemoApp \
    ScalableUiHmiPhoneDemoApp \
    ScalableUiHmiMediaDemoApp \
    ScalableUiHmiStatusDemoApp \
    ScalableUiHmiControlsDemoApp \
    ScalableUiHmiShortcutsDemoApp \
    ScalableUiHmiEnergyDemoApp \
    ScalableUiHmiSettingsDemoApp \
    ScalableUiHmiDebugDemoApp \
    ScalableUiHmiPassengerDemoApp \
    ScalableUiHmiCalmDemoApp
}

hmi_build_modules_for_slug() {
  local slug="$1"
  if [[ "$slug" == "declarative-multipanel" ]]; then
    printf '%s\n' \
      CarSystemUI \
      CarFrameworkScalableUiDeclarativeMultipanelRRO \
      CarServiceScalableUiDeclarativeMultipanelRRO \
      CarSystemUIScalableUiDeclarativeMultipanelRRO \
      StubCarLauncher
  fi
  if hmi_variant_uses_common_runtime_patches "$slug"; then
    hmi_demo_app_modules
  fi
  hmi_rro_module_for_slug "$slug"
}
