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
    DemoApp("map", "ScalableUiHmiMapDemoApp", "com.android.car.scalableui.hmi.map", "MapActivity", "ScalableUI Map", "MAP"),
    DemoApp("gball", "ScalableUiHmiGBallDemoApp", "com.android.car.scalableui.hmi.gball", "GBallActivity", "G Ball", "GBALL"),
    DemoApp("widgets", "ScalableUiHmiWidgetsDemoApp", "com.android.car.scalableui.hmi.widgets", "WidgetActivity", "ScalableUI Widgets", "WIDGET"),
    DemoApp("panel_menu", "ScalableUiHmiPanelMenuDemoApp", "com.android.car.scalableui.hmi.panelmenu", "PanelMenuActivity", "ScalableUI Panel Menu", "PANEL_MENU"),
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
DEMO_ACTIVITY_TO_KEY = {
    "MapPanelActivity": "map",
    "GBallActivity": "gball",
    "WidgetPanelActivity": "widgets",
    "PanelMenuActivity": "panel_menu",
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
PANEL_MENU_COMPONENT = DEMO_BY_KEY["panel_menu"].component
CALENDAR_COMPONENT = "com.android.calendar/.AllInOneActivity"
RADIO_COMPONENT = "com.android.car.radio/.RadioActivity"
APP_GRID_COMPONENT = "com.android.car.carlauncher/.AppGridActivity"


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


@dataclass(frozen=True)
class Variant:
    slug: str
    title: str
    product_suffix: str
    summary: str
    use_cases: tuple[str, ...]
    panels: tuple[Panel, ...]
    notes: tuple[str, ...] = ()

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
            "An interactive left menu launches map, G Ball, widget, media, and task apps into "
            "one ScalableUI workspace panel so users can swap the panel content at runtime."
        ),
        use_cases=(
            "runtime panel app swapping",
            "widget interaction demo",
            "map and G Ball sample validation",
        ),
        panels=(
            Panel(
                "panel_menu",
                "Panel Menu",
                PANEL_MENU_COMPONENT,
                ("2%", "3%", "22%", "97%"),
                55,
            ),
            Panel(
                "workspace_panel",
                "Interactive Workspace",
                (
                    WIDGET_COMPONENT,
                    MAP_COMPONENT,
                    GBALL_COMPONENT,
                    demo_activity("MediaPanelActivity"),
                    demo_activity("TaskPanelActivity"),
                ),
                ("24%", "3%", "98%", "68%"),
                35,
                corner="24dp",
            ),
            Panel(
                "widget_controls_panel",
                "Widget Controls",
                demo_activity("ControlsPanelActivity"),
                ("24%", "72%", "60%", "97%"),
                42,
                corner="22dp",
            ),
            Panel(
                "workspace_status_panel",
                "Workspace Status",
                demo_activity("StatusPanelActivity"),
                ("62%", "72%", "98%", "97%"),
                43,
                corner="22dp",
            ),
        ),
        notes=(
            "workspace_panel uses a role string-array so multiple apps can be routed to one panel.",
            "Panel Menu starts the selected component; ScalableUI routes it into workspace_panel.",
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


def panel_xml(panel: Panel) -> str:
    left, top, right, bottom = panel.bounds
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
    return dedent(
        f"""\
        <?xml version="1.0" encoding="utf-8"?>
        <Panel id="{panel.panel_id}" defaultVariant="@id/opened" role="{role}" displayId="{panel.display_id}">
            <Variant id="@+id/opened">
                <Layer layer="@integer/{layer}"/>
                <Visibility isVisible="true"/>
                <Bounds left="{left}" top="{top}" right="{right}" bottom="{bottom}"/>{corner}{background}
            </Variant>
            <Variant id="@+id/closed">
                <Layer layer="@integer/{layer}"/>
                <Visibility isVisible="false"/>
                <Bounds left="0" top="100%" right="100%" bottom="200%"/>
            </Variant>
        </Panel>
        """
    )


def app_panel_xml(variant: Variant) -> str:
    if variant.slug == "app-with-rail":
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


def app_grid_xml(default_open: bool = False) -> str:
    default = "opened" if default_open else "closed"
    return dedent(
        f"""\
        <?xml version="1.0" encoding="utf-8"?>
        <Panel id="panel_app_grid" defaultVariant="@id/{default}" role="@string/appgrid_componentName" displayId="0">
            <Variant id="@+id/opened">
                <Layer layer="@integer/app_grid_panel_layer"/>
                <Visibility isVisible="true"/>
                <Bounds left="0" top="0" right="100%" bottom="100%"/>
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
    demo_packages = " \\\n    ".join(app.module for app in DEMO_APPS)
    panel_items = "\n".join(f"        <item>@xml/{p.panel_id}</item>" for p in variant.panels)
    default_items = "\n".join(
        f"        <item>{p.panel_id};{default_component(p.component)}</item>"
        for p in variant.panels
        if p.role_kind == "activity" and default_component(p.component)
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
        files[f"{rro_base}/res/xml/{panel.panel_id}.xml"] = panel_xml(panel)
    files[f"{rro_base}/res/xml/app_panel.xml"] = app_panel_xml(variant)
    files[f"{rro_base}/res/xml/panel_app_grid.xml"] = app_grid_xml(
        default_open=variant.slug == "app-grid-hub"
    )
    return files


def demo_app_files() -> dict[str, str]:
    base = "car_product/scalableui_hmi_demo_apps"
    module_blocks = "\n".join(
        f"""\
android_app {{
    name: "{app.module}",
    srcs: ["apps/{app.key}/src/**/*.java"],
    manifest: "apps/{app.key}/AndroidManifest.xml",
    certificate: "platform",
    sdk_version: "current",
    system_ext_specific: true,
    privileged: true,
    static_libs: ["ScalableUiHmiDemoCommon"],
}}
"""
        for app in DEMO_APPS
    )
    menu_targets = "\n".join(
        f'            new LaunchTarget("{DEMO_BY_KEY[key].label}", "{DEMO_BY_KEY[key].component}"),'
        for key in ("widgets", "map", "gball", "media", "tasks")
    )
    java = """\
package com.android.car.scalableui.hmi.demo.common;

import android.app.Activity;
import android.content.ComponentName;
import android.content.Intent;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.RectF;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.os.Bundle;
import android.view.Gravity;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.SeekBar;
import android.widget.Switch;
import android.widget.TextView;

public abstract class DemoBaseActivity extends Activity {
    protected static final int DEMO_INFO = 0;
    protected static final int DEMO_MAP = 1;
    protected static final int DEMO_GBALL = 2;
    protected static final int DEMO_WIDGET = 3;
    protected static final int DEMO_PANEL_MENU = 4;

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

    private LinearLayout createPanelMenu() {
        LinearLayout root = createVerticalShell("Panel Menu", "Swap the workspace panel");
        for (LaunchTarget target : MENU_TARGETS) {
            addLaunchButton(root, target);
        }
        return root;
    }

    private LinearLayout createWidgetPanel() {
        LinearLayout root = createVerticalShell("Interactive Widgets", "Tap, slide, and toggle");

        TextView status = new TextView(this);
        status.setText("Cabin: 22 C  |  Fan: 35%  |  Drive mode: Comfort");
        status.setTextColor(Color.WHITE);
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
        quiet.setTextColor(Color.rgb(222, 238, 246));
        quiet.setTextSize(18f);
        quiet.setPadding(0, 18, 0, 18);
        root.addView(quiet, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT));

        Button action = createButton("Apply widget layout");
        action.setOnClickListener(v -> status.setText(
                quiet.isChecked() ? "Quiet widget layout applied" : "Widget layout applied"));
        root.addView(action);
        return root;
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

    private void addLaunchButton(LinearLayout root, LaunchTarget target) {
        Button button = createButton(target.label);
        button.setOnClickListener(v -> {
            Intent intent = new Intent(Intent.ACTION_MAIN);
            ComponentName component = ComponentName.unflattenFromString(target.component);
            intent.setComponent(component);
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            startActivity(intent);
        });
        root.addView(button, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));
    }

    private Button createButton(String label) {
        Button button = new Button(this);
        button.setText(label);
        button.setTextSize(16f);
        button.setAllCaps(false);
        return button;
    }

    private static final LaunchTarget[] MENU_TARGETS = new LaunchTarget[] {
__MENU_TARGETS__
    };

    private static final class LaunchTarget {
        final String label;
        final String component;

        LaunchTarget(String label, String component) {
            this.label = label;
            this.component = component;
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

{module_blocks}
"""
        ),
        f"{base}/common/src/com/android/car/scalableui/hmi/demo/common/DemoBaseActivity.java": java,
    }
    for app in DEMO_APPS:
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
