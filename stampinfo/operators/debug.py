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
This module is used for debug
"""


import bpy
from bpy.types import Operator, Panel

from ..utils import utils_render

from .. import stamper

import logging

_logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------#
#                                Debug Panel                             #
# ------------------------------------------------------------------------#


class UAS_PT_StampInfoDebug(Panel):
    bl_idname = "UAS_PT_StampInfoDebug"
    bl_label = "Debug"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Stamp Info"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        row = layout.row()
        row.prop(scene.UAS_StampInfo_Settings, "debugMode")

        row = layout.row()
        row.prop(scene.UAS_StampInfo_Settings, "debug_DrawTextLines")
        #    row.prop(scene.UAS_StampInfo_Settings, "offsetToCenterHNorm")

        if not utils_render.isRenderPathValid(context.scene):
            row = layout.row()
            row.alert = True
            row.label(text="Invalid render path")


_classes = (UAS_PT_StampInfoDebug,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
