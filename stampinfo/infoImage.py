import os
import ntpath

import bpy

from datetime import datetime
from .stamper import (
    getRenderResolution,
    getRenderResolutionForStampInfo,
    getRenderRange,
    getInnerHeight,
    getInfoFileFullPath,
)

# Called by the Pre renderer callback
# Preparation of the files
def renderTmpImageWithStampedInfo(scene, currentFrame):
    """  Called by the Pre renderer callback
        Preparation of the files
    """
    # Notes
    #   - Image origine is at TOP LEFT corner
    #   - Everything is proportionnal to the HEIGHT of the output image
    #
    # Metadata from Blender:
    #   top:    file, date, render time, host, note, memory         frame range
    #   bottom: marker, timecode, frame, camera, lens               sequencer strip, strip metadata

    from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageEnhance

    print("\n       renderTmpImageWithStampedInfo ")

    userSettings = scene.UAS_StampInfo_Settings
    paddingLeftMetadataTopNorm = 0.0
    paddingLeftMetadataBottomNorm = 0.0

    # stamp_background
    # stamp_font_size
    # stamp_foreground
    # stamp_note_text
    # use_stamp
    # use_stamp_camera
    # use_stamp_date
    # use_stamp_filename
    # use_stamp_frame
    # use_stamp_frame_range
    # use_stamp_hostname
    # use_stamp_labels
    # use_stamp_lens
    # use_stamp_marker
    # use_stamp_memory
    # use_stamp_note
    # use_stamp_render_time
    # use_stamp_scene
    # use_stamp_sequencer_strip
    # use_stamp_strip_meta
    # use_stamp_time
    # support of metadata from Blender
    if scene.render.use_stamp:
        if (
            scene.render.use_stamp_filename
            or scene.render.use_stamp_date
            or scene.render.use_stamp_render_time
            or scene.render.use_stamp_hostname
            or scene.render.use_stamp_note
            or scene.render.use_stamp_frame_range
            or scene.render.use_stamp_memory
        ):
            paddingLeftMetadataTopNorm = 0.2

        if (
            scene.render.use_stamp_marker
            or scene.render.use_stamp_time
            or scene.render.use_stamp_frame
            or scene.render.use_stamp_camera
            or scene.render.use_stamp_lens
            or scene.render.use_stamp_sequencer_strip
            or scene.render.use_strip_meta
        ):
            paddingLeftMetadataBottomNorm = 0.2

    # variables
    # renderW             = int(getRenderResolution(scene)[0])
    # renderH             = int(getRenderResolution(scene)[1])
    renderW = int(getRenderResolutionForStampInfo(scene)[0])
    renderH = int(getRenderResolutionForStampInfo(scene)[1])
    #  print("   renderW: " + str(renderW) + ", renderH: " + str(renderH))

    innerH = getInnerHeight(scene)

    borderTopH = max(
        int((renderH - innerH) * 0.5), 0
    )  # border cannot be negative, which happens if render ratio < inner ratio
    borderBottomH = borderTopH

    # ---------- framing control settings ----------------
    paddingTopExtNorm = (
        userSettings.extPaddingNorm
    )  # 0.03      # padding near the exterior of the image on the border rectangle
    paddingTopIntNorm = 0.04  # not used here # padding near the interior of the image on the border rectangle
    paddingLeftNorm = 0.03
    textLineNorm = userSettings.fontScaleHNorm
    textInterlineNorm = userSettings.interlineHNorm  # 0.01
    numLinesTop = 3
    numLinesBottom = numLinesTop

    if userSettings.automaticTextSize:
        borderTopNorm = min(0.5, borderTopH / renderH)
        paddingTopExtNormInBorder = userSettings.extPaddingNorm * 10.0  # 0.2
        paddingTopIntNormInBorder = 0.1
        paddingTopExtNorm = paddingTopExtNormInBorder * borderTopNorm
        paddingTopIntNorm = paddingTopIntNormInBorder * borderTopNorm

        textInterlineNormInBorder = userSettings.interlineHNorm  # 0.04
        textInterlineNorm = textInterlineNormInBorder * borderTopNorm

        textBorderNorm = borderTopNorm - paddingTopExtNorm - paddingTopIntNorm
        if textBorderNorm <= (numLinesTop - 1) * textInterlineNorm:
            textBorderNorm = 0.0
            textLineNorm = 0.0
        else:
            textLineNorm = min(textLineNorm, (textBorderNorm - (numLinesTop - 1) * textInterlineNorm) / 3.0)

    # ---------- framing control settings ----------------

    # All dimensions are normalized as if the image had the size 1.0 * 1.0
    # fontScaleHNorm      = userSettings.fontScaleHNorm        #0.03
    # fontsize            = int(fontScaleHNorm * renderH)
    # font                = ImageFont.truetype("arial", fontsize)
    # textLineH           = (font.getsize("Aj"))[1]            # line height

    textLineH = int(renderH * textLineNorm)
    textInterlineH = int(renderH * textInterlineNorm)

    fontsize = int(1.0 * textLineNorm * renderH)
    font = ImageFont.truetype("arial", fontsize)
    fontLarge = ImageFont.truetype("arial", fontsize * 2)

    paddingLeft = int((paddingLeftNorm) * renderW)
    paddingLeftMetadataTop = int((paddingLeftMetadataTopNorm) * renderW)
    paddingLeftMetadataBottom = int((paddingLeftMetadataBottomNorm) * renderW)
    # paddingLeft         = int((paddingLeftNorm + paddingLeftMetadataTopNorm) * renderW)
    paddingRight = paddingLeft

    paddingTopExt = int(paddingTopExtNorm * renderH)
    paddingBottomExt = paddingTopExt
    paddingTopInt = int(paddingTopIntNorm * renderH)
    paddingBottomInt = paddingTopInt

    borderColorRGB = userSettings.borderColor  # (0, 0, 0, 255)
    borderColorRGBA = (
        int(borderColorRGB[0] * 255),
        int(borderColorRGB[1] * 255),
        int(borderColorRGB[2] * 255),
        int(borderColorRGB[3] * 255),
    )

    #   borderColorOpacity  = userSettings.borderColorOpacity                  #(0, 0, 0, 255)
    #   borderColorRGBA = (int(borderColorRGB[0] * borderColorOpacity * 255), int(borderColorRGB[1] * borderColorOpacity * 255), int(borderColorRGB[2] * borderColorOpacity * 255), int(borderColorOpacity * 255) )
    #   borderColorRGBA = (int(borderColorRGB[0] * 255), int(borderColorRGB[1] * 255), int(borderColorRGB[2] * 255), int(borderColorOpacity * 255) )
    # print("borderColor: " + str(borderColor[0]))
    #  borderColor         = (0, 0, 0, 255)

    # innerAspectRatio    = userSettings.innerImageRatio              #16/9   # must be >= 1
    # if 1.0 >= innerAspectRatio:
    #     innerAspectRatio = 1.0
    # innerH              = renderW * 1.0 / innerAspectRatio
    textColorRGB = userSettings.textColor  # (0, 0, 0, 255)
    #   textColorOpacity  = userSettings.textColorOpacity                  #(0, 0, 0, 255)
    #  textColorRGBA = (int(textColorRGB[0] * textColorOpacity * 255), int(textColorRGB[1] * textColorOpacity * 255), int(textColorRGB[2] * textColorOpacity * 255), int(textColorOpacity * 255) )
    textColorRGBA = (
        int(textColorRGB[0] * 255),
        int(textColorRGB[1] * 255),
        int(textColorRGB[2] * 255),
        int(textColorRGB[3] * 255),
    )

    # move the content (border + text) toward center
    offsetToCenterH = int(userSettings.offsetToCenterHNorm * renderH)

    imgInfo = Image.new("RGBA", (renderW, renderH), (0, 0, 0, 0))

    # -------------------------------- #
    # stamp borders with PIL
    # -------------------------------- #
    if userSettings.borderUsed:
        imgBorderRect = Image.new("RGBA", (renderW, borderTopH), borderColorRGBA)
        imgInfo.paste(imgBorderRect, (0, offsetToCenterH))
        imgBorderRect = Image.new("RGBA", (renderW, borderBottomH), borderColorRGBA)
        imgInfo.paste(imgBorderRect, (0, renderH - borderBottomH - offsetToCenterH))

    # -------------------------------- #
    # Debug - Draw text lines
    # -------------------------------- #
    if userSettings.debug_DrawTextLines:
        currentTextLeft = paddingLeft + paddingLeftMetadataTop
        currentTextTop = offsetToCenterH + paddingTopExt

        for borderInd in range(0, 2):
            if 0 == borderInd:  # top
                numLines = numLinesTop
                currentTextLeft = paddingLeft + paddingLeftMetadataTop
                currentTextTop = offsetToCenterH + paddingTopExt
            else:  # bottom
                numLines = numLinesBottom
                currentTextLeft = paddingLeft + paddingLeftMetadataTop
                currentTextTop = (
                    renderH
                    - paddingBottomExt
                    - numLines * textLineH
                    - (numLines - 1) * textInterlineH
                    - offsetToCenterH
                )

            for lineInd in range(0, numLines):
                # first line top
                myCol = (255, 20, 0, 200)
                imgBorderRect = Image.new("RGBA", (80, textLineH), myCol)
                imgInfo.paste(imgBorderRect, (currentTextLeft + lineInd * 20, currentTextTop))

                currentTextTop += textLineH

                if lineInd < numLines - 1:
                    # first line spacer top
                    myCol = (20, 250, 0, 100)
                    imgBorderRect = Image.new("RGBA", (1200, textInterlineH), myCol)
                    imgInfo.paste(imgBorderRect, (currentTextLeft + lineInd * 20, currentTextTop))

                    currentTextTop += textInterlineH

    # -------------------------------- #
    # stamp logo
    # if the logo is not found a red fake logo is stamped instead
    # -------------------------------- #
    logoFile = userSettings.logoFilepath
    #  print("  Logo: userSettings.logoFilepath: " + userSettings.logoFilepath)

    filename, extension = os.path.splitext(logoFile)
    # print('Selected file:', self.filepath)
    # print('File name:', filename)
    # print('File extension:', extension)

    logoFilePathIsValid = False

    # if path is relative then get the full path
    if "//" == logoFile[0:2] and bpy.data.is_saved:
        # print("Logo path is relative")
        logoFile = bpy.path.abspath(logoFile)

    if os.path.exists(logoFile):
        print("  Logo path is valid")
        logoFilePathIsValid = True
    else:
        if userSettings.logoUsed:
            print("  Logo path is NOT valid")
            # wkip mettre alert rouge

    if userSettings.logoUsed:
        # logoScaleW = 0.09                                         # logo size is in % of width relatively to the outpur render size. In other words: 1.0 => logo width = renderW
        # logoScaleH = 0.08                                         # logo size is in % of height relatively to the outpur render size. In other words: 1.0 => logo height = renderH
        logoScaleH = userSettings.logoScaleH
        logoPositionNorm = [
            renderW * userSettings.logoPosNormX,
            renderH * userSettings.logoPosNormY,
        ]  # normalized in range [0,1]

        imgLogoSource = None
        if logoFilePathIsValid:
            imgLogoSource = Image.open(logoFile).convert("RGBA")
            if imgLogoSource is None:
                print("******* Cannot open sepcified logo !!! *********")
                logoFilePathIsValid = False

        if not logoFilePathIsValid:
            imgLogoSource = Image.new("RGBA", (150, 150), "red")

        #   logoScaleH = logoScaleW * imgLogoSource.size[1] * 1.0 / imgLogoSource.size[0]
        #   newLogoSize = (int(logoScaleW * renderW), int(logoScaleH * renderW)                                         # preserve logo size on widht
        logoScaleW = logoScaleH * imgLogoSource.size[0] * 1.0 / imgLogoSource.size[1]
        newLogoSize = (int(logoScaleW * renderH), int(logoScaleH * renderH))  # preserve logo size on height

        #  newLogoSize = (int(logoScale * imgLogoSource.size[0]), int(logoScale * imgLogoSource.size[1]))             # to get a precise logo size when output res in pixels is known
        imgLogoSource = imgLogoSource.resize(newLogoSize, Image.ANTIALIAS)  # size in pixels # resamplming mode

        # put logo on image in position (0, 0)
        imgInfo.paste(
            imgLogoSource, (int(logoPositionNorm[0]), int(logoPositionNorm[1])), mask=imgLogoSource
        )  # left align
    # imgInfo.paste(imgLogoSource, (renderW - newLogoSize[0] - paddingRight, paddingRight), mask = imgLogoSource)      # right align

    # put text on image
    img_draw = ImageDraw.Draw(imgInfo)

    stampLabel = userSettings.stampPropertyLabel
    stampValue = userSettings.stampPropertyValue
    textProp = ""

    # ---------------------------------
    # top border
    # ---------------------------------

    col01 = paddingLeft
    col01 = col01 + paddingLeftMetadataTop
    col02 = 0.1 * renderW
    col03 = 0.75 * renderW
    col04 = 0.8 * renderW

    currentTextTop = offsetToCenterH + paddingTopExt

    # ---------- project -------------
    if userSettings.projectUsed:
        textProp = "Project: " if stampLabel and not stampValue else ""
        textProp += userSettings.projectName if stampValue else ""
        img_draw.text((col02, currentTextTop), textProp, font=fontLarge, fill=textColorRGBA)

    # ---------- date -------------

    # wkip use pytz to get the right time zone
    currentTextTop += 2 * (textLineH + textInterlineH)

    now = datetime.now()
    timeStr = now.strftime("%H:%M:%S")
    if userSettings.dateUsed:
        textProp = "Date: " if stampLabel else ""
        textProp += now.strftime("%b-%d-%Y") if stampValue else ""  # Month abbreviation, day and year
        if userSettings.timeUsed:
            textProp += "  " + timeStr if stampValue else ""
    elif userSettings.timeUsed:
        textProp = "Time: " if stampLabel else ""
        textProp += "  " + timeStr if stampValue else ""

    if userSettings.dateUsed or userSettings.timeUsed:
        img_draw.text((col02, currentTextTop), textProp, font=font, fill=textColorRGBA)

    # ---------- image sequence indices -------------
    currentTextTop += textLineH + textInterlineH

    # if userSettings.videoFrameUsed:
    textProp = "Video: " if stampLabel else ""
    currentTextTopFor3DFrames = offsetToCenterH + paddingTopExt + textLineH + textInterlineH
    currentTextLeftFor3DFrames = renderW * (1.0 - 0.05)
    currentImage = scene.frame_current - scene.frame_start + 1
    totalImages = scene.frame_end - scene.frame_start + 1
    # we consider video frames starts at 1, not 0!
    drawRangesAndFrame(
        scene,
        img_draw,
        "VIDEOFRAME",
        currentImage,
        1,
        totalImages,
        userSettings.shotHandles,
        userSettings.videoFrameUsed,
        userSettings.videoRangeUsed,
        userSettings.videoHandlesUsed,
        currentTextLeftFor3DFrames,
        currentTextTopFor3DFrames,
        font,
        fontLarge,
        textColorRGBA,
    )

    currentTextTop = currentTextTopFor3DFrames + textLineH + textInterlineH

    if userSettings.framerateUsed:
        textProp = "Framerate: " if stampLabel else ""
        textProp += str(scene.render.fps) + " fps" if stampValue else ""
        img_draw.text(
            (currentTextLeftFor3DFrames - (font.getsize(textProp))[0], currentTextTop),
            textProp,
            font=font,
            fill=textColorRGBA,
        )

    if userSettings.edit3DFrameUsed:
        textProp = "Index in 3D Edit: " if stampLabel else ""
        #  textProp += '{:03d}'.format(scene.render.fps) + " fps" if stampValue else ""
        currentImage = userSettings.edit3DFrame
        totalImages = userSettings.edit3DTotalNumber
        textProp += str(currentImage) if stampValue else ""
        if userSettings.edit3DTotalNumberUsed:
            textProp += " / " + str(totalImages) if stampValue else ""
        img_draw.text((col03, currentTextTop), textProp, font=font, fill=textColorRGBA)

    # currentTextTop += textLineH + textInterlineH

    # ---------- notes -------------
    currentTextTop = offsetToCenterH + paddingTopExt
    colNotesLabel = 0.25 * renderW
    colNotes = 0.29 * renderW
    if userSettings.notesUsed:
        textProp = "Notes: " if stampLabel else ""
        img_draw.text((colNotesLabel, currentTextTop), textProp, font=font, fill=textColorRGBA)

        textProp = userSettings.notesLine01 if stampValue else ("Notes Line 1" if stampLabel else "")
        img_draw.text((colNotes, currentTextTop), textProp, font=font, fill=textColorRGBA)

        currentTextTop += textLineH + textInterlineH
        textProp = userSettings.notesLine02 if stampValue else ("Notes Line 2" if stampLabel else "")
        img_draw.text((colNotes, currentTextTop), textProp, font=font, fill=textColorRGBA)

        currentTextTop += textLineH + textInterlineH
        textProp = userSettings.notesLine03 if stampValue else ("Notes Line 3" if stampLabel else "")
        img_draw.text((colNotes, currentTextTop), textProp, font=font, fill=textColorRGBA)

    # ---------------------------------
    # bottom border
    # ---------------------------------

    col01 = paddingLeft
    col02 = 0.19 * renderW
    col03 = 0.34 * renderW
    col04 = 0.5 * renderW
    col05 = 0.7 * renderW
    currentTextTop = (
        renderH
        - paddingBottomExt
        - numLinesBottom * textLineH
        - (numLinesBottom - 1) * textInterlineH
        - offsetToCenterH
    )
    currentTextTopFor3DFrames = currentTextTop
    col01 = col01 + paddingLeftMetadataBottom

    # ---------- scene take shot cam -------------
    stampLabel3D = stampLabel or stampValue
    if userSettings.sceneUsed:
        textProp = "Scene: " if stampLabel3D else ""
        textProp += str(scene.name) if stampValue else ""
        img_draw.text((col01, currentTextTop), textProp, font=font, fill=textColorRGBA)

    if userSettings.takeUsed:
        textProp = "Take: " if stampLabel3D else ""
        textProp += userSettings.takeName if stampValue else ""
        img_draw.text((col02, currentTextTop), textProp, font=font, fill=textColorRGBA)

    if userSettings.shotUsed:
        textProp = "Shot: " if stampLabel3D else ""
        textProp += userSettings.shotName if stampValue else ""
        img_draw.text((col03, currentTextTop), textProp, font=font, fill=textColorRGBA)

    # ---------- camera -------------

    if userSettings.cameraLensUsed and not userSettings.cameraUsed:
        textProp = "Lens: " if stampLabel else ""
        # textProp += f"{(scene.camera.data.lens):05.0f}" + " mm" if stampValue else ""       # :05.2f}
        textProp += (str(int(scene.camera.data.lens))).rjust(3, " ") + " mm" if stampValue else ""  # :05.2f}
        img_draw.text((col04, currentTextTop), textProp, font=font, fill=textColorRGBA)
    else:
        if userSettings.cameraUsed:
            textProp = "Cam: " if stampLabel3D else ""
            textProp += str(scene.camera.name) if stampValue else ""
            if userSettings.cameraLensUsed:
                textProp += "   " + (str(int(scene.camera.data.lens))).rjust(3, " ") + " mm" if stampValue else ""
            img_draw.text((col04, currentTextTop), textProp, font=font, fill=textColorRGBA)

    # ---------- 3d frames and range -------------

    currentTextTopFor3DFrames += textLineH + textInterlineH
    currentTextLeftFor3DFrames = renderW * (1.0 - 0.05)
    drawRangesAndFrame(
        scene,
        img_draw,
        "3DFRAME",
        currentFrame,
        scene.frame_start,
        scene.frame_end,
        userSettings.shotHandles,
        userSettings.currentFrameUsed,
        userSettings.frameRangeUsed,
        userSettings.frameHandlesUsed,
        currentTextLeftFor3DFrames,
        currentTextTopFor3DFrames,
        font,
        fontLarge,
        textColorRGBA,
    )

    # ---------- file -------------
    currentTextTop += 2 * (textLineH + textInterlineH)

    if userSettings.filenameUsed or userSettings.filepathUsed:
        textProp = "Blender file: " if stampLabel else ""
        if stampValue:
            if "" == bpy.data.filepath:
                textProp += "*** File not saved ***"
            else:
                head, tail = ntpath.split(bpy.data.filepath)
                if userSettings.filepathUsed:
                    textProp += os.path.abspath(head) + "\\"
                if userSettings.filenameUsed:
                    textProp += tail
                # textProp  += str(os.path.basename(bpy.data.filepath))
        img_draw.text((col01, currentTextTop), textProp, font=font, fill=textColorRGBA)

    dirAndFilename = getInfoFileFullPath(scene, currentFrame)
    filepath = dirAndFilename[0] + dirAndFilename[1]
    print("  01 filepath: dirAndFilename[0]: ", dirAndFilename[0])
    print("  02 filepath: dirAndFilename[1]: ", dirAndFilename[1])

    # filepath = r"Z:\EvalSofts\Blender\DevPython_Data\UAS_StampInfo_Data\Outputs"
    print("Info file rendered name: ", (filepath))
    imgInfo.save(filepath)


def drawRangesAndFrame(
    scene,
    img_draw,
    framemode,
    currentFrame,
    startRange,
    endRange,
    handle,
    frameUsed,
    rangeUsed,
    handlesUsed,
    textRight,
    textTop,
    font,
    fontLarge,
    color,
):
    """
        framemode can be '3DFRAME' or 'VIDEOFRAME'
    """
    userSettings = scene.UAS_StampInfo_Settings

    display3DFrame = "3DFRAME" == framemode
    #    currentTextTopFor3DFrames += textLineH + textInterlineH
    #    currentTextLeftFor3DFrames = renderW * (1.0 - 0.05)

    currentTextTopFor3DFrames = textTop
    currentTextLeftFor3DFrames = textRight
    textColorRGBA = color
    textColorGray = (128, 128, 128, 255)
    textColorWhite = (200, 200, 200, 255)
    textColorRed = (200, 200, 200, 255)

    stampLabel = userSettings.stampPropertyLabel
    stampValue = userSettings.stampPropertyValue
    textProp = ""

    # fontsize            = int(fontScaleHNorm * renderH)
    # font                = ImageFont.truetype("arial", fontsize)
    # textLineH           = (font.getsize("Aj"))[1]            # line height

    ### text is aligned on the right !!! ###

    if stampValue:
        if rangeUsed or handlesUsed:
            textProp = " ]"
            currentTextLeftFor3DFrames -= (font.getsize(textProp))[0]
            img_draw.text(
                (currentTextLeftFor3DFrames, currentTextTopFor3DFrames), textProp, font=font, fill=textColorRGBA
            )

        if rangeUsed:
            textProp = "{:03d}".format(endRange)
            currentTextLeftFor3DFrames -= (font.getsize(textProp))[0]
            img_draw.text(
                (currentTextLeftFor3DFrames, currentTextTopFor3DFrames), textProp, font=font, fill=textColorGray
            )

        if rangeUsed and handlesUsed:
            textProp = " / "
            currentTextLeftFor3DFrames -= (font.getsize(textProp))[0]
            img_draw.text(
                (currentTextLeftFor3DFrames, currentTextTopFor3DFrames), textProp, font=font, fill=textColorRGBA
            )

        if handlesUsed:
            textProp = "{:03d}".format(endRange - handle)
            currentTextLeftFor3DFrames -= (font.getsize(textProp))[0]
            img_draw.text(
                (currentTextLeftFor3DFrames, currentTextTopFor3DFrames), textProp, font=font, fill=textColorWhite
            )

        if rangeUsed or handlesUsed:
            textProp = " / "
            currentTextLeftFor3DFrames -= (font.getsize(textProp))[0]
            img_draw.text(
                (currentTextLeftFor3DFrames, currentTextTopFor3DFrames), textProp, font=font, fill=textColorRGBA
            )

        if frameUsed:
            textProp = "{:03d}".format(currentFrame)
            currentTextLeftFor3DFrames -= (fontLarge.getsize(textProp))[0]
            currentTextHeight = (font.getsize(textProp))[1]
            newTextHeight = (fontLarge.getsize(textProp))[1] - (font.getsize(textProp))[1]
            img_draw.text(
                (currentTextLeftFor3DFrames, currentTextTopFor3DFrames - newTextHeight),
                textProp,
                font=fontLarge,
                fill=textColorRGBA,
            )

        if (rangeUsed or handlesUsed) and frameUsed:
            textProp = " /  "
            currentTextLeftFor3DFrames -= (font.getsize(textProp))[0]
            img_draw.text(
                (currentTextLeftFor3DFrames, currentTextTopFor3DFrames), textProp, font=font, fill=textColorRGBA
            )

        if handlesUsed:
            textProp = "{:03d}".format(startRange + handle)
            currentTextLeftFor3DFrames -= (font.getsize(textProp))[0]
            img_draw.text(
                (currentTextLeftFor3DFrames, currentTextTopFor3DFrames), textProp, font=font, fill=textColorWhite
            )

        if rangeUsed and handlesUsed:
            textProp = " / "
            currentTextLeftFor3DFrames -= (font.getsize(textProp))[0]
            img_draw.text(
                (currentTextLeftFor3DFrames, currentTextTopFor3DFrames), textProp, font=font, fill=textColorRGBA
            )

        if rangeUsed:
            textProp = "{:03d}".format(startRange)
            currentTextLeftFor3DFrames -= (font.getsize(textProp))[0]
            img_draw.text(
                (currentTextLeftFor3DFrames, currentTextTopFor3DFrames), textProp, font=font, fill=textColorGray
            )

        if rangeUsed or handlesUsed:
            textProp = "[ "
            currentTextLeftFor3DFrames -= (font.getsize(textProp))[0]
            img_draw.text(
                (currentTextLeftFor3DFrames, currentTextTopFor3DFrames), textProp, font=font, fill=textColorRGBA
            )

    if frameUsed and stampLabel:
        textProp = "Range / " if rangeUsed else ""
        textProp += "Handles / " if handlesUsed else ""
        textProp += "3D Frame: " if frameUsed else ""
        currentTextLeftFor3DFrames -= (font.getsize(textProp))[0]
        img_draw.text((currentTextLeftFor3DFrames, currentTextTopFor3DFrames), textProp, font=font, fill=textColorRGBA)

        # if userSettings.frameHandlesUsed:
        #     textProp += " / " + '{:03d}'.format(scene.frame_end - userSettings.shotHandles) + " / " if stampValue else ""
        # if userSettings.frameRangeUsed:
        #     textProp += '{:03d}'.format(scene.frame_end) + "]" if stampValue else ""
        # img_draw.text((currentTextLeftFor3DFrames, currentTextTop ), textProp, font=font, fill=textColorRGBA )

    # if userSettings.frameRangeUsed:
    #     textProp = "Range: " if stampLabel else ""
    #     textProp += "[" + str(scene.frame_start) + " / " + str(scene.frame_end) + "]" if stampValue else ""
    #     img_draw.text((col03, currentTextTop), textProp, font=font, fill=textColorRGBA )
