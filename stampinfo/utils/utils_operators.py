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

import os
from pathlib import Path
import subprocess

import bpy
from bpy.types import Operator
from bpy.props import StringProperty
from .utils_os import open_folder

# for file browser:
from bpy_extras.io_utils import ImportHelper


###################
# UI
###################


class UAS_OT_Open_Documentation_Url(Operator):  # noqa 801
    bl_idname = "stampinfo.open_documentation_url"
    bl_label = "Open Documentation Web Page"
    bl_description = "Open web page.\nShift + Click: Copy the URL into the clipboard"

    path: StringProperty()

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
                from ..utils.utils import ShowMessageBox

                ShowMessageBox(f"{absPathToOpen} not found", "Open Explorer - Directory not found", "ERROR")

        return {"FINISHED"}


_classes = (UAS_StampInfo_OpenExplorer, UAS_OT_Open_Documentation_Url, UAS_OpenFileBrowser)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
