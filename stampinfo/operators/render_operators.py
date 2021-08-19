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

# from ..utils.utils_render import getRenderOutputFilename
from ..utils.utils_filenames import SequencePath
from ..utils.utils_os import delete_folder
from ..utils import utils

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

        # abort rendering if the file is not saved
        # note: removed: using blender temp dir instead
        # if not bpy.data.is_saved:
        #     utils.ShowMessageBox("File not saved - Rendering aborted", "Render aborted", icon="ERROR")
        #     # if None == (getInfoFileFullPath(scene, -1)[0]):
        #     return {"FINISHED"}

        if not bpy.data.is_saved and "ANIMATION" == self.renderMode:
            utils.ShowMessageBox(
                "The file need to be saved in order to render the animation", "Rendering aborted", icon="ERROR"
            )
            return {"FINISHED"}

        if not stampInfoSettings.stampInfoUsed:
            if "STILL" == self.renderMode:
                bpy.ops.render.render("INVOKE_DEFAULT", use_viewport=True)
            elif "ANIMATION" == self.renderMode:
                bpy.ops.render.render("INVOKE_DEFAULT", animation=True, use_viewport=True)
            return {"FINISHED"}

        vse_render = context.window_manager.stampinfo_vse_render
        prefs = context.preferences.addons["stampinfo"].preferences

        previousRenderPath = scene.render.filepath
        renderFrame = scene.frame_current

        # note: if scene.render.filepath is empty the Blender temp folder and a temp filename are used
        render_filepath = stamper.getStampInfoRenderFilepath(scene)

        seqPath = SequencePath(bpy.path.abspath(render_filepath))
        print(f"file path {bpy.path.abspath(render_filepath)}")
        # if config.uasDebug:
        seqPath.print(at_frame=renderFrame)

        if "" == seqPath.sequence_name():
            utils.ShowMessageBox("Invalid sequence name - Rendering aborted", "Rendering aborted", icon="ERROR")
            return {"FINISHED"}

        print(f"seqPath.sequence_name(): {seqPath.sequence_name()}")
        tempFramedRenderPath = seqPath.parent() + "_tmp_StampInfo_framing" + "\\"
        print(f"tempFramedRenderPath: {tempFramedRenderPath}")
        if not Path(tempFramedRenderPath).exists():
            Path(tempFramedRenderPath).mkdir(parents=True, exist_ok=True)

        tempImgRenderPath = seqPath.parent() + "_tmp_StampInfo_render" + "\\"
        print(f"tempImgRenderPath: {tempImgRenderPath}")
        if not Path(tempImgRenderPath).exists():
            Path(tempImgRenderPath).mkdir(parents=True, exist_ok=True)

        tmpFileBasenamePattern = "tmp_StampInfo_"
        outputStillFile = ""

        if "STILL" == self.renderMode:
            print("Render a still image at current frame")
            if not prefs.write_still:
                outputStillFile = "_Still_"

            scene.render.filepath = (
                f"{tempImgRenderPath}{outputStillFile}{seqPath.sequence_name(at_frame=scene.frame_current)}"
            )

            print(f" scene.render.filepath: {scene.render.filepath}")

            displayRenderWindow = False
            #     bpy.ops.render.view_show()
            # bpy.ops.render.render(use_viewport=True)
            if displayRenderWindow:
                bpy.ops.render.render("INVOKE_DEFAULT", animation=False, write_still=True, use_viewport=False)
            else:
                bpy.ops.render.render(animation=False, write_still=True, use_viewport=False)

            tempFramedRenderFilenameStill = (
                outputStillFile
                + seqPath.sequence_basename()
                + tmpFileBasenamePattern
                + seqPath.sequence_indices(at_frame=renderFrame)
                + ".png"
            )
            stampInfoSettings.renderTmpImageWithStampedInfo(
                scene, renderFrame, renderPath=tempFramedRenderPath, renderFilename=tempFramedRenderFilenameStill,
            )

        elif "ANIMATION" == self.renderMode:
            print("Render animation")

            scene.render.filepath = f"{tempImgRenderPath}{seqPath.sequence_name()}"
            print(f" scene.render.filepath: {scene.render.filepath}")

            displayRenderWindow = False
            #     bpy.ops.render.view_show()
            # bpy.ops.render.render(use_viewport=True)
            if displayRenderWindow:
                bpy.ops.render.render("INVOKE_DEFAULT", animation=True, use_viewport=False)
            else:
                bpy.ops.render.render(animation=True, use_viewport=False)

            #    outputFiles = getRenderOutputFilename(scene)

            for currentFrame in range(scene.frame_start, scene.frame_end + 1):
                scene.frame_set(currentFrame)
                # scene.UAS_StampInfo_Settings.renderRootPathUsed = True
                # scene.UAS_StampInfo_Settings.renderRootPath = tempRenderPath

                tempFramedRenderFilename = (
                    seqPath.sequence_basename()
                    + tmpFileBasenamePattern
                    + seqPath.sequence_indices(at_frame=currentFrame)
                    + ".png"
                )

                stampInfoSettings.renderTmpImageWithStampedInfo(
                    scene, currentFrame, renderPath=tempFramedRenderPath, renderFilename=tempFramedRenderFilename
                )

            # lister images temps stamp info
            # lister images temp image

        # for some reason this cannot be set right after the call to the render otherwise it is considered as the effective render path
        scene.render.filepath = previousRenderPath
        scene.frame_current = renderFrame

        # compositer
        # use vse_render to store all the elements to composite
        atSpecificFrame = None
        if "STILL" == self.renderMode:
            atSpecificFrame = renderFrame

        # vse_render.clearMedia()
        # vse_render.inputBGMediaPath = (
        #     tempImgRenderPath + outputStillFile + seqPath.sequence_name(at_frame=atSpecificFrame)
        # )
        # print(f" vse BG: vse_render.inputBGMediaPath: {vse_render.inputBGMediaPath}")
        # vse_render.inputBGResolution = res

        tempFramedRenderFilenameGeneric = (
            outputStillFile
            + seqPath.sequence_basename()
            + tmpFileBasenamePattern
            + seqPath.sequence_indices(at_frame=atSpecificFrame)
            + seqPath.extension()
        )
        infoImgSeq = tempFramedRenderPath + tempFramedRenderFilenameGeneric

        print(f" vse over: infoImgSeq: {infoImgSeq}")

        #        res = [scene.render.resolution_x, scene.render.resolution_y]
        res = stamper.getRenderResolutionForStampInfo(scene)  # wkip float!!

        bgMedia = tempImgRenderPath + outputStillFile + seqPath.sequence_name(at_frame=atSpecificFrame)
        bgRes = stamper.getRenderResolution(scene)
        fgMedia = infoImgSeq
        fgRes = stamper.getRenderResolutionForStampInfo(scene)  # wkip int !!!

        # vse_render.inputOverMediaPath = infoImgSeq
        # vse_render.inputOverResolution = res

        # vse_render.inputAudioMediaPath = audioFilePath

        #        compositedMediaPath = renderPath + "FramedOutput" + "\\"
        compositedMediaFile = f"{seqPath.parent()}{outputStillFile}{seqPath.sequence_name(at_frame=atSpecificFrame)}"
        print(f"compositedMediaFile: {compositedMediaFile}")

        if "STILL" == self.renderMode:
            video_frame_start = renderFrame
            video_frame_end = renderFrame
        else:
            video_frame_start = scene.frame_start
            video_frame_end = scene.frame_end

        if True:
            #            vse_render.compositeVideoInVSE(
            vse_render.compositeMedia(
                scene,
                bg_file=bgMedia,
                bg_res=bgRes,
                fg_file=fgMedia,
                fg_res=fgRes,
                frame_start=video_frame_start,
                frame_end=video_frame_end,
                output_file=compositedMediaFile,
                postfix_scene_name="_StampInfoRender",
                output_resolution=res,
                import_at_frame=video_frame_start,
                clean_temp_scene=prefs.delete_temp_scene,
            )

        if prefs.delete_temp_images:
            print("Cleaning temp dirs")
            delete_folder(tempFramedRenderPath)
            delete_folder(tempImgRenderPath)

        return {"FINISHED"}


_classes = (UAS_PT_StampInfo_Render,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
