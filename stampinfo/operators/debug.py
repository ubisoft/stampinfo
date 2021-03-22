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

import logging

_logger = logging.getLogger(__name__)

import bpy
from bpy.types import Operator, Panel

from ..utils import utils_render

from .. import stamper

# ------------------------------------------------------------------------#
#                                Debug Panel                             #
# ------------------------------------------------------------------------#


class UAS_PT_StampInfoDebug(Panel):
    bl_idname = "UAS_PT_StampInfoDebug"
    bl_label = "Debug"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "UAS StampInfo"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        row = layout.row()
        row.prop(scene.UAS_StampInfo_Settings, "debugMode")

        row = layout.row()
        row.prop(scene.UAS_StampInfo_Settings, "debug_DrawTextLines")
        #    row.prop(scene.UAS_StampInfo_Settings, "offsetToCenterHNorm")

        row = layout.row()
        row.operator("stampinfo.resethandlersandcomponodes", emboss=True)

        row = layout.row()
        row.operator("debug.lauchrrsrender", emboss=True)

        if not utils_render.isRenderPathValid(context.scene):
            row = layout.row()
            row.alert = True
            row.label(text="Invalid render path")

        row = layout.row()
        row.operator("debug.createcomponodes", emboss=True)
        row.operator("debug.clearcomponodes", emboss=True)


class UAS_PT_StampInfoDebugCompo(Panel):
    bl_idname = "UAS_PT_StampInfoDebugCompo"
    bl_label = "Debug"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "UAS StampInfo"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        row = layout.row()
        row.prop(scene.UAS_StampInfo_Settings, "debugMode")

        row = layout.row()
        row.prop(scene.UAS_StampInfo_Settings, "debug_DrawTextLines")
        #    row.prop(scene.UAS_StampInfo_Settings, "offsetToCenterHNorm")

        row = layout.row()
        row.operator("stampinfo.resethandlersandcomponodes", emboss=True)

        row = layout.row()
        row.operator("debug.lauchrrsrender", emboss=True)

        if not utils_render.isRenderPathValid(context.scene):
            row = layout.row()
            row.alert = True
            row.label(text="Invalid render path")

        row = layout.row()
        row.operator("debug.createcomponodes", emboss=True)
        row.operator("debug.clearcomponodes", emboss=True)


class UAS_LaunchRRSRender(Operator):
    bl_idname = "debug.lauchrrsrender"
    bl_label = "RRS Render Script"
    bl_description = "Run the RRS Render Script"

    def execute(self, context):
        """Use the selected file as a stamped logo"""
        print(" UAS_LaunchRRSRender")

        from . import RRS_StampInfoRun

        RRS_StampInfoRun.setRRSRender(context.scene, "My Shot")

        return {"FINISHED"}


class UAS_CreateCompoNodes(Operator):
    bl_idname = "debug.createcomponodes"
    bl_label = "Create Compo Nodes"
    bl_description = ""

    def execute(self, context):
        """Create Compo Nodes"""
        stamper.createInfoCompoNodes(context.scene, context.scene.frame_current)

        return {"FINISHED"}


class UAS_ClearCompoNodes(Operator):
    bl_idname = "debug.clearcomponodes"
    bl_label = "Clear Compo Nodes"
    bl_description = ""

    def execute(self, context):
        """Clear Compo Nodes"""
        stamper.clearInfoCompoNodes(context.scene)

        return {"FINISHED"}


_classes = (
    UAS_PT_StampInfoDebug,
    UAS_PT_StampInfoDebugCompo,
    UAS_CreateCompoNodes,
    UAS_ClearCompoNodes,
    UAS_LaunchRRSRender,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
