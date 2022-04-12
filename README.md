![header](https://user-images.githubusercontent.com/15351728/162640003-898076d6-ac5d-4215-9ac1-cabfcb45eef1.png)

# Introduction

This Blender & Figma addon offers you the possibility to load textures directly from Figma into Blender file.
You can apply them directly to selected objects or simply paste them as a plane.


## How to?

Search the "Blender connect" plugin in figma and install it.
Download the "Figma Blender Addon" from here: https://ph1p.gumroad.com/l/figma-blender-addon and install it (Edit -> Preferences -> Addons -> Install...)

- Start both Plugins. **Blender may freeze for a few seconds the first time, as dependencies are installed in the background.**
- Press `n` in Blender to open you the sidebar
- Click on `Figma` and choose a folder for your textures
- Next start the server and you're now able to import textures

## How is this repository structured?

* addon -> Includes the Blender addon
* plugin -> Includes the Figma plugin!

## FAQ

### My Plugin does no start!

The plugin may not have been able to install the `wesocket` dependency. So you can also do this manually via the command line. You have to replace the Blender-Version (`2.92`) and maybe the python executable (`python3.7m`).

**MacOS**

```bash
 /Applications/Blender.app/Contents/Resources/2.92/python/bin/python3.7m -m pip install websockets
```

**Windows**

Run `cmd` and run this with admin rights.

```bash
"C:\Program Files\Blender Foundation\Blender 3.1\3.1\python\bin\python.exe" -m pip install websockets"
```

## Development

### Figma

Just go into the **plugin** folder and run the following commands:

```bash
yarn install
yarn start # runs dev server
```

### Blender

I developed the plugin mainly with VSCode and this plugin https://marketplace.visualstudio.com/items?itemName=JacquesLucke.blender-development

You have to open the **addon** folder with VSCode and run the blender VSCode plugin.
