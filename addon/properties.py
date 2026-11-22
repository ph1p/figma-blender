import bpy

from bpy.types import PropertyGroup
from bpy.props import EnumProperty, StringProperty

globalDict = {
    "server_task": None,
    "ws_server": None,
    "connected": None,
    "is_started": False,
    # True only once the socket is bound; is_started flips before that.
    "is_listening": False,
    "is_loading": False,
    "plugin_connected": False,
    "elements": [],
}


def get_items(self, context):
    return globalDict["elements"]


class FigmaProperties(PropertyGroup):
    folder_path: StringProperty(default="")
    page_name: StringProperty(default="")
    elements: EnumProperty(
        name="Elements", description="Found elements in figma file", items=get_items
    )
