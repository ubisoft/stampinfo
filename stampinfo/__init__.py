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
Main init

"""

import logging

import os
from pathlib import Path
import subprocess

import bpy
import bpy.utils.previews
from bpy.types import Operator
from bpy.props import StringProperty, PointerProperty

# for file browser:
from bpy_extras.io_utils import ImportHelper


import importlib

from .config import config

from .utils.utils_render import Utils_LaunchRender
from .utils.utils import display_addon_registered_version
from .utils.utils_os import open_folder
from .utils import utils_vse_render
from .utils import utils_operators

from . import stamper
from . import stampInfoSettings


from .ui import si_ui

from .operators import debug

importlib.reload(stampInfoSettings)
importlib.reload(stamper)
importlib.reload(debug)


bl_info = {
    "name": "Stamp Info",
    "author": "Julien Blervaque (aka Werwack)",
    "description": "Stamp scene information on the rendered images - Ubisoft"
    "\nRequiers (and automatically install if not found) the Python library named Pillow",
    "blender": (2, 92, 0),
    "version": (1, 0, 5),
    "location": "Right panel in the 3D View",
    "wiki_url": "https://mdc-web-tomcat17.ubisoft.org/confluence/display/UASTech/UAS+StampInfo",
    # "warning": "BETA Version",
    "category": "Ubisoft",
}

__version__ = ".".join(str(i) for i in bl_info["version"])
display_version = __version__

###########
# Logging
###########

_logger = logging.getLogger(__name__)
_logger.propagate = False
MODULE_PATH = Path(__file__).parent.parent
logging.basicConfig(level=logging.INFO)
_logger.setLevel(logging.DEBUG)  # CRITICAL ERROR WARNING INFO DEBUG NOTSET

pil_logger = logging.getLogger("PIL")
pil_logger.setLevel(logging.INFO)

# _logger.info(f"Logger {}")
# _logger.warning(f"logger {}")
# _logger.error(f"error {}")
# _logger.debug(f"debug {}")


class Formatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def format(self, record: logging.LogRecord):
        """
        The role of this custom formatter is:
        - append filepath and lineno to logging format but shorten path to files, to make logs more clear
        - to append "./" at the begining to permit going to the line quickly with VS Code CTRL+click from terminal
        """
        s = super().format(record)
        # s = record
        pathname = Path(record.pathname).relative_to(MODULE_PATH)
        s += f" [{os.curdir}{os.sep}{pathname}:{record.lineno}]"
        return s


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


classes = (
    stampInfoSettings.UAS_StampInfoSettings,
    Utils_LaunchRender,
    UAS_OT_Open_Documentation_Url,
    UAS_OpenFileBrowser,
)


def module_can_be_imported(name):
    try:
        __import__(name)
        return True
    except ModuleNotFoundError:
        return False


def register():
    from stampinfo import ui
    from stampinfo import icons
    from .properties import addon_prefs
    from .operators import render_operators

    display_addon_registered_version("Stamp Info")

    config.initGlobalVariables()

    ###################
    # logging
    ###################

    if len(_logger.handlers) == 0:
        _logger.setLevel(logging.WARNING)
        formatter = Formatter("{asctime} {levelname[0]} {name:<36}  - {message:<80}", style="{")
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        _logger.addHandler(handler)

    ###################
    # Pillow lib installation
    ###################

    if not module_can_be_imported("PIL"):
        subprocess.run([bpy.app.binary_path_python, "-m", "pip", "install", "pillow"])

    for cls in classes:
        bpy.utils.register_class(cls)

    icons.register()
    addon_prefs.register()
    render_operators.register()
    si_ui.register()
    ui.register()
    utils_vse_render.register()
    utils_operators.register()

    # debug tools
    if config.uasDebug:
        debug.register()

    bpy.types.Scene.UAS_StampInfo_Settings = PointerProperty(type=stampInfoSettings.UAS_StampInfoSettings)


def unregister():

    # from .ui import si_ui
    from stampinfo import ui
    from stampinfo import icons
    from .operators import render_operators
    from .properties import addon_prefs

    # debug tools
    if config.uasDebug:
        debug.unregister()

    utils_operators.unregister()
    utils_vse_render.unregister()
    ui.unregister()
    si_ui.unregister()
    render_operators.unregister()
    addon_prefs.unregister()
    icons.unregister()

    for cls in reversed(classes):
        # print(str(cls) + " being unregistered...")
        bpy.utils.unregister_class(cls)

    config.releaseGlobalVariables()
