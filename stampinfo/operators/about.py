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
from bpy.types import Operator

from ..utils import utils


class UAS_StampInfo_OT_About(Operator):
    bl_idname = "uas_stamp_info.about"
    bl_label = "About UAS Stamp Info..."
    bl_description = "More information about UAS Stamp Info..."
    bl_options = {"INTERNAL"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        props = context.scene.UAS_StampInfo_Settings
        layout = self.layout
        box = layout.box()

        # Version
        ###############
        row = box.row()
        row.separator()
        row.label(
            text="Version:" + props.version()[0] + "   -    (" + "July 2020" + ")" + "   -    Ubisoft Animation Studio"
        )

        # Authors
        ###############
        row = box.row()
        row.separator()
        row.label(text="Written by Julien Blervaque (aka Werwack)")

        # Purpose
        ###############
        row = box.row()
        row.label(text="Purpose:")
        row = box.row()
        row.separator()
        row.label(text="Write scene information on the rendered images.")
        # row = box.row()
        # row.separator()
        # row.label(text="bla bla.")

        # Dependencies
        ###############
        row = box.row()
        row.label(text="Dependencies:")
        row = box.row()
        row.separator()

        row.label(text="- Pillow")
        try:
            import PIL as pillow

            pillowVersion = pillow.__version__
            row.label(text="V." + pillowVersion)
        except Exception as e:
            row.label(text="Module not found")

        # row = box.row()
        # row.separator()
        # row.label(text="- UAS Stamp Info")
        # if props.isStampInfoAvailable():
        #     versionStr = utils.addonVersion("UAS_StampInfo")
        #     row.label(text="V." + versionStr[0])
        # else:
        #     row.label(text="Add-on not found")

        box.separator()

        layout.separator()

    def execute(self, context):
        return {"FINISHED"}


_classes = (UAS_StampInfo_OT_About,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
