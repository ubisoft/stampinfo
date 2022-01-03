.. _features:


Setting up the final resolution
===============================

The Final Resolution Mode defines how the metadata will be arranged over the rendered image.

* **Over Rendered images:** 

In this mode the black bands on which metadata text will be written directly on the image. It
will then hide a part of it at the top and bottom. The final image still have the same resolution
than the rendering output image.

..  image:: /img/features/StampInfoModes_Over.jpg
    :align: center


* **Outside Rendered images:**

In this second mode the metadata are written outside the rendering output image, making the final composited
image higher than the resolution specified in the Blender Rendering panel.

..  image:: /img/features/StampInfoModes_Outside.jpg
    :align: center


Both have advantages and inconvenients. We suggest to use the mode "Outside Rendered Images" when in a production context,
it saves rendering time while preserving the same aspect ratio for the cameras in the viewports.

For a more detailed description of these values watch `this part of the video tutorial <https://youtu.be/Sj2GyYhxFX4?t=272>`__.


Information categories
======================

Time and frames
----------------

Information related to the frame index, animation range and framerate...

Animation range
+++++++++++++++

    ..  image:: /img/features/SI_Range__0001_Conventions-02.jpg
        :align: center

    ..  image:: /img/features/SI_Range__0004_Consequences-on-range-03.jpg
        :align: center

    ..  image:: /img/features/SI_Range__0005_Consequences-on-duration.jpg
        :align: center



Handles
+++++++

    ..  image:: /img/features/SI_Hand__0002_Handles-03.jpg
        :align: center

    ..  image:: /img/features/SI_Hand__0005_Handles-Tips-03.jpg
        :align: center

    ..  image:: /img/features/SI_Hand__0007_Handles-Tips-05.jpg
        :align: center




Shot and camera
---------------

Scene, sequence, take and shot names, as well as camera name and lens value.


Metadata
--------

Project name and logo, user name, rendering date and time, custom notes.


Layout categories
=================

Text and layout
---------------

How information is organised on the rendered frame.

