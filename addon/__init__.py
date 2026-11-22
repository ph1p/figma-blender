import bpy
import asyncio
from bpy.types import Scene, AddonPreferences
from bpy.props import PointerProperty, BoolProperty

from .properties import FigmaProperties
from .panels import (
    FIGMA_PT_elements,
    FIGMA_PT_folder_path,
    FIGMA_PT_main,
)
from .operators import FIGMA_OT_add_to_scene, FIGMA_OT_Server, FIGMA_OT_OpenBrowser, FIGMA_OT_TestServer

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
    """Process asyncio events on a timer.

    Register with persistent=True. Blender drops non-persistent timers when a
    file is loaded, which would leave the socket open with nothing pumping it.
    """
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
        except Exception:
            pass

        return 0.1  # Keep running every 0.1 seconds
    return None  # Stop timer when server is not running

def auto_start_server_if_enabled():
    """Auto-start server if preference is enabled."""
    from .properties import globalDict

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
                bpy.app.timers.register(process_asyncio_events, first_interval=0.1, persistent=True)

            print("Figma addon: Server auto-started successfully")

    return None

def register():
    setup_asyncio()

    for cls in classes:
        bpy.utils.register_class(cls)

    Scene.figma = PointerProperty(type=FigmaProperties)

    bpy.app.timers.register(auto_start_server_if_enabled, first_interval=1.0, persistent=True)

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