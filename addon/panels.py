import bpy

from bpy.types import Panel
from .handle_material import get_selected_faces
from .properties import globalDict


class FigmaPanel(Panel):
    """The Figma Panel"""
    bl_label = "Figma"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Figma"


class FIGMA_PT_main(FigmaPanel, Panel):
    bl_idname = "FIGMA_PT_main"
    bl_label = "Figma"

    def draw(self, context):
        layout = self.layout

        if not globalDict["deps_installed"]:
            row = layout.row()
            row.label(text='Check/Installing dependencies...', icon="INFO")


class FIGMA_PT_folder_path(FigmaPanel, Panel):
    bl_label = "Folder settings"
    bl_parent_id = "FIGMA_PT_main"

    def draw(self, context):
        layout = self.layout

        figma = context.scene.figma

        if figma.folder_path:
            row = layout.row()
            row.label(text=figma.folder_path, icon="FILE_FOLDER")

        row = layout.row()
        row.operator('figma.open_browser', text="Choose Folder")

        if not figma.folder_path:
            row = layout.row()
            row.label(text='Please choose a folder first', icon="INFO")


class FIGMA_PT_server(FigmaPanel, Panel):
    bl_label = "Server"
    bl_parent_id = "FIGMA_PT_main"

    @classmethod
    def poll(self, context):
        return not context.scene.figma is None and context.scene.figma.folder_path != ""

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        if globalDict["is_started"]:
            row.operator('figma.server', text="Stop server")
        else:
            row.operator('figma.server', text="Start server")


class FIGMA_PT_elements(FigmaPanel, Panel):
    bl_label = "Elements"
    bl_parent_id = "FIGMA_PT_main"

    @classmethod
    def poll(self, context):
        return globalDict["is_started"] and not globalDict["connected"] is None and context.scene.figma.folder_path != ""

    def draw(self, context):
        layout = self.layout

        figma = context.scene.figma

        if not globalDict["plugin_connected"]:
            row = layout.row()
            row.label(text='Waiting for plugin...', icon="INFO")
        else:
            row = layout.row()
            row.label(text='Page: ' + figma.page_name, icon="FILE_BLANK")

            row = layout.row()
            row.prop(figma, 'elements', icon="TEXTURE")

            row = layout.row()
            if context.object.mode == 'EDIT':
                if len(get_selected_faces()) > 0:
                    row.operator('figma.add_to_scene',
                                 text="Add/Update face")
                else:
                    row.label(
                        text='Please select a face', icon="INFO")
            else:
                if len(context.view_layer.objects.selected) > 0:
                    row.operator('figma.add_to_scene',
                                 text="Add/Update texture")
                else:
                    row.operator('figma.add_to_scene')
