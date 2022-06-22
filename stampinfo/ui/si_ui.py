# GPLv3 License
#
# Copyright (C) 2022 Ubisoft
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Main panel UI
"""


import bpy
import bpy.utils.previews
from bpy.types import Panel, Operator

import importlib

from stampinfo.config import config
from stampinfo import icons
from stampinfo.utils.utils_ui import collapsable_panel

from ..properties import stamper
from .. import stampInfoSettings

from stampinfo.utils import utils
from ..utils.utils_os import module_can_be_imported

from stampinfo.operators import debug

from stampinfo.config import sm_logging

_logger = sm_logging.getLogger(__name__)


importlib.reload(stampInfoSettings)
importlib.reload(stamper)
importlib.reload(debug)


# ------------------------------------------------------------------------#
#                               Main Panel                               #
# ------------------------------------------------------------------------#


class UAS_PT_StampInfoAddon(Panel):
    bl_idname = "UAS_PT_StampInfoAddon"
    # bl_label = f"UAS StampInfo {'.'.join ( str ( v ) for v in bl_info['version'] ) }"
    bl_label = " Stamp Info   V. " + utils.addonVersion("Stamp Info")[0]
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Stamp Info"

    @classmethod
    def poll(self, context):
        prefs = context.preferences.addons["stampinfo"].preferences
        return prefs.display_main_panel

    # About panel ###
    def draw_header(self, context):
        layout = self.layout
        layout.emboss = "NONE"
        row = layout.row(align=True)

        icon = icons.icons_col["StampInfo_32"]
        row.operator("uas_stamp_info.about", text="", icon_value=icon.icon_id)

    def draw_header_preset(self, context):
        prefs = context.preferences.addons["stampinfo"].preferences
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

        # row.separator(factor=2)
        # icon = config.icons_col["General_Explorer_32"]
        # row.operator("uas_stamp_info.open_explorer", text="", icon_value=icon.icon_id).path = bpy.path.abspath(
        #     bpy.data.filepath
        # )

        row.separator(factor=2)
        row.menu("UAS_MT_StampInfo_prefs_mainmenu", icon="PREFERENCES", text="")

        if not config.devDebug and prefs.checkForNewAvailableVersion and prefs.newAvailableVersion:
            row.separator(factor=0.5)
            subRow = row.row()
            subRow.alert = True
            subRow.operator("uas_stamp_info.update_dialog", text="", icon="WORLD_DATA")

        row.separator(factor=1.0)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        prefs = context.preferences.addons["stampinfo"].preferences
        siSettings = scene.UAS_StampInfo_Settings
        okForRenderStill = True
        okForRenderAnim = True

        import addon_utils

        addonWarning = [
            addon.bl_info.get("warning", "") for addon in addon_utils.modules() if addon.bl_info["name"] == "Stamp Info"
        ]
        warnCol = layout.column(align=False)
        warnCol.scale_y = 0.8

        if "" != addonWarning[0]:
            row = warnCol.row()
            row.alignment = "CENTER"
            row.alert = True
            row.label(text=f" ***  {addonWarning[0]}  ***")

        if not module_can_be_imported("PIL"):
            row = warnCol.row()
            row.alignment = "CENTER"
            row.alert = True
            row.label(text=" *** PIL Library not found - Stamp Info cannot work normally ***")

        if config.devDebug:
            row = warnCol.row()
            row.alignment = "CENTER"
            row.alert = True
            row.label(text=" *** Debug Mode ***")

        #    row     = warnCol.row ()
        #    row.operator("stampinfo.clearhandlers")
        #    row.operator("stampinfo.createhandlers")
        #    row.menu(SCENECAMERA_MT_SelectMenu.bl_idname,text="Selection",icon='BORDERMOVE')

        # ready to render text
        # note: we can also use bpy.data.is_saved
        if "" == bpy.data.filepath:
            if config.devDebug:
                row = warnCol.row()
                row.alert = True
                row.label(text="*** File Not Saved ***")
            okForRenderStill = True
            okForRenderAnim = True
        else:
            if None == (stamper.getInfoFileFullPath(context.scene, -1)[0]):
                row = warnCol.row()
                row.alert = True
                row.label(text="*** Invalid Output Path ***")
                okForRenderStill = False
                okForRenderAnim = False
            elif "" == stamper.getRenderFileName(scene):
                row = warnCol.row()
                row.alert = True
                row.label(text="*** Invalid Output File Name for Animation Rendering***")
                okForRenderStill = False
                okForRenderAnim = False

        # if camera doen't exist
        if scene.camera is None:
            row = warnCol.row()
            row.alert = True
            row.label(text="*** No Camera in the Scene ***")
            okForRenderStill = False
            okForRenderAnim = False

        # if current res is not multiples of 2
        if 0 != scene.render.resolution_x % 2 or 0 != scene.render.resolution_y % 2:
            row = warnCol.row()
            row.alert = True
            row.label(text="*** Rendering resolution must use multiples of 2 ***")
            okForRenderStill = False
            okForRenderAnim = False

        # if still image file format is invalid
        if scene.render.image_settings.file_format in ["FFMPEG", "AVI_RAW", "AVI_JPEG"]:
            row = warnCol.row()
            row.alert = True
            row.label(text="*** Rendering file format is not suitable for still image ***")
            okForRenderStill = False
            okForRenderAnim = True

        # if still image file format is invalid
        # if scene.render.image_settings.file_format in ['BMP', 'IRIS', 'PNG', 'JPEG', 'JPEG2000', 'TARGA', 'TARGA_RAW', 'CINEON', 'DPX', 'OPEN_EXR_MULTILAYER', 'OPEN_EXR', 'HDR', 'TIFF', 'AVI_JPEG', 'AVI_RAW', 'FFMPEG']:
        if scene.render.image_settings.file_format not in ["PNG", "FFMPEG"]:  # "JPEG",
            row = warnCol.row()
            row.alert = True
            row.label(text="*** Rendering file formats other than PNG and FFMPEG are not supported yet ***")
            okForRenderStill = False
            okForRenderAnim = False

        # ready to render text
        if okForRenderStill and okForRenderAnim and config.devDebug:
            row = warnCol.row()
            row.label(text="Ready to render")

        # NOTE: Shot Manager Prefs and Shot Manager scene instance are initialized here:
        if not siSettings.isInitialized:
            layout.separator()
            row = layout.row()
            row.alert = True
            row.operator("uas_stamp_info.initialize")
            row.alert = False
            layout.separator()

        # render buttons
        renderMainRow = layout.split(factor=0.45, align=False)
        renderMainRow.scale_y = 1.4
        renderStillRow = renderMainRow.row()
        renderStillRow.enabled = okForRenderStill
        renderStillRow.operator("uas_stampinfo.render", text=" Render Image", icon="IMAGE_DATA").renderMode = "STILL"

        renderAnimRow = renderMainRow.row()
        renderAnimRow.enabled = okForRenderAnim
        renderAnimRow.operator(
            "uas_stampinfo.render", text=" Render Animation", icon="RENDER_ANIMATION"
        ).renderMode = "ANIMATION"

        col = layout.column(align=False)
        col.scale_y = 0.9

        sepRow = col.row()
        sepRow.separator(factor=0.2)

        row = col.row()
        row.prop(siSettings, "stampInfoUsed", text="Use Stamp Info")

        row = col.row()
        row.enabled = siSettings.stampInfoUsed
        split = row.split(factor=0.5)
        split.label(text="Output Images Indices:")

        subRow = split.row()
        icon = icons.icons_col["General_Explorer_32"]
        renderPath = stamper.getInfoFileFullPath(context.scene, -1)[0]
        subRow.alignment = "RIGHT"
        subRow.prop(siSettings, "outputImgIndicesMode", text="")
        subRow.operator("uas_stampinfo.open_explorer", text="", icon_value=icon.icon_id).path = bpy.path.abspath(
            renderPath
        )

        sepRow = col.row()
        sepRow.separator(factor=0.2)

        # main settings
        ##################################

        if siSettings.stampInfoUsed:
            outputResStampInfo = stamper.getRenderResolutionForStampInfo(scene, forceMultiplesOf2=False)
            resStr = "Final Res: " + str(outputResStampInfo[0]) + " x " + str(outputResStampInfo[1]) + " px"
        else:
            outputResRender = stamper.getRenderResolution(scene)
            resStr = "Final Res: " + str(outputResRender[0]) + " x " + str(outputResRender[1]) + " px"

        resStr02 = "-  Inner Height: " + str(stamper.getInnerHeight(scene)) + " px"

        panelTitleRow = layout.row(align=True)
        collapsable_panel(panelTitleRow, prefs, "panelExpanded_mode", text=resStr)

        if prefs.panelExpanded_mode:
            box = layout.box()
            row = box.row(align=True)
            row.enabled = siSettings.stampInfoUsed
            row.prop(siSettings, "stampInfoRenderMode")

            #    print("   init ui: stampInfoRenderMode: " + str(siSettings['stampInfoRenderMode']))
            #    print("   init ui: stampInfoRenderMode: " + str(siSettings.stampInfoRenderMode))

            if "OVER" == siSettings.stampInfoRenderMode:
                row = box.row(align=True)
                row.enabled = siSettings.stampInfoUsed
                row.prop(siSettings, "stampRenderResOver_percentage")

                row = box.row(align=True)
                innerIsInAcceptableRange = 10.0 <= siSettings.stampRenderResOver_percentage <= 95.0
                subrowLeft = row.row()
                #  row.alert = not innerIsInAcceptableRange
                subrowLeft.alignment = "LEFT"
                subrowLeft.label(text=resStr)
                subrowRight = row.row()
                subrowRight.alert = not innerIsInAcceptableRange and siSettings.stampInfoUsed
                subrowRight.enabled = siSettings.stampInfoUsed
                subrowRight.alignment = "LEFT"
                subrowRight.label(text=resStr02)

            elif "OUTSIDE" == siSettings.stampInfoRenderMode:
                row = box.row(align=True)
                row.enabled = siSettings.stampInfoUsed
                row.prop(siSettings, "stampRenderResYOutside_percentage")

                row = box.row(align=True)
                outsideIsInAcceptableRange = 4.0 <= siSettings.stampRenderResYOutside_percentage <= 33.35  # 18.65
                subrowLeft = row.row()
                # row.alert = not outsideIsInAcceptableRange
                subrowLeft.alert = not outsideIsInAcceptableRange and siSettings.stampInfoUsed
                subrowLeft.alignment = "LEFT"
                subrowLeft.label(text=resStr)
                subrowRight = row.row()
                subrowRight.enabled = siSettings.stampInfoUsed
                subrowRight.alignment = "LEFT"
                subrowRight.label(text=resStr02)


# ------------------------------------------------------------------------#
#                             Time and Frames Panel                       #
# ------------------------------------------------------------------------#


def _getQuickHelp(topic):

    docPath = "https://ubisoft-stampinfo.readthedocs.io/en/latest/features/time-and-frame-info.html"

    if "3D_FRAME" == topic:
        title = "3D Frame"
        text = "Stamp the current frame index and the animation range on the output images."
        text += "\nFrames will be in the 3D time, which is the time of the current scene."
        text += "\n\nIf Frame Range property is checked then the animation range will be displayed as:"
        text += "\n    [ Start  /  current frame  /  End ]"
        text += "\n\nIf Handles property is also checked then the display will be:"
        text += "\n    [ Start  /  Start + Handle  / current frame  /  End - Handle  /  End ]"
        text += "\n\nUI text is displayed in red when the current time is out of the animation range"

        # TODO wkip add doc anchor to each path
        docPath += ""
    elif "VIDEO_FRAME" == topic:
        title = "Video Frame"
        text = "Stamp the current frame index and the animation range on the output images"
        text += "\nIN THE TIME OF THE VIDEO."
        text += "\n\nIf Frame Range property is checked then the animation range will be displayed as:"
        text += "\n    [ 0  /  current frame - Start  /  End - Start ]"
        text += "\n\nIf Handles property is also checked then the display will be:"
        text += "\n    [ 0  /  Handle  / current frame - Start  /  End - Start - Handle  /  End - Start ]"
        text += "\n\nUI text is displayed in red when the current time is out of the animation range"

    tooltip = "Quick tips about " + title
    return (tooltip, title, text, docPath)


class UAS_PT_StampInfoTimeAndFrames(Panel):
    bl_idname = "UAS_PT_StampInfoTimeAndFrames"
    bl_label = "Time and Frames"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Stamp Info"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(self, context):
        prefs = context.preferences.addons["stampinfo"].preferences
        return prefs.display_main_panel

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        siSettings = scene.UAS_StampInfo_Settings
        splitFactor = 0.35
        # prefs = context.preferences.addons["stampinfo"].preferences

        def _formatRangeString(current=None, animRange=None, handles=None, start=None, end=None, offset=0, padding=3):
            str = ""
            fmt = f"0{padding}d"

            if animRange is not None:
                str += "["
                if start is not None:
                    str += f"{start + offset:{fmt}} / "
            if handles is not None and start is not None and animRange is not None:
                str += f"{(start + handles + offset):{fmt}} / "

            if current is not None:
                str += f" {current + offset:{fmt}} "

            if handles is not None and end is not None and animRange is not None:
                str += f" / {(end - handles + offset):{fmt}}"
            if animRange is not None:
                if end is not None:
                    str += f" / {end + offset:{fmt}}"
                str += "]"

            # return True if current frame is in the animation range
            isInRange = True
            if current is not None and animRange is not None:
                # this is not dependent on handles
                # if handles is not None:
                isInRange = start <= current <= end
                # else:
                #     isInRange = start + handles <= current <= end + handles

            return str, isInRange

        #        layout.label(text="Top: Project and Editing Info")

        box = layout.box()
        col = box.column(align=False)

        # ---------- 3D edit frame -------------
        if config.devDebug:
            #   box = layout.box()
            row = col.row(align=True)
            row.prop(siSettings, "edit3DFrameUsed", text="3D Edit Frame")
            videoFrameStr, isInRange = _formatRangeString(
                current=scene.frame_current - scene.frame_start,
                animRange=None if not siSettings.animRangeUsed else False,
                handles=None if not siSettings.handlesUsed else siSettings.shotHandles,
                start=0,
                end=scene.frame_end - scene.frame_start,
                offset=0,
                padding=siSettings.frameDigitsPadding,
            )

        #        row.prop(siSettings, "edit3DTotalNumberUsed", text="3D Edit Duration")

        # ---------- video frame -------------
        row = col.row(align=True)
        split = row.split(factor=splitFactor)
        subRow = split.row(align=True)
        subRow.prop(siSettings, "videoFrameUsed")

        videoFrameStr, isInRange = _formatRangeString(
            current=scene.frame_current - scene.frame_start,
            animRange=None if not siSettings.animRangeUsed else False,
            handles=None if not siSettings.handlesUsed else siSettings.shotHandles,
            start=0,
            end=scene.frame_end - scene.frame_start,
            offset=siSettings.videoFirstFrameIndex if siSettings.videoFirstFrameIndexUsed else 0,
            padding=siSettings.frameDigitsPadding,
        )

        subRowLeft = split.row(align=True)
        subRowLeft.enabled = siSettings.videoFrameUsed
        subRowLeft.alignment = "CENTER"
        subRowLeft.alert = not isInRange
        subRowLeft.label(text=videoFrameStr)

        # help tooltip and doc
        subRowRight = row.row(align=True)
        subRowRight.emboss = "NONE"
        subRowRight.alignment = "RIGHT"
        doc_op = subRowRight.operator("stampinfo.open_documentation_url", text="", icon="INFO")
        quickHelpInfo = _getQuickHelp("VIDEO_FRAME")
        doc_op.path = quickHelpInfo[3]
        tooltipStr = quickHelpInfo[1]
        tooltipStr += f"\n{quickHelpInfo[2]}"
        tooltipStr += f"\n\nOpen Stamp Info online documentation:\n     {doc_op.path}"
        doc_op.tooltip = tooltipStr

        subRow = col.row(align=True)
        subRow.enabled = siSettings.videoFrameUsed
        split = subRow.split(factor=0.5)
        labSubRow = split.row()
        labSubRow.separator(factor=2)
        labSubRow.prop(siSettings, "videoFirstFrameIndexUsed", text="First Frame Index")
        frameIndSubRow = split.row()
        frameIndSubRow.enabled = siSettings.videoFirstFrameIndexUsed
        frameIndSubRow.prop(siSettings, "videoFirstFrameIndex", text="")

        # ---------- 3D frame -------------
        row = col.row(align=True)
        split = row.split(factor=splitFactor)
        subRow = split.row(align=True)
        subRow.prop(siSettings, "currentFrameUsed")

        sceneFrameStr, isInRange = _formatRangeString(
            current=scene.frame_current,
            animRange=None if not siSettings.animRangeUsed else False,
            handles=None if not siSettings.handlesUsed else siSettings.shotHandles,
            start=scene.frame_start,
            end=scene.frame_end,
            padding=siSettings.frameDigitsPadding,
        )

        subRowLeft = split.row(align=True)
        subRowLeft.enabled = siSettings.currentFrameUsed
        subRowLeft.alignment = "CENTER"
        subRowLeft.alert = not isInRange
        subRowLeft.label(text=sceneFrameStr)

        # help tooltip and doc
        subRowRight = row.row(align=True)
        subRowRight.emboss = "NONE"
        subRowRight.alignment = "RIGHT"
        doc_op = subRowRight.operator("stampinfo.open_documentation_url", text="", icon="INFO")
        quickHelpInfo = _getQuickHelp("3D_FRAME")
        doc_op.path = quickHelpInfo[3]
        tooltipStr = quickHelpInfo[1]
        tooltipStr += f"\n{quickHelpInfo[2]}"
        tooltipStr += f"\n\nOpen Stamp Info online documentation for a more detailed explanation:\n     {doc_op.path}"
        doc_op.tooltip = tooltipStr

        # ---------- shared settings -------------
        layout.label(text="Shared Settings:")
        box = layout.box()
        col = box.column(align=False)
        row = col.row(align=True)

        row.prop(siSettings, "animRangeUsed")

        handlesRow = col.row()
        handlesRow.enabled = siSettings.animRangeUsed
        # handlesRow = col.split(factor=0.5)
        split = handlesRow.split(factor=0.5)
        handlesSubRow = split.row()
        handlesSubRow.separator(factor=2)
        handlesSubRow.prop(siSettings, "handlesUsed", text="Handles (Advanced)")
        #   row.prop(siSettings, "sceneFrameHandlesUsed", text = "")
        handlesSubRow = split.row()
        handlesSubRow.enabled = siSettings.handlesUsed
        handlesSubRow.prop(siSettings, "shotHandles", text="Handles")

        sepRow = col.row()
        sepRow.separator(factor=0.2)

        paddingRow = col.row()
        split = paddingRow.split(factor=0.5)
        split.label(text="Digits Padding")
        split.prop(siSettings, "frameDigitsPadding", text="")

        # ---------- animation duration -------------
        box = layout.box()
        col = box.column(align=False)
        row = col.row(align=True)
        row.prop(siSettings, "animDurationUsed")
        subrow = row.row(align=True)
        subrow.enabled = siSettings.animDurationUsed
        subrow.label(text=f"{scene.frame_end - scene.frame_start + 1} frames")
        row = col.row(align=True)
        row.prop(siSettings, "framerateUsed")
        subrow = row.row(align=True)
        subrow.enabled = siSettings.framerateUsed
        subrow.label(text=f"{scene.render.fps} fps")


# ------------------------------------------------------------------------#
#                             Shot and cam Panel                          #
# ------------------------------------------------------------------------#
class UAS_PT_StampInfoShot(Panel):
    bl_idname = "UAS_PT_StampInfoShot"
    bl_label = "Shot and Camera"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Stamp Info"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(self, context):
        prefs = context.preferences.addons["stampinfo"].preferences
        return prefs.display_main_panel

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        siSettings = scene.UAS_StampInfo_Settings
        splitFactor = 0.35
        # prefs = context.preferences.addons["stampinfo"].preferences

        # ---------- shot -------------
        # To be filled by a production script or by UAS Shot Manager
        box = layout.box()
        col = box.column(align=False)
        row = col.row(align=True)
        row.prop(siSettings, "sceneUsed")

        split = col.split(factor=splitFactor)
        split.prop(siSettings, "sequenceUsed")
        split.prop(siSettings, "sequenceName", text="")

        split = col.split(factor=splitFactor)
        split.prop(siSettings, "takeUsed")
        split.prop(siSettings, "takeName", text="")

        split = col.split(factor=splitFactor)
        split.prop(siSettings, "shotUsed")
        split.prop(siSettings, "shotName", text="")

        # ---------- camera -------------
        split = col.split(factor=splitFactor)
        split.prop(siSettings, "cameraUsed")
        split.prop(siSettings, "cameraLensUsed")

        # ---------- Shot duration -------------
        box = layout.box()
        row = box.row(align=True)
        row.prop(siSettings, "shotDurationUsed")


# ------------------------------------------------------------------------#
#                             Metadata Panel                             #
# ------------------------------------------------------------------------#
class UAS_PT_StampInfoMetadata(Panel):
    bl_idname = "UAS_PT_StampInfoMetadata"
    bl_label = "Metadata"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Stamp Info"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(self, context):
        prefs = context.preferences.addons["stampinfo"].preferences
        return prefs.display_main_panel

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        # prefs = context.preferences.addons["stampinfo"].preferences
        siSettings = scene.UAS_StampInfo_Settings

        layout.label(text="Top: Project and Editing Info")
        box = layout.box()

        # ---------- logo -------------
        row = box.row(align=True)
        row.prop(siSettings, "logoUsed")

        if siSettings.logoUsed:

            row = box.row(align=False)
            row.prop(siSettings, "logoMode", text="")

            if "BUILTIN" == siSettings.logoMode:
                row.prop(siSettings, "logoBuiltinName", text="")

            else:
                subRow = row.row(align=True)
                subRow.prop(siSettings, "logoFilepath")
                subRow.operator("stampinfo.openfilebrowser", text="", icon="FILEBROWSER", emboss=True)

            row = box.row(align=True)
            row.prop(siSettings, "logoScaleH")

            row = box.row(align=True)
            row.prop(siSettings, "logoPosNormX")
            row.prop(siSettings, "logoPosNormY")

        # ---------- project -------------
        if siSettings.logoUsed:
            box.separator(factor=0.3)
        row = box.row(align=True)
        row.prop(siSettings, "projectUsed")
        row.prop(siSettings, "projectName")

        # ---------- date and user ----
        box = layout.box()
        col = box.column(align=False)
        row = col.row(align=True)
        row.prop(siSettings, "dateUsed")
        row.prop(siSettings, "timeUsed")
        row = col.row(align=True)
        row.prop(siSettings, "userNameUsed")

        # ---------- file -------------
        box = layout.box()
        row = box.row(align=True)
        row.prop(siSettings, "filenameUsed")
        row.prop(siSettings, "filepathUsed")

        # ---------- notes -------------
        box = layout.box()
        col = box.column(align=False)
        col.prop(siSettings, "notesUsed")
        if siSettings.notesUsed:
            col.prop(siSettings, "notesLine01", text="")
            col.prop(siSettings, "notesLine02", text="")
            col.prop(siSettings, "notesLine03", text="")

        # ---------- corner note -------------
        box = layout.box()
        col = box.column(align=False)
        col.prop(siSettings, "cornerNoteUsed")
        if siSettings.cornerNoteUsed:
            col.prop(siSettings, "cornerNote", text="")

        # ---------- bottom note -------------
        box = layout.box()
        col = box.column(align=False)
        row.prop(siSettings, "bottomNoteUsed")
        if siSettings.bottomNoteUsed:
            col.prop(siSettings, "bottomNote", text="")


# ------------------------------------------------------------------------#
#                             Layout Panel                               #
# ------------------------------------------------------------------------#
class UAS_PT_StampInfoLayout(Panel):
    bl_idname = "UAS_PT_StampInfoLayout"
    bl_label = "Text and Layout"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Stamp Info"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(self, context):
        prefs = context.preferences.addons["stampinfo"].preferences
        return prefs.display_main_panel

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        siSettings = scene.UAS_StampInfo_Settings

        box = layout.box()
        row = box.row()
        row.prop(siSettings, "textColor")

        row = box.row()
        row.prop(siSettings, "automaticTextSize", text="Fit Text in Borders")

        # if not siSettings.automaticTextSize:
        row = box.row()
        row.prop(siSettings, "fontScaleHNorm", text="Text Size")

        row = box.row()
        row.prop(siSettings, "interlineHNorm", text="Interline Size")

        row = box.row()
        row.prop(siSettings, "extPaddingNorm")

        row = box.row()
        row.prop(siSettings, "extPaddingHorizNorm")

        # ---------- border -------------
        box = layout.box()
        row = box.row(align=True)

        # if stamper.getRenderRatio(scene) + 0.002 >= siSettings.innerImageRatio \
        #     and siSettings.borderUsed:
        #     row.alert = True

        row.prop(siSettings, "borderUsed")
        row.prop(siSettings, "borderColor")

    #    row.prop(siSettings, "innerImageRatio")

    # row = layout.row()
    # row.prop(siSettings, "linkTextToBorderEdge")


# ------------------------------------------------------------------------#
#                             Settings Panel                             #
# ------------------------------------------------------------------------#
class UAS_PT_StampInfoSettings(Panel):
    bl_idname = "UAS_PT_StampInfoSettings"
    bl_label = "Settings"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Stamp Info"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(self, context):
        prefs = context.preferences.addons["stampinfo"].preferences
        return prefs.display_main_panel

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        siSettings = scene.UAS_StampInfo_Settings

        # row = layout.row()
        # row.prop(siSettings, "linkTextToBorderEdge")

        row = layout.row()
        row.prop(siSettings, "stampPropertyLabel")

        row = layout.row()
        row.prop(siSettings, "stampPropertyValue")


#########
# MISC
#########


class UAS_PT_StampInfo_Initialize(Operator):
    bl_idname = "uas_stamp_info.initialize"
    bl_label = "Initialize Stamp Info"
    bl_description = "Initialize Stamp Info"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        context.scene.UAS_StampInfo_Settings.initialize_stamp_info()

        return {"FINISHED"}


classes = (
    UAS_PT_StampInfoAddon,
    UAS_PT_StampInfoTimeAndFrames,
    UAS_PT_StampInfoShot,
    UAS_PT_StampInfoMetadata,
    UAS_PT_StampInfoLayout,
    UAS_PT_StampInfoSettings,
    UAS_PT_StampInfo_Initialize,
)


def register():
    _logger.debug_ext("       - Registering Main UI Package", form="REG")

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    _logger.debug_ext("       - Unregistering Main UI Package", form="UNREG")

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
