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

import bpy
import bpy.utils.previews
from bpy.props import PointerProperty

import importlib

from .config import config

from .utils import utils
from .utils.utils_render import Utils_LaunchRender

from .utils import utils_vse_render

from . import stamper
from .properties import stampInfoSettings


from .ui import si_ui

from .operators import debug
from .install_dependencies import install_dependencies

importlib.reload(stampInfoSettings)
importlib.reload(stamper)
importlib.reload(debug)


bl_info = {
    "name": "Stamp Info",
    "author": "Julien Blervaque (aka Werwack)",
    "description": "Stamp scene information on the rendered images - Ubisoft"
    "\nRequiers (and automatically install if not found) the Python library named Pillow",
    "blender": (2, 92, 0),
    "version": (1, 0, 11),
    "location": "Right panel in the 3D View",
    "wiki_url": "https://ubisoft-stampinfo.readthedocs.io",
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


def stampInfo_resetProperties():
    from .utils.utils_inspectors import resetAttrs

    # print("stampInfo_resetProperties...")
    # print(f"Scene name: {bpy.context.scene.name}")

    props = bpy.context.scene.UAS_StampInfo_Settings
    resetAttrs(props)


def register():
    from .utils import utils_ui

    utils_ui.register()

    utils.display_addon_registered_version("Stamp Info")

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

    # Install dependencies and required Python libraries
    ####################################################
    # try to install dependencies and collect the errors in case of troubles
    # If some mandatory libraries cannot be loaded then an alternative Add-on Preferences panel
    # is used and provide some visibility to the user to solve the issue
    # Pillow lib is installed there
    config.installation_errors = install_dependencies()
    # config.installation_errors = []

    if 0 < len(config.installation_errors):
        from .addon_prefs import addon_error_prefs

        print(
            "\n   !!! Something went wrong during the installation of the add-on - Check the Stamp Info add-on Preferences panel !!!"
        )

        addon_error_prefs.register()

    else:
        from stampinfo import ui
        from stampinfo import icons
        from .addon_prefs import addon_prefs
        from .operators import render_operators

        for cls in classes:
            bpy.utils.register_class(cls)

        icons.register()
        addon_prefs.register()
        render_operators.register()
        si_ui.register()
        ui.register()
        utils_vse_render.register()

        bpy.types.Scene.UAS_StampInfo_Settings = PointerProperty(type=stampInfoSettings.UAS_StampInfoSettings)

    # debug tools
    debug.register()

    print("")


def unregister():
    # from .ui import si_ui
    from .utils import utils_ui

    # debug tools
    debug.unregister()

    # unregistering add-on in the case it has been registered with install errors
    prefs_addon = bpy.context.preferences.addons["stampinfo"].preferences
    if prefs_addon.install_failed:
        from .addon_prefs import addon_error_prefs

        print("      **************** Uninstall failed addon ***************")
        # viewport_3d.unregister()
        addon_error_prefs.unregister()

        # return ()

    else:
        from stampinfo import ui
        from stampinfo import icons
        from .operators import render_operators
        from .addon_prefs import addon_prefs

        utils_vse_render.unregister()
        ui.unregister()
        si_ui.unregister()
        render_operators.unregister()
        addon_prefs.unregister()
        icons.unregister()

        for cls in reversed(classes):
            # print(str(cls) + " being unregistered...")
            bpy.utils.unregister_class(cls)

    utils_ui.unregister()
    config.releaseGlobalVariables()

    print("")
