# -*- coding: utf-8 -*-
#
# This addon creates a frame around the rendered images and writes scene information on it.
# It is a flexible alternative to the Metadata post processing integrated system of Blender.
#
# Installation:
#
#   - The addon must be installed in Administrator mode so that the Pillow Python library can
#     be downloaded and deployed correctly.
#
#
#
# Dev notes:
#  * To do:
#       - callback de restoration       -- intégrée à la fin du script RRS?
#       - delete the temp file
#       - mieux gérer les paths relatifs et messages de chemin invalide
#
#       - restaurer les prefs précédentes
#       - clean compo nodes (only them!!)
#       - prémultipier les images PIL!!!

#       - Stocker Last Rendered Frame pour pouvoir cleaner en cas de cancel et single rendered frame
#       - garder les infos dans la scene
#
#       - mettre les nodes compo à la fin du graph
#
#       - faire un compo premult correct
#
# Possible future improvements:
#       - Add hair cross, safe frame
#       - Display metadata labels
#       - Compositing nodes could be put in a separated scene to avoid breaking any existing compositing graph
#
#
# Principle:
#   - At Prerender Init time:
#       - creation of the postprocess nodes
#           - we detect if there is a Composite note (expected to be the standard output)
#               - if yes: we plug our graph on it with a mix
#               - if not: we create our own graph
#           - The resulting image has:
#               - a large image at the stamp info res fully transparent
#               - the stamped info
#               - a RGB that is the rendered image below the stamped info
#
#
#
#
#   - At Pre render Frame:
#       - Voir si on peut rendre les frames de cadrage à ce moment là seulement
#
#   - At Completed or Cancel:
#       - cleaning of the nodes
#       - the handlers stay in place
#
#
# Dev notes:
#   - Handlers are NOT persistent
#   - Compositing nodes are removed at the end of the process
#   - Temp files used for the information are deleted at the next frame
#   - Temp files are created in the render directory
#
#
#
# Resources:
#   - Renderer:     https://docs.blender.org/api/current/bpy.ops.render.html?highlight=render#module-bpy.ops.render
#   - handlers:     https://docs.blender.org/api/current/bpy.app.handlers.html
#   - Compo nodes:  https://docs.blender.org/api/current/bpy.types.CompositorNodeImage.html
#

import os
import subprocess

import bpy
import bpy.utils.previews
from bpy.types import Operator, Panel
from bpy.props import StringProperty, PointerProperty


# for file browser:
from bpy_extras.io_utils import ImportHelper

import importlib

from .utils import utils_render

from . import handlers
from . import stamper
from . import stampInfoSettings
from .operators import debug

importlib.reload(stampInfoSettings)
importlib.reload(stamper)
importlib.reload(handlers)
importlib.reload(debug)


bl_info = {
    "name": "UAS_StampInfo",
    "author": "Julien Blervaque (aka Werwack)",
    "description": "Stamp scene information on the rendered images - Ubisoft Animation Studio"
    "\nRequiers (and automatically install if not found) the Python library named Pillow",
    "blender": (2, 82, 0),
    "version": (0, 9, 14),
    "location": "Right panel in the 3D View",
    "wiki_url": "https://mdc-web-tomcat17.ubisoft.org/confluence/display/UASTech/UAS+StampInfo",
    "warning": "",
    "category": "UAS",
}

# ------------------------------------------------------------------------#
#                               Main Panel                               #
# ------------------------------------------------------------------------#


class UAS_PT_StampInfoAddon(Panel):
    bl_idname = "UAS_PT_StampInfoAddon"
    bl_label = f"UAS StampInfo {'.'.join ( str ( v ) for v in bl_info['version'] ) }"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "UAS StampInfo"

    def draw_header_preset(self, context):
        layout = self.layout
        layout.emboss = "NONE"
        row = layout.row(align=True)

        # row.operator("render.render", text="", icon='IMAGE_DATA').animation = False            # not working with stampInfo
        # row.operator("render.render", text="", icon='RENDER_ANIMATION').animation = True       # ok
        row.operator("utils.launchrender", text="", icon="RENDER_STILL").renderMode = "STILL"
        row.operator("utils.launchrender", text="", icon="RENDER_ANIMATION").renderMode = "ANIMATION"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        #    row     = layout.row ()
        #    row.operator("stampinfo.clearhandlers")
        #    row.operator("stampinfo.createhandlers")
        #    row.menu(SCENECAMERA_MT_SelectMenu.bl_idname,text="Selection",icon='BORDERMOVE')

        row = layout.row()
        row.prop(scene.UAS_StampInfo_Settings, "stampInfoUsed")

        # ensure consistency between stampInfoUsed status and handle
        if not scene.UAS_StampInfo_Settings.handlersRegistered():
            scene.UAS_StampInfo_Settings.registerRenderHandlers()

        if scene.UAS_StampInfo_Settings.handlersRegistered():
            row.scale_x = 0.2
            if not scene.UAS_StampInfo_Settings.stampInfoUsed:
                row.alert = True
            row.operator("stampinfo.resethandlers", text="Y")  # , icon = 'CHECKMARK' )
        else:
            row.scale_x = 0.2
            if scene.UAS_StampInfo_Settings.stampInfoUsed:
                row.alert = True
            row.operator("stampinfo.resethandlers", text="N")  # , icon = 'ERROR'

        # ready to render text
        row = layout.row()
        # if '' == bpy.data.filepath:
        #     row.alert = True
        #     row.label ( text = "*** Save file first ***" )
        # el
        if None == (stamper.getInfoFileFullPath(context.scene, -1)[0]):
            row.alert = True
            row.label(text="*** Invalid Output Path ***")
        elif "" == stamper.getRenderFileName(scene):
            row.alert = True
            row.label(text="*** Invalid Output File Name ***")
        else:
            row.label(text="Ready to render")

        row = layout.row()
        row.alert = True
        row.label(text="Warning: This version completely clears the compo graph!!")

        box = layout.box()
        row = box.row(align=True)
        row.prop(scene.UAS_StampInfo_Settings, "stampInfoRenderMode")

        #    print("   init ui: stampInfoRenderMode: " + str(scene.UAS_StampInfo_Settings['stampInfoRenderMode']))
        #    print("   init ui: stampInfoRenderMode: " + str(scene.UAS_StampInfo_Settings.stampInfoRenderMode))

        if "DIRECTTOCOMPOSITE" == scene.UAS_StampInfo_Settings.stampInfoRenderMode:
            #  if 0 == scene.UAS_StampInfo_Settings['stampInfoRenderMode']:
            # row = box.row(align=True)
            # row.prop(scene.UAS_StampInfo_Settings, "stampRenderResYDirToCompo_percentage")

            row = box.row(align=True)
            #   if scene.UAS_StampInfo_Settings.innerImageHeight >= stamper.getRenderResolution(scene)[1]:
            # row.prop(scene.UAS_StampInfo_Settings, "innerImageHeight")
            # row.prop(scene.UAS_StampInfo_Settings, "innerImageHeight_percentage")
            row.prop(scene.UAS_StampInfo_Settings, "stampRenderResYDirToCompo_percentage")

            row = box.row(align=True)
            if scene.UAS_StampInfo_Settings.stampRenderResYDirToCompo_percentage >= 100.0:
                row.alert = True
            outputResStampInfoH = int(stamper.getRenderResolutionForStampInfo(scene)[1])

            resStr = (
                "Out: "
                + str(int(stamper.getRenderResolutionForStampInfo(scene)[0]))
                + " px x "
                + str(outputResStampInfoH)
                + " px"
            )
            resStr += " - Inner: " + str(stamper.getInnerHeight(scene)) + "px"
            row.label(text=resStr)

        if "SEPARATEOUTPUT" == scene.UAS_StampInfo_Settings.stampInfoRenderMode:
            row = box.row(align=True)
            row.prop(scene.UAS_StampInfo_Settings, "stampRenderResX_percentage")
            row.prop(scene.UAS_StampInfo_Settings, "stampRenderResY_percentage")

            row = box.row(align=True)
            if (
                scene.UAS_StampInfo_Settings.stampRenderResX_percentage < 100.0
                or scene.UAS_StampInfo_Settings.stampRenderResY_percentage <= 100.0
            ):
                row.alert = True
            outputResStampInfoH = int(stamper.getRenderResolutionForStampInfo(scene)[1])

            resStr = (
                "Stamp Res: "
                + str(int(stamper.getRenderResolutionForStampInfo(scene)[0]))
                + " px x "
                + str(outputResStampInfoH)
                + " px"
            )
            resStr += " - Inner: " + str(stamper.getInnerHeight(scene)) + "px"
            row.label(text=resStr)

        row = layout.row()
        row.operator("stampinfo.openexplorer", emboss=True)


# ------------------------------------------------------------------------#
#                             Metadata Panel                             #
# ------------------------------------------------------------------------#
class UAS_PT_StampInfoMetadata(Panel):
    bl_idname = "UAS_PT_StampInfoMetadata"
    bl_label = "Metadata"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "UAS StampInfo"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text="Top: Project and Editing Info")
        box = layout.box()

        # ---------- logo -------------
        # box = layout.box()
        row = box.row(align=True)
        row.prop(scene.UAS_StampInfo_Settings, "logoUsed")

        if scene.UAS_StampInfo_Settings.logoUsed:
            row = box.row(align=True)
            row.prop(scene.UAS_StampInfo_Settings, "logoFilepath")
            row.operator("stampinfo.openfilebrowser", text="", icon="FILEBROWSER", emboss=True)
            row.prop(scene.UAS_StampInfo_Settings, "logoName")

            row = box.row(align=True)
            row.prop(scene.UAS_StampInfo_Settings, "logoScaleH")

            row = box.row(align=True)
            row.prop(scene.UAS_StampInfo_Settings, "logoPosNormX")
            row.prop(scene.UAS_StampInfo_Settings, "logoPosNormY")

        # ---------- project -------------
        row = box.row(align=True)
        row.prop(scene.UAS_StampInfo_Settings, "projectUsed")
        row.prop(scene.UAS_StampInfo_Settings, "projectName")

        # ---------- date -------------
        box = layout.box()
        row = box.row(align=True)
        row.prop(scene.UAS_StampInfo_Settings, "dateUsed")
        row.prop(scene.UAS_StampInfo_Settings, "timeUsed")

        # ---------- notes -------------
        box = layout.box()
        row = box.row(align=True)
        row.prop(scene.UAS_StampInfo_Settings, "notesUsed")

        if scene.UAS_StampInfo_Settings.notesUsed:
            row = box.row(align=True)
            row.prop(scene.UAS_StampInfo_Settings, "notesLine01", text="")
            row = box.row(align=True)
            row.prop(scene.UAS_StampInfo_Settings, "notesLine02", text="")
            row = box.row(align=True)
            row.prop(scene.UAS_StampInfo_Settings, "notesLine03", text="")

        # ---------- video image -------------
        box = layout.box()
        row = box.row(align=True)
        row.prop(scene.UAS_StampInfo_Settings, "videoFrameUsed")
        row.prop(scene.UAS_StampInfo_Settings, "videoRangeUsed")
        row.prop(scene.UAS_StampInfo_Settings, "videoHandlesUsed", text="Handles")

        # ---------- 3d edit frame -------------
        row = box.row(align=True)
        row.prop(scene.UAS_StampInfo_Settings, "edit3DFrameUsed", text="3D Edit Frame")
        # row.prop(scene.UAS_StampInfo_Settings, "edit3DFrame", text="3D Edit Frame")
        # row = box.row(align=True)
        row.prop(scene.UAS_StampInfo_Settings, "edit3DTotalNumberUsed", text="3D Edit Duration")
        # row.prop(scene.UAS_StampInfo_Settings, "edit3DTotalNumber", text="3D Edit Duration")

        #  row = box.row(align=True)
        row.prop(scene.UAS_StampInfo_Settings, "framerateUsed")

        layout.separator()
        layout.label(text="Bottom: 3D Info")

        # ---------- shot -------------
        # To be filled by a production script or by UAS Shot Manager
        box = layout.box()
        row = box.row(align=True)
        row.prop(scene.UAS_StampInfo_Settings, "sceneUsed")
        row = box.row(align=True)
        row.prop(scene.UAS_StampInfo_Settings, "takeUsed")
        row.prop(scene.UAS_StampInfo_Settings, "takeName", text="")

        row = box.row(align=True)
        row.prop(scene.UAS_StampInfo_Settings, "shotUsed")
        row.prop(scene.UAS_StampInfo_Settings, "shotName", text="")
        row = box.row(align=True)
        row.separator(factor=4)
        #   row.prop(scene.UAS_StampInfo_Settings, "frameHandlesUsed", text = "")
        row.prop(scene.UAS_StampInfo_Settings, "shotHandles", text="Handles")

        # ---------- camera -------------
        row = box.row(align=True)
        row.prop(scene.UAS_StampInfo_Settings, "cameraUsed")
        row.prop(scene.UAS_StampInfo_Settings, "cameraLensUsed")

        # ---------- 3D frame -------------
        box = layout.box()
        row = box.row(align=True)
        row.prop(scene.UAS_StampInfo_Settings, "currentFrameUsed")
        row.prop(scene.UAS_StampInfo_Settings, "frameRangeUsed")
        row.prop(scene.UAS_StampInfo_Settings, "frameHandlesUsed", text="Handles")

        # ---------- file -------------
        box = layout.box()
        row = box.row(align=True)
        row.prop(scene.UAS_StampInfo_Settings, "filenameUsed")
        row.prop(scene.UAS_StampInfo_Settings, "filepathUsed")


# ------------------------------------------------------------------------#
#                             Layout Panel                               #
# ------------------------------------------------------------------------#
class UAS_PT_StampInfoLayout(Panel):
    bl_idname = "UAS_PT_StampInfoLayout"
    bl_label = "Frame Layout"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "UAS StampInfo"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        box = layout.box()
        row = box.row()
        row.prop(scene.UAS_StampInfo_Settings, "textColor")

        row = box.row()
        row.prop(scene.UAS_StampInfo_Settings, "automaticTextSize", text="Fit Text in Borders")

        # if not scene.UAS_StampInfo_Settings.automaticTextSize:
        row = box.row()
        row.prop(scene.UAS_StampInfo_Settings, "fontScaleHNorm", text="Text Size")

        row = box.row()
        row.prop(scene.UAS_StampInfo_Settings, "interlineHNorm", text="Interline Size")

        row = box.row()
        row.prop(scene.UAS_StampInfo_Settings, "extPaddingNorm")

        # ---------- border -------------
        box = layout.box()
        row = box.row(align=True)

        # if stamper.getRenderRatio(scene) + 0.002 >= scene.UAS_StampInfo_Settings.innerImageRatio \
        #     and scene.UAS_StampInfo_Settings.borderUsed:
        #     row.alert = True

        row.prop(scene.UAS_StampInfo_Settings, "borderUsed")
        row.prop(context.scene.UAS_StampInfo_Settings, "borderColor")

    #    row.prop(scene.UAS_StampInfo_Settings, "innerImageRatio")

    # row = layout.row()
    # row.prop(scene.UAS_StampInfo_Settings, "linkTextToBorderEdge")


# ------------------------------------------------------------------------#
#                             Settings Panel                             #
# ------------------------------------------------------------------------#
class UAS_PT_StampInfoSettings(Panel):
    bl_idname = "UAS_PT_StampInfoSettings"
    bl_label = "Settings"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "UAS StampInfo"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # row = layout.row()
        # row.prop(scene.UAS_StampInfo_Settings, "linkTextToBorderEdge")

        row = layout.row()
        row.prop(scene.UAS_StampInfo_Settings, "stampPropertyLabel")

        row = layout.row()
        row.prop(scene.UAS_StampInfo_Settings, "stampPropertyValue")


# This operator requires   from bpy_extras.io_utils import ImportHelper
# See https://sinestesia.co/blog/tutorials/using-blenders-filebrowser-with-python/
class UAS_OpenFileBrowser(Operator, ImportHelper):
    bl_idname = "stampinfo.openfilebrowser"
    bl_label = "Open"
    bl_description = (
        "Open the file browser to define the image to stamp\n"
        "Relative path must be set directly in the text field and must start with ''//''"
    )

    filter_glob: StringProperty(default="*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.tga,*.bmp", options={"HIDDEN"})

    def execute(self, context):
        """Use the selected file as a stamped logo"""
        filename, extension = os.path.splitext(self.filepath)
        #   print('Selected file:', self.filepath)
        #   print('File name:', filename)
        #   print('File extension:', extension)
        bpy.context.scene.UAS_StampInfo_Settings.logoFilepath = self.filepath

        return {"FINISHED"}


class UAS_OpenExplorer(Operator):
    bl_idname = "stampinfo.openexplorer"
    bl_label = "Open Explorer"
    bl_description = "Open an Explorer window located at the render output directory"

    # wkip use icon FILEBROWSER

    def execute(self, context):
        """Open an Explorer window located at the render output directory"""

        renderPath = stamper.getInfoFileFullPath(context.scene, -1)[0]

        # cf https://stackoverflow.com/questions/281888/open-explorer-on-a-file
        import subprocess

        # subprocess.Popen(r'explorer "C:\tmp"')
        subprocess.Popen('explorer "' + renderPath + '"')

        print(" UAS_OpenExplorer: Open " + renderPath)

        return {"FINISHED"}


class UAS_ResetHandlers(Operator):
    bl_idname = "stampinfo.resethandlers"
    bl_label = "Reset Handlers"
    bl_description = (
        "Y if handlers are installed, N if not.\nRed if the status of the handlers is not the expected one according to\n"
        "the stateof Use Stamp Info.\nButton pressed: Reset Handlers to the expected state"
    )

    def execute(self, context):
        """Clear Compo Nodes"""
        print(" UAS_ResetHandlersAndCompoNodes")

        # stamper.clearInfoCompoNodes(context.scene)

        # context.scene.UAS_StampInfo_Settings.clearRenderHandlers()     # not needed cause also called in registerRenderHandlers
        context.scene.UAS_StampInfo_Settings.registerRenderHandlers()

        return {"FINISHED"}


class UAS_ResetHandlersAndCompoNodes(Operator):
    bl_idname = "stampinfo.resethandlersandcomponodes"
    bl_label = "Reset Handlers and Compo"
    bl_description = "Clear and register again the handlers and clear the Compo Nodes"

    def execute(self, context):
        """Clear Compo Nodes"""
        print(" UAS_ResetHandlersAndCompoNodes")

        context.scene.UAS_StampInfo_Settings.clearRenderHandlers()

        stamper.clearInfoCompoNodes(context.scene)

        context.scene.UAS_StampInfo_Settings.registerRenderHandlers()

        return {"FINISHED"}


classes = [
    UAS_PT_StampInfoAddon,
    UAS_PT_StampInfoMetadata,
    UAS_PT_StampInfoLayout,
    UAS_PT_StampInfoSettings,
    stampInfoSettings.UAS_StampInfoSettings,
    utils_render.Utils_LaunchRender,
    UAS_OpenFileBrowser,
    UAS_OpenExplorer,
    UAS_ResetHandlersAndCompoNodes,
    UAS_ResetHandlers,
]
# debug:
#   handlers.UAS_StampInfoCreateHandlers,
#   handlers.UAS_StampInfoClearHandlers,


def module_can_be_imported(name):
    try:
        __import__(name)
        return True
    except ModuleNotFoundError:
        return False


def register():
    print("\n--------- Registering UAS_StampInfo ---------")

    # Pillow lib installation
    if not module_can_be_imported("PIL"):
        subprocess.run([bpy.app.binary_path_python, "-m", "pip", "install", "pillow"])

    for cls in classes:
        bpy.utils.register_class(cls)

    debug.register()

    bpy.types.Scene.UAS_StampInfo_Settings = PointerProperty(type=stampInfoSettings.UAS_StampInfoSettings)

    # stampInfoSettings.registerRenderHandlers()

    # handlers.registerPostLoadHandler()


def unregister():

    debug.unregister()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    # clearing handlers
    # https://blender.stackexchange.com/questions/53894/how-to-avoid-multiple-running-instances-of-same-handler-function-when-running-it
    # bpy.app.handlers.render_init.clear()
    # bpy.app.handlers.render_pre.clear()
    # bpy.app.handlers.render_complete.clear()
    # bpy.app.handlers.render_cancel.clear()
    # bpy.app.handlers.render_init.remove(my_handlder)
