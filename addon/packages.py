import subprocess
import sys
import bpy
import asyncio

from importlib import util
from bpy.app.handlers import persistent, depsgraph_update_pre
from .properties import globalDict


@persistent
def check_deps_on_startup(scene):
    """Check for dependencies and install missing"""
    if scene is not None:
        print("install...")
        globalDict["deps_installed"] = False
        websockets_find = util.find_spec('websockets')

        if websockets_find is None:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(install())

        globalDict["deps_installed"] = True
        if not bpy.context.area is None:
            bpy.context.area.tag_redraw()

        depsgraph_update_pre.remove(check_deps_on_startup)


async def install():
    py_exec = str(sys.executable)
    subprocess.call([str(py_exec), "-m", "ensurepip"])
    subprocess.call([str(py_exec), "-m", "pip", "install", "--upgrade", "pip"])
    subprocess.call([str(py_exec), "-m", "pip", "install", "websockets"])
