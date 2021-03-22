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
from bpy.types import Panel, Operator, Menu

from ..config import config

#############
# Preferences
#############


class UAS_MT_StampInfo_Prefs_MainMenu(Menu):
    bl_idname = "UAS_MT_StampInfo_prefs_mainmenu"
    bl_label = "General Preferences"
    # bl_description = "General Preferences"

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)

        # row.operator("uas_shot_manager.general_prefs", text="Preferences...")
        # row = layout.row(align=True)
        # row.operator("uas_shot_manager.project_settings_prefs", text="Project Settings...")

        # layout.separator()
        # row = layout.row(align=True)

        row.operator("uas_stamp_info.about", text="About...")


_classes = (UAS_MT_StampInfo_Prefs_MainMenu,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
