import logging

_logger = logging.getLogger(__name__)

import os
from pathlib import Path
import subprocess

import bpy
import bpy.utils.previews
from bpy.types import Operator, Panel
from bpy.props import StringProperty, PointerProperty, BoolProperty

# for file browser:
from bpy_extras.io_utils import ImportHelper


import importlib

from stampinfo.config import config


from .. import handlers
from .. import stamper
from .. import stampInfoSettings

from stampinfo.utils import utils

from stampinfo.operators import prefs
from stampinfo.operators import about

from stampinfo.operators import debug

importlib.reload(stampInfoSettings)
importlib.reload(stamper)
importlib.reload(handlers)
importlib.reload(debug)


# ------------------------------------------------------------------------#
#                               Main Panel                               #
# ------------------------------------------------------------------------#


class UAS_PT_StampInfoAddon(Panel):
    bl_idname = "UAS_PT_StampInfoAddon"
    # bl_label = f"UAS StampInfo {'.'.join ( str ( v ) for v in bl_info['version'] ) }"
    bl_label = " UAS Stamp Info   V. " + utils.addonVersion("UAS_StampInfo")[0]
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "UAS StampInfo"

    # About panel ###
    def draw_header(self, context):
        layout = self.layout
        layout.emboss = "NONE"
        row = layout.row(align=True)

        icon = config.icons_col["General_Ubisoft_32"]
        row.operator("uas_stamp_info.about", text="", icon_value=icon.icon_id)

    def draw_header_preset(self, context):
        layout = self.layout
        layout.emboss = "NONE"
        row = layout.row(align=True)

        # row.operator("render.render", text="", icon='IMAGE_DATA').animation = False            # not working with stampInfo
        # row.operator("render.render", text="", icon='RENDER_ANIMATION').animation = True       # ok
        # row.operator("utils.launchrender", text="", icon="RENDER_STILL").renderMode = "STILL"
        # row.operator("utils.launchrender", text="", icon="RENDER_ANIMATION").renderMode = "ANIMATION"

        row.separator(factor=2)

        #    row.operator("render.opengl", text="", icon='IMAGE_DATA')
        #   row.operator("render.opengl", text="", icon='RENDER_ANIMATION').animation = True
        #    row.operator("screen.screen_full_area", text ="", icon = 'FULLSCREEN_ENTER').use_hide_panels=False

        # row.operator("uas_shot_manager.go_to_video_shot_manager", text="", icon="SEQ_STRIP_DUPLICATE")

        # row.separator(factor=2)
        # icon = config.icons_col["General_Explorer_32"]
        # row.operator("uas_shot_manager.open_explorer", text="", icon_value=icon.icon_id).path = bpy.path.abspath(
        #     bpy.data.filepath
        # )

        row.separator(factor=2)
        row.menu("UAS_MT_StampInfo_prefs_mainmenu", icon="PREFERENCES", text="")

        row.separator(factor=3)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        okForRender = True

        import addon_utils

        addonWarning = [
            addon.bl_info.get("warning", "")
            for addon in addon_utils.modules()
            if addon.bl_info["name"] == "UAS_StampInfo"
        ]

        if "" != addonWarning[0]:
            row = layout.row()
            row.alignment = "CENTER"
            row.alert = True
            row.label(text=f" ***  {addonWarning[0]}  ***")
            row.alert = False

        if config.uasDebug:
            row = layout.row()
            row.alignment = "CENTER"
            row.alert = True
            row.label(text=" *** Debug Mode ***")
            row.alert = False

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
        # if '' == bpy.data.filepath:
        #     row.alert = True
        #     row.label ( text = "*** Save file first ***" )
        if None == (stamper.getInfoFileFullPath(context.scene, -1)[0]):
            row = layout.row()
            row.alert = True
            row.label(text="*** Invalid Output Path ***")
            okForRender = False
        elif "" == stamper.getRenderFileName(scene):
            row = layout.row()
            row.alert = True
            row.label(text="*** Invalid Output File Name ***")
            okForRender = False

        # if camera doen't exist
        if scene.camera is None:
            row = layout.row()
            row.alert = True
            row.label(text="*** No Camera in the Scene ***")
            okForRender = False

        # ready to render text
        if okForRender:
            row = layout.row()
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

        # ---------- corner note -------------
        box = layout.box()
        row = box.row(align=True)
        row.prop(scene.UAS_StampInfo_Settings, "cornerNoteUsed")
        if scene.UAS_StampInfo_Settings.cornerNoteUsed:
            row = box.row(align=True)
            row.prop(scene.UAS_StampInfo_Settings, "cornerNote", text="")

        # ---------- Video duration -------------
        box = layout.box()
        row = box.row(align=True)
        row.prop(scene.UAS_StampInfo_Settings, "videoDurationUsed")

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

        # ---------- Shot duration -------------
        box = layout.box()
        row = box.row(align=True)
        row.prop(scene.UAS_StampInfo_Settings, "shotDurationUsed")

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

        row = layout.row()
        row.label(text="Advanced:")
        row = layout.row()
        box = layout.box()
        box.prop(scene.UAS_StampInfo_Settings, "mediaFistFrameIsZero")


classes = (
    UAS_PT_StampInfoAddon,
    UAS_PT_StampInfoMetadata,
    UAS_PT_StampInfoLayout,
    UAS_PT_StampInfoSettings,
)
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
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
