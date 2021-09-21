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
This module defines the global preferences of the add-on
"""

import bpy
from bpy.types import AddonPreferences
from bpy.props import BoolProperty

from ..config import config
from ..ui.dependencies_ui import drawDependencies


class UAS_StampInfo_AddonPrefs(AddonPreferences):
    """
        Use this to get these prefs:
        prefs = context.preferences.addons["stampinfo"].preferences
    """

    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package
    bl_idname = "stampinfo"

    install_failed: BoolProperty(
        name="Install failed", default=False,
    )

    mediaFirstFrameIsZero: BoolProperty(
        name="Output Media First Frame is 0",
        description="If checked (most common approach) then the first frame of the output\nmedia has index 0 (last then have index (seq. number of frames - 1).\n"
        "If not checked then it has index 1 and the last frame has the index equal to the media duration",
        default=True,
        options=set(),
    )

    write_still: BoolProperty(
        name="Write rendered still images on disk",
        description="If checked then writes rendered still images on disk.\n"
        "If not checked (most common approach) then the images are written with a name starting with '_Still_' in order to prevent modification on a single frame"
        "in an already rendered image sequences",
        default=False,
        options=set(),
    )

    delete_temp_scene: BoolProperty(
        name="Delete the temporary scene used for VSE rendering",
        description="Delete temporary scene used for VSE rendering",
        default=True,
        options=set(),
    )

    delete_temp_images: BoolProperty(
        name="Delete the temporary images used for VSE rendering",
        description="Delete temporary images used for VSE rendering",
        default=True,
        options=set(),
    )

    def draw(self, context):
        layout = self.layout
        splitFactor = 0.3

        box = layout.box()
        row = box.row()
        row.separator(factor=3)
        subCol = row.column()
        subCol.prop(self, "mediaFirstFrameIsZero")
        subCol.prop(self, "write_still")

        layout.separator(factor=0.5)
        layout.label(text="Technical Settings:")
        box = layout.box()
        box.label(text="Stamped Images Compositing:")
        row = box.row()
        row.separator(factor=3)
        subCol = row.column()
        subCol.prop(self, "delete_temp_scene")
        subCol.prop(self, "delete_temp_images")

        # Dependencies
        ###############
        drawDependencies(context, layout)

        # Dev and debug
        ###############
        box = layout.box()

        split = box.split(factor=splitFactor)
        rowLeft = split.row()
        rowLeft.label(text="Development and Debug:")
        rowRight = split.row()

        if config.devDebug:
            strDebug = " *** Debug Mode is On ***"
            rowRight.alignment = "RIGHT"
            rowRight.alert = True
            rowRight.label(text=strDebug)

        split = box.split(factor=splitFactor)
        rowLeft = split.row()
        rowLeft.alignment = "RIGHT"
        rowLeft.label(text="Debug Mode")
        rowRight = split.row()
        if config.devDebug:
            rowRight.alert = True
            rowRight.operator("uas_stamp_info.enable_debug", text="Turn Off").enable_debug = False
        else:
            rowRight.operator("uas_stamp_info.enable_debug", text="Turn On").enable_debug = True

    # -----------------------------------------------------------
    # UI user preferences - Not exposed
    # -----------------------------------------------------------
    panelExpanded_mode: BoolProperty(
        name="Expand Render Mode Properties", default=True,
    )


_classes = (UAS_StampInfo_AddonPrefs,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)

