- [Features](#features)
- [Limitations](#limitations)

# Features

Stamp Info can display a wide range of custom information on the rendered images. It can be scene properties,
user and rendering details, safe frame and cross hair... Integrated Blender metadata are also supported.

The following displayed properties may not be self-explainatory and worth to be described.

Since Stamp Info was designed to keep tracks of the place of images in a rendered animation several properties
of the add-on are related to frames and time. We will use the term **image sequence** to refer indiferently to
an effective image sequence or a video.

## Logo
Logo path can be relative to the path of the current blender file. It must then start with //


## Video Duration
The **video duration** is the exact number of frames contained in the image sequence.


## Video Frame / Video Range / Handles
These 3 properties refer to the frame index in the image sequence and to its range.

They are displayed at the **top right corner** of the image.

**They are all expressed in the video time system.**

- The **video frame** is the frame index of the considered image.
- The **video range** is the range of frames available in the image sequence. In practice
it is the index of the first frame (which is always 0 by definition) and the index of the __last included frame__
(which is equal to the video duration - 1).
- The **Handles** are defining a set of frames at the begining and at the end of the image sequence that
are used as additional in and out frames at edit time. When the frame index of the image is in the "in" set
it is displayed in green. When it is in the "out" set it is displayed in orange. When inbetween it is displayed
in the color defined for the text.
    
## 3D Edit Frame / 3D Edit Duration / Handles
These 3 properties refer to the frame index in the image sequence and to its range.

They are displayed at the **top right corner** of the image.

**They are all expressed in the video time system.**

- The **video frame** is the frame index of the considered image.
- The **video range** is the range of frames available in the image sequence. In practice
it is the index of the first frame (which is always 0 by definition) and the index of the __last included frame__
(which is equal to the video duration - 1).
- The **Handles** are defining a set of frames at the begining and at the end of the image sequence that
are used as additional in and out frames at edit time. When the frame index of the image is in the "in" set
it is displayed in green. When it is in the "out" set it is displayed in orange. When inbetween it is displayed
in the color defined for the text.

<br />

# Limitations

- The layout for the text and information stamped on the framed image is currenly better fitted for 16:9 ratio.
Other ratios may produce unpredictable results. We have consideration for that issue for the future.