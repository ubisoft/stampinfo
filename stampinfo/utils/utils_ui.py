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
UI utilities
"""


import os
from pathlib import Path
import subprocess

import bpy
from bpy.types import Operator
from bpy.props import StringProperty

# for file browser:
from bpy_extras.io_utils import ImportHelper

from .utils_os import open_folder

###################
# UI
###################


def collapsable_panel(
    layout: bpy.types.UILayout, data: bpy.types.AnyType, property: str, alert: bool = False, **kwargs
):
    row = layout.row()
    row.prop(
        data, property, icon="TRIA_DOWN" if getattr(data, property) else "TRIA_RIGHT", icon_only=True, emboss=False,
    )
    if alert:
        row.alert = True
        row.label(text="", icon="ERROR")
    row.label(**kwargs)
    return getattr(data, property)


###################
# Open doc and explorers
###################


class UAS_StampInfo_OpenExplorer(Operator):
    bl_idname = "uas_stampinfo.open_explorer"
    bl_label = "Open Explorer"
    bl_description = "Open an Explorer window located at the render output directory.\nShift + Click: Copy the path into the clipboard"

    path: StringProperty()

    def invoke(self, context, event):
        absPathToOpen = bpy.path.abspath(self.path)
        head, tail = os.path.split(absPathToOpen)
        absPathToOpen = head + "\\"

        if event.shift:

            def _copy_to_clipboard(txt):
                cmd = "echo " + txt.strip() + "|clip"
                return subprocess.check_call(cmd, shell=True)

            _copy_to_clipboard(absPathToOpen)

        else:
            # wkipwkip
            if Path(absPathToOpen).exists():
                subprocess.Popen(f'explorer "{Path(absPathToOpen)}"')
            elif Path(absPathToOpen).parent.exists():
                subprocess.Popen(f'explorer "{Path(absPathToOpen).parent}"')
            elif Path(absPathToOpen).parent.parent.exists():
                subprocess.Popen(f'explorer "{Path(absPathToOpen).parent.parent}"')
            else:
                print(f"Open Explorer failed: Path not found: {Path(absPathToOpen)}")
                from ..utils.utils_ui import show_message_box

                show_message_box(f"{absPathToOpen} not found", "Open Explorer - Directory not found", "ERROR")

        return {"FINISHED"}


class UAS_OT_Open_Documentation_Url(Operator):  # noqa 801
    bl_idname = "stampinfo.open_documentation_url"
    bl_label = ""
    bl_description = "Open web page.\nShift + Click: Copy the URL into the clipboard"

    tooltip: StringProperty(default="")
    path: StringProperty()

    @classmethod
    def description(self, context, properties):
        descr = properties.tooltip if "" != properties.tooltip else "Open web page."
        descr += "\nShift + Click: Copy the URL into the clipboard"
        return descr

    def invoke(self, context, event):
        if event.shift:
            # copy path to clipboard
            cmd = "echo " + (self.path).strip() + "|clip"
            subprocess.check_call(cmd, shell=True)
        else:
            open_folder(self.path)

        return {"FINISHED"}


# This operator requires   from bpy_extras.io_utils import ImportHelper
# See https://sinestesia.co/blog/tutorials/using-blenders-filebrowser-with-python/
class UAS_OpenFileBrowser(Operator, ImportHelper):
    bl_idname = "stampinfo.openfilebrowser"
    bl_label = "Open"
    bl_description = (
        "Open the file browser to define the image to stamp\n"
        "Relative path must be set directly in the text field and must start with ''//''"
    )

    filter_glob: StringProperty(default="*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.tga,*.bmp", options={"HIDDEN"})

    def execute(self, context):
        """Use the selected file as a stamped logo"""
        filename, extension = os.path.splitext(self.filepath)
        #   print('Selected file:', self.filepath)
        #   print('File name:', filename)
        #   print('File extension:', extension)
        bpy.context.scene.UAS_StampInfo_Settings.logoFilepath = self.filepath

        return {"FINISHED"}


####################################################################


def show_message_box(message="", title="Message Box", icon="INFO"):
    """Display a message box

    A message can be drawn on several lines when containing the separator \n

    Shows a message box with a specific message:
    -> show_message_box("This is a message")

    Shows a message box with a message and custom title
    -> show_message_box("This is a message", "This is a custom title")

    Shows a message box with a message, custom title, and a specific icon
    -> show_message_box("This is a message", "This is a custom title", 'ERROR')
    """

    messages = message.split("\n")

    def draw(self, context):
        layout = self.layout

        for s in messages:
            layout.label(text=s)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


# TODO: Cleaning
# Dev note: This function has to be here for the moment cause it is passed
# in stampinfo code to a call to uas_stamp_info.querybox
def reset_all_properties():
    import stampinfo

    print("reset_all_properties")
    stampinfo.stampInfo_resetProperties()


class UAS_StampInfo_OT_Querybox(Operator):
    """Display a query dialog box

    A message can be drawn on several lines when containing the separator \n
    """

    bl_idname = "uas_stamp_info.querybox"
    bl_label = "Please confirm:"
    # bl_description = "..."
    bl_options = {"INTERNAL"}

    width: bpy.props.IntProperty(default=400)
    message: bpy.props.StringProperty(default="Do you confirm the operation?")
    function_name: bpy.props.StringProperty(default="")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=self.width)

    def draw(self, context):

        messages = self.message.split("\n")

        layout = self.layout
        layout.separator(factor=1)

        for s in messages:
            layout.label(text=s)

        # row = layout.row()
        # row.separator(factor=2)
        # row.label(text=self.message)

        layout.separator()

    def execute(self, context):
        eval(self.function_name + "()")
        # try:
        #     eval(self.function_name + "()")
        # except Exception:
        #     print(f"*** Function {self.function_name} not found ***")

        return {"FINISHED"}


####################################################################

_classes = (UAS_StampInfo_OpenExplorer, UAS_OT_Open_Documentation_Url, UAS_OpenFileBrowser, UAS_StampInfo_OT_Querybox)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
