import bpy

from bpy.types import PropertyGroup
from bpy.props import EnumProperty, BoolProperty, CollectionProperty, StringProperty

globalDict = {
    "server_task": None,
    "connected": set()
}


def get_items(self, context):
    items = []
    for item in bpy.context.scene.figma.items:
        items.append((item.id, item.name, ""))
    return items


class FrameItemGroup(bpy.types.PropertyGroup):
    id: StringProperty()
    name: StringProperty()


class FigmaProperties(PropertyGroup):
    items: CollectionProperty(type=FrameItemGroup)
    folder_path: StringProperty(default="")
    page_name: StringProperty(default="")

    elements: EnumProperty(
        name='Elements',
        description='Found elements in figma file',
        items=get_items)

    is_started: BoolProperty(default=False)

    is_loading: BoolProperty(default=False)

    plugin_connected: BoolProperty(default=False)

    deps_installed: BoolProperty(default=False)
