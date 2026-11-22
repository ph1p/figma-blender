![header](https://user-images.githubusercontent.com/15351728/162640003-898076d6-ac5d-4215-9ac1-cabfcb45eef1.png)

# Introduction

This Blender & Figma addon offers you the possibility to load textures directly from Figma into Blender file.
You can apply them directly to selected objects or simply paste them as a plane.

## Demo

https://user-images.githubusercontent.com/15351728/163018521-d6d704bb-f280-499c-a4bb-7cf3d3fea132.mp4


## How to?

Search the "Blender connect" plugin in figma and install it.
Download the "Figma Blender Addon" from here: https://ph1p.gumroad.com/l/figma-blender-addon and install the zip (Blender 4.2+: _Edit → Preferences → Get Extensions → ⌄ → Install from Disk…_). Remove any older "Figma" add-on first.

- Start Figma Plugin (https://www.figma.com/community/plugin/1095047912165244715/Blender-connect)
- Start Blender Addon
- Press `n` in Blender to open the sidebar
- Click on `Figma` and choose a folder for your textures
- Next start the server. The figma plugin UI should change and you're now able to import textures

## How is this repository structured?

* addon -> Includes the Blender addon
* plugin -> Includes the Figma plugin!

## FAQ

### My Plugin does not start!

The `websockets` dependency ships inside the extension zip, so nothing has to be installed. Check that port `1410` is free (only one Blender instance can run the server) and look at the system console for `Figma addon:` messages.

## Development

### Figma

The plugin is built with [pnpm](https://pnpm.io/). Go into the **plugin** folder and run the following commands:

```bash
pnpm install
pnpm watch # rebuilds dist/ on every change
```

After that, import it into the Figma **desktop** app under _Plugins → Development → Import plugin from manifest…_ and select `plugin/dist/manifest.json`. Re-run the plugin in Figma to pick up a rebuild.

Use `pnpm build` for a one-off production build.

### Packaging the Blender addon

```bash
scripts/build_addon.sh   # -> dist/figma_connect-<version>.zip
```

It validates and builds the extension with Blender (set `BLENDER=/path/to/blender` if it is not on your `PATH`). Bump `version` in `addon/blender_manifest.toml` before each release. To update the bundled `websockets`, replace the wheel in `addon/wheels/` and its file name in the manifest.

### Blender

I developed the plugin mainly with VSCode and this plugin https://marketplace.visualstudio.com/items?itemName=JacquesLucke.blender-development

You have to open the **addon** folder with VSCode and run the blender VSCode plugin.

### Testing the WebSocket Server

The `scripts/test_server.py` script can be used to verify that the WebSocket server is running correctly in Blender.

To test the server:

1. Start Blender and enable the Figma addon
2. Start the server from the Figma panel in Blender
3. Run the test script with a Python that has `websockets` available. Blender's bundled interpreter always does, so it is the safest choice:

```bash
# MacOS
/Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13 scripts/test_server.py

# Windows
"C:\Program Files\Blender Foundation\Blender 5.2\5.2\python\bin\python.exe" scripts/test_server.py
```

The test script will:
- Check if port 1410 is listening
- Establish a WebSocket connection
- Verify server responses
- Report the connection status

This is useful for debugging connection issues between Blender and the Figma plugin.
