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
from bpy.props import PointerProperty

import importlib

from .config import config

from .utils.utils_render import Utils_LaunchRender
from .utils.utils import display_addon_registered_version

from .utils import utils_vse_render

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
    "version": (1, 0, 8),
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


classes = (
    stampInfoSettings.UAS_StampInfoSettings,
    Utils_LaunchRender,
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
    from .utils import utils_ui

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
    utils_ui.register()

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
    from .utils import utils_ui

    # debug tools
    if config.uasDebug:
        debug.unregister()

    utils_ui.unregister()
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
