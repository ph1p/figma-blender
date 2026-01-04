import bpy

from bpy.types import Panel
from .handle_material import get_selected_faces
from .properties import globalDict


class FigmaPanel(Panel):
    """The Figma Panel"""

    bl_label = "Figma"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Figma"


class FIGMA_PT_main(FigmaPanel, Panel):
    bl_idname = "FIGMA_PT_main"
    bl_label = "Figma"

    def draw_header(self, context):
        layout = self.layout
        if globalDict.get("deps_installed", False):
            if globalDict.get("is_started", False):
                if globalDict.get("plugin_connected", False):
                    layout.label(text="", icon='LINKED')
                else:
                    layout.label(text="", icon='RADIOBUT_ON')
            else:
                layout.label(text="", icon='RADIOBUT_OFF')
        else:
            layout.label(text="", icon='ERROR')

    def draw(self, context):
        layout = self.layout

        if globalDict.get("deps_installed", False):
            box = layout.box()
            col = box.column(align=True)

            row = col.row(align=True)
            if globalDict.get("is_started", False):
                row.label(text="Server: Running", icon='CHECKMARK')
                row.operator("figma.server", text="Stop", icon='PAUSE')
            else:
                row.label(text="Server: Stopped", icon='CANCEL')
                row.operator("figma.server", text="Start", icon='PLAY')

            row = col.row()
            if globalDict.get("plugin_connected", False):
                row.label(text="Plugin: Connected", icon='LINKED')
            else:
                if globalDict.get("is_started", False):
                    row.label(text="Plugin: Not connected", icon='UNLINKED')
                else:
                    row.label(text="Plugin: Waiting for server", icon='UNLINKED')

        if globalDict.get("deps_checking", False):
            row = layout.row()
            row.label(text="Installing dependencies...", icon="SORTTIME")
            row = layout.row()
            row.label(text="This may take a minute", icon="INFO")
            row = layout.row()
            row.label(text="Check console for progress", icon="CONSOLE")
        elif not globalDict.get("deps_installed", False):
            if globalDict.get("deps_needs_restart", False):
                row = layout.row()
                row.label(text="Dependencies installed!", icon="CHECKMARK")
                row = layout.row()
                row.label(text="Please RESTART BLENDER", icon="ERROR")
            else:
                row = layout.row()
                row.label(text="Dependencies not installed", icon="ERROR")
                row = layout.row()
                row.operator("figma.install_deps", text="Install Dependencies", icon="IMPORT")
                row = layout.row()
                row.label(text="Check console for error details", icon="INFO")


class FIGMA_PT_folder_path(FigmaPanel, Panel):
    bl_label = "Folder settings"
    bl_parent_id = "FIGMA_PT_main"

    @classmethod
    def poll(cls, context):
        return globalDict.get("deps_installed", False)

    def draw(self, context):
        layout = self.layout

        figma = context.scene.figma

        if figma.folder_path:
            row = layout.row()
            row.label(text=figma.folder_path, icon="FILE_FOLDER")

        row = layout.row()
        row.operator("figma.open_browser", text="Choose Folder")

        if not figma.folder_path:
            row = layout.row()
            row.label(text="Please choose a folder first", icon="INFO")


class FIGMA_PT_elements(FigmaPanel, Panel):
    bl_label = "Elements"
    bl_parent_id = "FIGMA_PT_main"

    @classmethod
    def poll(cls, context):
        return (
            globalDict.get("deps_installed", False)
            and globalDict.get("is_started", False)
            and globalDict.get("connected") is not None
            and context.scene.figma is not None
            and context.scene.figma.folder_path != ""
        )

    def draw(self, context):
        layout = self.layout

        figma = context.scene.figma

        if not globalDict["plugin_connected"]:
            row = layout.row()
            row.label(text="Waiting for plugin...", icon="INFO")
        else:
            row = layout.row()
            row.label(text="Page: " + figma.page_name, icon="FILE_BLANK")

            row = layout.row()
            row.prop(figma, "elements", icon="TEXTURE")

            if globalDict.get("is_loading", False):
                row = layout.row()
                row.label(text="Loading texture...", icon="SORTTIME")
                row = layout.row()
                row.enabled = False  # Disable the button while loading
            else:
                row = layout.row()

            if context.object and context.object.mode == "EDIT":
                if len(get_selected_faces()) > 0:
                    row.operator("figma.add_to_scene", text="Add/Update face")
                else:
                    row.label(text="Please select a face", icon="INFO")
            else:
                if len(context.view_layer.objects.selected) > 0:
                    row.operator("figma.add_to_scene", text="Add/Update texture")
                else:
                    row.operator("figma.add_to_scene")
