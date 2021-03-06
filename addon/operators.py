import bpy
import asyncio
import os

from bpy.types import Operator
from .properties import globalDict

from .socket_server import get_element, server
from .async_loop import *


class FIGMA_OT_add_to_scene(Operator):
    """Add frame to scene"""
    bl_idname = "figma.add_to_scene"
    bl_label = "Add to scene"

    @classmethod
    def poll(cls, context):
        return not globalDict["is_loading"]

    def execute(self, context):
        get_element(context.scene.figma.elements)

        context.area.tag_redraw()

        return {'FINISHED'}


class FIGMA_OT_Server(Operator):
    """Start/Stop the websocket server"""
    bl_idname = "figma.server"
    bl_label = "Start server"

    def execute(self, context):
        globalDict["is_loading"] = False

        if not globalDict["is_started"]:
            globalDict["server_task"] = asyncio.ensure_future(server())
            ensure_async_loop()
            globalDict["is_started"] = True
        else:
            globalDict["server_task"].cancel()
            asyncio.get_event_loop().stop()
            globalDict["is_started"] = False
            globalDict["connected"] = None

        context.area.tag_redraw()

        return {'FINISHED'}


class FIGMA_OT_OpenBrowser(Operator):
    """Open file browser to choose folder"""
    bl_idname = "figma.open_browser"
    bl_label = "Open folder"

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        context.scene.figma.folder_path = os.path.dirname(self.filepath)
        bpy.context.area.tag_redraw()

        return {'FINISHED'}

    def invoke(self, context, event):

        context.window_manager.fileselect_add(self)

        return {'RUNNING_MODAL'}
