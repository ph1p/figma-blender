import os
import tempfile

import bmesh
import bpy

from .properties import globalDict


def safe_file_name(name):
    """Keep the name inside the texture folder.

    The name comes over the socket, so "../" or an absolute path must not let
    it write anywhere else.
    """
    return os.path.basename(str(name).replace("\\", "/")).strip(". ")


def default_texture_folder():
    """Fallback when no folder is chosen. The temp dir gets wiped, which would
    break the image paths saved in the .blend, so prefer the extension's own
    user directory."""
    try:
        return bpy.utils.extension_path_user(__package__, path="textures", create=True)
    except Exception:
        # Loaded as a legacy add-on (e.g. from the VS Code dev setup).
        return tempfile.gettempdir()


def find_material_index(obj, name):
    for index, material in enumerate(obj.data.materials):
        if material is not None and material.name == name:
            return index
    return -1


def ensure_image_node(mat, name, file_path):
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    bsdf = nodes.get("Principled BSDF")
    if bsdf is None:
        bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")

    tex_image = nodes.get(name)

    if tex_image is None:
        tex_image = nodes.new("ShaderNodeTexImage")
        tex_image.label = name
        tex_image.name = name
        tex_image.image = bpy.data.images.load(file_path)

        links.new(bsdf.inputs["Base Color"], tex_image.outputs["Color"])

        if "Alpha" in bsdf.inputs and "Alpha" in tex_image.outputs:
            links.new(bsdf.inputs["Alpha"], tex_image.outputs["Alpha"])
    elif tex_image.image is None:
        tex_image.image = bpy.data.images.load(file_path)
    else:
        # Point the existing image at the new file: the folder may have changed,
        # and Blender may have renamed the datablock (e.g. "name.png.001").
        tex_image.image.filepath = file_path
        tex_image.image.reload()


def apply_to_objects(mat, name, width, height):
    selected = bpy.context.view_layer.objects.selected

    if len(selected) == 0:
        bpy.ops.mesh.primitive_plane_add()
        ob = bpy.context.view_layer.objects.active
        ob.scale[0] = 1
        ob.scale[1] = height / width
        ob.data.materials.append(mat)
        return

    for ob in selected:
        if not hasattr(ob.data, "materials"):
            print(f"Figma addon: '{ob.name}' cannot have materials, skipped")
            continue

        index = find_material_index(ob, name)
        if index >= 0:
            ob.data.materials[index] = mat
        else:
            ob.data.materials.append(mat)


def apply_to_selected_faces(name):
    for obj in bpy.context.objects_in_mode:
        index = find_material_index(obj, name)
        if index < 0:
            continue

        bm = bmesh.from_edit_mesh(obj.data)
        for face in bm.faces:
            if face.select:
                face.material_index = index
        bmesh.update_edit_mesh(obj.data)


def handle_material(data, name, width, height):
    figma = bpy.context.scene.figma
    name = safe_file_name(name)

    globalDict["is_loading"] = True
    if bpy.context.area:
        bpy.context.area.tag_redraw()

    try:
        if not name:
            raise ValueError("empty element name")

        folder = figma.folder_path or default_texture_folder()
        file_path = os.path.join(folder, name + ".png")

        with open(file_path, "wb") as file:
            file.write(data)

        mat = bpy.data.materials.get(name) or bpy.data.materials.new(name=name)
        mat.use_nodes = True

        ensure_image_node(mat, name, file_path)
        apply_to_objects(mat, name, width, height)

        if bpy.context.mode == "EDIT_MESH":
            apply_to_selected_faces(name)

        print(f"Figma addon: Texture '{name}' applied successfully")

    except Exception as e:
        print(f"Figma addon: Error applying texture '{name}': {e!r}")

    finally:
        globalDict["is_loading"] = False
        if bpy.context.area:
            bpy.context.area.tag_redraw()


def has_selected_faces():
    for obj in bpy.context.objects_in_mode:
        bm = bmesh.from_edit_mesh(obj.data)
        if any(face.select for face in bm.faces):
            return True
    return False
