import asyncio
import importlib
import json
import os.path
import time

import bpy

from .errors import cannot_start_server, element_not_found, folder_not_writeable
from .handle_material import handle_material
from .properties import globalDict

# Figma runs plugin UIs in a sandboxed iframe, which sends "Origin: null".
# Rejecting every other origin keeps arbitrary websites open in a browser from
# talking to Blender. None admits clients that send no Origin header at all,
# i.e. local tools such as scripts/test_server.py rather than browsers.
ALLOWED_ORIGINS = ["null", None]

# Sent with "init" so the plugin can pick a transfer format this addon
# understands. Bump on breaking changes to the wire format.
#   1: image chunks as JSON FILE_DATA messages (no version field sent)
#   2: image chunks as raw binary frames
PROTOCOL_VERSION = 2


def tag_redraw():
    if bpy.context.area:
        bpy.context.area.tag_redraw()


def set_loading(value):
    globalDict["is_loading"] = value
    tag_redraw()


def get_element(id):
    if not os.path.isdir(bpy.context.scene.figma.folder_path):
        bpy.context.scene.figma.folder_path = ""
        bpy.context.window_manager.popup_menu(
            folder_not_writeable, title="Error", icon='ERROR')
        return

    websocket = globalDict["connected"]
    if websocket is None:
        return

    set_loading(True)

    try:
        asyncio.get_event_loop().run_until_complete(websocket.send(json.dumps({
            "event": "get_element",
            "id": id
        })))
    except Exception as e:
        print(f"Figma addon: Could not request element: {e}")
        set_loading(False)


def update_elements(payload):
    figma = bpy.context.scene.figma
    if figma is None:
        return

    figma.page_name = payload.get("page_name", "")

    # An empty page must clear the list, not leave the previous page's elements.
    globalDict["elements"].clear()
    for element in payload.get("elements") or []:
        globalDict["elements"].append((element["id"], element["name"], ""))


async def websocket_handler(websocket):
    print(f"Figma addon: New WebSocket connection from {websocket.remote_address}")

    if globalDict["connected"] is not None:
        print("Figma addon: Rejecting connection - already connected")
        await websocket.send(json.dumps({"event": "not_allowed"}))
        # Closing lets the plugin retry, so it gets in once the slot is free.
        await websocket.close()
        return

    print("Figma addon: Accepting connection")
    globalDict["connected"] = websocket
    globalDict["plugin_connected"] = True
    tag_redraw()

    image_bytes = bytearray()

    try:
        await websocket.send(json.dumps({
            "event": "init",
            "protocol": PROTOCOL_VERSION,
        }))

        async for message in websocket:
            # Image data arrives as binary frames, everything else as JSON.
            if isinstance(message, bytes):
                image_bytes.extend(message)
                continue

            try:
                payload = json.loads(message)
                event = payload.get("event")

                if event == "data":
                    update_elements(payload)
                    tag_redraw()

                elif event == "element_data":
                    if payload["type"] == "FILE_DATA":
                        # Protocol 1 plugins send chunks as JSON byte arrays.
                        image_bytes.extend(bytes(payload["data"]))
                    elif payload["type"] == "FILE_END":
                        handle_material(
                            bytes(image_bytes),
                            payload["name"],
                            payload["width"],
                            payload["height"],
                        )
                        image_bytes.clear()
                    elif payload["type"] == "FILE_ERROR":
                        image_bytes.clear()
                        set_loading(False)
                        bpy.context.window_manager.popup_menu(
                            element_not_found, title="Error", icon='ERROR')

            except Exception as e:
                # One malformed message must not drop the whole connection.
                print(f"Figma addon: Could not handle message: {type(e).__name__}: {e}")
    finally:
        # Only the accepted connection owns this state.
        if globalDict["connected"] is websocket:
            globalDict["connected"] = None
            globalDict["plugin_connected"] = False
            # A transfer cut off by the disconnect never sends FILE_END.
            set_loading(False)


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
        async with websockets.serve(
            websocket_handler, "localhost", 1410, origins=ALLOWED_ORIGINS
        ) as ws_server:
            globalDict["ws_server"] = ws_server
            globalDict["is_listening"] = True
            tag_redraw()
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
            except Exception:
                pass
    finally:
        print("Figma addon: Server stopped")

        # A task that failed to bind must not clear state owned by the server
        # that is still running.
        if globalDict.get("server_task") is asyncio.current_task():
            globalDict["ws_server"] = None
            globalDict["connected"] = None
            globalDict["is_started"] = False
            globalDict["is_listening"] = False

        tag_redraw()


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
    globalDict["is_listening"] = False
    globalDict["is_loading"] = False
