# context.area: VIEW_3D
import bpy
import asyncio

from bpy.types import Scene
from bpy.props import PointerProperty
from bpy.app.handlers import depsgraph_update_pre

from .packages import check_deps_on_startup
from .properties import FigmaProperties, globalDict
from .panels import (
    FIGMA_PT_elements,
    FIGMA_PT_folder_path,
    FIGMA_PT_main,
    FIGMA_PT_server,
)
from .operators import FIGMA_OT_add_to_scene, FIGMA_OT_Server, FIGMA_OT_OpenBrowser
from .async_loop import *

bl_info = {
    "name": "Figma",
    "author": "Philip Stapelfeldt",
    "location": "View3D > Panel > Figma",
    "version": (0, 0, 3),
    "blender": (2, 81, 0),
    "description": "Import textures from figma",
    "warning": "Blender does not respond for a few seconds when first started because dependencies are being installed",
    "doc_url": "https://github.com/ph1p/figma-blender",
    "support": "COMMUNITY",
    "category": "3D View",
}


classes = (
    AsyncLoopModalOperator,
    FIGMA_OT_Server,
    FigmaProperties,
    FIGMA_PT_main,
    FIGMA_PT_elements,
    FIGMA_PT_folder_path,
    FIGMA_PT_server,
    FIGMA_OT_OpenBrowser,
    FIGMA_OT_add_to_scene,
)


def register():
    setup_asyncio_executor()

    for cls in classes:
        bpy.utils.register_class(cls)

    depsgraph_update_pre.append(check_deps_on_startup)

    Scene.figma = PointerProperty(type=FigmaProperties)


def unregister():
    if not globalDict["server_task"] is None:
        globalDict["server_task"].cancel()
        bpy.context.scene.figma.is_started = False

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
