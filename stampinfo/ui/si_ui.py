# GPLv3 License
#
# Copyright (C) 2021 Ubisoft
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

import logging

import bpy
import bpy.utils.previews
from bpy.types import Panel

import importlib

from stampinfo.config import config
from stampinfo import icons
from stampinfo.utils.utils_ui import collapsable_panel

from .. import stamper
from .. import stampInfoSettings

from stampinfo.utils import utils
from ..utils.utils_os import module_can_be_imported

from stampinfo.operators import debug

_logger = logging.getLogger(__name__)


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

    # About panel ###
    def draw_header(self, context):
        layout = self.layout
        layout.emboss = "NONE"
        row = layout.row(align=True)

        icon = icons.icons_col["StampInfo_32"]
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

        row.separator(factor=1.0)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        prefs = context.preferences.addons["stampinfo"].preferences
        okForRenderStill = True
        okForRenderAnim = True

        import addon_utils

        addonWarning = [
            addon.bl_info.get("warning", "") for addon in addon_utils.modules() if addon.bl_info["name"] == "Stamp Info"
        ]

        if "" != addonWarning[0]:
            row = layout.row()
            row.alignment = "CENTER"
            row.alert = True
            row.label(text=f" ***  {addonWarning[0]}  ***")

        if not module_can_be_imported("PIL"):
            row = layout.row()
            row.alignment = "CENTER"
            row.alert = True
            row.label(text=" *** PIL Library not found - Stamp Info cannot work normaly ***")

        if config.devDebug:
            row = layout.row()
            row.alignment = "CENTER"
            row.alert = True
            row.label(text=" *** Debug Mode ***")

        #    row     = layout.row ()
        #    row.operator("stampinfo.clearhandlers")
        #    row.operator("stampinfo.createhandlers")
        #    row.menu(SCENECAMERA_MT_SelectMenu.bl_idname,text="Selection",icon='BORDERMOVE')

        # ready to render text
        # note: we can also use bpy.data.is_saved
        if "" == bpy.data.filepath:
            if config.devDebug:
                row = layout.row()
                row.alert = True
                row.label(text="*** File Not Saved ***")
            okForRenderStill = True
            okForRenderAnim = True
        else:
            if None == (stamper.getInfoFileFullPath(context.scene, -1)[0]):
                row = layout.row()
                row.alert = True
                row.label(text="*** Invalid Output Path ***")
                okForRenderStill = False
                okForRenderAnim = False
            elif "" == stamper.getRenderFileName(scene):
                row = layout.row()
                row.alert = True
                row.label(text="*** Invalid Output File Name for Animation Rendering***")
                okForRenderStill = False
                okForRenderAnim = False

        # if camera doen't exist
        if scene.camera is None:
            row = layout.row()
            row.alert = True
            row.label(text="*** No Camera in the Scene ***")
            okForRenderStill = False
            okForRenderAnim = False

        # ready to render text
        if okForRenderStill and okForRenderAnim and config.devDebug:
            row = layout.row()
            row.label(text="Ready to render")

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

        layout.separator(factor=0.2)

        row = layout.row()
        row.prop(scene.UAS_StampInfo_Settings, "stampInfoUsed", text="Use Stamp info Framing")

        icon = icons.icons_col["General_Explorer_32"]
        renderPath = stamper.getInfoFileFullPath(context.scene, -1)[0]
        row.operator("uas_stampinfo.open_explorer", text="", icon_value=icon.icon_id).path = bpy.path.abspath(
            renderPath
        )
        layout.separator(factor=0.7)

        # main settings

        if scene.UAS_StampInfo_Settings.stampInfoUsed:
            outputResStampInfo = stamper.getRenderResolutionForStampInfo(scene)
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
            row.enabled = scene.UAS_StampInfo_Settings.stampInfoUsed
            row.prop(scene.UAS_StampInfo_Settings, "stampInfoRenderMode")

            #    print("   init ui: stampInfoRenderMode: " + str(scene.UAS_StampInfo_Settings['stampInfoRenderMode']))
            #    print("   init ui: stampInfoRenderMode: " + str(scene.UAS_StampInfo_Settings.stampInfoRenderMode))

            if "OVER" == scene.UAS_StampInfo_Settings.stampInfoRenderMode:
                row = box.row(align=True)
                row.enabled = scene.UAS_StampInfo_Settings.stampInfoUsed
                row.prop(scene.UAS_StampInfo_Settings, "stampRenderResOver_percentage")

                row = box.row(align=True)
                innerIsInAcceptableRange = 10.0 <= scene.UAS_StampInfo_Settings.stampRenderResOver_percentage <= 95.0
                subrowLeft = row.row()
                #  row.alert = not innerIsInAcceptableRange
                subrowLeft.alignment = "LEFT"
                subrowLeft.label(text=resStr)
                subrowRight = row.row()
                subrowRight.alert = not innerIsInAcceptableRange and scene.UAS_StampInfo_Settings.stampInfoUsed
                subrowRight.enabled = scene.UAS_StampInfo_Settings.stampInfoUsed
                subrowRight.alignment = "LEFT"
                subrowRight.label(text=resStr02)

            elif "OUTSIDE" == scene.UAS_StampInfo_Settings.stampInfoRenderMode:
                row = box.row(align=True)
                row.enabled = scene.UAS_StampInfo_Settings.stampInfoUsed
                row.prop(scene.UAS_StampInfo_Settings, "stampRenderResYOutside_percentage")

                row = box.row(align=True)
                outsideIsInAcceptableRange = (
                    4.0 <= scene.UAS_StampInfo_Settings.stampRenderResYOutside_percentage <= 33.35  # 18.65
                )
                subrowLeft = row.row()
                # row.alert = not outsideIsInAcceptableRange
                subrowLeft.alert = not outsideIsInAcceptableRange and scene.UAS_StampInfo_Settings.stampInfoUsed
                subrowLeft.alignment = "LEFT"
                subrowLeft.label(text=resStr)
                subrowRight = row.row()
                subrowRight.enabled = scene.UAS_StampInfo_Settings.stampInfoUsed
                subrowRight.alignment = "LEFT"
                subrowRight.label(text=resStr02)


# ------------------------------------------------------------------------#
#                             Time and Frames Panel                       #
# ------------------------------------------------------------------------#


def _getQuickHelp(topic):

    docPath = "https://ubisoft-stampinfo.readthedocs.io/"

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

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        splitFactor = 0.35
        # prefs = context.preferences.addons["stampinfo"].preferences

        def _formatRangeString(current=None, animRange=None, handles=None, start=None, end=None):
            str = ""

            if animRange is not None:
                str += "["
                if start is not None:
                    str += f"{start:03d} / "
            if handles is not None and start is not None and animRange is not None:
                str += f"{(start + handles):03d} / "

            if current is not None:
                str += f" {current:03d} "

            if handles is not None and end is not None and animRange is not None:
                str += f" / {(end - handles):03d}"
            if animRange is not None:
                if end is not None:
                    str += f" / {end:03d}"
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

        # ---------- 3D frame -------------
        box = layout.box()
        col = box.column(align=False)

        row = col.row(align=True)
        split = row.split(factor=splitFactor)
        subRow = split.row(align=True)
        subRow.prop(scene.UAS_StampInfo_Settings, "currentFrameUsed")

        sceneFrameStr, isInRange = _formatRangeString(
            current=scene.frame_current,
            animRange=None if not scene.UAS_StampInfo_Settings.animRangeUsed else False,
            handles=None if not scene.UAS_StampInfo_Settings.handlesUsed else scene.UAS_StampInfo_Settings.shotHandles,
            start=scene.frame_start,
            end=scene.frame_end,
        )

        subRowLeft = split.row(align=True)
        subRowLeft.enabled = scene.UAS_StampInfo_Settings.currentFrameUsed
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
        tooltipStr += f"\n\nOpen Stamp Info online documentation for a more detailed explaination:\n     {doc_op.path}"
        doc_op.tooltip = tooltipStr

        # ---------- 3D edit frame -------------
        if config.devDebug:
            #   box = layout.box()
            row = col.row(align=True)
            row.prop(scene.UAS_StampInfo_Settings, "edit3DFrameUsed", text="3D Edit Frame")
            videoFrameStr, isInRange = _formatRangeString(
                current=scene.frame_current - scene.frame_start,
                animRange=None if not scene.UAS_StampInfo_Settings.animRangeUsed else False,
                handles=None
                if not scene.UAS_StampInfo_Settings.handlesUsed
                else scene.UAS_StampInfo_Settings.shotHandles,
                start=0,
                end=scene.frame_end - scene.frame_start,
            )

        #        row.prop(scene.UAS_StampInfo_Settings, "edit3DTotalNumberUsed", text="3D Edit Duration")

        # ---------- video frame -------------
        row = col.row(align=True)
        split = row.split(factor=splitFactor)
        subRow = split.row(align=True)
        subRow.prop(scene.UAS_StampInfo_Settings, "videoFrameUsed")

        videoFrameStr, isInRange = _formatRangeString(
            current=scene.frame_current - scene.frame_start,
            animRange=None if not scene.UAS_StampInfo_Settings.animRangeUsed else False,
            handles=None if not scene.UAS_StampInfo_Settings.handlesUsed else scene.UAS_StampInfo_Settings.shotHandles,
            start=0,
            end=scene.frame_end - scene.frame_start,
        )

        subRowLeft = split.row(align=True)
        subRowLeft.enabled = scene.UAS_StampInfo_Settings.videoFrameUsed
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

        # ---------- shared settings -------------
        layout.label(text="Shared Settings:")
        box = layout.box()
        col = box.column(align=False)
        row = col.row(align=True)

        row.prop(scene.UAS_StampInfo_Settings, "animRangeUsed")

        handlesRow = col.row()
        handlesRow.enabled = scene.UAS_StampInfo_Settings.animRangeUsed
        # handlesRow = col.split(factor=0.5)
        split = handlesRow.split(factor=0.5)
        handlesSubRow = split.row()
        handlesSubRow.separator(factor=2)
        handlesSubRow.prop(scene.UAS_StampInfo_Settings, "handlesUsed", text="Handles (Advanced)")
        #   row.prop(scene.UAS_StampInfo_Settings, "sceneFrameHandlesUsed", text = "")
        handlesSubRow = split.row()
        handlesSubRow.enabled = scene.UAS_StampInfo_Settings.handlesUsed
        handlesSubRow.prop(scene.UAS_StampInfo_Settings, "shotHandles", text="Handles")

        # ---------- animation duration -------------
        box = layout.box()
        col = box.column(align=False)
        row = col.row(align=True)
        row.prop(scene.UAS_StampInfo_Settings, "animDurationUsed")
        subrow = row.row(align=True)
        subrow.enabled = scene.UAS_StampInfo_Settings.animDurationUsed
        subrow.label(text=f"{scene.frame_end - scene.frame_start + 1} frames")
        row = col.row(align=True)
        row.prop(scene.UAS_StampInfo_Settings, "framerateUsed")
        subrow = row.row(align=True)
        subrow.enabled = scene.UAS_StampInfo_Settings.framerateUsed
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

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        splitFactor = 0.35
        # prefs = context.preferences.addons["stampinfo"].preferences

        # ---------- shot -------------
        # To be filled by a production script or by UAS Shot Manager
        box = layout.box()
        col = box.column(align=False)
        row = col.row(align=True)
        row.prop(scene.UAS_StampInfo_Settings, "sceneUsed")

        split = col.split(factor=splitFactor)
        split.prop(scene.UAS_StampInfo_Settings, "sequenceUsed")
        split.prop(scene.UAS_StampInfo_Settings, "sequenceName", text="")

        split = col.split(factor=splitFactor)
        split.prop(scene.UAS_StampInfo_Settings, "shotUsed")
        split.prop(scene.UAS_StampInfo_Settings, "shotName", text="")

        split = col.split(factor=splitFactor)
        split.prop(scene.UAS_StampInfo_Settings, "takeUsed")
        split.prop(scene.UAS_StampInfo_Settings, "takeName", text="")

        # ---------- camera -------------
        split = col.split(factor=splitFactor)
        split.prop(scene.UAS_StampInfo_Settings, "cameraUsed")
        split.prop(scene.UAS_StampInfo_Settings, "cameraLensUsed")

        # ---------- Shot duration -------------
        box = layout.box()
        row = box.row(align=True)
        row.prop(scene.UAS_StampInfo_Settings, "shotDurationUsed")


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

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        # prefs = context.preferences.addons["stampinfo"].preferences

        layout.label(text="Top: Project and Editing Info")
        box = layout.box()

        # ---------- logo -------------
        # box = layout.box()
        row = box.row(align=True)
        row.prop(scene.UAS_StampInfo_Settings, "logoUsed")

        if scene.UAS_StampInfo_Settings.logoUsed:

            row = box.row(align=False)
            row.prop(scene.UAS_StampInfo_Settings, "logoMode", text="")

            if "BUILTIN" == scene.UAS_StampInfo_Settings.logoMode:
                row.prop(scene.UAS_StampInfo_Settings, "logoBuiltinName", text="")

            else:
                subRow = row.row(align=True)
                subRow.prop(scene.UAS_StampInfo_Settings, "logoFilepath")
                subRow.operator("stampinfo.openfilebrowser", text="", icon="FILEBROWSER", emboss=True)

            row = box.row(align=True)
            row.prop(scene.UAS_StampInfo_Settings, "logoScaleH")

            row = box.row(align=True)
            row.prop(scene.UAS_StampInfo_Settings, "logoPosNormX")
            row.prop(scene.UAS_StampInfo_Settings, "logoPosNormY")

        # ---------- project -------------
        if scene.UAS_StampInfo_Settings.logoUsed:
            box.separator(factor=0.3)
        row = box.row(align=True)
        row.prop(scene.UAS_StampInfo_Settings, "projectUsed")
        row.prop(scene.UAS_StampInfo_Settings, "projectName")

        # ---------- date and user ----
        box = layout.box()
        col = box.column(align=False)
        row = col.row(align=True)
        row.prop(scene.UAS_StampInfo_Settings, "dateUsed")
        row.prop(scene.UAS_StampInfo_Settings, "timeUsed")
        row = col.row(align=True)
        row.prop(scene.UAS_StampInfo_Settings, "userNameUsed")

        # ---------- file -------------
        box = layout.box()
        row = box.row(align=True)
        row.prop(scene.UAS_StampInfo_Settings, "filenameUsed")
        row.prop(scene.UAS_StampInfo_Settings, "filepathUsed")

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

        # ---------- bottom note -------------
        box = layout.box()
        row = box.row(align=True)
        row.prop(scene.UAS_StampInfo_Settings, "bottomNoteUsed")
        if scene.UAS_StampInfo_Settings.bottomNoteUsed:
            row = box.row(align=True)
            row.prop(scene.UAS_StampInfo_Settings, "bottomNote", text="")


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

        row = box.row()
        row.prop(scene.UAS_StampInfo_Settings, "extPaddingHorizNorm")

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
    bl_category = "Stamp Info"
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


classes = (
    UAS_PT_StampInfoAddon,
    UAS_PT_StampInfoTimeAndFrames,
    UAS_PT_StampInfoShot,
    UAS_PT_StampInfoMetadata,
    UAS_PT_StampInfoLayout,
    UAS_PT_StampInfoSettings,
)


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
