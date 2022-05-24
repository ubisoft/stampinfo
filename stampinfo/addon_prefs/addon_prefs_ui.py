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
UI for the Add-on Preferences
"""

from stampinfo.config import config
from stampinfo.ui.dependencies_ui import drawDependencies

##################################################################################
# Draw
##################################################################################


def draw_addon_prefs(self, context):
    layout = self.layout
    # layout = layout.column(align=False)

    splitFactor = 0.3

    box = layout.box()
    row = box.row()
    row.separator(factor=3)
    subCol = row.column()
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
