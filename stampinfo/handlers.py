# -*- coding: utf-8 -*-

import bpy

from bpy.app.handlers import persistent
from bpy.types import Operator

from . import stamper

from . import infoImage


# global vars
if not "gbWkDebug" in vars() and not "gbWkDebug" in globals():
    gbWkDebug = False

if gbWkDebug:
    if not "gbWkDebug_DontDeleteCompoNodes" in vars() and not "gbWkDebug_DontDeleteCompoNodes" in globals():
        gbWkDebug_DontDeleteCompoNodes = True

    if not "gbWkDebug_DontDeleteTmpFiles" in vars() and not "gbWkDebug_DontDeleteTmpFiles" in globals():
        gbWkDebug_DontDeleteTmpFiles = True

    if not "gbWkDebug_DrawTextLines" in vars() and not "gbWkDebug_DrawTextLines" in globals():
        gbWkDebug_DrawTextLines = True

else:
    if not "gbWkDebug_DontDeleteCompoNodes" in vars() and not "gbWkDebug_DontDeleteCompoNodes" in globals():
        gbWkDebug_DontDeleteCompoNodes = False

    if not "gbWkDebug_DontDeleteTmpFiles" in vars() and not "gbWkDebug_DontDeleteTmpFiles" in globals():
        gbWkDebug_DontDeleteTmpFiles = False

    if not "gbWkDebug_DrawTextLines" in vars() and not "gbWkDebug_DrawTextLines" in globals():
        gbWkDebug_DrawTextLines = False


# class UAS_StampInfoClearHandlers ( Operator ):
#     """Clear StampInfo Handlers"""  #tooltio
#     bl_idname       = "stampinfo.clearhandlers"   # identifiant   PAS DE MAJ  besoin d'un point
#     bl_label        = "Clear StampInfo Handlers"
#     bl_description  = "Set the handlers added by StampInfo"
#     bl_options      = {'INTERNAL'}

#     def execute(self, context):    # est appelé par invoke, code d'execution de l'operateur
#         print("\nUAS_StampInfoClearHandlers\n\n")
#         clearRenderHandlers()

#       #  if 2 != context.scene.UAS_StampInfo_Settings['stampInfoRenderMode']:              # USEEXISTING
#         if 'USECOMPOSITINGNODES' != context.scene.UAS_StampInfo_Settings.stampInfoRenderMode:              # USEEXISTING
#             stamper.clearInfoCompoNodes(context.scene)
#         return {"FINISHED"}


# class UAS_StampInfoCreateHandlers ( Operator ):
#     """Create Handlers"""  #tooltio
#     bl_idname       = "stampinfo.createhandlers"   # identifiant   PAS DE MAJ  besoin d'un point
#     bl_label        = "Create Handlers"
#     bl_description  = "Set the blabla"
#     bl_options      = {'INTERNAL'}

#     def execute(self, context):    # est appelé par invoke, code d'execution de l'operateur
#         print("\nUAS_StampInfoCreateHandlers\n\n")
#         context.scene.UAS_StampInfo_Settings.registerRenderHandlers()
#         return {"FINISHED"}


# --------------------------------------------------------------------------

#                                 Handlers

# --------------------------------------------------------------------------


# Init renderer callback
# Preparation of the files
# @persistent
def uas_stampinfo_renderInitHandler(scene):
    print("\n ** -- ** Handler uas_stampinfo_renderInitHandler ** -- **")
    #   print("     Mode: " + str(scene.UAS_StampInfo_Settings['stampInfoRenderMode']))
    print("     Mode: " + str(scene.UAS_StampInfo_Settings.stampInfoRenderMode))
    print("     scene.UAS_StampInfo_Settings.stampInfoUsed: " + str(scene.UAS_StampInfo_Settings.stampInfoUsed))
    #  renderFrameInd = scene.frame_current
    #  print(" - renderFrameInd: ", renderFrameInd)

    # wkip gros hack degueu to demove!!!
    #  scene.UAS_StampInfo_Settings.registerRenderHandlers()
    #   if 'USECOMPOSITINGNODES' != scene.UAS_StampInfo_Settings.stampInfoRenderMode:              # USEEXISTING
    #       stamper.clearInfoCompoNodes(context.scene)

    rangeStart = stamper.getRenderRange(scene)[0]
    # bpy.context.scene.frame_set(rangeStart)            # !!!! important Set Current Frame

    if scene.UAS_StampInfo_Settings.stampInfoUsed:
        # if 0 == scene.UAS_StampInfo_Settings['stampInfoRenderMode']:              # OVERSIZE
        stamper.createInfoCompoNodes(scene, rangeStart)
    # bpy.context.scene.frame_set(rangeStart)


# Pre renderer callback - for all rendered frames
# Preparation of the files
# @persistent
def uas_stampinfo_renderPreHandler(scene):

    if scene.UAS_StampInfo_Settings.stampInfoUsed:
        renderFrameInd = scene.frame_current
        bpy.context.scene.frame_set(renderFrameInd)  # !!!! important Set Current Frame
        renderFrameInd = scene.frame_current

        print("\n ** -- ** Handler uas_stampinfo_renderPreHandler ** -- **")
        print(
            "    Rendering frame: "
            + str(renderFrameInd)
            + " in range [ "
            + str(scene.frame_start)
            + " / "
            + str(scene.frame_end)
            + " ]"
        )

        infoImage.renderTmpImageWithStampedInfo(scene, renderFrameInd)
        stamper.updateInfoCompoNodes(scene, renderFrameInd)
    #    if not gbWkDebug_DontDeleteTmpFiles:
    #        infoImage.deletePreviousInfoImage(scene, renderFrameInd)


# Post renderer callback
# Cleaning of the files
# @persistent
def uas_stampinfo_renderCompleteHandler(scene):
    print("\n ** -- ** Handler uas_stampinfo_renderCompleteHandler  ** -- **")
    print("   scene.UAS_StampInfo_Settings.stampInfoUsed: " + str(scene.UAS_StampInfo_Settings.stampInfoUsed))
    if scene.UAS_StampInfo_Settings.stampInfoUsed:
        if (
            not gbWkDebug_DontDeleteCompoNodes and 2 != scene.UAS_StampInfo_Settings["stampInfoRenderMode"]
        ):  # USEEXISTING
            stamper.clearInfoCompoNodes(scene)
        if not gbWkDebug_DontDeleteTmpFiles:
            stamper.deletePreviousInfoImage(scene, scene.frame_end + 1)
            #    if 2 != scene.UAS_StampInfo_Settings['stampInfoRenderMode']:              # USEEXISTING
            if "USECOMPOSITINGNODES" != scene.UAS_StampInfo_Settings.stampInfoRenderMode:  # USEEXISTING
                stamper.deleteTempImage(scene)


# Post renderer callback
# Cleaning of the files
# @persistent
def uas_stampinfo_renderCancelHandler(scene):
    print("\n ** -- ** Handler uas_stampinfo_renderCancelHandler ** -- **")
    print("   scene.UAS_StampInfo_Settings.stampInfoUsed: " + str(scene.UAS_StampInfo_Settings.stampInfoUsed))

    if (
        scene.UAS_StampInfo_Settings.stampInfoUsed and 2 != scene.UAS_StampInfo_Settings["stampInfoRenderMode"]
    ):  # USEEXISTING
        if not gbWkDebug_DontDeleteCompoNodes:
            stamper.clearInfoCompoNodes(scene)
        if not gbWkDebug_DontDeleteTmpFiles:
            #       stamper.deletePreviousInfoImage(scene, scene.frame_end)    # commented cause last rendered frame may not be the last of the range
            #   if 2 != scene.UAS_StampInfo_Settings['stampInfoRenderMode']:              # USEEXISTING
            if "USECOMPOSITINGNODES" != scene.UAS_StampInfo_Settings.stampInfoRenderMode:  # USEEXISTING
                stamper.deleteTempImage(scene)


@persistent
def uas_stampinfo_postFileLoadHandler(scene):
    print("\n ** -- ** Handler uas_stampinfo_postFileLoadHandler ** -- **")
    if None != scene:
        scene.UAS_StampInfo_Settings.clearRenderHandlers()
        if scene.UAS_StampInfo_Settings.stampInfoUsed:
            scene.UAS_StampInfo_Settings.registerRenderHandlers()


def registerPostLoadHandler():
    bpy.app.handlers.load_post.append(uas_stampinfo_postFileLoadHandler)
