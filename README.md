![header](https://user-images.githubusercontent.com/15351728/162640003-898076d6-ac5d-4215-9ac1-cabfcb45eef1.png)

# Introduction

This Blender & Figma addon offers you the possibility to load textures directly from Figma into Blender file.
You can apply them directly to selected objects or simply paste them as a plane.

## Demo

https://user-images.githubusercontent.com/15351728/163018521-d6d704bb-f280-499c-a4bb-7cf3d3fea132.mp4


## How to?

Search the "Blender connect" plugin in figma and install it.
Download the "Figma Blender Addon" from here: https://ph1p.gumroad.com/l/figma-blender-addon and install it (Edit -> Preferences -> Addons -> Install...)

- Start Figma Plugin (https://www.figma.com/community/plugin/1095047912165244715/Blender-connect)
- Start Blender Addon. **Blender may freeze for a few seconds the first time, as dependencies are installed in the background.**
- Press `n` in Blender to open the sidebar
- Click on `Figma` and choose a folder for your textures
- Next start the server. The figma plugin UI should change and you're now able to import textures

## How is this repository structured?

* addon -> Includes the Blender addon
* plugin -> Includes the Figma plugin!

## FAQ

### My Plugin does no start!

The addon may not have been able to install the `websockets` dependency. You can also do this manually via the command line, using **Blender's own Python** rather than a system Python. Replace the Blender version (`5.2`) and the Python version (`python3.13`) in the paths if yours differ.

**MacOS**

```bash
/Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13 -m pip install --user websockets
```

**Windows**

```bash
"C:\Program Files\Blender Foundation\Blender 5.2\5.2\python\bin\python.exe" -m pip install --user websockets
```

`--user` installs into your per-user site-packages, so no admin rights are needed — Blender's own `site-packages` lives under the read-only installation directory. The addon adds the user directory to `sys.path` on startup. Restart Blender once the install finishes.

## Development

### Figma

The plugin is built with [pnpm](https://pnpm.io/). Go into the **plugin** folder and run the following commands:

```bash
pnpm install
pnpm watch # rebuilds dist/ on every change
```

After that, import it into the Figma **desktop** app under _Plugins → Development → Import plugin from manifest…_ and select `plugin/dist/manifest.json`. Re-run the plugin in Figma to pick up a rebuild.

Use `pnpm build` for a one-off production build.

### Blender

I developed the plugin mainly with VSCode and this plugin https://marketplace.visualstudio.com/items?itemName=JacquesLucke.blender-development

You have to open the **addon** folder with VSCode and run the blender VSCode plugin.

### Testing the WebSocket Server

The `addon/test_server.py` script can be used to verify that the WebSocket server is running correctly in Blender.

To test the server:

1. Start Blender and enable the Figma addon
2. Start the server from the Figma panel in Blender
3. Run the test script with a Python that has `websockets` available. Blender's bundled interpreter always does, so it is the safest choice:

```bash
# MacOS
/Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13 addon/test_server.py

# Windows
"C:\Program Files\Blender Foundation\Blender 5.2\5.2\python\bin\python.exe" addon/test_server.py
```

The test script will:
- Check if port 1410 is listening
- Establish a WebSocket connection
- Verify server responses
- Report the connection status

This is useful for debugging connection issues between Blender and the Figma plugin.
