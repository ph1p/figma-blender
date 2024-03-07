import bmesh
import bpy
import os
import itertools

from .properties import globalDict


def handle_material(data, name, width, height):
    figma = bpy.context.scene.figma

    if not globalDict["is_loading"]:
        globalDict["is_loading"] = True
        if bpy.context.area:
            bpy.context.area.tag_redraw()

        path = "/tmp/"

        if figma.folder_path:
            path = figma.folder_path

        try:
            mat = bpy.data.materials.get(name)

            if mat is None:
                mat = bpy.data.materials.new(name=name)

            file_path = os.path.join(path, name + ".png")

            file = open(file_path, "wb")
            file.write(data)
            file.close()

            mat.use_nodes = True
            nodes = mat.node_tree.nodes

            bsdf = nodes.get("Principled BSDF")

            if not bsdf:
                bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")

            texImage = nodes.get(name)

            if texImage is None:
                texImage = nodes.new("ShaderNodeTexImage")
                texImage.label = name
                texImage.name = name
                texImage.image = bpy.data.images.load(file_path)

                if bsdf and texImage:
                    mat.node_tree.links.new(
                        bsdf.inputs["Base Color"], texImage.outputs["Color"]
                    )

                    if "BSDF Alpha" in bsdf.inputs and "Alpha" in texImage.outputs:
                        mat.node_tree.links.new(
                            bsdf.inputs["BSDF Alpha"], texImage.outputs["Alpha"]
                        )
            else:
                if not texImage.image is None:
                    bpy.data.images[name + ".png"].reload()
                else:
                    texImage.image = bpy.data.images.load(file_path)

            if len(bpy.context.view_layer.objects.selected) == 0:
                ob = bpy.ops.mesh.primitive_plane_add()
                ob = bpy.context.view_layer.objects.active
                ob.scale[0] = 1
                ob.scale[1] = 1 / width * height
                ob.data.materials.append(mat)
            else:
                for ob in bpy.context.view_layer.objects.selected:
                    try:
                        for index, m in enumerate(ob.data.materials):
                            if not m is None and m.name == name:
                                ob.data.materials[index] = mat
                                break
                        else:
                            ob.data.materials.append(mat)
                    except AttributeError:
                        print("object has no material")

            if bpy.context.object.mode == "EDIT":
                for obj in bpy.context.objects_in_mode:
                    found_index = -1
                    for index, m in enumerate(obj.data.materials):
                        if not m is None and m.name == name:
                            found_index = index
                            break

                    if found_index >= 0:
                        bm = bmesh.from_edit_mesh(obj.data)
                        for face in bm.faces:
                            if face.select:
                                face.material_index = found_index
                                bm.verts.index_update()
                                bmesh.update_edit_mesh(obj.data)

        except Exception as e:
            print("Error: %s", repr(e))

        finally:
            del data

    globalDict["is_loading"] = False
    if bpy.context.area:
        bpy.context.area.tag_redraw()


def get_selected_faces_of_object(obj):
    faces = []

    bm = bmesh.from_edit_mesh(obj.data)
    for f in bm.faces:
        if f.select:
            faces.append(f)

    return faces


def get_selected_faces():
    faces = []

    for obj in bpy.context.objects_in_mode:
        faces.append(get_selected_faces_of_object(obj))

    return list(itertools.chain(*faces))
