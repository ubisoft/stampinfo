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
All the functions used to write on the output frame images
"""


import logging

_logger = logging.getLogger(__name__)


import os

import bpy
import bpy.utils.previews


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

    return stampRenderRes


# returns the height (integer) in pixels of the image between the 2 borders according to the current mode
def getInnerHeight(scene):
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


def getInfoFileFullPath(scene, renderFrameInd=None):
    """
        returns the path of the info image corresponding to the specified frame
        path of temp info files is the same as the render output files
        renderFrameInd can be None to get only the path
        *** Validity of the path is NOT tested
    """
    #   print("\n getInfoFileFullPath ")
    filepath = ""

    if scene.UAS_StampInfo_Settings.renderRootPathUsed:
        filepath = scene.UAS_StampInfo_Settings.renderRootPath
    else:
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

    # validity is NOT tested
    filePathIsValid = True

    renderPath = None
    renderedInfoFileName = None
    if filePathIsValid:
        renderPath = head + "\\"  # get only path part
        #  renderPath = os.path.dirname(head) + "\\"              # get only path part
        #     renderPath = os.path.dirname(filepath)
        #      filenameNoExt, fileExt = os.path.splitext(getRenderFileName(scene))
        filenameNoExt, fileExt = os.path.splitext(tail)

        if renderFrameInd is None:
            renderedInfoFileName = filenameNoExt
        renderedInfoFileName += r"_tmp_StampInfo." + "{:05d}".format(renderFrameInd) + ".png"

    #       renderedInfoFileName = r"\_tmp_StampInfo." + '{:05d}'.format(renderFrameInd) + ".png"

    #  print("    Temp Info Filepath renderPath: ", renderPath)
    #  print("    Temp Info Filepath renderedInfoFileName: ", renderedInfoFileName)
    return (renderPath, renderedInfoFileName)


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
