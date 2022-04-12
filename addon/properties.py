import bpy

from bpy.types import PropertyGroup
from bpy.props import EnumProperty, BoolProperty, CollectionProperty, StringProperty

globalDict = {
    "server_task": None,
    "connected": None,
    "is_started": False,
    "is_loading": False,
    "plugin_connected": False,
    "deps_installed": False,
    "elements": []
}


def get_items(self, context):
    return globalDict["elements"]


class FigmaProperties(PropertyGroup):
    folder_path: StringProperty(default="")
    page_name: StringProperty(default="")
    elements: EnumProperty(
        name='Elements',
        description='Found elements in figma file',
        items=get_items)
