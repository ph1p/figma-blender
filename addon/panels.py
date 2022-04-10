from bpy.types import Panel


class FIGMA_PT_Panel(Panel):
    """The Figma Panel"""
    bl_label = "Figma"
    bl_idname = "FIGMA_PT_figma_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Figma"

    @classmethod
    def poll(self, context):
        return context.scene.figma is not None

    def draw(self, context):
        layout = self.layout

        figma = context.scene.figma

        if figma.folder_path:
            row = layout.row()
            row.label(text=figma.folder_path, icon="FILE_FOLDER")

        row = layout.row()
        row.operator('figma.open_browser', text="Choose Folder")

        if figma.deps_installed:
            if not figma.folder_path:
                row = layout.row()
                row.label(text='Please choose a folder first', icon="INFO")
            else:
                if figma.is_started:
                    layout.row().separator()

                    row = layout.row()
                    if figma.plugin_connected:
                        row.label(text='Plugin connected', icon="HIDE_OFF")
                    else:
                        row.label(text='Plugin not connected', icon="HIDE_ON")

                    if figma.plugin_connected:
                        row = layout.row()
                        row.label(text='Page: ' + figma.page_name)

                        row = layout.row()
                        row.prop(figma, 'elements', icon="WINDOW")

                        row = layout.row()
                        if len(context.view_layer.objects.selected) > 0:
                            row.operator('figma.add_to_scene',
                                         text="Add/Update texture")
                        else:
                            row.operator('figma.add_to_scene')

                layout.row().separator()

                row = layout.row()
                if figma.is_started:
                    row.operator('figma.server', text="Stop server")
                else:
                    row.operator('figma.server', text="Start server")

        else:
            row = layout.row()
            row.label(text='Check/Installing dependencies...', icon="INFO")
