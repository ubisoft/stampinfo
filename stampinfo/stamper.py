# -*- coding: utf-8 -*-

import os
from pathlib import Path


import bpy
import bpy.utils.previews
from bpy.props import (
    CollectionProperty,
    IntProperty,
    StringProperty,
    EnumProperty,
    BoolProperty,
    PointerProperty,
    FloatProperty,
    FloatVectorProperty,
)

# for file browser:
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator


from .utils import utils_render


# from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageEnhance


def getRenderRange(scene):
    rangeStart, rangeEnd = scene.frame_start, scene.frame_end
    return (rangeStart, rangeEnd)


# returns the rendered image output resolution as float tupple (not int !) and with taking into account the render percentage
def getRenderResolution(scene):
    renderResolution = (
        scene.render.resolution_x * scene.render.resolution_percentage * 0.01,
        scene.render.resolution_y * scene.render.resolution_percentage * 0.01,
    )
    return renderResolution


def getRenderRatio(scene):
    return scene.render.resolution_x / scene.render.resolution_y


# returns the rendered stamp info image output resolution as float tupple (not int !) and with taking into account the render percentage
def getRenderResolutionForStampInfo(scene):
    stampRenderRes = [0.0, 0.0]

    # if   0 == scene.UAS_StampInfo_Settings['stampInfoRenderMode']:               # DIRECTTOCOMPOSITE
    if "DIRECTTOCOMPOSITE" == scene.UAS_StampInfo_Settings.stampInfoRenderMode:  # DIRECTTOCOMPOSITE
        #    stampRenderRes = getRenderResolution(scene)
        stampRenderRes = (getRenderResolution(scene)[0], getRenderResolution(scene)[1])

    elif "SEPARATEOUTPUT" == scene.UAS_StampInfo_Settings.stampInfoRenderMode:  # SEPARATEOUTPUT
        # elif 1 == scene.UAS_StampInfo_Settings['stampInfoRenderMode']:              # SEPARATEOUTPUT
        # stampRenderRes      = ( getRenderResolution(scene)[0] * scene.UAS_StampInfo_Settings.stampRenderResX_percentage * 0.01, \
        #                         getRenderResolution(scene)[1] * scene.UAS_StampInfo_Settings.stampRenderResY_percentage * 0.01 )
        stampRenderRes = (
            getRenderResolution(scene)[0] * scene.UAS_StampInfo_Settings.stampRenderResX_percentage * 0.01,
            max(
                getRenderResolution(scene)[1],
                getRenderResolution(scene)[1] * scene.UAS_StampInfo_Settings.stampRenderResY_percentage * 0.01,
            ),
        )

    else:  # USECOMPOSITINGNODES
        stampRenderRes = getRenderResolution(scene)

    return stampRenderRes


# returns the height (integer) in pixels of the image between the 2 borders according to the current mode
def getInnerHeight(scene):
    stampRenderRes = [0.0, 0.0]
    innerH = -1

    if "DIRECTTOCOMPOSITE" == scene.UAS_StampInfo_Settings.stampInfoRenderMode:  # DIRECTTOCOMPOSITE
        #    stampRenderRes = getRenderResolution(scene)
        innerH = min(
            int(getRenderResolution(scene)[1]),
            int(
                getRenderResolution(scene)[1] * scene.UAS_StampInfo_Settings.stampRenderResYDirToCompo_percentage * 0.01
            ),
        )

    elif "SEPARATEOUTPUT" == scene.UAS_StampInfo_Settings.stampInfoRenderMode:  # SEPARATEOUTPUT
        innerH = min(
            int(getRenderResolution(scene)[1]),
            int(getRenderResolution(scene)[1] * scene.UAS_StampInfo_Settings.stampRenderResY_percentage * 0.01),
        )
        #      int(getRenderResolutionForStampInfo(scene)[1]) )

    else:  # USECOMPOSITINGNODES
        innerH = -1

    return innerH


# wkip traiter cas quand aps de nom de fichier
def getRenderFileName(scene):
    #   print("\n getRenderFileName ")
    # filename is parsed in order to remove the last block in case it doesn't finish with \ or / (otherwise it is
    # the name of the file)
    filename = scene.render.filepath
    lastOccSeparator = filename.rfind("\\")
    if -1 != lastOccSeparator:
        filename = filename[lastOccSeparator + 1 :]

    #   print("    filename: " + filename)
    return filename


# returns the path of the info image corresponding to the specified frame
# path of temp info files is the same as the render output files
# renderFrameInd can be None to get only the path
def getInfoFileFullPath(scene, renderFrameInd):
    #   print("\n getInfoFileFullPath ")

    filepath = scene.render.filepath
    filepath = bpy.path.abspath(filepath)
    #    print("    Temp Info Filepath: ", filepath)

    head, tail = os.path.split(filepath)

    #  filepath = head
    #   print("    Temp Info Filepath head: ", head)
    #   print("    Temp Info Filepath tail: ", tail)

    filePathIsValid = False

    #     # if path is relative then get the full path
    #     if '//' == filepath[0:2]:                        #and bpy.data.is_saved:
    #         # print("Rendering path is relative")
    #         filepath = bpy.path.abspath(filepath)

    #     filepath = bpy.path.abspath(filepath)
    # #    print("    Temp Info Filepath 02: ", filepath)

    # filename is parsed in order to remove the last block in case it doesn't finish with \ or / (otherwise it is
    # the name of the file)
    #     lastOccSeparator = filepath.rfind("\\")
    #     if -1 != lastOccSeparator:
    #         filepath = filepath[0:lastOccSeparator + 1]
    # #        print("    Temp Info Filepath 03: ", filepath)

    if os.path.exists(head):
        #        print("  Rendering path is valid")
        filePathIsValid = True

    renderPath = None
    renderedInfoFileName = None
    if filePathIsValid:
        renderPath = head + "\\"  # get only path part
        #  renderPath = os.path.dirname(head) + "\\"              # get only path part
        #     renderPath = os.path.dirname(filepath)
        #  renderPath = r"Z:\EvalSofts\Blender\DevPython_Data\UAS_StampInfo_Data\Outputs"
        #      filenameNoExt, fileExt = os.path.splitext(getRenderFileName(scene))
        filenameNoExt, fileExt = os.path.splitext(tail)

        if None != renderFrameInd:
            renderedInfoFileName = filenameNoExt
        renderedInfoFileName += r"_tmp_StampInfo." + "{:04d}".format(renderFrameInd) + ".png"

    #       renderedInfoFileName = r"\_tmp_StampInfo." + '{:04d}'.format(renderFrameInd) + ".png"

    #  print("    Temp Info Filepath renderPath: ", renderPath)
    #  print("    Temp Info Filepath renderedInfoFileName: ", renderedInfoFileName)
    return (renderPath, renderedInfoFileName)


def clearInfoCompoNodes(scene):
    print("\n\n**** ****** ******** *********** ********** ********* ********* ******** *******  ****")
    print("\n**** clearInfoCompoNodes ****")
    print("**** ****** ******** *********** ********** ********* ********* ******** *******  ****")

    # if gbWkDebug_DontDeleteCompoNodes: return()
    ### wkip to remove !!! ###
    # clear all nodes
    scene.use_nodes = False
    allCompoNodes = scene.node_tree
    for currentNode in allCompoNodes.nodes:
        allCompoNodes.nodes.remove(currentNode)
    return ()

    # relink
    if None != scene.node_tree:

        # if None == scene.node_tree:
        #     scene.use_nodes = True
        # links = scene.node_tree.links

        links = scene.node_tree.links

        compoNode_OutputToStamp_Img = scene.node_tree.nodes.get("UAS_StampInfo_OutputToStamp_Img")
        if None != compoNode_OutputToStamp_Img:
            print("compoNode_OutputToStamp_Img found ")
            # get composite
            if 0 < len(compoNode_OutputToStamp_Img.inputs[0].links):
                print("from_socket: ", compoNode_OutputToStamp_Img.inputs[0].links[0].from_node)
                print("to socket: ", compoNode_OutputToStamp_Img.outputs[0].links[0].to_node)
                links.new(
                    compoNode_OutputToStamp_Img.inputs[0].links[0].from_socket,
                    compoNode_OutputToStamp_Img.outputs[0].links[0].to_socket,
                )

        allCompoNodes = scene.node_tree
        # print("    allCompoNodes: ", allCompoNodes)
        if None != allCompoNodes:
            namePrefix = "UAS_StampInfo_"
            for currentNode in reversed(allCompoNodes.nodes):
                if namePrefix == currentNode.name[0 : len(namePrefix)]:
                    allCompoNodes.nodes.remove(currentNode)

        scene.use_nodes = False  # scene.UAS_StampInfo_Settings.use_nodes


def getTempBGImageBaseName():
    return r"_tmp_StampInfo_BGImage.png"


def createTempBGImage(scene):
    """ Create the temporaty image used to set the render size (not the one with the stamped info)
    """
    from PIL import Image

    print("\n createTempBGImage ")
    dirAndFilename = getInfoFileFullPath(scene, 0)
    filepath = dirAndFilename[0] + getTempBGImageBaseName()
    print("    filepath tmp image in create: " + filepath)

    renderStampInfoResW = int(getRenderResolutionForStampInfo(scene)[0])
    renderStampInfoResH = int(getRenderResolutionForStampInfo(scene)[1])

    # PIL
    # Black image with transparent alpha
    #   imgTmpInfo             = Image.new('RGBA', (100, 100), (255,0,128,1))
    #   imgTmpInfo             = Image.new('RGBA', (1280, 960), (0,0,0,1))
    imgTmpInfo = Image.new("RGBA", (renderStampInfoResW, renderStampInfoResH), (0, 0, 0, 1))
    imgTmpInfo.save(filepath)

    return filepath


# wkip jamais appelé!!!!
def deleteTempImage(scene):
    print("\n deleteTempImage ")
    dirAndFilename = getInfoFileFullPath(scene, -1)
    filepath = dirAndFilename[0] + r"_StampInfo_TmpImage.png"
    print("    filepath tmp image in delete: " + filepath)

    try:
        os.remove(filepath)
    except OSError:
        print(" *** Cannot delete file " + filepath)
        pass


# return the specified node from the compo graph, None if not found
def getNodeFromGraph(scene, nodeType, namePrefix=""):
    nodeFromGraph = None
    nodeFound = False
    if None != scene.node_tree:
        i = 0
        while None == nodeFromGraph and len(scene.node_tree.nodes) > i and not nodeFound:
            # print(  "  i: ", i)
            if nodeType == scene.node_tree.nodes[i].type:
                if "" == namePrefix or scene.node_tree.nodes[i].name == namePrefix:
                    nodeFromGraph = scene.node_tree.nodes[i]
                    nodeFound = True
            i += 1

    return nodeFromGraph


# called at the very beginning of the render process by the Init handler
# origine of the nodes grid is bottom left
def createInfoCompoNodes(scene, renderFrameInd):
    print("\n\n**** ****** ******** *********** ********** ********* ********* ******** *******  ****")
    print("\n**** createInfoCompoNodes ****")
    print("**** ****** ******** *********** ********** ********* ********* ******** *******  ****")
    # compositing
    # switch on nodes and get reference
    #  scene.UAS_StampInfo_Settings.use_nodes  = scene.use_nodes

    if not utils_render.isRenderPathValid(scene):
        print("!!! Invalid Render Path -- Compo Nodes Creation aborted !!!")
        return ()

    scene.use_nodes = True
    links = scene.node_tree.links
    filepath = createTempBGImage(scene)
    print("    Tmp BG Image Filepath: ", filepath)
    image = bpy.data.images.load(filepath)
    print("    image: ", str(image))

    allCompoNodes = scene.node_tree

    compoNodeComposite = None
    compoNodeInput = None
    compoNodeRLayers = None
    compoNodeMix = None
    compoNodeOutput = None

    compoNode_OutputToStamp_Img = None
    compoNode_OutputToStamp_A = None

    # node used to easily get the output of the graph that was set by the user
    compoNode_OutputToStamp_Img = getNodeFromGraph(scene, "TRANSLATE", "UAS_StampInfo_OutputToStamp_Img")
    # if None != compoNode_OutputToStamp_Img: allCompoNodes.nodes.remove(compoNode_OutputToStamp_Img)
    if None == compoNode_OutputToStamp_Img:
        print("  Create new compoNode_OutputToStamp_Img")
        compoNode_OutputToStamp_Img = scene.node_tree.nodes.new("CompositorNodeTranslate")
        compoNode_OutputToStamp_Img.name = "UAS_StampInfo_OutputToStamp_Img"
        compoNode_OutputToStamp_Img.location = -100, 0

    compoNode_OutputToStamp_A = getNodeFromGraph(scene, "SEPRGBA", "UAS_StampInfo_OutputToStamp_Alpha")
    # if None != compoNode_OutputToStamp_A: allCompoNodes.nodes.remove(compoNode_OutputToStamp_A)
    if None == compoNode_OutputToStamp_A:
        compoNode_OutputToStamp_A = scene.node_tree.nodes.new("CompositorNodeSepRGBA")
        compoNode_OutputToStamp_A.name = "UAS_StampInfo_OutputToStamp_Alpha"
        compoNode_OutputToStamp_A.location = -100, 200

    # detect missing nodes, create them otherwise
    #   if not 2 == scene.UAS_StampInfo_Settings['stampInfoRenderMode']:        # USECOMPOSITINGNODES
    # if not 'USECOMPOSITINGNODES' == scene.UAS_StampInfo_Settings.stampInfoRenderMode:        # USECOMPOSITINGNODES
    #     #clearInfoCompoNodes(scene)
    #     pass
    # else:
    compoNodeComposite = getNodeFromGraph(scene, "COMPOSITE")
    #    compoNodeRLayers    = getNodeFromGraph(scene, 'R_LAYERS')
    #    compoNodeInput      = getNodeFromGraph(scene, 'IMAGE')

    #    compoNodeOutput     = getNodeFromGraph(scene, 'OUTPUT_FILE')

    isCompoNodeCompositeFound = None == compoNodeComposite

    if None == compoNodeComposite:
        print("   composite not found")
    else:
        print("  compoNodeComposite found: " + compoNodeComposite.name)
    #   compoNode_OutputToStamp_Img

    # if None == compoNodeRLayers:
    #     print("   RLayer not found")
    # else:
    #     print("  compoNodeRLayers found: " + compoNodeRLayers.name)

    # an existing composite has not been found and has to be created
    if None == compoNodeComposite:
        compoNodeComposite = scene.node_tree.nodes.new("CompositorNodeComposite")
        compoNodeComposite.name = "UAS_StampInfo_InputInfoComposite"
        compoNodeComposite.location = 400, 200

    print("   wkip crash marker 01")

    compoNodeInput = getNodeFromGraph(scene, "IMAGE", "UAS_StampInfo_InputBGImage")
    if None != compoNodeInput:
        allCompoNodes.nodes.remove(compoNodeInput)
    compoNodeInput = scene.node_tree.nodes.new("CompositorNodeImage")
    compoNodeInput.name = "UAS_StampInfo_InputBGImage"
    compoNodeInput.location = -250, -300
    print("   wkip crash marker 02-1")
    compoNodeInput.image = image
    print("   wkip crash marker 02-2")

    #    compoNodeMix        = getNodeFromGraph('MIX_RGB')
    # compoNodeMix                    = scene.node_tree.nodes.new('CompositorNodeMixRGB')
    # compoNodeMix.name               = "UAS_StampInfo_InputInfoMix"
    # compoNodeMix.location           = 100, 0

    compoNodeMix = getNodeFromGraph(scene, "ALPHAOVER", "UAS_StampInfo_InputInfoMix")
    if None != compoNodeMix:
        allCompoNodes.nodes.remove(compoNodeMix)
    compoNodeMix = scene.node_tree.nodes.new("CompositorNodeAlphaOver")
    compoNodeMix.name = "UAS_StampInfo_InputInfoMix"
    compoNodeMix.location = 100, -150
    compoNodeMix.use_premultiply = True

    print("   wkip crash marker 03")
    # if not 2 == scene.UAS_StampInfo_Settings['stampInfoRenderMode']:         # USECOMPOSITINGNODES

    #    if 0 == scene.UAS_StampInfo_Settings['stampInfoRenderMode']:              # DIRECTTOCOMPOSITE
    if "DIRECTTOCOMPOSITE" == scene.UAS_StampInfo_Settings.stampInfoRenderMode:  # DIRECTTOCOMPOSITE
        print("   before linking - DIRECTTOCOMPOSITE")

        if compoNodeComposite.inputs[0].is_linked:
            print("  compoNodeComposite.inputs[0].is_linked: true")
            # insering the OutputToStamp nodes between the composite node and its input
            if compoNodeComposite.inputs[0].links[0].from_node != compoNodeMix:
                print("  compoNodeComposite.inputs[0].is_linked: true   --- new links")
                try:
                    links.new(compoNodeComposite.inputs[0].links[0].from_socket, compoNode_OutputToStamp_Img.inputs[0])
                    links.new(compoNodeComposite.inputs[0].links[0].from_socket, compoNode_OutputToStamp_A.inputs[0])

                except OSError:
                    print("\n----------- >|< Oops!  Crash marker 04...")
        else:
            print("  compoNodeComposite.inputs[0].is_linked: false")
            compoNodeRLayers = getNodeFromGraph(scene, "R_LAYERS", "UAS_StampInfo_InputInfoRLayers")
            # if None != compoNodeRLayers: allCompoNodes.nodes.remove(compoNodeRLayers)
            try:
                if None == compoNodeRLayers:
                    compoNodeRLayers = scene.node_tree.nodes.new("CompositorNodeRLayers")
                    compoNodeRLayers.name = "UAS_StampInfo_InputInfoRLayers"
                    compoNodeRLayers.location = -500, 200
                    links.new(compoNodeRLayers.outputs["Image"], compoNode_OutputToStamp_Img.inputs[0])
                    links.new(compoNodeRLayers.outputs["Alpha"], compoNode_OutputToStamp_A.inputs[0])
            except OSError:
                print("\n----------- >|< Oops!  Crash marker 04 B ...")

        print("   wkip crash marker 05")

        try:
            links.new(compoNode_OutputToStamp_Img.outputs["Image"], compoNodeMix.inputs[1])
            links.new(compoNodeInput.outputs["Image"], compoNodeMix.inputs[2])
            links.new(compoNodeInput.outputs["Alpha"], compoNodeMix.inputs[0])
            links.new(compoNodeMix.outputs["Image"], compoNodeComposite.inputs[0])
        except OSError:
            print("\n----------- >|< Oops!  Crash marker 05 b ...")

        print("   wkip crash marker 06")

    #   elif 1 == scene.UAS_StampInfo_Settings['stampInfoRenderMode']:            # SEPARATEOUTPUT
    elif "SEPARATEOUTPUT" == scene.UAS_StampInfo_Settings.stampInfoRenderMode:  # SEPARATEOUTPUT
        print("   before linking - SEPARATEOUTPUT")
        compoNodeOutput = getNodeFromGraph(scene, "OUTPUT_FILE", "UAS_StampInfo_OutputInfo")
        print("   wkip crash marker 03-b-1")
        if None != compoNodeOutput:
            allCompoNodes.nodes.remove(compoNodeOutput)
        # create output node
        compoNodeOutput = scene.node_tree.nodes.new("CompositorNodeOutputFile")
        compoNodeOutput.name = "UAS_StampInfo_OutputInfo"
        compoNodeOutput.location = 400, -200
        print("   wkip crash marker 03-b-2")
        compoNodeOutput.base_path = (getInfoFileFullPath(scene, 0))[0]
        print("    getInfoFileFullPath in SEPARATEOUTPUT")
        compoNodeOutput.format.file_format = "PNG"
        compoNodeOutput.format.color_mode = "RGBA"

        print("   wkip crash marker 03-b-3")

        if compoNodeComposite.inputs[0].is_linked:
            print("  compoNodeComposite.inputs[0].is_linked: true")
            # insering the OutputToStamp nodes between the composite node and its input
            if compoNodeComposite.inputs[0].links[0].from_node != compoNode_OutputToStamp_Img:
                print("  compoNodeComposite.inputs[0].is_linked: true   --- new links")
                print(
                    "  compoNodeComposite.inputs[0].links[0].from_node: ",
                    compoNodeComposite.inputs[0].links[0].from_socket.name,
                )
                print("  compoNode_OutputToStamp_Img: ", compoNode_OutputToStamp_Img.name)
                links.new(compoNodeComposite.inputs[0].links[0].from_socket, compoNode_OutputToStamp_Img.inputs[0])
                links.new(compoNodeComposite.inputs[0].links[0].from_socket, compoNode_OutputToStamp_A.inputs[0])
        else:
            print("  compoNodeComposite.inputs[0].is_linked: false")
            compoNodeRLayers = getNodeFromGraph(scene, "R_LAYERS", "UAS_StampInfo_InputInfoRLayers")
            # if None != compoNodeRLayers: allCompoNodes.nodes.remove(compoNodeRLayers)
            if None == compoNodeRLayers:
                print("      one == compoNodeRLayers")
                compoNodeRLayers = scene.node_tree.nodes.new("CompositorNodeRLayers")
                compoNodeRLayers.name = "UAS_StampInfo_InputInfoRLayers"
                compoNodeRLayers.location = -500, 200
                links.new(compoNodeRLayers.outputs["Image"], compoNode_OutputToStamp_Img.inputs[0])
                links.new(compoNodeRLayers.outputs["Alpha"], compoNode_OutputToStamp_A.inputs[0])
                print("     02 one == compoNodeRLayers")

        print("   wkip crash marker 03-b-4")

        #  compoNodeOutput.file_slots[0].path = "StampedInfo"
        # compoNodeOutput.file_slots[0].path = (getInfoFileFullPath(scene, 0))[1]
        tmpFileName = getRenderFileName(scene)
        if "." == tmpFileName[-1]:
            tmpFileName = tmpFileName[0:-2]
        compoNodeOutput.file_slots[0].path = tmpFileName + "_Stamp.####"

        links.new(compoNode_OutputToStamp_Img.outputs["Image"], compoNodeComposite.inputs[0])
        links.new(compoNode_OutputToStamp_Img.outputs["Image"], compoNodeMix.inputs[2])
        links.new(compoNode_OutputToStamp_A.outputs[3], compoNodeMix.inputs[0])  # rendered image alpha is used for mix

        links.new(compoNodeInput.outputs["Image"], compoNodeMix.inputs[1])  # stampinfo image is put in BG
        #    links.new(compoNodeInput.outputs['Alpha'], compoNodeMix.inputs[0])

        links.new(compoNodeMix.outputs["Image"], compoNodeOutput.inputs[0])

    #   links.new(compoNodeRLayers.outputs['Image'], compoNodeComposite.inputs[0])


# called at every rendered frame by the pre render handler
def updateInfoCompoNodes(scene, renderFrameInd):
    """ Set the info image to composite on the CompositorNodeImage node,
        called at every rendered frame by the pre render handler
    """
    print("\n\n**** ****** ******** *********** ********** ********* ********* ******** *******  ****")
    print("\n**** updateInfoCompoNodes ****")
    print("**** ****** ******** *********** ********** ********* ********* ******** *******  ****")

    dirAndFilename = getInfoFileFullPath(scene, renderFrameInd)
    filepath = dirAndFilename[0] + dirAndFilename[1]

    print("      getInfoFileFullPath in updateInfoCompoNodes filepath: " + filepath)
    image = bpy.data.images.load(filepath)

    compoNodeInput = scene.node_tree.nodes["UAS_StampInfo_InputBGImage"]
    #  compoNodeInput.image            = image                # !!!! Doesn't work!!!
    compoNodeInput.image.filepath = image.filepath

    print("     updateInfoCompoNodes  ] ")


# Delete only the info image file rendered in the previous frame
def deletePreviousInfoImage(scene, currentFrame):
    print("\n   deletePreviousInfoImage [ ")
    rangeStart = getRenderRange(scene)[0]

    print("\n    rangeStart: ", rangeStart)
    print("\n    frame to delete: ", (currentFrame - 1))

    if rangeStart <= currentFrame - 1:
        dirAndFilename = getInfoFileFullPath(scene, currentFrame - 1)
        filepath = dirAndFilename[0] + dirAndFilename[1]

        print("   getInfoFileFullPath in deletePreviousInfoImage filepath: " + filepath)
        try:
            os.remove(filepath)
        except OSError:
            print(" *** Cannot delete file " + filepath)
            pass

    print("\n   deletePreviousInfoImage ] ")
