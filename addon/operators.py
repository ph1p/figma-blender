import bpy
import asyncio
import os
from bpy.types import Operator
from .socket_server import server, get_element
from .properties import globalDict

class FIGMA_OT_Server(Operator):
    """Start/Stop the websocket server"""
    bl_idname = "figma.server"
    bl_label = "Start server"

    @classmethod
    def get_server(cls):
        return globalDict.get("server_task")

    def execute(self, context):
        return self.invoke(context, None)

    def invoke(self, context, event):
        from . import process_asyncio_events

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            print("Figma addon: No event loop found, creating new one")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if not globalDict.get("is_started", False):
            print("Figma addon: Starting server (manual)")

            globalDict["server_task"] = asyncio.ensure_future(server())
            globalDict["is_started"] = True

            if not bpy.app.timers.is_registered(process_asyncio_events):
                bpy.app.timers.register(process_asyncio_events, first_interval=0.1)

            print(f"Figma addon: Server task created: {globalDict['server_task']}")

            if context.area:
                context.area.tag_redraw()
            return {'FINISHED'}
        else:
            print("Figma addon: Stopping server (manual)")
            if globalDict.get("server_task"):
                try:
                    globalDict["server_task"].cancel()
                    print("Figma addon: Server task cancelled")
                except Exception as e:
                    print(f"Figma addon: Error cancelling task: {e}")

            globalDict["is_started"] = False
            globalDict["connected"] = None
            globalDict["plugin_connected"] = False
            globalDict["server_task"] = None

            if context.area:
                context.area.tag_redraw()
            return {'FINISHED'}


class FIGMA_OT_OpenBrowser(Operator):
    """Open file browser to select folder for textures"""
    bl_idname = "figma.open_browser"
    bl_label = "Choose Folder"

    directory: bpy.props.StringProperty(  # type: ignore
        name="Folder Path",
        description="Choose a folder to save textures",
        subtype='DIR_PATH'
    )

    def execute(self, context):
        if self.directory and os.path.isdir(self.directory):
            context.scene.figma.folder_path = self.directory
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class FIGMA_OT_add_to_scene(Operator):
    """Add or update selected element from Figma"""
    bl_idname = "figma.add_to_scene"
    bl_label = "Add to scene"

    def execute(self, context):
        figma = context.scene.figma

        if figma.elements and figma.elements != "":
            element_name = None
            for item in globalDict.get("elements", []):
                if item[0] == figma.elements:
                    element_name = item[1]
                    break

            if element_name:
                self.report({'INFO'}, f"Fetching texture: {element_name}...")
            else:
                self.report({'INFO'}, "Fetching texture...")

            get_element(figma.elements)
        else:
            self.report({'WARNING'}, "No element selected")

        return {'FINISHED'}


class FIGMA_OT_InstallDeps(Operator):
    """Manually install websockets dependency"""
    bl_idname = "figma.install_deps"
    bl_label = "Install Dependencies"

    def execute(self, context):
        from .packages import install
        from .properties import globalDict

        self.report({'INFO'}, "Installing websockets... This may take a moment.")
        print("Figma addon: Manual dependency installation started")

        success = install()

        if success:
            globalDict["deps_installed"] = True
            self.report({'INFO'}, "Dependencies installed! Please restart Blender.")
            print("Figma addon: Manual installation successful - restart Blender")
        else:
            globalDict["deps_installed"] = False
            self.report({'ERROR'}, "Failed to install dependencies. Check console for details.")
            print("Figma addon: Manual installation failed - check console")

        return {'FINISHED'}


class FIGMA_OT_TestServer(Operator):
    """Test if the WebSocket server is responding"""
    bl_idname = "figma.test_server"
    bl_label = "Test Server Connection"

    def execute(self, context):
        from .properties import globalDict
        import socket

        if not globalDict.get("is_started", False):
            self.report({'ERROR'}, "Server is not running. Please start it first.")
            return {'CANCELLED'}

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', 1410))
            sock.close()

            if result == 0:
                self.report({'INFO'}, "✓ Server is listening on port 1410")
                print("Figma addon: Server test - Port 1410 is open")

                try:
                    loop = asyncio.get_event_loop()
                    print(f"Figma addon: Event loop status - Running: {loop.is_running()}, Closed: {loop.is_closed()}")

                    if globalDict.get("server_task"):
                        task = globalDict["server_task"]
                        print(f"Figma addon: Server task status - Done: {task.done()}, Cancelled: {task.cancelled()}")
                        if task.done() and not task.cancelled():
                            try:
                                exc = task.exception()
                                if exc:
                                    print(f"Figma addon: Server task has exception: {exc}")
                                    self.report({'ERROR'}, f"Server task error: {exc}")
                                    return {'CANCELLED'}
                            except:
                                pass
                    else:
                        print("Figma addon: No server task found")
                        self.report({'WARNING'}, "Server task not found")

                except Exception as e:
                    print(f"Figma addon: Error checking event loop: {e}")

                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "✗ Port 1410 is not responding")
                print(f"Figma addon: Server test - Port check failed with code {result}")
                return {'CANCELLED'}

        except Exception as e:
            self.report({'ERROR'}, f"Test failed: {e}")
            print(f"Figma addon: Server test error: {e}")
            return {'CANCELLED'}