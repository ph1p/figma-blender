import bpy
import json
import importlib
import asyncio
import os.path
import time

from .properties import globalDict
from .handle_material import handle_material
from .errors import cannot_start_server, element_not_found, folder_not_writeable


def get_element(id):
    if os.path.isdir(bpy.context.scene.figma.folder_path):
        loop = asyncio.get_event_loop()

        if not globalDict["connected"] is None:
            globalDict["is_loading"] = True
            if bpy.context.area:
                bpy.context.area.tag_redraw()

            loop.run_until_complete(globalDict["connected"].send(json.dumps({
                "event": "get_element",
                "id": id
            })))
    else:
        bpy.context.scene.figma.folder_path = ""
        bpy.context.window_manager.popup_menu(
            folder_not_writeable, title="Error", icon='ERROR')


async def websocket_handler(websocket):
    print(f"Figma addon: New WebSocket connection from {websocket.remote_address}")
    globalDict["plugin_connected"] = True
    if bpy.context.area:
        bpy.context.area.tag_redraw()

    if not globalDict["connected"] is None:
        print("Figma addon: Rejecting connection - already connected")
        await websocket.send(json.dumps({
            "event": "not_allowed",
        }))
    else:
        print("Figma addon: Accepting connection")
        globalDict["connected"] = websocket

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

                        globalDict["elements"].clear()
                        for frame in payload["elements"]:
                            globalDict["elements"].append(
                                (frame["id"], frame["name"], ""))
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

    globalDict["connected"] = None
    globalDict["plugin_connected"] = False

    if bpy.context.area:
        bpy.context.area.tag_redraw()


async def server():
    try:
        websockets = importlib.import_module("websockets")
    except ImportError as e:
        print(f"Figma addon: Failed to import websockets: {e}")
        globalDict["is_started"] = False
        if bpy.context.window_manager:
            bpy.context.window_manager.popup_menu(
                cannot_start_server, title="Error", icon='ERROR')
        return

    try:
        print("Figma addon: Starting websocket server on localhost:1410")
        async with websockets.serve(websocket_handler, "localhost", 1410) as ws_server:
            globalDict["ws_server"] = ws_server
            print("Figma addon: Websocket server started successfully")
            await asyncio.Future()  # Run forever until cancelled
    except asyncio.CancelledError:
        print("Figma addon: Server task cancelled")
    except Exception as e:
        print(f"Figma addon: Server error: {type(e).__name__}: {e}")

        if bpy.context.window_manager:
            try:
                bpy.context.window_manager.popup_menu(
                    cannot_start_server, title="Error", icon='ERROR')
            except:
                pass
    finally:
        print("Figma addon: Server stopped")

        # A task that failed to bind must not clear state owned by the server
        # that is still running.
        if globalDict.get("server_task") is asyncio.current_task():
            globalDict["ws_server"] = None
            globalDict["connected"] = None
            globalDict["is_started"] = False

        if bpy.context.area:
            bpy.context.area.tag_redraw()


def stop_server(timeout=2.0):
    """Close the server and drain the loop until port 1410 is free.

    cancel() alone leaks the socket: it lands on a later loop iteration, but the
    pump timer retires the moment is_started goes False.
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = None

    ws_server = globalDict.get("ws_server")
    task = globalDict.get("server_task")

    if ws_server is not None:
        try:
            ws_server.close()
        except Exception as e:
            print(f"Figma addon: Error closing server: {e}")

    if task is not None:
        try:
            task.cancel()
        except Exception as e:
            print(f"Figma addon: Error cancelling task: {e}")

    if loop is not None and task is not None:
        deadline = time.monotonic() + timeout

        while not task.done() and time.monotonic() < deadline:
            try:
                loop.stop()
                loop.run_forever()
            except Exception as e:
                print(f"Figma addon: Error draining event loop: {e}")
                break
            time.sleep(0.005)

        if not task.done():
            print("Figma addon: Server did not shut down in time, port may stay bound")

    globalDict["ws_server"] = None
    globalDict["server_task"] = None
    globalDict["connected"] = None
    globalDict["plugin_connected"] = False
    globalDict["is_started"] = False
