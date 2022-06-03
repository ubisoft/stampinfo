# GPLv3 License
#
# Copyright (C) 2022 Ubisoft
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

# import os
# from pathlib import Path

import bpy
import bpy.utils.previews
from bpy.props import IntProperty, PointerProperty


from .config import config
from .utils import utils
from .utils.utils_render import Utils_LaunchRender
from .utils import utils_vse_render
from .properties import stampInfoSettings
from .operators import debug
from .properties import stamper
from .ui import si_ui

import importlib

importlib.reload(stampInfoSettings)
importlib.reload(stamper)
importlib.reload(debug)

from stampinfo.config import sm_logging

_logger = sm_logging.getLogger(__name__)


bl_info = {
    "name": "Stamp Info",
    "author": "Julien Blervaque (aka Werwack) - Ubisoft",
    "description": "Stamp scene information on the rendered images",
    "blender": (3, 1, 0),
    "version": (1, 3, 1),
    "location": "View3D > Stamp Info",
    "wiki_url": "https://ubisoft-stampinfo.readthedocs.io",
    "tracker_url": "https://github.com/ubisoft/stampinfo/issues",
    "support": "COMMUNITY",
    # "warning": "BETA Version",
    "category": "Ubisoft",
}

__version__ = ".".join(str(i) for i in bl_info["version"])
display_version = __version__

###########
# Logging
###########

# _logger = sm_logging.getLogger(__name__)
# _logger.propagate = False
# MODULE_PATH = Path(__file__).parent.parent
# logging.basicConfig(level=logging.INFO)
# _logger.setLevel(logging.DEBUG)  # CRITICAL ERROR WARNING INFO DEBUG NOTSET

import logging

pil_logger = logging.getLogger("PIL")
pil_logger.setLevel(logging.INFO)

# # _logger.info(f"Logger {}")
# # _logger.warning(f"logger {}")
# # _logger.error(f"error {}")
# # _logger.debug(f"debug {}")


# class Formatter(logging.Formatter):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#     def format(self, record: logging.LogRecord):
#         """
#         The role of this custom formatter is:
#         - append filepath and lineno to logging format but shorten path to files, to make logs more clear
#         - to append "./" at the begining to permit going to the line quickly with VS Code CTRL+click from terminal
#         """
#         s = super().format(record)
#         # s = record
#         pathname = Path(record.pathname).relative_to(MODULE_PATH)
#         s += f" [{os.curdir}{os.sep}{pathname}:{record.lineno}]"
#         return s


classes = (
    stampInfoSettings.UAS_StampInfoSettings,
    Utils_LaunchRender,
)


def stampInfo_resetProperties():
    from .utils.utils_inspectors import resetAttrs

    # print("stampInfo_resetProperties...")
    # print(f"Scene name: {bpy.context.scene.name}")

    props = bpy.context.scene.UAS_StampInfo_Settings
    resetAttrs(props)


def register():

    config.initGlobalVariables()

    from .utils import utils_ui

    utils_ui.register()

    sm_logging.initialize(addonName="Stamp Info", prefix="SI")
    if config.devDebug:
        _logger.setLevel("DEBUG")  # CRITICAL ERROR WARNING INFO DEBUG NOTSET

    logger_level = f"Logger level: {sm_logging.getLevelName()}"
    versionTupple = utils.display_addon_registered_version("Stamp Info", more_info=logger_level)

    # # logging
    # ###################
    # if len(_logger.handlers) == 0:
    #     _logger.setLevel(logging.WARNING)
    #     formatter = Formatter("{asctime} {levelname[0]} {name:<36}  - {message:<80}", style="{")
    #     handler = logging.StreamHandler()
    #     handler.setFormatter(formatter)
    #     _logger.addHandler(handler)

    # install dependencies and required Python libraries
    ###################
    # try to install dependencies and collect the errors in case of troubles
    # If some mandatory libraries cannot be loaded then an alternative Add-on Preferences panel
    # is used and provide some visibility to the user to solve the issue
    # Pillow lib is installed there
    from .install.install_dependencies import install_dependencies

    installErrorCode = install_dependencies([("PIL", "pillow")], retries=1, timeout=5)
    if 0 != installErrorCode:
        return installErrorCode
    print("  Pillow Imaging Library (PIL) correctly installed for Ubisoft Stamp Info")

    # if install went right then register other packages
    ###################
    from stampinfo import ui
    from stampinfo import icons
    from .addon_prefs import addon_prefs
    from .operators import render_operators

    ###################
    # update data
    ###################

    bpy.types.WindowManager.UAS_stamp_info_version = IntProperty(
        name="Add-on Version Int", description="Add-on version as integer", default=versionTupple[1]
    )

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
    print("\n*** --- Unregistering Stamp Info Add-on --- ***")
    from .utils import utils_ui

    # Unregister packages that may have been registered if the install had errors
    ###################
    from .install.install_dependencies import unregister_from_failed_install

    if unregister_from_failed_install():
        utils_ui.unregister()
        config.releaseGlobalVariables()
        return ()

    # Unregister packages that were registered if the install went right
    ###################

    # debug tools
    debug.unregister()

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
        bpy.utils.unregister_class(cls)

    del bpy.types.WindowManager.UAS_stamp_info_version

    utils_ui.unregister()
    config.releaseGlobalVariables()

    print("")
