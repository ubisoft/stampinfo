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

from stampinfo import icons
from stampinfo.config import config
from stampinfo.ui.dependencies_ui import drawDependencies

##################################################################################
# Draw
##################################################################################


def draw_addon_prefs(self, context):
    layout = self.layout
    # layout = layout.column(align=False)
    mainCol = self.layout.column(align=False)

    # Dependencies
    ###############
    drawDependencies(context, mainCol)

    # General
    ###############

    # Dependencies
    ###############
    drawDependencies(context, layout)

    # General
    ###############

    splitFactor = 0.3

    box = mainCol.box()
    row = box.row()
    row.separator(factor=3)
    subCol = row.column()
    subCol.prop(self, "display_main_panel", text="Display Stamp Info panel in the 3D View tabs")
    subCol.prop(self, "write_still")

    drawGeneral(context, self, mainCol)

    # Technical settings
    ###############

    mainCol.separator(factor=0.5)
    mainCol.label(text="Technical Settings:")
    box = mainCol.box()
    box.label(text="Stamped Images Compositing:")
    row = box.row()
    row.separator(factor=3)
    subCol = row.column()
    subCol.prop(self, "delete_temp_scene")
    subCol.prop(self, "delete_temp_images")

    # Dev and debug
    ###############
    box = mainCol.box()
    colSepHeight = 0.5

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

    box.separator(factor=colSepHeight)
    row = box.row()
    iconExplorer = icons.icons_col["General_Explorer_32"]
    row.operator("uas_si_utils.open_addon_folder", text="Open add-on Folder", icon_value=iconExplorer.icon_id)

    if config.devDebug:
        # initialization state
        initRow = box.row()
        initRow.prop(self, "isInitialized")


##################################################################
# Draw functions
##################################################################


def drawGeneral(context, prefs, layout):
    box = layout.box()
    # collapsable_panel(box, prefs, "addonPrefs_ui_expanded", text="UI")
    # if prefs.addonPrefs_ui_expanded:
    uiSplitFactor = 0.15

    # column component here is technicaly not necessary but reduces the space between lines
    col = box.column()

    # split = col.split(factor=uiSplitFactor)
    # rowLeft = split.row()
    # rowLeft.separator()
    # rowRight = split.row()
    row = col.row()
    row.separator(factor=3)
    row.prop(prefs, "checkForNewAvailableVersion", text="Check for Updates")
