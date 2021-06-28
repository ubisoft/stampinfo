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
To do: module description here.
"""

import bpy
from bpy.types import Operator
from bpy.props import EnumProperty
from ..utils.utils_render import getRenderOutputFilename
from ..utils.utils_filenames import SequencePath

from pathlib import Path

from stampinfo import stamper


class UAS_PT_StampInfo_Render(Operator):
    bl_idname = "uas_stampinfo.render"
    bl_label = "Render"
    bl_description = "Render."
    bl_options = {"INTERNAL"}

    renderMode: EnumProperty(
        name="Display Shot Properties Mode",
        description="Update the content of the Shot Properties panel either on the current shot\nor on the shot seleted in the shots list",
        items=(("STILL", "Still", ""), ("ANIMATION", "Animation", "")),
        default="STILL",
    )

    @classmethod
    def description(self, context, properties):
        descr = "_"
        # print("properties: ", properties)
        # print("properties action: ", properties.action)
        if "STILL" == properties.renderMode:
            descr = "Render a still image at current frame"

        elif "ANIMATION" == properties.renderMode:
            descr = "Render animation"
        return descr

    # def invoke(self, context, event):
    #     # context.window_manager.modal_handler_add(self)
    #     return {"RUNNING_MODAL"}

    # def modal(self, context, event):
    #     # https://blender.stackexchange.com/questions/78069/modal-function-of-a-modal-operator-is-never-called
    #     if event.type == "SPACE":
    #         # wm = context.window_manager
    #         # wm.invoke_popup(self)
    #         # #wm.invoke_props_dialog(self)
    #         print("Space")

    #     if event.type in {"ESC"}:
    #         return {"CANCELLED"}

    #     return {"RUNNING_MODAL"}

    def execute(self, context):

        scene = context.scene
        stampInfoSettings = scene.UAS_StampInfo_Settings

        if not stampInfoSettings.stampInfoUsed:
            if "STILL" == self.renderMode:
                bpy.ops.render.render("INVOKE_DEFAULT", use_viewport=True)
            elif "ANIMATION" == self.renderMode:
                bpy.ops.render.render("INVOKE_DEFAULT", animation=True, use_viewport=True)
            return {"FINISHED"}

        vse_render = context.window_manager.UAS_vse_render

        previousRenderPath = scene.render.filepath

        seqPath = SequencePath(bpy.path.abspath(scene.render.filepath))
        seqPath.print()

        print(f"seqPath.sequence_name(): {seqPath.sequence_name()}")
        tempFramedRenderPath = seqPath.parent() + "_tmp_StampInfo_framing" + "\\"
        print(f"tempFramedRenderPath: {tempFramedRenderPath}")
        if not Path(tempFramedRenderPath).exists():
            Path(tempFramedRenderPath).mkdir(parents=True, exist_ok=True)

        tempImgRenderPath = seqPath.parent() + "_tmp_StampInfo_render" + "\\"
        print(f"tempImgRenderPath: {tempImgRenderPath}")
        if not Path(tempImgRenderPath).exists():
            Path(tempImgRenderPath).mkdir(parents=True, exist_ok=True)

        scene.render.filepath = f"{tempImgRenderPath}{seqPath.sequence_name()}"
        print(f" scene.render.filepath: {scene.render.filepath}")

        if "STILL" == self.renderMode:
            print("Render a still image at current frame")

            displayRenderWindow = False
            #     bpy.ops.render.view_show()
            # bpy.ops.render.render(use_viewport=True)
            if displayRenderWindow:
                bpy.ops.render.render("INVOKE_DEFAULT", animation=False, write_still=True, use_viewport=False)
            else:
                bpy.ops.render.render(animation=False, write_still=True, use_viewport=False)

            stampInfoSettings.renderTmpImageWithStampedInfo(scene, scene.frame_current, renderPath=tempFramedRenderPath)

        elif "ANIMATION" == self.renderMode:
            print("Render animation")

            displayRenderWindow = False
            #     bpy.ops.render.view_show()
            # bpy.ops.render.render(use_viewport=True)
            if displayRenderWindow:
                bpy.ops.render.render("INVOKE_DEFAULT", animation=True, use_viewport=False)
            else:
                bpy.ops.render.render(animation=True, use_viewport=False)

            #    outputFiles = getRenderOutputFilename(scene)

            for currentFrame in range(scene.frame_start, scene.frame_end + 1):
                # scene.frame_current = currentFrame
                scene.frame_set(currentFrame)
                # scene.UAS_StampInfo_Settings.renderRootPathUsed = True
                # scene.UAS_StampInfo_Settings.renderRootPath = tempRenderPath

                stampInfoSettings.renderTmpImageWithStampedInfo(
                    scene, scene.frame_current, renderPath=tempFramedRenderPath
                )

            # lister images temps stamp info
            # lister images temp image

        # for some reason this cannot be set right after the call to the render otherwise it is considered as the effective render path
        scene.render.filepath = previousRenderPath

        # compositer
        # use vse_render to store all the elements to composite
        res = [scene.render.resolution_x, scene.render.resolution_y]
        vse_render.clearMedia()
        vse_render.inputBGMediaPath = tempImgRenderPath + seqPath.sequence_name()
        print(f" vse BG: vse_render.inputBGMediaPath: {vse_render.inputBGMediaPath}")
        vse_render.inputBGResolution = res

        specificFrame = None
        if "STILL" == self.renderMode:
            specificFrame = scene.frame_current

        # frameIndStr = "####" if specificFrame is None else f"{specificFrame:04}"
        # #  _logger.debug(f"\n - specificFrame: {specificFrame}")
        # infoImgSeq = tempFramedRenderPath + "_tmp_StampInfo." + frameIndStr + ".png"

        dirAndFilename = stamper.getInfoFileFullPath(scene, specificFrame)
        infoImgSeq = tempFramedRenderPath + dirAndFilename[1]

        print(f" vse over: infoImgSeq: {infoImgSeq}")
        vse_render.inputOverMediaPath = infoImgSeq
        vse_render.inputOverResolution = res

        # vse_render.inputAudioMediaPath = audioFilePath

        #        compositedMediaPath = renderPath + "FramedOutput" + "\\"
        compositedMediaPath = f"{seqPath.parent()}"
        print(f"compositedMediaPath: {compositedMediaPath}")

        if "STILL" == self.renderMode:
            video_frame_end = 1
        else:
            video_frame_end = scene.frame_end - scene.frame_start + 1

        if True:
            vse_render.compositeVideoInVSE(
                scene.render.fps,
                1,
                video_frame_end,
                compositedMediaPath + seqPath.sequence_name(),
                # compositedMediaPath + "def###.png",
                "defrender",
                output_resolution=res,
            )
        # cleaner

        # en bg, ne s'arrete pas
        # bpy.ops.render.render(animation = True)

        # bpy.ops.render.opengl ( animation = True )

        # props = context.scene.UAS_shot_manager_props
        # prefs = context.preferences.addons["shotmanager"].preferences
        # prefs.renderMode = self.renderMode

        # # update UI
        # if "STILL" == prefs.renderMode:
        #     props.displayStillProps = True
        # elif "ANIMATION" == prefs.renderMode:
        #     props.displayAnimationProps = True
        # elif "ALL" == prefs.renderMode:
        #     props.displayAllEditsProps = True
        # elif "OTIO" == prefs.renderMode:
        #     props.displayOtioProps = True
        # elif "PLAYBLAST" == prefs.renderMode:
        #     props.displayPlayblastProps = True

        # if not props.sceneIsReady():
        #     return {"CANCELLED"}

        # if "ANIMATION" == prefs.renderMode:
        #     currentShot = props.getCurrentShot()
        #     if currentShot is None:
        #         utils.ShowMessageBox("Current Shot not found - Rendering aborted", "Render aborted")
        #         return {"CANCELLED"}
        #     if not currentShot.enabled:
        #         utils.ShowMessageBox("Current Shot is not enabled - Rendering aborted", "Render aborted")
        #         return {"CANCELLED"}

        # # renderWarnings = ""
        # # if props.renderRootPath.startswith("//"):
        # #     if "" == bpy.data.filepath:
        # #         renderWarnings = "*** Save file first ***"
        # # elif "" == props.renderRootPath:
        # #     renderWarnings = "*** Invalid Output File Name ***"

        # # if "" != renderWarnings:
        # #     from ..utils.utils import ShowMessageBox

        # #     ShowMessageBox(renderWarnings, "Render Aborted", "ERROR")
        # #     print("Render aborted before start: " + renderWarnings)
        # #     return {"CANCELLED"}

        # if "OTIO" == prefs.renderMode:
        #     bpy.ops.uas_shot_manager.export_otio()
        # else:
        #     renderRootPath = props.renderRootPath if "" != props.renderRootPath else "//"
        #     bpy.path.abspath(renderRootPath)
        #     if not (renderRootPath.endswith("/") or renderRootPath.endswith("\\")):
        #         renderRootPath += "\\"

        #     # if props.isRenderRootPathValid():
        #     launchRender(
        #         context,
        #         prefs.renderMode,
        #         renderRootPath,
        #         # useStampInfo=props.useStampInfoDuringRendering,
        #         area=context.area,
        #     )

        # #   return {"RUNNING_MODAL"}
        return {"FINISHED"}


_classes = (UAS_PT_StampInfo_Render,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
