#!/usr/bin/env python3
"""Generate ScalableUI HMI variant docs and patch packs.

The generated patch files are intentionally plain `git apply` patches so the
public repo can be used from a clean AAOS15 checkout without requiring this
script at apply time.
"""

from __future__ import annotations

import difflib
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent


REPO = Path(__file__).resolve().parents[1]
AAOS_ROOT = REPO.parents[1]

@dataclass(frozen=True)
class DemoApp:
    key: str
    module: str
    package: str
    activity: str
    label: str
    kind: str

    @property
    def component(self) -> str:
        return f"{self.package}/.{self.activity}"


DEMO_APPS: tuple[DemoApp, ...] = (
    DemoApp("home", "ScalableUiHmiHomeDemoApp", "com.android.car.scalableui.hmi.home", "HomeActivity", "ScalableUI Home", "HOME"),
    DemoApp("map", "ScalableUiHmiMapDemoApp", "com.android.car.scalableui.hmi.map", "MapActivity", "ScalableUI Map", "MAP"),
    DemoApp("gball", "ScalableUiHmiGBallDemoApp", "com.android.car.scalableui.hmi.gball", "GBallActivity", "G Ball", "GBALL"),
    DemoApp("widgets", "ScalableUiHmiWidgetsDemoApp", "com.android.car.scalableui.hmi.widgets", "WidgetActivity", "ScalableUI Widgets", "WIDGET"),
    DemoApp("calendar_demo", "ScalableUiHmiCalendarDemoApp", "com.android.car.scalableui.hmi.calendar", "CalendarActivity", "Widget B Calendar", "CALENDAR"),
    DemoApp("weather_demo", "ScalableUiHmiWeatherDemoApp", "com.android.car.scalableui.hmi.weather", "WeatherActivity", "Widget C Weather", "WEATHER"),
    DemoApp("widget_menu", "ScalableUiHmiWidgetMenuDemoApp", "com.android.car.scalableui.hmi.widgetmenu", "WidgetMenuActivity", "Widget Layout Menu", "WIDGET_MENU"),
    DemoApp("widget_menu_button", "ScalableUiHmiWidgetMenuButtonDemoApp", "com.android.car.scalableui.hmi.widgetmenubutton", "WidgetMenuButtonActivity", "Widget Layout", "WIDGET_MENU_BUTTON"),
    DemoApp("widget_dropzone", "ScalableUiHmiWidgetDropZoneDemoApp", "com.android.car.scalableui.hmi.widgetdropzone", "WidgetDropZoneActivity", "Widget Drop Zone", "WIDGET_DROP_ZONE"),
    DemoApp("panel_menu", "ScalableUiHmiPanelMenuDemoApp", "com.android.car.scalableui.hmi.panelmenu", "PanelMenuActivity", "ScalableUI Panel Menu", "PANEL_MENU"),
    DemoApp("panel_menu_button", "ScalableUiHmiPanelMenuButtonDemoApp", "com.android.car.scalableui.hmi.panelmenubutton", "PanelMenuButtonActivity", "Panel Control", "PANEL_MENU_BUTTON"),
    DemoApp("tasks", "ScalableUiHmiTasksDemoApp", "com.android.car.scalableui.hmi.tasks", "TaskActivity", "ScalableUI Tasks", "INFO"),
    DemoApp("phone", "ScalableUiHmiPhoneDemoApp", "com.android.car.scalableui.hmi.phone", "PhoneActivity", "ScalableUI Phone", "INFO"),
    DemoApp("media", "ScalableUiHmiMediaDemoApp", "com.android.car.scalableui.hmi.media", "MediaActivity", "ScalableUI Media", "INFO"),
    DemoApp("status", "ScalableUiHmiStatusDemoApp", "com.android.car.scalableui.hmi.status", "StatusActivity", "ScalableUI Status", "INFO"),
    DemoApp("controls", "ScalableUiHmiControlsDemoApp", "com.android.car.scalableui.hmi.controls", "ControlsActivity", "ScalableUI Controls", "INFO"),
    DemoApp("shortcuts", "ScalableUiHmiShortcutsDemoApp", "com.android.car.scalableui.hmi.shortcuts", "ShortcutsActivity", "ScalableUI Shortcuts", "INFO"),
    DemoApp("energy", "ScalableUiHmiEnergyDemoApp", "com.android.car.scalableui.hmi.energy", "EnergyActivity", "ScalableUI Energy", "INFO"),
    DemoApp("settings", "ScalableUiHmiSettingsDemoApp", "com.android.car.scalableui.hmi.settings", "SettingsActivity", "ScalableUI Settings", "INFO"),
    DemoApp("debug", "ScalableUiHmiDebugDemoApp", "com.android.car.scalableui.hmi.debug", "DebugActivity", "ScalableUI Debug", "INFO"),
    DemoApp("passenger", "ScalableUiHmiPassengerDemoApp", "com.android.car.scalableui.hmi.passenger", "PassengerActivity", "ScalableUI Passenger", "INFO"),
    DemoApp("calm", "ScalableUiHmiCalmDemoApp", "com.android.car.scalableui.hmi.calm", "CalmActivity", "ScalableUI Calm", "INFO"),
)

DEMO_BY_KEY = {app.key: app for app in DEMO_APPS}
COMMON_HMI_PACKAGES: tuple[str, ...] = ("ScalableUiHmiFrameworkConfigRRO",)
DEMO_ACTIVITY_TO_KEY = {
    "MapPanelActivity": "map",
    "GBallActivity": "gball",
    "WidgetPanelActivity": "widgets",
    "CalendarDemoActivity": "calendar_demo",
    "WeatherDemoActivity": "weather_demo",
    "WidgetMenuActivity": "widget_menu",
    "WidgetMenuButtonActivity": "widget_menu_button",
    "WidgetDropZoneActivity": "widget_dropzone",
    "PanelMenuActivity": "panel_menu",
    "PanelMenuButtonActivity": "panel_menu_button",
    "TaskPanelActivity": "tasks",
    "PhonePanelActivity": "phone",
    "MediaPanelActivity": "media",
    "StatusPanelActivity": "status",
    "ControlsPanelActivity": "controls",
    "ShortcutsPanelActivity": "shortcuts",
    "EnergyPanelActivity": "energy",
    "SettingsPanelActivity": "settings",
    "DebugPanelActivity": "debug",
    "PassengerPanelActivity": "passenger",
    "CalmPanelActivity": "calm",
}

MAP_COMPONENT = DEMO_BY_KEY["map"].component
GBALL_COMPONENT = DEMO_BY_KEY["gball"].component
WIDGET_COMPONENT = DEMO_BY_KEY["widgets"].component
CALENDAR_DEMO_COMPONENT = DEMO_BY_KEY["calendar_demo"].component
WEATHER_DEMO_COMPONENT = DEMO_BY_KEY["weather_demo"].component
WIDGET_MENU_COMPONENT = DEMO_BY_KEY["widget_menu"].component
WIDGET_MENU_BUTTON_COMPONENT = DEMO_BY_KEY["widget_menu_button"].component
WIDGET_DROP_ZONE_COMPONENT = DEMO_BY_KEY["widget_dropzone"].component
PANEL_MENU_COMPONENT = DEMO_BY_KEY["panel_menu"].component
PANEL_MENU_BUTTON_COMPONENT = DEMO_BY_KEY["panel_menu_button"].component
CALENDAR_COMPONENT = "com.android.calendar/.AllInOneActivity"
RADIO_COMPONENT = "com.android.car.radio/.RadioActivity"
APP_GRID_COMPONENT = "com.android.car.carlauncher/.AppGridActivity"


@dataclass(frozen=True)
class PanelVariant:
    variant_id: str
    bounds: tuple[str, str, str, str]
    visible: bool = True
    alpha: str | None = None
    corner: str | None = None


@dataclass(frozen=True)
class PanelTransition:
    event: str
    to_variant: str
    tokens: str | None = None
    duration: str | None = None


@dataclass(frozen=True)
class Panel:
    panel_id: str
    title: str
    component: str | tuple[str, ...] | None
    bounds: tuple[str, str, str, str]
    layer: int
    role_kind: str = "activity"
    display_id: int = 0
    corner: str | None = "18dp"
    background: str | None = None
    default_open: bool = True
    default_launch: bool = True
    close_on_task_open: bool = False
    closed_bounds: tuple[str, str, str, str] = ("0", "100%", "100%", "200%")
    opened_alpha: str | None = None
    closed_alpha: str | None = None
    extra_variants: tuple[PanelVariant, ...] = ()
    extra_transitions: tuple[PanelTransition, ...] = ()


@dataclass(frozen=True)
class Variant:
    slug: str
    title: str
    product_suffix: str
    summary: str
    use_cases: tuple[str, ...]
    panels: tuple[Panel, ...]
    notes: tuple[str, ...] = ()
    app_panel_bounds: tuple[str, str, str, str] | None = None
    app_grid_bounds: tuple[str, str, str, str] | None = None

    @property
    def product_name(self) -> str:
        return f"sdk_car_scalableui_{self.product_suffix}_x86_64"

    @property
    def car_product_dir(self) -> str:
        return f"scalableui_hmi_{self.product_suffix}"

    @property
    def rro_name(self) -> str:
        return "CarSystemUIScalableUiHmi" + "".join(
            part.capitalize() for part in self.product_suffix.split("_")
        ) + "RRO"


def demo_activity(name: str) -> str:
    try:
        return DEMO_BY_KEY[DEMO_ACTIVITY_TO_KEY[name]].component
    except KeyError as exc:
        raise ValueError(f"Unknown demo activity: {name}") from exc


def normalize_alpha(value: str | None) -> str | None:
    if value is None:
        return None
    try:
        parsed = float(value)
    except ValueError:
        return value
    if "." in value or "e" in value.lower():
        return value
    return f"{parsed:.1f}"


VARIANTS: tuple[Variant, ...] = (
    Variant(
        slug="fixed-3zone",
        title="Fixed 3-zone cockpit",
        product_suffix="fixed_3zone",
        summary="Map, calendar, and radio are always visible in a stable 3-zone layout.",
        use_cases=("baseline cockpit", "navigation with schedule", "radio demo"),
        panels=(
            Panel("map_panel", "Map", MAP_COMPONENT, ("2%", "3%", "58%", "97%"), 20),
            Panel("calendar_panel", "Calendar", CALENDAR_COMPONENT, ("60%", "3%", "98%", "48%"), 30),
            Panel("radio_panel", "Radio", RADIO_COMPONENT, ("60%", "52%", "98%", "97%"), 25),
        ),
    ),
    Variant(
        slug="map-first",
        title="Map-first navigation cockpit",
        product_suffix="map_first",
        summary="The map owns most of the display while a narrow right rail shows glanceable context.",
        use_cases=("wide navigation", "ETA/status rail", "route guidance demo"),
        panels=(
            Panel("map_panel", "Wide Map", MAP_COMPONENT, ("2%", "3%", "72%", "97%"), 20),
            Panel("event_panel", "Next Event", CALENDAR_COMPONENT, ("74%", "3%", "98%", "31%"), 30),
            Panel("media_mini_panel", "Media Mini", demo_activity("MediaPanelActivity"), ("74%", "35%", "98%", "64%"), 31),
            Panel("status_panel", "Vehicle Status", demo_activity("StatusPanelActivity"), ("74%", "68%", "98%", "97%"), 32),
        ),
    ),
    Variant(
        slug="media-dock",
        title="Media dock cockpit",
        product_suffix="media_dock",
        summary="Media controls are emphasized with a large bottom dock and compact navigation.",
        use_cases=("audio-first demo", "radio/media comparison", "bottom dock exploration"),
        panels=(
            Panel("map_mini_panel", "Map Mini", MAP_COMPONENT, ("2%", "3%", "38%", "44%"), 20),
            Panel("now_playing_panel", "Now Playing", demo_activity("MediaPanelActivity"), ("40%", "3%", "98%", "44%"), 30),
            Panel("media_dock_panel", "Media Dock", demo_activity("ControlsPanelActivity"), ("2%", "48%", "98%", "97%"), 35),
        ),
    ),
    Variant(
        slug="productivity-dashboard",
        title="Productivity assistant dashboard",
        product_suffix="productivity_dashboard",
        summary="Calendar, tasks, phone, and map are arranged as a parked or pre-drive assistant view.",
        use_cases=("calendar/task review", "fleet workflow", "communication demo"),
        panels=(
            Panel("calendar_panel", "Calendar", CALENDAR_COMPONENT, ("2%", "3%", "49%", "48%"), 30),
            Panel("task_panel", "Tasks", demo_activity("TaskPanelActivity"), ("51%", "3%", "98%", "48%"), 31),
            Panel("map_mini_panel", "Map Mini", MAP_COMPONENT, ("2%", "52%", "49%", "97%"), 20),
            Panel("phone_panel", "Phone", demo_activity("PhonePanelActivity"), ("51%", "52%", "98%", "97%"), 32),
        ),
        notes=("Use this variant mostly for parked or pre-drive evaluation.",),
    ),
    Variant(
        slug="app-with-rail",
        title="Fullscreen app with persistent rail",
        product_suffix="app_with_rail",
        summary="A large app workspace remains available while a side rail keeps shortcuts and status visible.",
        use_cases=("tablet-like app mode", "persistent shortcuts", "fullscreen routing study"),
        panels=(
            Panel("rail_shortcuts_panel", "Shortcuts", demo_activity("ShortcutsPanelActivity"), ("82%", "3%", "98%", "31%"), 40),
            Panel("rail_media_panel", "Media Mini", demo_activity("MediaPanelActivity"), ("82%", "35%", "98%", "64%"), 41),
            Panel("rail_status_panel", "Status", demo_activity("StatusPanelActivity"), ("82%", "68%", "98%", "97%"), 42),
        ),
        notes=("The DEFAULT app_panel opens in the left 80% instead of covering the rail.",),
    ),
    Variant(
        slug="floating-card",
        title="Floating card HMI",
        product_suffix="floating_card",
        summary="A full-screen map/background is combined with floating rounded cards.",
        use_cases=("modern floating UI", "map card exploration", "ambient cockpit"),
        panels=(
            Panel("map_background_panel", "Map Background", MAP_COMPONENT, ("0", "0", "100%", "100%"), 10, corner=None),
            Panel("primary_card_panel", "Primary Card", CALENDAR_COMPONENT, ("8%", "12%", "55%", "52%"), 40, corner="28dp"),
            Panel("secondary_card_panel", "Secondary Card", demo_activity("MediaPanelActivity"), ("58%", "58%", "94%", "90%"), 41, corner="28dp"),
        ),
    ),
    Variant(
        slug="app-grid-hub",
        title="App grid hub",
        product_suffix="app_grid_hub",
        summary="All apps is treated as the central hub and launched apps are routed to fullscreen.",
        use_cases=("demo launcher", "many app trials", "fullscreen app launching"),
        panels=(
            Panel("home_status_panel", "Home Status", demo_activity("StatusPanelActivity"), ("2%", "3%", "98%", "18%"), 20),
            Panel("media_mini_panel", "Media Mini", demo_activity("MediaPanelActivity"), ("2%", "82%", "98%", "97%"), 21),
        ),
        notes=("panel_app_grid defaults to opened for this hub-like variant.",),
    ),
    Variant(
        slug="calm-mode",
        title="Calm mode minimal HMI",
        product_suffix="calm_mode",
        summary="Information density is reduced to map, media mini, and small status surfaces.",
        use_cases=("low distraction demo", "focus mode", "normal vs calm comparison"),
        panels=(
            Panel("map_panel", "Calm Map", MAP_COMPONENT, ("4%", "6%", "96%", "78%"), 20, corner="26dp"),
            Panel("media_mini_panel", "Media Mini", demo_activity("MediaPanelActivity"), ("4%", "82%", "58%", "96%"), 25, corner="22dp"),
            Panel("status_panel", "Status", demo_activity("StatusPanelActivity"), ("62%", "82%", "96%", "96%"), 26, corner="22dp"),
        ),
    ),
    Variant(
        slug="parking-mode",
        title="Parking and charging dashboard",
        product_suffix="parking_mode",
        summary="Parking and charging use cases get a dense dashboard with energy, media, settings, and shortcuts.",
        use_cases=("charging dashboard", "parked app mode", "energy/status demo"),
        panels=(
            Panel("energy_panel", "Energy", demo_activity("EnergyPanelActivity"), ("2%", "3%", "49%", "48%"), 30),
            Panel("media_panel", "Media", demo_activity("MediaPanelActivity"), ("51%", "3%", "98%", "48%"), 31),
            Panel("settings_panel", "Settings", demo_activity("SettingsPanelActivity"), ("2%", "52%", "49%", "97%"), 32),
            Panel("shortcuts_panel", "Shortcuts", demo_activity("ShortcutsPanelActivity"), ("51%", "52%", "98%", "97%"), 33),
        ),
        notes=("Vehicle parked/charging event wiring is not included; this is a build-time HMI variant.",),
    ),
    Variant(
        slug="developer-cockpit",
        title="Diagnostics developer cockpit",
        product_suffix="developer_cockpit",
        summary="Debug status, controls, app-under-test, and map/media panels are arranged for PoC validation.",
        use_cases=("developer testbench", "demo operation", "diagnostics visualization"),
        panels=(
            Panel("debug_status_panel", "Debug Status", demo_activity("DebugPanelActivity"), ("2%", "3%", "39%", "48%"), 45),
            Panel("app_under_test_panel", "App Under Test", demo_activity("TaskPanelActivity"), ("41%", "3%", "98%", "48%"), 30),
            Panel("control_panel", "Controls", demo_activity("ControlsPanelActivity"), ("2%", "52%", "39%", "97%"), 46),
            Panel("map_media_panel", "Map Media", MAP_COMPONENT, ("41%", "52%", "98%", "97%"), 20),
        ),
    ),
    Variant(
        slug="dual-display",
        title="Driver and passenger display HMI",
        product_suffix="dual_display",
        summary="Driver and passenger panels are split by displayId for multi-display exploration.",
        use_cases=("multi-display planning", "driver/passenger separation", "target display study"),
        panels=(
            Panel("driver_map_panel", "Driver Map", MAP_COMPONENT, ("2%", "3%", "72%", "97%"), 20, display_id=0),
            Panel("driver_media_panel", "Driver Media", demo_activity("MediaPanelActivity"), ("74%", "3%", "98%", "97%"), 30, display_id=0),
            Panel("passenger_app_panel", "Passenger App", demo_activity("PassengerPanelActivity"), ("0", "0", "100%", "100%"), 20, display_id=1),
        ),
        notes=("Requires a multi-display emulator or target to validate displayId=1 behavior.",),
    ),
    Variant(
        slug="showcase-modes",
        title="Mode-switching showcase",
        product_suffix="showcase_modes",
        summary="A comparison layout keeps normal, calm, and app-focus concepts visible as separate regions.",
        use_cases=("mode comparison", "stakeholder demo", "variant planning"),
        panels=(
            Panel("normal_map_panel", "Normal Map", MAP_COMPONENT, ("2%", "3%", "49%", "48%"), 20),
            Panel("normal_context_panel", "Normal Context", CALENDAR_COMPONENT, ("51%", "3%", "98%", "48%"), 30),
            Panel("calm_preview_panel", "Calm Preview", demo_activity("CalmPanelActivity"), ("2%", "52%", "49%", "97%"), 31),
            Panel("app_focus_preview_panel", "App Focus Preview", demo_activity("TaskPanelActivity"), ("51%", "52%", "98%", "97%"), 32),
        ),
        notes=("This variant is a static showcase; interactive mode buttons can be added later.",),
    ),
    Variant(
        slug="widget-workspace",
        title="Widget workspace cockpit",
        product_suffix="widget_workspace",
        summary=(
            "A compact Panel Control button reveals a hidden runtime menu. Users choose a "
            "destination panel, then choose which demo app should appear in that panel."
        ),
        use_cases=(
            "user-selected panel app swapping",
            "hidden runtime HMI control menu",
            "widget interaction demo",
            "map and G Ball sample validation",
        ),
        panels=(
            Panel(
                "panel_menu_button",
                "Panel Control Button",
                PANEL_MENU_BUTTON_COMPONENT,
                ("2%", "3%", "11%", "12%"),
                62,
                corner="22dp",
            ),
            Panel(
                "panel_menu",
                "Hidden Panel Menu",
                PANEL_MENU_COMPONENT,
                ("2%", "14%", "34%", "88%"),
                205,
                corner="24dp",
                default_open=False,
                default_launch=False,
                close_on_task_open=True,
            ),
            Panel(
                "workspace_panel",
                "Interactive Workspace",
                WIDGET_COMPONENT,
                ("13%", "3%", "98%", "68%"),
                35,
                corner="24dp",
            ),
            Panel(
                "widget_controls_panel",
                "Widget Controls",
                demo_activity("ControlsPanelActivity"),
                ("13%", "72%", "55%", "97%"),
                42,
                corner="22dp",
            ),
            Panel(
                "workspace_status_panel",
                "Workspace Status",
                demo_activity("StatusPanelActivity"),
                ("57%", "72%", "98%", "97%"),
                43,
                corner="22dp",
            ),
        ),
        notes=(
            "Panel Control opens the hidden menu only when the user asks for it.",
            "Panel Menu adds a target panel extra so SystemUI can route the selected app to the requested panel.",
            "All Apps launches are kept separate and should open in the fullscreen app_panel.",
        ),
    ),
    Variant(
        slug="editable-home",
        title="Editable multipanel home",
        product_suffix="editable_home",
        summary=(
            "A ScalableUI-based multipanel home keeps system bars outside the managed area, "
            "lets the user choose L1/L2/L3 layouts plus per-panel apps, and restores the saved "
            "assignment on the next Home entry."
        ),
        use_cases=(
            "multipanel home host evaluation",
            "layout preset switching with persistence",
            "user-selected panel app assignment",
            "system-bar-safe content area validation",
        ),
        panels=(
            Panel(
                "home_panel_primary",
                "Home Primary",
                (
                    MAP_COMPONENT,
                    demo_activity("MediaPanelActivity"),
                    demo_activity("ControlsPanelActivity"),
                    CALENDAR_DEMO_COMPONENT,
                    demo_activity("SettingsPanelActivity"),
                    GBALL_COMPONENT,
                ),
                ("4%", "12%", "62%", "84%"),
                30,
                corner="24dp",
                default_launch=False,
                extra_variants=(
                    PanelVariant("layout_l1", ("4%", "12%", "48%", "84%"), corner="24dp"),
                    PanelVariant("layout_l3", ("4%", "12%", "96%", "50%"), corner="24dp"),
                ),
                extra_transitions=(
                    PanelTransition("_Custom_HomeLayoutChanged", "layout_l1",
                            tokens="panelId=home_root;panelToVariantId=L1"),
                    PanelTransition("_Custom_HomeLayoutChanged", "opened",
                            tokens="panelId=home_root;panelToVariantId=L2"),
                    PanelTransition("_Custom_HomeLayoutChanged", "layout_l3",
                            tokens="panelId=home_root;panelToVariantId=L3"),
                ),
            ),
            Panel(
                "home_panel_secondary_top",
                "Home Secondary Top",
                (
                    MAP_COMPONENT,
                    demo_activity("MediaPanelActivity"),
                    demo_activity("ControlsPanelActivity"),
                    CALENDAR_DEMO_COMPONENT,
                    demo_activity("SettingsPanelActivity"),
                    GBALL_COMPONENT,
                ),
                ("64%", "12%", "96%", "46%"),
                31,
                corner="22dp",
                default_launch=False,
                extra_variants=(
                    PanelVariant("layout_l1", ("52%", "12%", "96%", "84%"), corner="24dp"),
                    PanelVariant("layout_l3", ("4%", "54%", "96%", "84%"), corner="22dp"),
                ),
                extra_transitions=(
                    PanelTransition("_Custom_HomeLayoutChanged", "layout_l1",
                            tokens="panelId=home_root;panelToVariantId=L1"),
                    PanelTransition("_Custom_HomeLayoutChanged", "opened",
                            tokens="panelId=home_root;panelToVariantId=L2"),
                    PanelTransition("_Custom_HomeLayoutChanged", "layout_l3",
                            tokens="panelId=home_root;panelToVariantId=L3"),
                ),
            ),
            Panel(
                "home_panel_secondary_bottom",
                "Home Secondary Bottom",
                (
                    MAP_COMPONENT,
                    demo_activity("MediaPanelActivity"),
                    demo_activity("ControlsPanelActivity"),
                    CALENDAR_DEMO_COMPONENT,
                    demo_activity("SettingsPanelActivity"),
                    GBALL_COMPONENT,
                ),
                ("64%", "50%", "96%", "84%"),
                32,
                corner="22dp",
                default_launch=False,
                closed_alpha="0",
                extra_variants=(
                    PanelVariant("layout_l1", ("100%", "100%", "130%", "130%"),
                            visible=False, alpha="0"),
                    PanelVariant("layout_l3", ("100%", "100%", "130%", "130%"),
                            visible=False, alpha="0"),
                ),
                extra_transitions=(
                    PanelTransition("_Custom_HomeLayoutChanged", "layout_l1",
                            tokens="panelId=home_root;panelToVariantId=L1"),
                    PanelTransition("_Custom_HomeLayoutChanged", "opened",
                            tokens="panelId=home_root;panelToVariantId=L2"),
                    PanelTransition("_Custom_HomeLayoutChanged", "layout_l3",
                            tokens="panelId=home_root;panelToVariantId=L3"),
                ),
            ),
            Panel(
                "home_edit_overlay",
                "Home Edit Overlay",
                None,
                ("3%", "10%", "97%", "88%"),
                160,
                role_kind="decor",
                corner="28dp",
                background="#A60A1320",
                default_open=False,
                default_launch=False,
                closed_alpha="0",
                extra_transitions=(
                    PanelTransition("_Custom_HomeEditModeEntered", "opened"),
                    PanelTransition("_Custom_HomeEditModeExited", "closed"),
                    PanelTransition("_Custom_HomeApplyRequested", "closed"),
                ),
            ),
        ),
        notes=(
            "The managed Home content area is inset so top bar and nav bar remain visible.",
            "HomeEditActivity stores layout id and per-panel assignment in SharedPreferences.",
            "Duplicate assignments are rejected when the user presses Save.",
            "The edit overlay is a ScalableUI decor panel; the editor UI itself opens inside app_panel.",
        ),
        app_panel_bounds=("5%", "11%", "95%", "87%"),
        app_grid_bounds=("3%", "10%", "97%", "88%"),
    ),
    Variant(
        slug="widget-layout-lab",
        title="Widget layout lab cockpit",
        product_suffix="widget_layout_lab",
        summary=(
            "A map-first widget cockpit with a hidden right-side widget menu. The menu can "
            "launch widget demo apps into named ScalableUI panels and switch between prepared "
            "layout patterns that mirror drag-and-drop HMI exploration."
        ),
        use_cases=(
            "map plus calendar and weather first screen",
            "right-side widget picker overlay",
            "predefined widget placement pattern switching",
            "drag-and-drop style widget evaluation",
        ),
        panels=(
            Panel(
                "lab_background_panel",
                "Lab Background",
                None,
                ("0", "0", "100%", "100%"),
                5,
                role_kind="decor",
                corner=None,
                default_launch=False,
            ),
            Panel(
                "widget_a_panel",
                "Widget A Map",
                MAP_COMPONENT,
                ("4%", "7%", "48%", "86%"),
                30,
                corner="10dp",
                extra_variants=(
                    PanelVariant("pattern_two_large", ("4%", "7%", "48%", "86%")),
                    PanelVariant("pattern_split_three", ("4%", "7%", "48%", "86%")),
                    PanelVariant("pattern_swap", ("52%", "7%", "94%", "86%")),
                    PanelVariant("pattern_stack_left", ("52%", "12%", "94%", "88%")),
                ),
                extra_transitions=(
                    PanelTransition("widget_layout_initial", "opened"),
                    PanelTransition("widget_layout_two_large", "pattern_two_large"),
                    PanelTransition("widget_layout_split_three", "pattern_split_three"),
                    PanelTransition("widget_layout_swap", "pattern_swap"),
                    PanelTransition("widget_layout_stack_left", "pattern_stack_left"),
                ),
            ),
            Panel(
                "widget_b_panel",
                "Widget B Calendar",
                CALENDAR_DEMO_COMPONENT,
                ("52%", "7%", "96%", "20%"),
                35,
                corner="8dp",
                extra_variants=(
                    PanelVariant("hidden", ("100%", "100%", "130%", "130%"), visible=False, alpha="0"),
                    PanelVariant("pattern_split_three", ("52%", "7%", "94%", "18%")),
                    PanelVariant("pattern_stack_left", ("8%", "67%", "48%", "76%")),
                ),
                extra_transitions=(
                    PanelTransition("widget_layout_initial", "opened"),
                    PanelTransition("widget_layout_two_large", "hidden"),
                    PanelTransition("widget_layout_split_three", "pattern_split_three"),
                    PanelTransition("widget_layout_swap", "hidden"),
                    PanelTransition("widget_layout_stack_left", "pattern_stack_left"),
                ),
            ),
            Panel(
                "widget_c_panel",
                "Widget C Weather",
                WEATHER_DEMO_COMPONENT,
                ("52%", "23%", "96%", "36%"),
                36,
                corner="8dp",
                extra_variants=(
                    PanelVariant("hidden", ("100%", "100%", "130%", "130%"), visible=False, alpha="0"),
                    PanelVariant("pattern_stack_left", ("8%", "38%", "48%", "47%")),
                ),
                extra_transitions=(
                    PanelTransition("widget_layout_initial", "opened"),
                    PanelTransition("widget_layout_two_large", "hidden"),
                    PanelTransition("widget_layout_split_three", "hidden"),
                    PanelTransition("widget_layout_swap", "hidden"),
                    PanelTransition("widget_layout_stack_left", "pattern_stack_left"),
                ),
            ),
            Panel(
                "widget_d_panel",
                "Widget D Media",
                demo_activity("MediaPanelActivity"),
                ("0", "100%", "30%", "130%"),
                37,
                corner="8dp",
                default_open=False,
                default_launch=False,
                closed_alpha="0",
                extra_variants=(
                    PanelVariant("pattern_split_three", ("51%", "74%", "93%", "86%")),
                    PanelVariant("pattern_stack_left", ("8%", "26%", "48%", "35%")),
                ),
                extra_transitions=(
                    PanelTransition("widget_layout_initial", "closed"),
                    PanelTransition("widget_layout_two_large", "closed"),
                    PanelTransition("widget_layout_split_three", "pattern_split_three"),
                    PanelTransition("widget_layout_swap", "closed"),
                    PanelTransition("widget_layout_stack_left", "pattern_stack_left"),
                ),
            ),
            Panel(
                "widget_e_panel",
                "Widget E Tasks",
                demo_activity("TaskPanelActivity"),
                ("0", "100%", "30%", "130%"),
                38,
                corner="8dp",
                default_open=False,
                default_launch=False,
                closed_alpha="0",
                extra_variants=(
                    PanelVariant("pattern_stack_left", ("8%", "52%", "48%", "61%")),
                ),
                extra_transitions=(
                    PanelTransition("widget_layout_initial", "closed"),
                    PanelTransition("widget_layout_two_large", "closed"),
                    PanelTransition("widget_layout_split_three", "closed"),
                    PanelTransition("widget_layout_swap", "closed"),
                    PanelTransition("widget_layout_stack_left", "pattern_stack_left"),
                ),
            ),
            Panel(
                "widget_f_panel",
                "Widget F Interactive",
                WIDGET_COMPONENT,
                ("0", "100%", "30%", "130%"),
                39,
                corner="10dp",
                default_open=False,
                default_launch=False,
                closed_alpha="0",
                extra_variants=(
                    PanelVariant("pattern_two_large", ("52%", "7%", "94%", "86%")),
                    PanelVariant("pattern_swap", ("4%", "7%", "48%", "86%")),
                ),
                extra_transitions=(
                    PanelTransition("widget_layout_initial", "closed"),
                    PanelTransition("widget_layout_two_large", "pattern_two_large"),
                    PanelTransition("widget_layout_split_three", "closed"),
                    PanelTransition("widget_layout_swap", "pattern_swap"),
                    PanelTransition("widget_layout_stack_left", "closed"),
                ),
            ),
            Panel(
                "widget_drop_zone_panel",
                "Widget Drop Zone",
                WIDGET_DROP_ZONE_COMPONENT,
                ("44%", "82%", "50%", "92%"),
                120,
                corner="18dp",
                default_open=False,
                default_launch=False,
                closed_alpha="0",
                extra_transitions=(
                    PanelTransition("widget_layout_hide_menu", "closed"),
                    PanelTransition("widget_layout_initial", "closed"),
                    PanelTransition("widget_layout_two_large", "closed"),
                    PanelTransition("widget_layout_split_three", "closed"),
                    PanelTransition("widget_layout_swap", "closed"),
                    PanelTransition("widget_layout_stack_left", "closed"),
                ),
            ),
            Panel(
                "widget_menu_button_panel",
                "Widget Menu Button",
                WIDGET_MENU_BUTTON_COMPONENT,
                ("91%", "82%", "97%", "92%"),
                150,
                corner="8dp",
            ),
            Panel(
                "widget_picker_panel",
                "Hidden Widget Picker",
                WIDGET_MENU_COMPONENT,
                ("73%", "0", "100%", "100%"),
                210,
                corner=None,
                default_open=False,
                default_launch=False,
                closed_bounds=("100%", "0", "127%", "100%"),
                closed_alpha="0",
                extra_transitions=(
                    PanelTransition("widget_layout_hide_menu", "closed"),
                    PanelTransition("widget_layout_initial", "closed"),
                    PanelTransition("widget_layout_two_large", "closed"),
                    PanelTransition("widget_layout_split_three", "closed"),
                    PanelTransition("widget_layout_swap", "closed"),
                    PanelTransition("widget_layout_stack_left", "closed"),
                ),
            ),
        ),
        notes=(
            "The right-side Widget Layout button launches the picker and a temporary drop zone.",
            "Pattern buttons dispatch ScalableUI custom events through the SystemUI broadcast bridge.",
            "Drag source cards use Android global drag data; dropping on the drop zone applies a prepared layout pattern.",
        ),
    ),
)


def copyright(prefix: str = "#") -> str:
    if prefix == "#":
        return dedent(
            """\
            #
            # Copyright (C) 2026 The Android Open Source Project
            #
            # Licensed under the Apache License, Version 2.0 (the "License");
            # you may not use this file except in compliance with the License.
            # You may obtain a copy of the License at
            #
            #      http://www.apache.org/licenses/LICENSE-2.0
            #
            # Unless required by applicable law or agreed to in writing, software
            # distributed under the License is distributed on an "AS IS" BASIS,
            # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
            # See the License for the specific language governing permissions and
            # limitations under the License.
            """
        )
    if prefix == "//":
        return dedent(
            """\
            //
            // Copyright (C) 2026 The Android Open Source Project
            //
            // Licensed under the Apache License, Version 2.0 (the "License");
            // you may not use this file except in compliance with the License.
            // You may obtain a copy of the License at
            //
            //      http://www.apache.org/licenses/LICENSE-2.0
            //
            // Unless required by applicable law or agreed to in writing, software
            // distributed under the License is distributed on an "AS IS" BASIS,
            // WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
            // See the License for the specific language governing permissions and
            // limitations under the License.
            //
            """
        )
    raise ValueError(prefix)


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write(path: Path, content: str, mode: int | None = None) -> None:
    ensure_dir(path.parent)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")
    if mode is not None:
        path.chmod(mode)


def new_file_patch(path: str, content: str, mode: str = "100644") -> str:
    content_lines = content.rstrip().splitlines()
    lines = [
        f"diff --git a/{path} b/{path}",
        f"new file mode {mode}",
        "index 0000000..1111111",
        "--- /dev/null",
        f"+++ b/{path}",
        f"@@ -0,0 +1,{len(content_lines)} @@",
    ]
    lines.extend("+" + line for line in content_lines)
    return "\n".join(lines) + "\n"


def modify_patch(path: str, old: str, new: str) -> str:
    diff = difflib.unified_diff(
        old.splitlines(),
        new.splitlines(),
        fromfile=f"a/{path}",
        tofile=f"b/{path}",
        lineterm="",
    )
    body = "\n".join(diff)
    return f"diff --git a/{path} b/{path}\nindex 1111111..2222222 100644\n{body}\n"


def panel_layer_name(panel_id: str) -> str:
    return f"{panel_id}_layer"


def component_string_name(panel_id: str) -> str:
    return f"{panel_id}_componentName"


def component_array_name(panel_id: str) -> str:
    return f"{panel_id}_componentNames"


def default_component(component: str | tuple[str, ...] | None) -> str | None:
    if component is None:
        return None
    if isinstance(component, tuple):
        return component[0] if component else None
    return component


def component_display(component: str | tuple[str, ...] | None, role_kind: str) -> str:
    if component is None:
        return role_kind
    if isinstance(component, tuple):
        return ", ".join(component)
    return component


def panel_xml(panel: Panel, close_when_open_panel_ids: tuple[str, ...] = ()) -> str:
    left, top, right, bottom = panel.bounds
    closed_left, closed_top, closed_right, closed_bottom = panel.closed_bounds
    layer = panel_layer_name(panel.panel_id)
    if panel.role_kind == "decor":
        role = "@layout/scalableui_hmi_decor_panel"
    elif isinstance(panel.component, tuple):
        role = f"@array/{component_array_name(panel.panel_id)}"
    else:
        role = f"@string/{component_string_name(panel.panel_id)}"
    corner = f"\n        <Corner radius=\"{panel.corner}\"/>" if panel.corner else ""
    background = ""
    if panel.background:
        background = f"\n        <Background color=\"{panel.background}\"/>"
    opened_alpha_value = normalize_alpha(panel.opened_alpha)
    closed_alpha_value = normalize_alpha(panel.closed_alpha)
    opened_alpha = f"\n        <Alpha alpha=\"{opened_alpha_value}\"/>" if opened_alpha_value else ""
    closed_alpha = f"\n        <Alpha alpha=\"{closed_alpha_value}\"/>" if closed_alpha_value else ""
    default_variant = "opened" if panel.default_open else "closed"
    extra_variants = ""
    for variant in panel.extra_variants:
        v_left, v_top, v_right, v_bottom = variant.bounds
        v_corner = variant.corner if variant.corner is not None else panel.corner
        extra_variants += f"""
    <Variant id="@+id/{variant.variant_id}">
        <Layer layer="@integer/{layer}"/>
        <Visibility isVisible="{str(variant.visible).lower()}"/>
        <Bounds left="{v_left}" top="{v_top}" right="{v_right}" bottom="{v_bottom}"/>"""
        if v_corner:
            extra_variants += f"""
        <Corner radius="{v_corner}"/>"""
        if panel.background:
            extra_variants += background
        variant_alpha = normalize_alpha(variant.alpha)
        if variant_alpha:
            extra_variants += f"""
        <Alpha alpha="{variant_alpha}"/>"""
        extra_variants += """
    </Variant>"""
    transitions = ""
    if not panel.default_open or panel.close_on_task_open or panel.extra_transitions:
        close_on_task_open = ""
        if panel.close_on_task_open:
            close_on_task_open = "\n".join(
                f'        <Transition onEvent="_System_TaskOpenEvent" onEventTokens="panelId={panel_id}" toVariant="@id/closed"/>'
                for panel_id in close_when_open_panel_ids
            )
            if close_on_task_open:
                close_on_task_open = "\n" + close_on_task_open
        custom_transitions = ""
        if panel.extra_transitions:
            transition_lines: list[str] = []
            for transition in panel.extra_transitions:
                tokens = f' onEventTokens="{transition.tokens}"' if transition.tokens else ""
                duration = f' duration="{transition.duration}"' if transition.duration else ""
                transition_lines.append(
                    f'        <Transition onEvent="{transition.event}"{tokens}{duration} '
                    f'toVariant="@id/{transition.to_variant}"/>'
                )
            custom_transitions = "\n".join(transition_lines)
            custom_transitions = "\n" + custom_transitions
        transitions = f"""
    <Transitions>
        <Transition onEvent="_System_TaskOpenEvent" onEventTokens="panelId={panel.panel_id}" toVariant="@id/opened"/>
        <Transition onEvent="_System_TaskCloseEvent" onEventTokens="panelId={panel.panel_id}" toVariant="@id/closed"/>
        <Transition onEvent="_System_OnHomeEvent" toVariant="@id/closed"/>
        <Transition onEvent="close_{panel.panel_id}" toVariant="@id/closed"/>{close_on_task_open}{custom_transitions}
    </Transitions>"""
    return dedent(
        f"""\
<?xml version="1.0" encoding="utf-8"?>
<Panel id="{panel.panel_id}" defaultVariant="@id/{default_variant}" role="{role}" displayId="{panel.display_id}">
    <Variant id="@+id/opened">
        <Layer layer="@integer/{layer}"/>
        <Visibility isVisible="true"/>
        <Bounds left="{left}" top="{top}" right="{right}" bottom="{bottom}"/>{corner}{background}{opened_alpha}
    </Variant>
    <Variant id="@+id/closed">
        <Layer layer="@integer/{layer}"/>
        <Visibility isVisible="false"/>
        <Bounds left="{closed_left}" top="{closed_top}" right="{closed_right}" bottom="{closed_bottom}"/>{closed_alpha}
    </Variant>{extra_variants}
{transitions}
</Panel>
"""
    )


def app_panel_xml(variant: Variant) -> str:
    if variant.app_panel_bounds is not None:
        left, top, right, bottom = variant.app_panel_bounds
        bounds = f'left="{left}" top="{top}" right="{right}" bottom="{bottom}"'
    elif variant.slug == "app-with-rail":
        bounds = 'left="0" top="0" right="80%" bottom="100%"'
    else:
        bounds = 'left="0" top="0" right="100%" bottom="100%"'
    close_transitions = "\n".join(
        f'        <Transition onEvent="_System_TaskOpenEvent" onEventTokens="panelId={p.panel_id}" toVariant="@id/closed"/>'
        for p in variant.panels
    )
    return dedent(
        f"""\
        <?xml version="1.0" encoding="utf-8"?>
        <Panel id="app_panel" defaultVariant="@id/closed" role="@string/default_config" displayId="0">
            <Variant id="@+id/opened">
                <Layer layer="@integer/app_panel_layer"/>
                <Visibility isVisible="true"/>
                <Bounds {bounds}/>
            </Variant>
            <Variant id="@+id/closed">
                <Layer layer="@integer/app_panel_layer"/>
                <Visibility isVisible="false"/>
                <Bounds left="0" top="100%" right="100%" bottom="200%"/>
            </Variant>
            <Transitions>
                <Transition onEvent="_System_TaskOpenEvent" onEventTokens="panelId=app_panel" toVariant="@id/opened"/>
                <Transition onEvent="_System_TaskOpenEvent" onEventTokens="panelId=panel_app_grid" toVariant="@id/closed"/>
{close_transitions}
                <Transition onEvent="_System_OnHomeEvent" toVariant="@id/closed"/>
                <Transition onEvent="_System_TaskCloseEvent" onEventTokens="panelId=app_panel" toVariant="@id/closed"/>
            </Transitions>
        </Panel>
        """
    )


def app_grid_xml(variant: Variant, default_open: bool = False) -> str:
    default = "opened" if default_open else "closed"
    bounds = 'left="0" top="0" right="100%" bottom="100%"'
    if variant.app_grid_bounds is not None:
        left, top, right, bottom = variant.app_grid_bounds
        bounds = f'left="{left}" top="{top}" right="{right}" bottom="{bottom}"'
    return dedent(
        f"""\
        <?xml version="1.0" encoding="utf-8"?>
        <Panel id="panel_app_grid" defaultVariant="@id/{default}" role="@string/appgrid_componentName" displayId="0">
            <Variant id="@+id/opened">
                <Layer layer="@integer/app_grid_panel_layer"/>
                <Visibility isVisible="true"/>
                <Bounds {bounds}/>
                <Focus onTransition="true"/>
            </Variant>
            <Variant id="@+id/closed">
                <Layer layer="@integer/app_grid_panel_layer"/>
                <Visibility isVisible="false"/>
                <Bounds left="0" top="100%" right="100%" bottom="200%"/>
            </Variant>
            <Transitions>
                <Transition onEvent="_System_TaskOpenEvent" onEventTokens="panelId=panel_app_grid" toVariant="@id/opened"/>
                <Transition onEvent="_System_TaskOpenEvent" onEventTokens="panelId=app_panel" toVariant="@id/closed"/>
                <Transition onEvent="_System_OnHomeEvent" toVariant="@id/closed"/>
                <Transition onEvent="close_app_grid" toVariant="@id/closed"/>
                <Transition onEvent="_System_TaskCloseEvent" onEventTokens="panelId=panel_app_grid" toVariant="@id/closed"/>
            </Transitions>
        </Panel>
        """
    )


def rro_files(variant: Variant) -> dict[str, str]:
    base = f"car_product/{variant.car_product_dir}"
    rro_base = f"{base}/rro/{variant.rro_name}"
    demo_packages = " \\\n    ".join(
        (*COMMON_HMI_PACKAGES, *(app.module for app in DEMO_APPS))
    )
    panel_items = "\n".join(f"        <item>@xml/{p.panel_id}</item>" for p in variant.panels)
    default_items = "\n".join(
        f"        <item>{p.panel_id};{default_component(p.component)}</item>"
        for p in variant.panels
        if p.role_kind == "activity" and p.default_launch and default_component(p.component)
    )
    string_blocks: list[str] = []
    for panel in variant.panels:
        if panel.role_kind != "activity" or panel.component is None:
            continue
        if isinstance(panel.component, tuple):
            items = "\n".join(f"        <item>{component}</item>" for component in panel.component)
            string_blocks.append(
                f"""\
    <string-array name="{component_array_name(panel.panel_id)}" translatable="false">
{items}
    </string-array>"""
            )
        else:
            string_blocks.append(
                f'    <string name="{component_string_name(panel.panel_id)}" translatable="false">{panel.component}</string>'
            )
    string_items = "\n".join(string_blocks)
    integer_items = "\n".join(
        f'    <integer name="{panel_layer_name(p.panel_id)}">{p.layer}</integer>'
        for p in variant.panels
    )
    files: dict[str, str] = {}
    files[f"{base}/car_scalableui_hmi_{variant.product_suffix}.mk"] = (
        copyright()
        + f"""

# Product layer for the {variant.title} ScalableUI HMI.
$(call inherit-product, packages/services/Car/car_product/{variant.car_product_dir}/rro/rro.mk)

PRODUCT_PACKAGES += \\
    Calendar \\
    {demo_packages}
"""
    )
    files[f"{base}/rro/rro.mk"] = (
        copyright()
        + f"""

PRODUCT_PACKAGES += \\
    {variant.rro_name} \\
"""
    )
    files[f"{rro_base}/Android.bp"] = (
        copyright("//")
        + f"""
package {{
    default_applicable_licenses: ["Android-Apache-2.0"],
}}

android_app {{
    name: "{variant.rro_name}",
    resource_dirs: ["res"],
    certificate: "platform",
    sdk_version: "current",
    manifest: "AndroidManifest.xml",
    system_ext_specific: true,
    static_libs: [
        "car-portrait-ui-common",
        "car-ui-lib",
    ],
    aaptflags: [
        "--no-resource-deduping",
        "--no-resource-removal",
    ],
}}
"""
    )
    files[f"{rro_base}/AndroidManifest.xml"] = f"""\
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
          package="com.android.systemui.rro.scalableui.hmi.{variant.product_suffix}">
    <application android:hasCode="false" />
    <overlay
        android:targetPackage="com.android.systemui"
        android:isStatic="true"
        android:resourcesMap="@xml/overlays"
        android:priority="{130 + VARIANTS.index(variant)}"
    />
</manifest>
"""
    files[f"{rro_base}/res/layout/scalableui_hmi_decor_panel.xml"] = """\
<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="#121820" />
"""
    files[f"{rro_base}/res/values/config.xml"] = f"""\
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <bool name="config_enableScalableUI" translatable="false">true</bool>
    <bool name="config_enableClearBackStack" translatable="false">false</bool>

    <array name="window_states">
{panel_items}
        <item>@xml/panel_app_grid</item>
        <item>@xml/app_panel</item>
    </array>

    <string-array name="config_untrimmable_activities" translatable="false">
    </string-array>

    <string-array name="config_default_activities" translatable="false">
{default_items}
        <item>panel_app_grid;{APP_GRID_COMPONENT}</item>
    </string-array>
</resources>
"""
    files[f"{rro_base}/res/values/dimens.xml"] = """\
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <dimen name="scalableui_hmi_card_radius">18dp</dimen>
    <dimen name="scalableui_hmi_panel_gap">12dp</dimen>
</resources>
"""
    files[f"{rro_base}/res/values/integers.xml"] = f"""\
<?xml version="1.0" encoding="utf-8"?>
<resources>
{integer_items}
    <integer name="app_panel_layer">180</integer>
    <integer name="app_grid_panel_layer">200</integer>
</resources>
"""
    files[f"{rro_base}/res/values/strings.xml"] = f"""\
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="default_config" translatable="false">DEFAULT</string>
    <string name="appgrid_componentName" translatable="false">{APP_GRID_COMPONENT}</string>
{string_items}
</resources>
"""
    files[f"{rro_base}/res/xml/overlays.xml"] = """\
<overlay>
    <item target="bool/config_enableScalableUI" value="@bool/config_enableScalableUI"/>
    <item target="bool/config_enableClearBackStack" value="@bool/config_enableClearBackStack"/>
    <item target="array/window_states" value="@array/window_states"/>
    <item target="array/config_untrimmable_activities" value="@array/config_untrimmable_activities"/>
    <item target="array/config_default_activities" value="@array/config_default_activities"/>
</overlay>
"""
    for panel in variant.panels:
        close_when_open_panel_ids = tuple(
            p.panel_id for p in variant.panels if p.panel_id != panel.panel_id
        ) + ("app_panel", "panel_app_grid")
        files[f"{rro_base}/res/xml/{panel.panel_id}.xml"] = panel_xml(
            panel, close_when_open_panel_ids
        )
    files[f"{rro_base}/res/xml/app_panel.xml"] = app_panel_xml(variant)
    files[f"{rro_base}/res/xml/panel_app_grid.xml"] = app_grid_xml(
        variant,
        default_open=variant.slug == "app-grid-hub"
    )
    return files


def demo_app_module_block(app: DemoApp) -> str:
    sdk_line = "" if app.kind == "HOME" else '    sdk_version: "current",\n'
    platform_line = "    platform_apis: true,\n" if app.kind == "HOME" else ""
    static_libs = (
        '"ScalableUiHmiDemoCommon", "SystemUISharedLib"'
        if app.kind == "HOME"
        else '"ScalableUiHmiDemoCommon"'
    )
    return f"""\
android_app {{
    name: "{app.module}",
    srcs: ["apps/{app.key}/src/**/*.java"],
    manifest: "apps/{app.key}/AndroidManifest.xml",
    certificate: "platform",
{sdk_line}\
    system_ext_specific: true,
    privileged: true,
{platform_line}\
    static_libs: [{static_libs}],
}}
"""


def home_layout_store_java(home_package: str) -> str:
    return f"""\
package {home_package};

import android.content.Context;
import android.content.SharedPreferences;
import android.os.Build;

import java.util.LinkedHashMap;
import java.util.Map;

final class HomeLayoutStore {{
    static final String PRODUCT_NAME = "sdk_car_scalableui_editable_home_x86_64";
    static final String PREFS_NAME = "com.android.systemui.scalableui_poc_preferences";
    static final String KEY_LAYOUT = "selected_layout";
    static final String KEY_EDIT_MODE = "edit_mode_enabled";
    static final String KEY_UPDATED = "last_updated_epoch_ms";

    static final String LAYOUT_L1 = "L1";
    static final String LAYOUT_L2 = "L2";
    static final String LAYOUT_L3 = "L3";

    static final String PANEL_PRIMARY = "home_panel_primary";
    static final String PANEL_SECONDARY_TOP = "home_panel_secondary_top";
    static final String PANEL_SECONDARY_BOTTOM = "home_panel_secondary_bottom";

    static final String EVENT_EDIT_ENTERED = "_Custom_HomeEditModeEntered";
    static final String EVENT_EDIT_EXITED = "_Custom_HomeEditModeExited";
    static final String EVENT_LAYOUT_CHANGED = "_Custom_HomeLayoutChanged";
    static final String EVENT_ASSIGNMENTS_CHANGED = "_Custom_HomeAssignmentsChanged";
    static final String EVENT_APPLY_REQUESTED = "_Custom_HomeApplyRequested";

    static final String[] PANEL_IDS = new String[] {{
            PANEL_PRIMARY,
            PANEL_SECONDARY_TOP,
            PANEL_SECONDARY_BOTTOM,
    }};

    static final AppOption[] APP_OPTIONS = new AppOption[] {{
            new AppOption("Maps mock", "{MAP_COMPONENT}"),
            new AppOption("Media mock", "{demo_activity("MediaPanelActivity")}"),
            new AppOption("Vehicle mock", "{demo_activity("ControlsPanelActivity")}"),
            new AppOption("Calendar mock", "{CALENDAR_DEMO_COMPONENT}"),
            new AppOption("Settings shortcut", "{demo_activity("SettingsPanelActivity")}"),
            new AppOption("G Ball", "{GBALL_COMPONENT}"),
    }};

    private HomeLayoutStore() {{}}

    static boolean isEditableHomeVariant() {{
        return PRODUCT_NAME.equals(Build.PRODUCT);
    }}

    static State load(Context context) {{
        SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
        State state = new State();
        state.selectedLayout = sanitizeLayout(prefs.getString(KEY_LAYOUT, LAYOUT_L2));
        state.editModeEnabled = prefs.getBoolean(KEY_EDIT_MODE, false);
        state.lastUpdatedEpochMs = prefs.getLong(KEY_UPDATED, 0L);
        for (String panelId : PANEL_IDS) {{
            String component = prefs.getString(prefKeyForPanel(panelId),
                    defaultComponentForPanel(panelId));
            if (!isAllowedComponent(component)) {{
                component = defaultComponentForPanel(panelId);
            }}
            state.assignments.put(panelId, component);
        }}
        return state;
    }}

    static void save(Context context, State state) {{
        SharedPreferences.Editor editor = context.getSharedPreferences(
                PREFS_NAME, Context.MODE_PRIVATE).edit();
        editor.putString(KEY_LAYOUT, sanitizeLayout(state.selectedLayout));
        editor.putBoolean(KEY_EDIT_MODE, state.editModeEnabled);
        editor.putLong(KEY_UPDATED, state.lastUpdatedEpochMs);
        for (String panelId : PANEL_IDS) {{
            editor.putString(prefKeyForPanel(panelId), sanitizeComponent(panelId,
                    state.assignments.get(panelId)));
        }}
        editor.apply();
    }}

    static void setEditMode(Context context, boolean enabled) {{
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
                .edit()
                .putBoolean(KEY_EDIT_MODE, enabled)
                .apply();
    }}

    static String sanitizeLayout(String layoutId) {{
        if (LAYOUT_L1.equals(layoutId) || LAYOUT_L2.equals(layoutId) || LAYOUT_L3.equals(layoutId)) {{
            return layoutId;
        }}
        return LAYOUT_L2;
    }}

    static boolean isAllowedComponent(String component) {{
        if (component == null) {{
            return false;
        }}
        for (AppOption option : APP_OPTIONS) {{
            if (option.component.equals(component)) {{
                return true;
            }}
        }}
        return false;
    }}

    static String labelForComponent(String component) {{
        for (AppOption option : APP_OPTIONS) {{
            if (option.component.equals(component)) {{
                return option.label;
            }}
        }}
        return "Unknown";
    }}

    static String defaultComponentForPanel(String panelId) {{
        if (PANEL_PRIMARY.equals(panelId)) {{
            return APP_OPTIONS[0].component;
        }}
        if (PANEL_SECONDARY_TOP.equals(panelId)) {{
            return APP_OPTIONS[1].component;
        }}
        return APP_OPTIONS[2].component;
    }}

    static String sanitizeComponent(String panelId, String component) {{
        return isAllowedComponent(component) ? component : defaultComponentForPanel(panelId);
    }}

    private static String prefKeyForPanel(String panelId) {{
        return "assignment_" + panelId;
    }}

    static final class AppOption {{
        final String label;
        final String component;

        AppOption(String label, String component) {{
            this.label = label;
            this.component = component;
        }}
    }}

    static final class State {{
        String selectedLayout = LAYOUT_L2;
        boolean editModeEnabled;
        long lastUpdatedEpochMs;
        final LinkedHashMap<String, String> assignments = new LinkedHashMap<>();
    }}
}}
"""


def home_activity_java(home_package: str) -> str:
    return f"""\
package {home_package};

import android.app.Activity;
import android.content.ComponentName;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.TextView;

public final class HomeActivity extends Activity {{
    private static final String ACTION_SCALABLEUI_PANEL_EVENT =
            "com.android.car.scalableui.ACTION_PANEL_EVENT";
    private static final String EXTRA_SCALABLEUI_EVENT_ID =
            "com.android.car.scalableui.extra.EVENT_ID";
    private static final String EXTRA_SCALABLEUI_EVENT_TOKENS =
            "com.android.car.scalableui.extra.EVENT_TOKENS";
    private static final String EXTRA_TARGET_PANEL_ID =
            "com.android.car.scalableui.extra.TARGET_PANEL_ID";
    private static final String TARGET_PANEL_URI_SCHEME = "scalableui-hmi";
    private static final String TARGET_PANEL_URI_HOST = "panel-launch";
    private static final String TARGET_PANEL_URI_PARAM = "target_panel";

    private final Handler mHandler = new Handler(Looper.getMainLooper());
    private final Runnable mApplyRunnable = this::applyCurrentVariantState;

    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);
        setContentView(createHomeSurface());
    }}

    @Override
    protected void onResume() {{
        super.onResume();
        mHandler.removeCallbacks(mApplyRunnable);
        if (isWidgetLayoutLabVariant() || HomeLayoutStore.isEditableHomeVariant()) {{
            mHandler.postDelayed(mApplyRunnable, 260L);
        }}
    }}

    @Override
    protected void onPause() {{
        super.onPause();
        mHandler.removeCallbacks(mApplyRunnable);
    }}

    private View createHomeSurface() {{
        if (HomeLayoutStore.isEditableHomeVariant()) {{
            return createEditableHomeSurface();
        }}
        if (isWidgetLayoutLabVariant()) {{
            View surface = new View(this);
            surface.setBackgroundColor(Color.rgb(32, 108, 141));
            return surface;
        }}
        FrameLayout root = new FrameLayout(this);
        root.setBackgroundColor(Color.rgb(18, 28, 40));
        TextView title = new TextView(this);
        title.setText("ScalableUI Home");
        title.setTextColor(Color.WHITE);
        title.setTextSize(28f);
        title.setTypeface(Typeface.DEFAULT_BOLD);
        title.setGravity(Gravity.CENTER);
        root.addView(title, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
        return root;
    }}

    private View createEditableHomeSurface() {{
        FrameLayout root = new FrameLayout(this);
        root.setBackgroundColor(Color.rgb(15, 30, 44));

        TextView title = new TextView(this);
        title.setText("Editable multipanel home");
        title.setTextColor(Color.WHITE);
        title.setTextSize(30f);
        title.setTypeface(Typeface.DEFAULT_BOLD);
        FrameLayout.LayoutParams titleParams = new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        titleParams.gravity = Gravity.TOP | Gravity.START;
        titleParams.leftMargin = 48;
        titleParams.topMargin = 36;
        root.addView(title, titleParams);

        TextView subtitle = new TextView(this);
        subtitle.setText("System bars stay visible. Tap Edit layout to change L1/L2/L3 and panel apps.");
        subtitle.setTextColor(Color.rgb(190, 212, 224));
        subtitle.setTextSize(16f);
        FrameLayout.LayoutParams subtitleParams = new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        subtitleParams.gravity = Gravity.TOP | Gravity.START;
        subtitleParams.leftMargin = 48;
        subtitleParams.topMargin = 86;
        root.addView(subtitle, subtitleParams);

        Button edit = new Button(this);
        edit.setText("Edit\\nlayout");
        edit.setAllCaps(false);
        edit.setTextSize(16f);
        edit.setTypeface(Typeface.DEFAULT_BOLD);
        edit.setTextColor(Color.BLACK);
        edit.setGravity(Gravity.CENTER);
        GradientDrawable background = new GradientDrawable();
        background.setColor(Color.rgb(241, 117, 44));
        background.setCornerRadius(24f);
        edit.setBackground(background);
        edit.setOnClickListener(v -> openHomeEditor());

        FrameLayout.LayoutParams editParams = new FrameLayout.LayoutParams(220, 140);
        editParams.gravity = Gravity.BOTTOM | Gravity.END;
        editParams.rightMargin = 44;
        editParams.bottomMargin = 38;
        root.addView(edit, editParams);
        return root;
    }}

    private void openHomeEditor() {{
        HomeLayoutStore.setEditMode(this, true);
        dispatchScalableUiEvent(HomeLayoutStore.EVENT_EDIT_ENTERED, "");
        launchToPanel(getPackageName() + "/.HomeEditActivity", "app_panel");
    }}

    private void applyCurrentVariantState() {{
        if (isFinishing() || isDestroyed()) {{
            return;
        }}
        if (isWidgetLayoutLabVariant()) {{
            applyWidgetLayoutLabDefaults();
            return;
        }}
        if (!HomeLayoutStore.isEditableHomeVariant()) {{
            return;
        }}
        HomeLayoutStore.State state = HomeLayoutStore.load(this);
        dispatchScalableUiEvent(HomeLayoutStore.EVENT_EDIT_EXITED, "");
        dispatchScalableUiEvent(HomeLayoutStore.EVENT_LAYOUT_CHANGED,
                "panelId=home_root;panelToVariantId=" + state.selectedLayout);
        postLaunch(150L, state.assignments.get(HomeLayoutStore.PANEL_PRIMARY),
                HomeLayoutStore.PANEL_PRIMARY);
        postLaunch(300L, state.assignments.get(HomeLayoutStore.PANEL_SECONDARY_TOP),
                HomeLayoutStore.PANEL_SECONDARY_TOP);
        postLaunch(450L, state.assignments.get(HomeLayoutStore.PANEL_SECONDARY_BOTTOM),
                HomeLayoutStore.PANEL_SECONDARY_BOTTOM);
    }}

    private void applyWidgetLayoutLabDefaults() {{
        dispatchScalableUiEvent("widget_layout_hide_menu", "");
        mHandler.postDelayed(() -> dispatchScalableUiEvent("widget_layout_initial", ""), 50L);
        postLaunch(160L, "{MAP_COMPONENT}", "widget_a_panel");
        postLaunch(320L, "{CALENDAR_DEMO_COMPONENT}", "widget_b_panel");
        postLaunch(480L, "{WEATHER_DEMO_COMPONENT}", "widget_c_panel");
        postLaunch(640L, "{WIDGET_MENU_BUTTON_COMPONENT}", "widget_menu_button_panel");
    }}

    private void postLaunch(long delayMs, String component, String panelId) {{
        if (component == null || panelId == null) {{
            return;
        }}
        mHandler.postDelayed(() -> {{
            if (isFinishing() || isDestroyed()) {{
                return;
            }}
            launchToPanel(component, panelId);
        }}, delayMs);
    }}

    private void launchToPanel(String componentString, String panelId) {{
        Intent intent = new Intent(Intent.ACTION_MAIN);
        intent.setComponent(ComponentName.unflattenFromString(componentString));
        intent.putExtra(EXTRA_TARGET_PANEL_ID, panelId);
        intent.setData(new Uri.Builder()
                .scheme(TARGET_PANEL_URI_SCHEME)
                .authority(TARGET_PANEL_URI_HOST)
                .appendQueryParameter(TARGET_PANEL_URI_PARAM, panelId)
                .build());
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK
                | Intent.FLAG_ACTIVITY_CLEAR_TOP
                | Intent.FLAG_ACTIVITY_SINGLE_TOP);
        startActivity(intent);
    }}

    private void dispatchScalableUiEvent(String eventId, String tokens) {{
        Intent intent = new Intent(ACTION_SCALABLEUI_PANEL_EVENT);
        intent.putExtra(EXTRA_SCALABLEUI_EVENT_ID, eventId);
        intent.putExtra(EXTRA_SCALABLEUI_EVENT_TOKENS, tokens);
        intent.setPackage("com.android.systemui");
        sendBroadcast(intent);
    }}

    private boolean isWidgetLayoutLabVariant() {{
        return "sdk_car_scalableui_widget_layout_lab_x86_64".equals(android.os.Build.PRODUCT);
    }}
}}
"""


def home_edit_activity_java(home_package: str) -> str:
    return f"""\
package {home_package};

import android.app.Activity;
import android.content.ComponentName;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.Gravity;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public final class HomeEditActivity extends Activity {{
    private static final String ACTION_SCALABLEUI_PANEL_EVENT =
            "com.android.car.scalableui.ACTION_PANEL_EVENT";
    private static final String EXTRA_SCALABLEUI_EVENT_ID =
            "com.android.car.scalableui.extra.EVENT_ID";
    private static final String EXTRA_SCALABLEUI_EVENT_TOKENS =
            "com.android.car.scalableui.extra.EVENT_TOKENS";
    private static final String EXTRA_TARGET_PANEL_ID =
            "com.android.car.scalableui.extra.TARGET_PANEL_ID";
    private static final String TARGET_PANEL_URI_SCHEME = "scalableui-hmi";
    private static final String TARGET_PANEL_URI_HOST = "panel-launch";
    private static final String TARGET_PANEL_URI_PARAM = "target_panel";

    private final Handler mHandler = new Handler(Looper.getMainLooper());
    private final LinkedHashMap<String, String> mAssignments = new LinkedHashMap<>();
    private final Map<String, TextView> mPanelSummaries = new HashMap<>();
    private final Map<String, List<Button>> mPanelButtons = new HashMap<>();
    private final Map<String, Button> mLayoutButtons = new HashMap<>();

    private String mSelectedLayout;

    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);
        if (!HomeLayoutStore.isEditableHomeVariant()) {{
            finish();
            return;
        }}
        HomeLayoutStore.State state = HomeLayoutStore.load(this);
        mSelectedLayout = state.selectedLayout;
        mAssignments.putAll(state.assignments);
        setContentView(createContent());
        refreshLayoutButtons();
        refreshAllPanels();
    }}

    @Override
    public void onBackPressed() {{
        cancelEditing();
    }}

    private ScrollView createContent() {{
        ScrollView scrollView = new ScrollView(this);
        scrollView.setFillViewport(true);
        scrollView.setBackgroundColor(Color.rgb(11, 18, 30));

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(34, 28, 34, 28);
        scrollView.addView(root, new ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));

        TextView title = createTitle("Home layout editor");
        root.addView(title);
        root.addView(createSubtitle(
                "Choose L1/L2/L3, pick one whitelisted app for each panel, then Save."));

        root.addView(createSectionLabel("Layout"));
        LinearLayout layoutRow = new LinearLayout(this);
        layoutRow.setOrientation(LinearLayout.HORIZONTAL);
        layoutRow.setPadding(0, 8, 0, 18);
        root.addView(layoutRow, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));
        addLayoutButton(layoutRow, HomeLayoutStore.LAYOUT_L1, "L1\\nTwo columns");
        addLayoutButton(layoutRow, HomeLayoutStore.LAYOUT_L2, "L2\\nLeft large");
        addLayoutButton(layoutRow, HomeLayoutStore.LAYOUT_L3, "L3\\nTop / bottom");

        addPanelSection(root, HomeLayoutStore.PANEL_PRIMARY, "Primary panel");
        addPanelSection(root, HomeLayoutStore.PANEL_SECONDARY_TOP, "Secondary top panel");
        addPanelSection(root, HomeLayoutStore.PANEL_SECONDARY_BOTTOM, "Secondary bottom panel");

        LinearLayout actionRow = new LinearLayout(this);
        actionRow.setOrientation(LinearLayout.HORIZONTAL);
        actionRow.setPadding(0, 22, 0, 0);
        root.addView(actionRow, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));

        Button cancel = createActionButton("Cancel", false);
        cancel.setOnClickListener(v -> cancelEditing());
        LinearLayout.LayoutParams cancelParams = new LinearLayout.LayoutParams(
                0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f);
        cancelParams.rightMargin = 10;
        actionRow.addView(cancel, cancelParams);

        Button save = createActionButton("Save", true);
        save.setOnClickListener(v -> saveAndApply());
        LinearLayout.LayoutParams saveParams = new LinearLayout.LayoutParams(
                0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f);
        saveParams.leftMargin = 10;
        actionRow.addView(save, saveParams);

        return scrollView;
    }}

    private void addLayoutButton(LinearLayout root, String layoutId, String label) {{
        Button button = createChoiceButton(label);
        button.setOnClickListener(v -> {{
            mSelectedLayout = layoutId;
            refreshLayoutButtons();
        }});
        mLayoutButtons.put(layoutId, button);
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(
                0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f);
        params.leftMargin = 8;
        params.rightMargin = 8;
        root.addView(button, params);
    }}

    private void addPanelSection(LinearLayout root, String panelId, String titleText) {{
        root.addView(createSectionLabel(titleText));
        TextView summary = createSubtitle("");
        summary.setPadding(0, 0, 0, 12);
        mPanelSummaries.put(panelId, summary);
        root.addView(summary);

        List<Button> buttons = new ArrayList<>();
        mPanelButtons.put(panelId, buttons);
        for (HomeLayoutStore.AppOption option : HomeLayoutStore.APP_OPTIONS) {{
            Button button = createChoiceButton(option.label);
            button.setOnClickListener(v -> {{
                mAssignments.put(panelId, option.component);
                refreshPanel(panelId);
            }});
            button.setTag(option.component);
            buttons.add(button);
            LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
            params.bottomMargin = 8;
            root.addView(button, params);
        }}
    }}

    private void refreshLayoutButtons() {{
        for (Map.Entry<String, Button> entry : mLayoutButtons.entrySet()) {{
            styleChoiceButton(entry.getValue(), entry.getKey().equals(mSelectedLayout));
        }}
    }}

    private void refreshAllPanels() {{
        for (String panelId : HomeLayoutStore.PANEL_IDS) {{
            refreshPanel(panelId);
        }}
    }}

    private void refreshPanel(String panelId) {{
        String component = HomeLayoutStore.sanitizeComponent(panelId, mAssignments.get(panelId));
        mAssignments.put(panelId, component);
        TextView summary = mPanelSummaries.get(panelId);
        if (summary != null) {{
            summary.setText("Current: " + HomeLayoutStore.labelForComponent(component));
        }}
        List<Button> buttons = mPanelButtons.get(panelId);
        if (buttons == null) {{
            return;
        }}
        for (Button button : buttons) {{
            styleChoiceButton(button, component.equals(button.getTag()));
        }}
    }}

    private void saveAndApply() {{
        String validationError = validateSelections();
        if (validationError != null) {{
            Toast.makeText(this, validationError, Toast.LENGTH_SHORT).show();
            return;
        }}
        HomeLayoutStore.State state = new HomeLayoutStore.State();
        state.selectedLayout = mSelectedLayout;
        state.editModeEnabled = false;
        state.lastUpdatedEpochMs = System.currentTimeMillis();
        state.assignments.putAll(mAssignments);
        HomeLayoutStore.save(this, state);

        dispatchScalableUiEvent(HomeLayoutStore.EVENT_LAYOUT_CHANGED,
                "panelId=home_root;panelToVariantId=" + mSelectedLayout);

        long delay = 140L;
        for (String panelId : HomeLayoutStore.PANEL_IDS) {{
            final String currentPanel = panelId;
            final String component = mAssignments.get(panelId);
            mHandler.postDelayed(() -> {{
                dispatchScalableUiEvent(HomeLayoutStore.EVENT_ASSIGNMENTS_CHANGED,
                        "panelId=" + currentPanel + ";component=" + component);
                launchToPanel(component, currentPanel);
            }}, delay);
            delay += 150L;
        }}

        mHandler.postDelayed(() -> {{
            dispatchScalableUiEvent(HomeLayoutStore.EVENT_APPLY_REQUESTED, "");
            dispatchScalableUiEvent(HomeLayoutStore.EVENT_EDIT_EXITED, "");
            finish();
        }}, delay + 80L);
    }}

    private String validateSelections() {{
        for (String panelId : HomeLayoutStore.PANEL_IDS) {{
            String component = mAssignments.get(panelId);
            if (!HomeLayoutStore.isAllowedComponent(component)) {{
                return "Whitelisted app only";
            }}
        }}
        for (int i = 0; i < HomeLayoutStore.PANEL_IDS.length; i++) {{
            String left = mAssignments.get(HomeLayoutStore.PANEL_IDS[i]);
            for (int j = i + 1; j < HomeLayoutStore.PANEL_IDS.length; j++) {{
                String right = mAssignments.get(HomeLayoutStore.PANEL_IDS[j]);
                if (left != null && left.equals(right)) {{
                    return "Duplicate assignment is not allowed";
                }}
            }}
        }}
        return null;
    }}

    private void cancelEditing() {{
        HomeLayoutStore.setEditMode(this, false);
        dispatchScalableUiEvent(HomeLayoutStore.EVENT_EDIT_EXITED, "");
        finish();
    }}

    private void launchToPanel(String componentString, String panelId) {{
        Intent intent = new Intent(Intent.ACTION_MAIN);
        intent.setComponent(ComponentName.unflattenFromString(componentString));
        intent.putExtra(EXTRA_TARGET_PANEL_ID, panelId);
        intent.setData(new Uri.Builder()
                .scheme(TARGET_PANEL_URI_SCHEME)
                .authority(TARGET_PANEL_URI_HOST)
                .appendQueryParameter(TARGET_PANEL_URI_PARAM, panelId)
                .build());
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK
                | Intent.FLAG_ACTIVITY_CLEAR_TOP
                | Intent.FLAG_ACTIVITY_SINGLE_TOP);
        startActivity(intent);
    }}

    private void dispatchScalableUiEvent(String eventId, String tokens) {{
        Intent intent = new Intent(ACTION_SCALABLEUI_PANEL_EVENT);
        intent.putExtra(EXTRA_SCALABLEUI_EVENT_ID, eventId);
        intent.putExtra(EXTRA_SCALABLEUI_EVENT_TOKENS, tokens);
        intent.setPackage("com.android.systemui");
        sendBroadcast(intent);
    }}

    private TextView createTitle(String text) {{
        TextView title = new TextView(this);
        title.setText(text);
        title.setTextColor(Color.WHITE);
        title.setTextSize(28f);
        title.setTypeface(Typeface.DEFAULT_BOLD);
        return title;
    }}

    private TextView createSubtitle(String text) {{
        TextView subtitle = new TextView(this);
        subtitle.setText(text);
        subtitle.setTextColor(Color.rgb(188, 210, 224));
        subtitle.setTextSize(15f);
        subtitle.setPadding(0, 8, 0, 8);
        return subtitle;
    }}

    private TextView createSectionLabel(String text) {{
        TextView label = new TextView(this);
        label.setText(text);
        label.setTextColor(Color.WHITE);
        label.setTextSize(18f);
        label.setTypeface(Typeface.DEFAULT_BOLD);
        label.setPadding(0, 18, 0, 8);
        return label;
    }}

    private Button createChoiceButton(String text) {{
        Button button = new Button(this);
        button.setText(text);
        button.setAllCaps(false);
        button.setTextSize(15f);
        button.setTypeface(Typeface.DEFAULT_BOLD);
        return button;
    }}

    private Button createActionButton(String text, boolean primary) {{
        Button button = createChoiceButton(text);
        GradientDrawable background = new GradientDrawable();
        background.setCornerRadius(18f);
        background.setColor(primary ? Color.rgb(241, 117, 44) : Color.rgb(36, 54, 72));
        button.setBackground(background);
        button.setTextColor(primary ? Color.BLACK : Color.WHITE);
        return button;
    }}

    private void styleChoiceButton(Button button, boolean selected) {{
        GradientDrawable background = new GradientDrawable();
        background.setCornerRadius(16f);
        background.setColor(selected ? Color.rgb(241, 117, 44) : Color.rgb(36, 54, 72));
        button.setBackground(background);
        button.setTextColor(selected ? Color.BLACK : Color.WHITE);
    }}
}}
"""


def demo_app_files() -> dict[str, str]:
    base = "car_product/scalableui_hmi_demo_apps"
    module_blocks = "\n".join(demo_app_module_block(app) for app in DEMO_APPS)
    menu_targets = "\n".join(
        f'            new LaunchTarget("{DEMO_BY_KEY[key].label}", "{DEMO_BY_KEY[key].component}"),'
        for key in ("widgets", "map", "gball", "media", "tasks")
    )
    java = """\
package com.android.car.scalableui.hmi.demo.common;

import android.app.Activity;
import android.content.ClipData;
import android.content.ComponentName;
import android.content.Intent;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.RectF;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.Gravity;
import android.view.DragEvent;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.SeekBar;
import android.widget.Switch;
import android.widget.TextView;
import android.widget.Toast;

public abstract class DemoBaseActivity extends Activity {
    private static final String ACTION_SCALABLEUI_PANEL_EVENT =
            "com.android.car.scalableui.ACTION_PANEL_EVENT";
    private static final String EXTRA_SCALABLEUI_EVENT_ID =
            "com.android.car.scalableui.extra.EVENT_ID";
    private static final String EXTRA_SCALABLEUI_EVENT_TOKENS =
            "com.android.car.scalableui.extra.EVENT_TOKENS";
    private static final String EXTRA_TARGET_PANEL_ID =
            "com.android.car.scalableui.extra.TARGET_PANEL_ID";
    private static final String TARGET_PANEL_URI_SCHEME = "scalableui-hmi";
    private static final String TARGET_PANEL_URI_HOST = "panel-launch";
    private static final String TARGET_PANEL_URI_PARAM = "target_panel";

    protected static final int DEMO_INFO = 0;
    protected static final int DEMO_MAP = 1;
    protected static final int DEMO_GBALL = 2;
    protected static final int DEMO_WIDGET = 3;
    protected static final int DEMO_PANEL_MENU = 4;
    protected static final int DEMO_PANEL_MENU_BUTTON = 5;
    protected static final int DEMO_HOME = 6;
    protected static final int DEMO_CALENDAR = 7;
    protected static final int DEMO_WEATHER = 8;
    protected static final int DEMO_WIDGET_MENU = 9;
    protected static final int DEMO_WIDGET_MENU_BUTTON = 10;
    protected static final int DEMO_WIDGET_DROP_ZONE = 11;

    private String mSelectedPanelId = "workspace_panel";
    private TextView mSelectedPanelStatus;
    private boolean mHomeLayoutBootstrapped;

    protected abstract int getDemoType();

    protected abstract String getDemoTitle();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        if (getDemoType() == DEMO_MAP) {
            setContentView(new SyntheticMapView(this));
            return;
        }
        if (getDemoType() == DEMO_GBALL) {
            setContentView(new GBallView(this));
            return;
        }
        if (getDemoType() == DEMO_WIDGET) {
            setContentView(createWidgetPanel());
            return;
        }
        if (getDemoType() == DEMO_PANEL_MENU) {
            setContentView(createPanelMenu());
            return;
        }
        if (getDemoType() == DEMO_PANEL_MENU_BUTTON) {
            setContentView(createPanelMenuButton());
            return;
        }
        if (getDemoType() == DEMO_HOME) {
            View homeSurface = createHomeSurface();
            setContentView(homeSurface);
            scheduleHomeLayoutBootstrap(homeSurface);
            return;
        }
        if (getDemoType() == DEMO_CALENDAR) {
            setContentView(createCalendarWidget());
            return;
        }
        if (getDemoType() == DEMO_WEATHER) {
            setContentView(createWeatherWidget());
            return;
        }
        if (getDemoType() == DEMO_WIDGET_MENU) {
            setContentView(createWidgetLayoutMenu());
            return;
        }
        if (getDemoType() == DEMO_WIDGET_MENU_BUTTON) {
            setContentView(createWidgetLayoutMenuButton());
            return;
        }
        if (getDemoType() == DEMO_WIDGET_DROP_ZONE) {
            setContentView(createWidgetDropZone());
            return;
        }

        setContentView(createInfoPanel(getDemoTitle(),
                "ScalableUI demo app\\n" + getPackageName()));
    }

    private LinearLayout createInfoPanel(String title, String bodyText) {
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setGravity(Gravity.CENTER);
        root.setPadding(40, 32, 40, 32);

        GradientDrawable background = new GradientDrawable(
                GradientDrawable.Orientation.TL_BR,
                new int[] {Color.rgb(20, 28, 38), Color.rgb(36, 51, 68)});
        background.setCornerRadius(28f);
        root.setBackground(background);

        TextView heading = new TextView(this);
        heading.setText(title);
        heading.setTextColor(Color.WHITE);
        heading.setTextSize(30f);
        heading.setTypeface(Typeface.DEFAULT_BOLD);
        heading.setGravity(Gravity.CENTER);

        TextView body = new TextView(this);
        body.setText(bodyText);
        body.setTextColor(Color.rgb(210, 224, 238));
        body.setTextSize(15f);
        body.setGravity(Gravity.CENTER);
        body.setPadding(0, 20, 0, 0);

        root.addView(heading, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));
        root.addView(body, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));
        return root;
    }

    private View createHomeSurface() {
        View view = new View(this);
        view.setBackgroundColor(Color.rgb(32, 108, 141));
        return view;
    }

    private void scheduleHomeLayoutBootstrap(View anchor) {
        if (mHomeLayoutBootstrapped) {
            return;
        }
        mHomeLayoutBootstrapped = true;
        anchor.postDelayed(this::bootstrapHomeLayout, 350L);
    }

    private void bootstrapHomeLayout() {
        if (isFinishing() || isDestroyed()) {
            return;
        }
        Handler handler = new Handler(Looper.getMainLooper());
        dispatchScalableUiEvent("widget_layout_hide_menu");
        handler.postDelayed(() -> dispatchScalableUiEvent("widget_layout_initial"), 60L);
        postPanelLaunch(handler, 160L, MAP_WIDGET);
        postPanelLaunch(handler, 320L, CALENDAR_WIDGET);
        postPanelLaunch(handler, 480L, WEATHER_WIDGET);
        postPanelLaunch(handler, 640L, WIDGET_MENU_BUTTON_WIDGET);
    }

    private void postPanelLaunch(Handler handler, long delayMs, LaunchTarget target) {
        handler.postDelayed(() -> {
            if (isFinishing() || isDestroyed()) {
                return;
            }
            launchToPanel(target.component, target.defaultPanelId);
        }, delayMs);
    }

    private LinearLayout createPanelMenu() {
        LinearLayout root = createVerticalShell("Panel Control", "Choose a panel, then choose an app");
        mSelectedPanelStatus = new TextView(this);
        mSelectedPanelStatus.setTextColor(Color.rgb(214, 235, 238));
        mSelectedPanelStatus.setTextSize(15f);
        mSelectedPanelStatus.setGravity(Gravity.CENTER);
        mSelectedPanelStatus.setPadding(0, 0, 0, 10);
        root.addView(mSelectedPanelStatus, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));
        updateSelectedPanelStatus();

        TextView panelLabel = createSectionLabel("Display target");
        root.addView(panelLabel);
        for (PanelTarget target : PANEL_TARGETS) {
            addPanelTargetButton(root, target);
        }

        TextView appLabel = createSectionLabel("App to show");
        appLabel.setPadding(0, 18, 0, 4);
        root.addView(appLabel);
        for (LaunchTarget target : MENU_TARGETS) {
            addLaunchButton(root, target);
        }

        Button close = createButton("Hide menu");
        close.setOnClickListener(v -> finish());
        root.addView(close, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));
        return root;
    }

    private View createPanelMenuButton() {
        Button button = createButton("Panel\\nControl");
        button.setTextSize(15f);
        button.setGravity(Gravity.CENTER);
        button.setOnClickListener(v -> {
            Intent intent = new Intent(Intent.ACTION_MAIN);
            intent.setComponent(ComponentName.unflattenFromString(
                    "com.android.car.scalableui.hmi.panelmenu/.PanelMenuActivity"));
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK
                    | Intent.FLAG_ACTIVITY_CLEAR_TOP
                    | Intent.FLAG_ACTIVITY_SINGLE_TOP);
            startActivity(intent);
        });
        return button;
    }

    private LinearLayout createWidgetPanel() {
        LinearLayout root = createWidgetShell("Widget F", "Controls");

        TextView status = new TextView(this);
        status.setText("Cabin: 22 C  |  Fan: 35%  |  Drive mode: Comfort");
        status.setTextColor(Color.BLACK);
        status.setTextSize(18f);
        status.setGravity(Gravity.CENTER);
        status.setPadding(0, 14, 0, 14);
        root.addView(status, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));

        SeekBar fan = new SeekBar(this);
        fan.setMax(100);
        fan.setProgress(35);
        fan.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                status.setText("Cabin: 22 C  |  Fan: " + progress + "%  |  Drive mode: Comfort");
            }

            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {}

            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {}
        });
        root.addView(fan, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));

        Switch quiet = new Switch(this);
        quiet.setText("Quiet cabin mode");
        quiet.setTextColor(Color.BLACK);
        quiet.setTextSize(18f);
        quiet.setPadding(0, 18, 0, 18);
        root.addView(quiet, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT));

        Button action = createButton("Apply widget layout");
        styleMenuCardButton(action);
        action.setTextSize(16f);
        action.setOnClickListener(v -> status.setText(
                quiet.isChecked() ? "Quiet widget layout applied" : "Widget layout applied"));
        root.addView(action);
        return root;
    }

    private LinearLayout createCalendarWidget() {
        LinearLayout root = createWidgetShell("Widget B", "Calendar");
        TextView day = new TextView(this);
        day.setText("Thu 23\\n09:30 Design sync\\n13:00 Charging review\\n17:30 Family pickup");
        day.setTextColor(Color.BLACK);
        day.setTextSize(22f);
        day.setGravity(Gravity.CENTER);
        day.setPadding(0, 16, 0, 0);
        root.addView(day, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));
        return root;
    }

    private LinearLayout createWeatherWidget() {
        LinearLayout root = createWidgetShell("Widget C", "Weather");
        TextView weather = new TextView(this);
        weather.setText("21 C  Clear\\nRain 10%  Wind 4 m/s");
        weather.setTextColor(Color.BLACK);
        weather.setTextSize(24f);
        weather.setGravity(Gravity.CENTER);
        weather.setPadding(0, 16, 0, 0);
        root.addView(weather, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));
        return root;
    }

    private LinearLayout createWidgetLayoutMenu() {
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setGravity(Gravity.CENTER_HORIZONTAL);
        root.setPadding(28, 18, 28, 18);
        root.setBackgroundColor(Color.rgb(70, 160, 35));

        TextView heading = new TextView(this);
        heading.setText("Widget layout");
        heading.setTextColor(Color.WHITE);
        heading.setTextSize(26f);
        heading.setTypeface(Typeface.DEFAULT_BOLD);
        heading.setGravity(Gravity.CENTER);
        root.addView(heading, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));

        TextView hint = createMenuHint("Tap to place. Long press and drag to the orange drop pad.");
        root.addView(hint);

        addWidgetCard(root, "Widget A  Map", MAP_WIDGET, "widget_a_panel",
                "widget_layout_initial");
        addWidgetCard(root, "Widget B  Calendar", CALENDAR_WIDGET, "widget_b_panel",
                "widget_layout_stack_left");
        addWidgetCard(root, "Widget C  Weather", WEATHER_WIDGET, "widget_c_panel",
                "widget_layout_stack_left");
        addWidgetCard(root, "Widget D  Media", MEDIA_WIDGET, "widget_d_panel",
                "widget_layout_split_three");
        addWidgetCard(root, "Widget E  Tasks", TASKS_WIDGET, "widget_e_panel",
                "widget_layout_stack_left");
        addWidgetCard(root, "Widget F  Controls", INTERACTIVE_WIDGET, "widget_f_panel",
                "widget_layout_two_large");

        addPatternButton(root, "Preset 1  A + B + C", "widget_layout_initial",
                MAP_WIDGET, CALENDAR_WIDGET, WEATHER_WIDGET);
        addPatternButton(root, "Preset 2  A + F", "widget_layout_two_large",
                MAP_WIDGET, INTERACTIVE_WIDGET);
        addPatternButton(root, "Preset 3  A + B + D", "widget_layout_split_three",
                MAP_WIDGET, CALENDAR_WIDGET, MEDIA_WIDGET);
        addPatternButton(root, "Preset 4  F + A", "widget_layout_swap",
                INTERACTIVE_WIDGET, MAP_WIDGET);
        addPatternButton(root, "Preset 5  Stack + A", "widget_layout_stack_left",
                TASKS_WIDGET, WEATHER_WIDGET, CALENDAR_WIDGET, MEDIA_WIDGET, MAP_WIDGET);

        Button close = createButton("Hide menu");
        styleSecondaryButton(close);
        close.setOnClickListener(v -> {
            dispatchScalableUiEvent("widget_layout_hide_menu");
            finish();
        });
        root.addView(close, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));
        return root;
    }

    private View createWidgetLayoutMenuButton() {
        Button button = createButton("Widget\\nLayout");
        styleMenuCardButton(button);
        button.setTextSize(16f);
        button.setGravity(Gravity.CENTER);
        button.setOnClickListener(v -> {
            launchToPanel(WIDGET_MENU_COMPONENT.component, "widget_picker_panel");
            launchToPanel(DROP_ZONE_WIDGET.component, "widget_drop_zone_panel");
        });
        return button;
    }

    private View createWidgetDropZone() {
        TextView dropZone = new TextView(this);
        dropZone.setText("Drop");
        dropZone.setTextColor(Color.BLACK);
        dropZone.setTextSize(18f);
        dropZone.setTypeface(Typeface.DEFAULT_BOLD);
        dropZone.setGravity(Gravity.CENTER);
        GradientDrawable background = new GradientDrawable();
        background.setColor(Color.rgb(241, 117, 44));
        background.setCornerRadius(18f);
        dropZone.setBackground(background);
        dropZone.setOnDragListener((view, event) -> {
            if (event.getAction() == DragEvent.ACTION_DRAG_ENTERED) {
                dropZone.setAlpha(.82f);
                return true;
            }
            if (event.getAction() == DragEvent.ACTION_DRAG_EXITED) {
                dropZone.setAlpha(1f);
                return true;
            }
            if (event.getAction() != DragEvent.ACTION_DROP) {
                return true;
            }
            dropZone.setAlpha(1f);
            ClipData data = event.getClipData();
            if (data == null || data.getItemCount() == 0) {
                return true;
            }
            String payload = String.valueOf(data.getItemAt(0).getText());
            String[] parts = payload.split("\\\\|", 3);
            if (parts.length != 3) {
                Toast.makeText(this, "Invalid widget payload", Toast.LENGTH_SHORT).show();
                return true;
            }
            dispatchScalableUiEvent(parts[0]);
            launchToPanel(parts[2], parts[1]);
            dispatchScalableUiEvent("widget_layout_hide_menu");
            Toast.makeText(this, "Widget placed", Toast.LENGTH_SHORT).show();
            finish();
            return true;
        });
        return dropZone;
    }

    private LinearLayout createVerticalShell(String heading, String subheading) {
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setGravity(Gravity.CENTER);
        root.setPadding(28, 24, 28, 24);
        GradientDrawable background = new GradientDrawable(
                GradientDrawable.Orientation.TL_BR,
                new int[] {Color.rgb(16, 25, 34), Color.rgb(30, 58, 66)});
        background.setCornerRadius(30f);
        root.setBackground(background);

        TextView title = new TextView(this);
        title.setText(heading);
        title.setTextColor(Color.WHITE);
        title.setTextSize(28f);
        title.setTypeface(Typeface.DEFAULT_BOLD);
        title.setGravity(Gravity.CENTER);
        root.addView(title, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));

        TextView subtitle = new TextView(this);
        subtitle.setText(subheading);
        subtitle.setTextColor(Color.rgb(188, 218, 224));
        subtitle.setTextSize(14f);
        subtitle.setGravity(Gravity.CENTER);
        subtitle.setPadding(0, 6, 0, 18);
        root.addView(subtitle, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));
        return root;
    }

    private LinearLayout createWidgetShell(String heading, String subheading) {
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setGravity(Gravity.CENTER);
        root.setPadding(28, 24, 28, 24);
        GradientDrawable background = new GradientDrawable();
        background.setColor(Color.rgb(241, 117, 44));
        background.setCornerRadius(30f);
        root.setBackground(background);

        TextView title = new TextView(this);
        title.setText(heading);
        title.setTextColor(Color.BLACK);
        title.setTextSize(28f);
        title.setTypeface(Typeface.DEFAULT_BOLD);
        title.setGravity(Gravity.CENTER);
        root.addView(title, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));

        TextView subtitle = new TextView(this);
        subtitle.setText(subheading);
        subtitle.setTextColor(Color.rgb(32, 32, 32));
        subtitle.setTextSize(16f);
        subtitle.setGravity(Gravity.CENTER);
        subtitle.setPadding(0, 6, 0, 18);
        root.addView(subtitle, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));
        return root;
    }

    private void addLaunchButton(LinearLayout root, LaunchTarget target) {
        Button button = createButton(target.label);
        button.setOnClickListener(v -> {
            Intent intent = new Intent(Intent.ACTION_MAIN);
            ComponentName component = ComponentName.unflattenFromString(target.component);
            intent.setComponent(component);
            intent.putExtra(EXTRA_TARGET_PANEL_ID, mSelectedPanelId);
            intent.setData(new Uri.Builder()
                    .scheme(TARGET_PANEL_URI_SCHEME)
                    .authority(TARGET_PANEL_URI_HOST)
                    .appendQueryParameter(TARGET_PANEL_URI_PARAM, mSelectedPanelId)
                    .build());
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK
                    | Intent.FLAG_ACTIVITY_CLEAR_TOP
                    | Intent.FLAG_ACTIVITY_SINGLE_TOP);
            startActivity(intent);
            finish();
        });
        root.addView(button, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));
    }

    private void addPanelTargetButton(LinearLayout root, PanelTarget target) {
        Button button = createButton(target.label);
        button.setOnClickListener(v -> {
            mSelectedPanelId = target.panelId;
            updateSelectedPanelStatus();
        });
        root.addView(button, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));
    }

    private TextView createSectionLabel(String text) {
        TextView label = new TextView(this);
        label.setText(text);
        label.setTextColor(Color.rgb(151, 212, 204));
        label.setTextSize(13f);
        label.setTypeface(Typeface.DEFAULT_BOLD);
        label.setGravity(Gravity.CENTER);
        label.setPadding(0, 4, 0, 4);
        return label;
    }

    private void updateSelectedPanelStatus() {
        if (mSelectedPanelStatus == null) {
            return;
        }
        String label = PANEL_TARGETS[0].label;
        for (PanelTarget target : PANEL_TARGETS) {
            if (target.panelId.equals(mSelectedPanelId)) {
                label = target.label;
                break;
            }
        }
        mSelectedPanelStatus.setText("Target panel: " + label);
    }

    private Button createButton(String label) {
        Button button = new Button(this);
        button.setText(label);
        button.setTextSize(16f);
        button.setAllCaps(false);
        return button;
    }

    private void styleMenuCardButton(Button button) {
        GradientDrawable background = new GradientDrawable();
        background.setColor(Color.rgb(241, 117, 44));
        background.setCornerRadius(18f);
        button.setBackground(background);
        button.setTextColor(Color.BLACK);
        button.setTypeface(Typeface.DEFAULT_BOLD);
    }

    private void styleSecondaryButton(Button button) {
        GradientDrawable background = new GradientDrawable();
        background.setColor(Color.rgb(28, 76, 24));
        background.setCornerRadius(16f);
        button.setBackground(background);
        button.setTextColor(Color.WHITE);
    }

    private TextView createMenuHint(String text) {
        TextView hint = new TextView(this);
        hint.setText(text);
        hint.setTextColor(Color.WHITE);
        hint.setTextSize(14f);
        hint.setGravity(Gravity.CENTER);
        hint.setPadding(0, 8, 0, 14);
        return hint;
    }

    private void addWidgetCard(LinearLayout root, String label, LaunchTarget target,
            String panelId, String eventId) {
        Button button = createButton(label);
        styleMenuCardButton(button);
        button.setTextSize(22f);
        button.setOnClickListener(v -> {
            dispatchScalableUiEvent(eventId);
            launchToPanel(target.component, panelId);
        });
        button.setOnLongClickListener(v -> {
            ClipData data = ClipData.newPlainText("scalableui-widget",
                    eventId + "|" + panelId + "|" + target.component);
            v.startDragAndDrop(data, new View.DragShadowBuilder(v), null, View.DRAG_FLAG_GLOBAL);
            return true;
        });
        root.addView(button, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));
    }

    private void addPatternButton(LinearLayout root, String label, String eventId,
            LaunchTarget... targets) {
        Button button = createButton(label);
        styleSecondaryButton(button);
        button.setTextSize(15f);
        button.setOnClickListener(v -> applyWidgetLayout(eventId, targets));
        root.addView(button, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));
    }

    private void applyWidgetLayout(String eventId, LaunchTarget... targets) {
        dispatchScalableUiEvent(eventId);
        for (LaunchTarget target : targets) {
            launchToPanel(target.component, target.defaultPanelId);
        }
        dispatchScalableUiEvent("widget_layout_hide_menu");
        finish();
    }

    private void launchToPanel(String componentString, String panelId) {
        Intent intent = new Intent(Intent.ACTION_MAIN);
        ComponentName component = ComponentName.unflattenFromString(componentString);
        intent.setComponent(component);
        intent.putExtra(EXTRA_TARGET_PANEL_ID, panelId);
        intent.setData(new Uri.Builder()
                .scheme(TARGET_PANEL_URI_SCHEME)
                .authority(TARGET_PANEL_URI_HOST)
                .appendQueryParameter(TARGET_PANEL_URI_PARAM, panelId)
                .build());
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK
                | Intent.FLAG_ACTIVITY_CLEAR_TOP
                | Intent.FLAG_ACTIVITY_SINGLE_TOP);
        startActivity(intent);
    }

    private void dispatchScalableUiEvent(String eventId) {
        Intent intent = new Intent(ACTION_SCALABLEUI_PANEL_EVENT);
        intent.putExtra(EXTRA_SCALABLEUI_EVENT_ID, eventId);
        intent.putExtra(EXTRA_SCALABLEUI_EVENT_TOKENS, "");
        intent.setPackage("com.android.systemui");
        sendBroadcast(intent);
    }

    private static final LaunchTarget[] MENU_TARGETS = new LaunchTarget[] {
__MENU_TARGETS__
    };

    private static final LaunchTarget MAP_WIDGET = new LaunchTarget(
            "Widget A Map", "com.android.car.scalableui.hmi.map/.MapActivity", "widget_a_panel");
    private static final LaunchTarget CALENDAR_WIDGET = new LaunchTarget(
            "Widget B Calendar", "com.android.car.scalableui.hmi.calendar/.CalendarActivity",
            "widget_b_panel");
    private static final LaunchTarget WEATHER_WIDGET = new LaunchTarget(
            "Widget C Weather", "com.android.car.scalableui.hmi.weather/.WeatherActivity",
            "widget_c_panel");
    private static final LaunchTarget MEDIA_WIDGET = new LaunchTarget(
            "Widget D Media", "com.android.car.scalableui.hmi.media/.MediaActivity",
            "widget_d_panel");
    private static final LaunchTarget TASKS_WIDGET = new LaunchTarget(
            "Widget E Tasks", "com.android.car.scalableui.hmi.tasks/.TaskActivity",
            "widget_e_panel");
    private static final LaunchTarget INTERACTIVE_WIDGET = new LaunchTarget(
            "Widget F Interactive", "com.android.car.scalableui.hmi.widgets/.WidgetActivity",
            "widget_f_panel");
    private static final LaunchTarget WIDGET_MENU_COMPONENT = new LaunchTarget(
            "Widget Layout Menu", "com.android.car.scalableui.hmi.widgetmenu/.WidgetMenuActivity",
            "widget_picker_panel");
    private static final LaunchTarget WIDGET_MENU_BUTTON_WIDGET = new LaunchTarget(
            "Widget Layout Button",
            "com.android.car.scalableui.hmi.widgetmenubutton/.WidgetMenuButtonActivity",
            "widget_menu_button_panel");
    private static final LaunchTarget DROP_ZONE_WIDGET = new LaunchTarget(
            "Widget Drop Zone",
            "com.android.car.scalableui.hmi.widgetdropzone/.WidgetDropZoneActivity",
            "widget_drop_zone_panel");

    private static final PanelTarget[] PANEL_TARGETS = new PanelTarget[] {
            new PanelTarget("Workspace", "workspace_panel"),
            new PanelTarget("Controls", "widget_controls_panel"),
            new PanelTarget("Status", "workspace_status_panel"),
            new PanelTarget("Fullscreen", "app_panel"),
    };

    private static final class LaunchTarget {
        final String label;
        final String component;
        final String defaultPanelId;

        LaunchTarget(String label, String component) {
            this(label, component, "");
        }

        LaunchTarget(String label, String component, String defaultPanelId) {
            this.label = label;
            this.component = component;
            this.defaultPanelId = defaultPanelId;
        }
    }

    private static final class PanelTarget {
        final String label;
        final String panelId;

        PanelTarget(String label, String panelId) {
            this.label = label;
            this.panelId = panelId;
        }
    }

    private static final class SyntheticMapView extends View {
        private final Paint mPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        private final Path mPath = new Path();

        SyntheticMapView(Activity activity) {
            super(activity);
            setBackgroundColor(Color.rgb(221, 231, 224));
        }

        @Override
        protected void onDraw(Canvas canvas) {
            super.onDraw(canvas);
            int width = getWidth();
            int height = getHeight();

            mPaint.setStyle(Paint.Style.FILL);
            mPaint.setColor(Color.rgb(198, 220, 205));
            canvas.drawRect(0, 0, width, height, mPaint);

            mPaint.setColor(Color.rgb(169, 205, 178));
            canvas.drawRoundRect(new RectF(width * .04f, height * .08f, width * .34f,
                    height * .38f), 28, 28, mPaint);
            canvas.drawRoundRect(new RectF(width * .68f, height * .52f, width * .96f,
                    height * .92f), 28, 28, mPaint);

            mPaint.setStyle(Paint.Style.STROKE);
            mPaint.setStrokeCap(Paint.Cap.ROUND);
            mPaint.setStrokeWidth(34f);
            mPaint.setColor(Color.rgb(244, 239, 218));
            mPath.reset();
            mPath.moveTo(width * .02f, height * .68f);
            mPath.cubicTo(width * .28f, height * .54f, width * .36f, height * .22f,
                    width * .62f, height * .28f);
            mPath.cubicTo(width * .80f, height * .32f, width * .78f, height * .74f,
                    width * .98f, height * .78f);
            canvas.drawPath(mPath, mPaint);

            mPaint.setStrokeWidth(10f);
            mPaint.setColor(Color.rgb(255, 194, 71));
            canvas.drawPath(mPath, mPaint);

            mPaint.setStrokeWidth(18f);
            mPaint.setColor(Color.rgb(235, 235, 229));
            canvas.drawLine(width * .18f, height * .02f, width * .90f, height * .96f, mPaint);
            canvas.drawLine(width * .04f, height * .42f, width * .96f, height * .18f, mPaint);
            canvas.drawLine(width * .10f, height * .90f, width * .88f, height * .44f, mPaint);

            mPaint.setStyle(Paint.Style.FILL);
            mPaint.setColor(Color.rgb(31, 83, 146));
            canvas.drawCircle(width * .52f, height * .50f, 16f, mPaint);
            mPaint.setColor(Color.rgb(14, 35, 48));
            mPaint.setTextSize(28f);
            mPaint.setTypeface(Typeface.DEFAULT_BOLD);
            canvas.drawText("Synthetic Map Sample", 28f, 42f, mPaint);
            mPaint.setTypeface(Typeface.DEFAULT);
            mPaint.setTextSize(18f);
            canvas.drawText("Bundled demo artwork, no external map tiles", 28f, 68f, mPaint);
        }
    }

    private static final class GBallView extends View {
        private final Paint mPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        private float mX;
        private float mY;
        private float mVx = 7f;
        private float mVy = 5f;

        GBallView(Activity activity) {
            super(activity);
            setBackgroundColor(Color.rgb(13, 21, 32));
        }

        @Override
        protected void onSizeChanged(int w, int h, int oldw, int oldh) {
            mX = w * .38f;
            mY = h * .42f;
        }

        @Override
        public boolean onTouchEvent(MotionEvent event) {
            if (event.getAction() == MotionEvent.ACTION_DOWN
                    || event.getAction() == MotionEvent.ACTION_MOVE) {
                mX = event.getX();
                mY = event.getY();
                invalidate();
                return true;
            }
            return true;
        }

        @Override
        protected void onDraw(Canvas canvas) {
            super.onDraw(canvas);
            int width = getWidth();
            int height = getHeight();
            float radius = Math.max(28f, Math.min(width, height) * .10f);
            mX += mVx;
            mY += mVy;
            if (mX < radius || mX > width - radius) {
                mVx = -mVx;
            }
            if (mY < radius || mY > height - radius) {
                mVy = -mVy;
            }
            mX = Math.max(radius, Math.min(width - radius, mX));
            mY = Math.max(radius, Math.min(height - radius, mY));

            mPaint.setStyle(Paint.Style.FILL);
            mPaint.setColor(Color.rgb(20, 34, 50));
            canvas.drawRoundRect(new RectF(18, 18, width - 18, height - 18), 36, 36, mPaint);
            mPaint.setColor(Color.rgb(76, 211, 194));
            canvas.drawCircle(mX, mY, radius, mPaint);
            mPaint.setColor(Color.WHITE);
            canvas.drawCircle(mX - radius * .28f, mY - radius * .32f, radius * .18f, mPaint);
            mPaint.setColor(Color.rgb(225, 240, 246));
            mPaint.setTextSize(28f);
            mPaint.setTypeface(Typeface.DEFAULT_BOLD);
            canvas.drawText("G Ball", 34f, 54f, mPaint);
            mPaint.setTypeface(Typeface.DEFAULT);
            mPaint.setTextSize(18f);
            canvas.drawText("Touch to reposition", 34f, 82f, mPaint);
            postInvalidateOnAnimation();
        }
    }
}
""".replace("__MENU_TARGETS__", menu_targets)
    files = {
        f"{base}/Android.bp": (
            copyright("//")
            + f"""
package {{
    default_applicable_licenses: ["Android-Apache-2.0"],
}}

java_library {{
    name: "ScalableUiHmiDemoCommon",
    srcs: ["common/src/**/*.java"],
    sdk_version: "current",
}}

runtime_resource_overlay {{
    name: "ScalableUiHmiFrameworkConfigRRO",
    resource_dirs: ["framework_rro/res"],
    certificate: "platform",
    manifest: "framework_rro/AndroidManifest.xml",
    system_ext_specific: true,
}}

{module_blocks}
"""
        ),
        f"{base}/common/src/com/android/car/scalableui/hmi/demo/common/DemoBaseActivity.java": java,
        f"{base}/framework_rro/AndroidManifest.xml": """\
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
          package="com.android.car.scalableui.hmi.framework.rro">
    <application android:hasCode="false" />
    <overlay
        android:targetPackage="android"
        android:isStatic="true"
        android:priority="900" />
</manifest>
""",
        f"{base}/framework_rro/res/values/config.xml": """\
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="config_recentsComponentName" translatable="false">com.android.car.scalableui.hmi.home/.NoOpRecentsActivity</string>
</resources>
""",
    }
    for app in DEMO_APPS:
        if app.kind == "HOME":
            files[f"{base}/apps/{app.key}/AndroidManifest.xml"] = f"""\
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
          package="{app.package}">
    <application
        android:theme="@android:style/Theme.Material.NoActionBar"
        android:label="{app.label}">
        <activity
            android:name=".{app.activity}"
            android:clearTaskOnLaunch="true"
            android:exported="true"
            android:excludeFromRecents="true"
            android:launchMode="singleTask"
            android:resizeableActivity="true"
            android:resumeWhilePausing="true"
            android:stateNotNeeded="true"
            android:label="{app.label}">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.HOME" />
                <category android:name="android.intent.category.SECONDARY_HOME" />
                <category android:name="android.intent.category.DEFAULT" />
            </intent-filter>
        </activity>
        <service
            android:name=".NoOpQuickStepService"
            android:permission="android.permission.STATUS_BAR_SERVICE"
            android:directBootAware="true"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.QUICKSTEP_SERVICE" />
            </intent-filter>
        </service>
        <activity
            android:name=".NoOpRecentsActivity"
            android:excludeFromRecents="true"
            android:exported="true"
            android:launchMode="singleInstance"
            android:resizeableActivity="true"
            android:stateNotNeeded="true" />
        <activity
            android:name=".HomeEditActivity"
            android:excludeFromRecents="true"
            android:exported="true"
            android:launchMode="singleTask"
            android:resizeableActivity="true"
            android:stateNotNeeded="true"
            android:label="Home layout editor" />
    </application>
</manifest>
"""
            files[
                f"{base}/apps/{app.key}/src/{app.package.replace('.', '/')}/NoOpRecentsActivity.java"
            ] = f"""\
package {app.package};

import android.app.Activity;
import android.graphics.Color;
import android.os.Bundle;
import android.view.View;

public final class NoOpRecentsActivity extends Activity {{
    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);
        View view = new View(this);
        view.setBackgroundColor(Color.BLACK);
        setContentView(view);
    }}
}}
"""
            files[
                f"{base}/apps/{app.key}/src/{app.package.replace('.', '/')}/NoOpQuickStepService.java"
            ] = f"""\
package {app.package};

import android.app.Service;
import android.content.Intent;
import android.graphics.Region;
import android.os.Bundle;
import android.os.IBinder;

import com.android.systemui.shared.recents.IOverviewProxy;

public final class NoOpQuickStepService extends Service {{
    @Override
    public IBinder onBind(Intent intent) {{
        return new IOverviewProxy.Stub() {{
            @Override
            public void onActiveNavBarRegionChanges(Region activeRegion) {{}}

            @Override
            public void onInitialize(Bundle params) {{}}

            @Override
            public void onOverviewToggle() {{}}

            @Override
            public void onOverviewShown(boolean triggeredFromAltTab) {{}}

            @Override
            public void onOverviewHidden(boolean triggeredFromAltTab,
                    boolean triggeredFromHomeKey) {{}}

            @Override
            public void onAssistantAvailable(boolean available, boolean longPressHomeEnabled) {{}}

            @Override
            public void onAssistantVisibilityChanged(float visibility) {{}}

            @Override
            public void onAssistantOverrideInvoked(int invocationType) {{}}

            @Override
            public void onSystemUiStateChanged(long stateFlags) {{}}

            @Override
            public void onRotationProposal(int rotation, boolean isValid) {{}}

            @Override
            public void disable(int displayId, int state1, int state2, boolean animate) {{}}

            @Override
            public void onSystemBarAttributesChanged(int displayId, int behavior) {{}}

            @Override
            public void onTransitionModeUpdated(int barMode, boolean checkBarModes) {{}}

            @Override
            public void onNavButtonsDarkIntensityChanged(float darkIntensity) {{}}

            @Override
            public void onNavigationBarLumaSamplingEnabled(int displayId, boolean enable) {{}}

            @Override
            public void enterStageSplitFromRunningApp(boolean leftOrTop) {{}}

            @Override
            public void onTaskbarToggled() {{}}

            @Override
            public void updateWallpaperVisibility(int displayId, boolean visible) {{}}

            @Override
            public void checkNavBarModes() {{}}

            @Override
            public void finishBarAnimations() {{}}

            @Override
            public void touchAutoDim(boolean reset) {{}}

            @Override
            public void transitionTo(int barMode, boolean animate) {{}}

            @Override
            public void appTransitionPending(boolean pending) {{}}
        }};
    }}
}}
"""
            files[
                f"{base}/apps/{app.key}/src/{app.package.replace('.', '/')}/HomeActivity.java"
            ] = home_activity_java(app.package)
            files[
                f"{base}/apps/{app.key}/src/{app.package.replace('.', '/')}/HomeEditActivity.java"
            ] = home_edit_activity_java(app.package)
            files[
                f"{base}/apps/{app.key}/src/{app.package.replace('.', '/')}/HomeLayoutStore.java"
            ] = home_layout_store_java(app.package)
        else:
            files[f"{base}/apps/{app.key}/AndroidManifest.xml"] = f"""\
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
          package="{app.package}">
    <application
        android:theme="@android:style/Theme.Material.NoActionBar"
        android:label="{app.label}">
        <activity
            android:name=".{app.activity}"
            android:exported="true"
            android:resizeableActivity="true"
            android:label="{app.label}">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
"""
        if app.kind != "HOME":
            files[f"{base}/apps/{app.key}/src/{app.package.replace('.', '/')}/{app.activity}.java"] = f"""\
package {app.package};

import com.android.car.scalableui.hmi.demo.common.DemoBaseActivity;

public final class {app.activity} extends DemoBaseActivity {{
    @Override
    protected int getDemoType() {{
        return DEMO_{app.kind};
    }}

    @Override
    protected String getDemoTitle() {{
        return "{app.label}";
    }}
}}
"""
    return files


def device_product_file(variant: Variant) -> str:
    return (
        copyright()
        + f"""

# Generated ScalableUI HMI product for: {variant.title}.
$(call inherit-product, device/generic/car/sdk_car_x86_64.mk)
$(call inherit-product, packages/services/Car/car_product/{variant.car_product_dir}/car_scalableui_hmi_{variant.product_suffix}.mk)

PRODUCT_NAME := {variant.product_name}
PRODUCT_DEVICE := emulator_car64_x86_64
PRODUCT_BRAND := Android
PRODUCT_MODEL := {variant.title} on x86_64 emulator

$(warning ${{PRODUCT_NAME}} is for ScalableUI HMI exploration only.)
"""
    )


def read_device_android_products() -> str:
    path = AAOS_ROOT / "device/generic/car/AndroidProducts.mk"
    try:
        import subprocess

        return subprocess.check_output(
            ["git", "-C", str(path.parent), "show", "HEAD:AndroidProducts.mk"],
            text=True,
        )
    except Exception:
        return path.read_text(encoding="utf-8")


def add_product_lines(base: str, variants: tuple[Variant, ...]) -> str:
    make_lines = [f"    $(LOCAL_DIR)/{v.product_name}.mk \\" for v in variants]
    lunch_lines = [f"    {v.product_name}-trunk_staging-userdebug \\" for v in variants]
    lines = base.splitlines()
    out: list[str] = []
    inserted_make = False
    inserted_lunch = False
    for line in lines:
        if not inserted_make and "sdk_car_cw_x86_64.mk" in line:
            out.extend(make_lines)
            inserted_make = True
        if not inserted_lunch and "sdk_car_cw_x86_64-trunk_staging-userdebug" in line:
            out.extend(lunch_lines)
            inserted_lunch = True
        out.append(line)
    if not inserted_make or not inserted_lunch:
        raise RuntimeError("Could not locate insertion points in AndroidProducts.mk")
    return "\n".join(out) + "\n"


def device_patch(variants: tuple[Variant, ...], patch_path: Path) -> None:
    base = read_device_android_products()
    updated = add_product_lines(base, variants)
    parts = [modify_patch("AndroidProducts.mk", base, updated)]
    for variant in variants:
        parts.append(new_file_patch(f"{variant.product_name}.mk", device_product_file(variant)))
    write(patch_path, "\n".join(parts))


def services_patch_for_variant(variant: Variant, patch_path: Path) -> None:
    parts = [
        new_file_patch(path, content)
        for path, content in sorted(rro_files(variant).items())
    ]
    write(patch_path, "\n".join(parts))


def services_demo_patch(patch_path: Path) -> None:
    parts = [
        new_file_patch(path, content)
        for path, content in sorted(demo_app_files().items())
    ]
    write(patch_path, "\n".join(parts))


def variant_readme(variant: Variant) -> str:
    panels = "\n".join(
        f"- `{p.panel_id}`: {p.title}, `{p.bounds[0]},{p.bounds[1]} - {p.bounds[2]},{p.bounds[3]}`"
        for p in variant.panels
    )
    use_cases = "\n".join(f"- {u}" for u in variant.use_cases)
    notes = "\n".join(f"- {n}" for n in variant.notes) or "- No special notes."
    return f"""\
# {variant.title}

## Summary

{variant.summary}

## Product

- Product: `{variant.product_name}`
- Lunch: `{variant.product_name}-trunk_staging-userdebug`
- RRO: `{variant.rro_name}`

## Use Cases

{use_cases}

## Panels

{panels}

## Apply This Variant Only

Run from the AAOS checkout root:

```bash
bash workdir/scalableui-poc/scripts/apply_hmi_variant.sh {variant.slug}
lunch {variant.product_name}-trunk_staging-userdebug
```

The script applies common ScalableUI routing patches, the common demo app patch,
the product patch for this variant, and the RRO patch for this variant.

## Notes

{notes}
"""


def variant_spec(variant: Variant) -> str:
    rows = "\n".join(
        f"| `{p.panel_id}` | {p.title} | `{component_display(p.component, p.role_kind)}` | "
        f"`{p.bounds[0]}` | `{p.bounds[1]}` | `{p.bounds[2]}` | `{p.bounds[3]}` | `{p.display_id}` |"
        for p in variant.panels
    )
    return f"""\
# {variant.title} Spec

## Intent

{variant.summary}

## Build Target

- `{variant.product_name}-trunk_staging-userdebug`

## Panel Table

| Panel | Label | Component | Left | Top | Right | Bottom | Display |
| --- | --- | --- | --- | --- | --- | --- | --- |
{rows}

## Routing

- Fixed panels are assigned through `config_default_activities`.
- Panels with multiple component names use a ScalableUI role string-array so
  user-launched apps can be routed into the same panel.
- `panel_app_grid` opens as the All apps overlay.
- `app_panel` is the `DEFAULT` launch-root fallback for generic apps.
- The common Launcher/SystemUI patches keep the All apps launch behavior aligned
  with the base PoC.

## Validation Checklist

1. Apply the variant patches.
2. Build the lunch target.
3. Confirm every fixed panel opens.
4. Open All apps and launch a non-fixed app.
5. Press Home and confirm overlays close.

## Variant Notes

{"\n".join(f"- {note}" for note in variant.notes) or "- No special notes."}
"""


def variant_wrapper(variant: Variant) -> str:
    return f"""\
#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../../../.." && pwd)"
exec "$ROOT_DIR/workdir/scalableui-poc/scripts/apply_hmi_variant.sh" "{variant.slug}"
"""


def suite_readme() -> str:
    rows = "\n".join(
        f"| `{v.slug}` | `{v.product_name}` | {v.title} |"
        for v in VARIANTS
    )
    return f"""\
# HMI Variant Suite

This directory contains generated patch packs for all HMI ideas described in
the wiki page `HMI_Pattern_Ideas_ja.md`.

## Variants

| Variant | Product | HMI |
| --- | --- | --- |
{rows}

## Apply All Variants

Run from the AAOS checkout root:

```bash
bash workdir/scalableui-poc/scripts/apply_hmi_suite.sh
```

After applying the suite, choose a product at build time:

```bash
lunch sdk_car_scalableui_map_first_x86_64-trunk_staging-userdebug
```

## Apply One Variant

```bash
bash workdir/scalableui-poc/scripts/apply_hmi_variant.sh map-first
lunch sdk_car_scalableui_map_first_x86_64-trunk_staging-userdebug
```

The suite is better when you want every HMI available in one checkout. The
single-variant script is better when you want a smaller patch surface.
"""


def generate() -> None:
    write(REPO / "hmi-variants/README.md", suite_readme())
    services_demo_patch(
        REPO / "common/patches/packages-services-Car/0001-add-scalableui-hmi-demo-apps.patch"
    )
    device_patch(
        VARIANTS,
        REPO / "common/patches/device-generic-car/0001-add-scalableui-hmi-suite-products.patch",
    )
    for variant in VARIANTS:
        variant_dir = REPO / "variants" / variant.slug
        if variant_dir.exists():
            shutil.rmtree(variant_dir)
        write(variant_dir / "README.md", variant_readme(variant))
        write(variant_dir / "docs/hmi_spec_ja.md", variant_spec(variant))
        write(variant_dir / "scripts/apply_patches.sh", variant_wrapper(variant), mode=0o755)
        services_patch_for_variant(
            variant,
            variant_dir
            / "patches/packages-services-Car"
            / f"0001-add-scalableui-hmi-{variant.product_suffix}-rro.patch",
        )
        device_patch(
            (variant,),
            variant_dir
            / "patches/device-generic-car"
            / f"0001-add-{variant.product_name}-product.patch",
        )


if __name__ == "__main__":
    generate()
