![header](https://user-images.githubusercontent.com/15351728/162640003-898076d6-ac5d-4215-9ac1-cabfcb45eef1.png)

# Introduction

This Blender & Figma addon offers you the possibility to load textures directly from Figma into Blender file.
You can apply them directly to selected objects or simply paste them as a plane.


## How to?

Search the "Blender connect" plugin in figma and install it.
Download the "Figma Blender Addon" from here: https://ph1p.gumroad.com/l/figma-blender-addon and install it (Edit -> Preferences -> Addons -> Install...)

- Start both Plugins. **Blender may freeze for a few seconds the first time, as dependencies are installed in the background.**
- Press `n` in Blender to open you
- In blender you should first choose a folder for the textures
- Next start the server and you're now able to import textures

## How is this repository structured?

* addon -> Includes the Blender addon
* plugin -> Includes the Figma plugin!

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
