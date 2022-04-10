import bpy
import asyncio

from bpy.types import Scene
from bpy.props import PointerProperty
from bpy.app.handlers import depsgraph_update_pre

from .packages import check_deps_on_startup
from .properties import FigmaProperties, FrameItemGroup, globalDict
from .panels import FIGMA_PT_Panel
from .operators import FIGMA_OT_add_to_scene, FIGMA_OT_Server, FIGMA_OT_OpenBrowser
from .async_loop import *

bl_info = {
    "name": "Figma",
    "author": "Philip Stapelfeldt",
    "location": "View3D > Panel > Figma",
    "version": (0, 0, 1),
    "blender": (2, 81, 0),
    "description": "Import textures from figma",
    "warning": "Blender does not respond for a few seconds when first started because dependencies are being installed",
    "doc_url": "https://github.com/ph1p/figma-blender",
    "support": "COMMUNITY",
    "category": "3D View"
}


classes = (
    AsyncLoopModalOperator,
    FIGMA_OT_Server,
    FrameItemGroup,
    FigmaProperties,
    FIGMA_PT_Panel,
    FIGMA_OT_OpenBrowser,
    FIGMA_OT_add_to_scene
)

# @persistent
# def check_selected_objects(scene):
#     print(bpy.context.view_layer.objects.selected)


def register():
    setup_asyncio_executor()

    for cls in classes:
        bpy.utils.register_class(cls)

    # depsgraph_update_post.append(check_selected_objects)
    depsgraph_update_pre.append(check_deps_on_startup)

    Scene.figma = PointerProperty(type=FigmaProperties)


def unregister():
    if not globalDict["server_task"] is None:
        globalDict["server_task"].cancel()
        bpy.context.scene.figma.is_started = False

    # depsgraph_update_post.remove(check_selected_objects)
    try:
        depsgraph_update_pre.remove(check_deps_on_startup)
    except ValueError:
        print("already removed")

    del Scene.figma
    asyncio.get_event_loop().stop()

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()