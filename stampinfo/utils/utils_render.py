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

import os

import bpy
from bpy.types import Operator


def isRenderPathValid(scene):
    filepath = bpy.path.abspath(scene.render.filepath)

    head, tail = os.path.split(filepath)

    filePathIsValid = os.path.exists(head)

    return filePathIsValid


class Utils_LaunchRender(Operator):
    bl_idname = "utils.launch_render"
    bl_label = "Render"
    bl_description = "Render"
    bl_options = {"INTERNAL"}

    renderMode: bpy.props.EnumProperty(
        name="Render", description="", items=(("STILL", "Still", ""), ("ANIMATION", "Animation", "")), default="STILL"
    )

    @classmethod
    def poll(cls, context):
        return context.scene.camera is not None

    def execute(self, context):

        if "STILL" == self.renderMode:
            #     bpy.ops.render.view_show()
            #     bpy.ops.render.render(use_viewport = True)
            bpy.ops.render.render("INVOKE_DEFAULT", animation=False, write_still=False)
        elif "ANIMATION" == self.renderMode:

            bpy.ops.render.render("INVOKE_DEFAULT", animation=True)

            # en bg, ne s'arrete pas
            # bpy.ops.render.render(animation = True)

            # bpy.ops.render.opengl ( animation = True )

        return {"FINISHED"}
