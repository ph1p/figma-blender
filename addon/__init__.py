import bpy
import asyncio
from bpy.types import Scene, AddonPreferences
from bpy.props import PointerProperty, BoolProperty

from .packages import check_deps_on_startup
from .properties import FigmaProperties
from .panels import (
    FIGMA_PT_elements,
    FIGMA_PT_folder_path,
    FIGMA_PT_main,
)
from .operators import FIGMA_OT_add_to_scene, FIGMA_OT_Server, FIGMA_OT_OpenBrowser, FIGMA_OT_InstallDeps, FIGMA_OT_TestServer

bl_info = {
    "name": "Figma",
    "author": "Philip Stapelfeldt",
    "location": "View3D > Panel > Figma",
    "version": (0, 0, 4),
    "blender": (2, 81, 0),
    "description": "Import textures from figma",
    "warning": "",
    "doc_url": "https://github.com/ph1p/figma-blender",
    "support": "COMMUNITY",
    "category": "3D View",
}

class FigmaAddonPreferences(AddonPreferences):
    bl_idname = __package__

    auto_start_server: bool = BoolProperty(
        name="Auto-start Server",
        description="Automatically start the WebSocket server when Blender starts",
        default=True
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "auto_start_server")

classes = (
    FigmaAddonPreferences,
    FIGMA_OT_Server,
    FIGMA_OT_InstallDeps,
    FIGMA_OT_TestServer,
    FigmaProperties,
    FIGMA_PT_main,
    FIGMA_PT_elements,
    FIGMA_PT_folder_path,
    FIGMA_OT_OpenBrowser,
    FIGMA_OT_add_to_scene,
)

def setup_asyncio():
    """Sets up AsyncIO to run properly on each platform."""
    import sys

    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

def process_asyncio_events():
    """Process asyncio events on a timer."""
    from .properties import globalDict

    if globalDict.get("is_started", False):
        try:
            loop = asyncio.get_event_loop()
            loop.stop()
            loop.run_forever()
        except Exception as e:
            if globalDict.get("is_started", False):
                print(f"Figma addon: Error processing asyncio events: {e}")

        try:
            for window in bpy.context.window_manager.windows:
                for area in window.screen.areas:
                    if area.type == 'VIEW_3D':
                        area.tag_redraw()
                        break
        except:
            pass

        return 0.1  # Keep running every 0.1 seconds
    return None  # Stop timer when server is not running

def auto_start_server_if_enabled():
    """Auto-start server if preference is enabled and dependencies are installed."""
    from .properties import globalDict

    if not globalDict.get("deps_installed", False):
        if globalDict.get("deps_checking", False):
            return 1.0
        return None

    preferences = bpy.context.preferences.addons.get(__package__)
    if preferences and preferences.preferences.auto_start_server:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if not globalDict.get("is_started", False):
            from .socket_server import server

            print("Figma addon: Auto-starting server")

            globalDict["server_task"] = asyncio.ensure_future(server())
            globalDict["is_started"] = True

            if not bpy.app.timers.is_registered(process_asyncio_events):
                bpy.app.timers.register(process_asyncio_events, first_interval=0.1)

            print(f"Figma addon: Server auto-started successfully")

    return None

def register():
    setup_asyncio()

    for cls in classes:
        bpy.utils.register_class(cls)

    Scene.figma = PointerProperty(type=FigmaProperties)

    check_deps_on_startup()
    bpy.app.timers.register(auto_start_server_if_enabled, first_interval=1.0)

def unregister():
    from .socket_server import stop_server

    # Disabling must release port 1410, or re-enabling cannot bind.
    stop_server()

    if bpy.app.timers.is_registered(process_asyncio_events):
        bpy.app.timers.unregister(process_asyncio_events)

    del Scene.figma

    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()