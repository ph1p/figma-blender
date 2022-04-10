import bpy


def handle_material(data, name, width, height):
    figma = bpy.context.scene.figma

    if not figma.is_loading:
        figma.is_loading = True
        if bpy.context.area:
            bpy.context.area.tag_redraw()

        path = "/tmp/"

        if figma.folder_path:
            path = figma.folder_path

        try:
            name = name.replace('/', '-').replace('\\', '-')

            mat = bpy.data.materials.get(name)

            if mat is None:
                mat = bpy.data.materials.new(name=name)

            file = open(path + mat.name + ".png", "wb")
            file.write(data)
            file.close()

            mat.use_nodes = True
            nodes = mat.node_tree.nodes

            bsdf = nodes["Principled BSDF"]
            texImage = nodes.get(mat.name)

            if texImage is None:
                texImage = nodes.new('ShaderNodeTexImage')
                texImage.label = mat.name
                texImage.name = mat.name
                texImage.image = bpy.data.images.load(path + mat.name + ".png")
                mat.node_tree.links.new(
                    bsdf.inputs['Base Color'], texImage.outputs['Color'])
            else:
                bpy.data.images[mat.name + ".png"].reload()

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
                            if m.name == mat.name:
                                ob.data.materials[index] = mat
                                break
                        else:
                            ob.data.materials.append(mat)
                    except AttributeError:
                        print("object has no material")
        finally:
            del data

    figma.is_loading = False
    if bpy.context.area:
        bpy.context.area.tag_redraw()
