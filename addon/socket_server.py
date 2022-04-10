import bpy
import json
import importlib
import asyncio
import os.path

from .properties import globalDict
from .handle_material import handle_material
from .async_loop import *


def element_not_found(self, context):
    self.layout.label(
        text="The element you're asking for seems not to be available anymore!")


def get_element(id):
    if os.path.isdir(bpy.context.scene.figma.folder_path):
        loop = asyncio.get_event_loop()

        for user in globalDict["connected"]:
            loop.run_until_complete(user.send(json.dumps({
                "event": "get_element",
                "id": id
            })))
    else:
        bpy.context.scene.figma.folder_path = ""


async def websocket_handler(websocket):
    bpy.context.scene.figma.plugin_connected = True
    if bpy.context.area:
        bpy.context.area.tag_redraw()

    if len(globalDict["connected"]) >= 1:
        await websocket.send(json.dumps({
            "event": "not_allowed",
        }))
    else:
        globalDict["connected"].add(websocket)

        image_bytes = b''

        await websocket.send(json.dumps({
            "event": "init",
        }))

        async for message in websocket:
            try:
                payload = json.loads(message)
                event = payload["event"]

                if event == "data":
                    if payload["elements"] and bpy.context.scene.figma is not None:
                        bpy.context.scene.figma.page_name = payload["page_name"]

                        bpy.context.scene.figma.items.clear()
                        for frame in payload["elements"]:
                            newFrame = bpy.context.scene.figma.items.add()
                            newFrame.id = frame["id"]
                            newFrame.name = frame["name"]
                    if bpy.context.area:
                        bpy.context.area.tag_redraw()

                if event == "element_data":
                    if payload['type'] == 'FILE_DATA':
                        image_bytes += bytes(payload['data'])
                    elif payload['type'] == 'FILE_END':
                        handle_material(image_bytes,
                                        payload['name'], payload['width'], payload['height'])
                        image_bytes = b""
                    elif payload['type'] == 'FILE_ERROR':
                        bpy.context.window_manager.popup_menu(
                            element_not_found, title="Error", icon='ERROR')
                    del payload

            except json.JSONDecodeError:
                print("payload error")

    await websocket.wait_closed()

    if websocket in globalDict["connected"]:
        globalDict["connected"].remove(websocket)

    if len(globalDict["connected"]) == 0:
        bpy.context.scene.figma.plugin_connected = False

    if bpy.context.area:
        bpy.context.area.tag_redraw()


async def server():
    websockets = importlib.import_module("websockets")

    async with websockets.serve(websocket_handler, "localhost", 1410):
        await asyncio.Future()
