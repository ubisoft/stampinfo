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
This module defines the global preferences of the add-on
"""

import bpy
from bpy.types import AddonPreferences
from bpy.props import IntProperty, BoolProperty

from .addon_prefs_ui import draw_addon_prefs

from stampinfo.utils import utils
from stampinfo.utils.utils_os import get_latest_release_version

from stampinfo.config import config
from stampinfo.config import sm_logging

_logger = sm_logging.getLogger(__name__)


class UAS_StampInfo_AddonPrefs(AddonPreferences):
    """
    Use this to get these prefs:
    prefs = context.preferences.addons["stampinfo"].preferences
    """

    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package
    bl_idname = "stampinfo"

    def version(self):
        """Return the add-on version in the form of a tupple made by:
            - a string x.y.z (eg: "1.21.3")
            - an integer. x.y.z becomes xxyyyzzz (eg: "1.21.3" becomes 1021003)
        Return None if the addon has not been found
        """
        return utils.addonVersion("Stamp Info")

    newAvailableVersion: IntProperty(
        description="Store the version of the latest release of the add-on as an integer if there is an online release"
        "\nthat is more recent than this version. If there is none then the value is 0",
        # default=2005001,
        default=1000000,
    )

    checkForNewAvailableVersion: BoolProperty(
        name="Check for Updates",
        description=(
            "If checked then the add-on automaticaly see if a new release\n"
            "is available online, and if so then a red world icon is displayed at the\n"
            "top right corner of the main panel"
        ),
        default=True,
    )

    isInitialized: BoolProperty(
        name="Preferences Initialization State",
        description=(
            "Flag to validate that Stamp Info preferences have been correctly initialized"
            "\nThis flag can be changed for debug purpose: activate the debug mode and go to the add-on Preferences, in the Debug tab"
        ),
        default=False,
    )

    def initialize_stamp_info_prefs(self):
        print("\nInitializing Stamp Info Preferences...")

        self.newAvailableVersion = 0

        if self.checkForNewAvailableVersion and not config.devDebug:
            versionStr = get_latest_release_version(
                "https://github.com/ubisoft/stampinfo/releases/latest", verbose=True
            )

            if versionStr is not None:
                # version string from the tags used by our releases on GitHub is formated as this: v<int>.<int>.<int>
                version = utils.convertVersionStrToInt(versionStr)

                _logger.debug_ext(
                    f"Checking for updates: Latest version of Ubisoft Stamp Info online is: {versionStr}", col="BLUE"
                )
                if self.version()[1] < version:
                    _logger.debug_ext("   New version available online...", col="BLUE")
                    self.newAvailableVersion = version
                else:
                    self.newAvailableVersion = 0
            else:
                self.newAvailableVersion = 0

        self.isInitialized = True

    install_failed: BoolProperty(
        name="Install failed",
        default=False,
    )

    display_main_panel: BoolProperty(
        name="Display Panel",
        description="Display the Stamp Info properties panel in the tab list in the 3D View",
        default=True,
    )

    write_still: BoolProperty(
        name="Write rendered still images on disk",
        description="If checked then writes rendered still images on disk.\n"
        "If not checked (most common approach) then the images are written with a name starting with '_Still_' in order to prevent modification on a single frame"
        "in an already rendered image sequences",
        default=False,
        options=set(),
    )

    delete_temp_scene: BoolProperty(
        name="Delete the temporary scene used for VSE rendering",
        description="Delete temporary scene used for VSE rendering",
        default=True,
        options=set(),
    )

    delete_temp_images: BoolProperty(
        name="Delete the temporary images used for VSE rendering",
        description="Delete temporary images used for VSE rendering",
        default=True,
        options=set(),
    )

    ##################################################################################
    # Draw
    ##################################################################################
    def draw(self, context):
        draw_addon_prefs(self, context)

    # -----------------------------------------------------------
    # UI user preferences - Not exposed
    # -----------------------------------------------------------
    panelExpanded_mode: BoolProperty(
        name="Expand Render Mode Properties",
        default=True,
    )


_classes = (UAS_StampInfo_AddonPrefs,)


def register():
    _logger.debug_ext("       - Registering Add-on Prefs Package", form="REG")

    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    _logger.debug_ext("       - Unregistering Add-on Prefs Package", form="UNREG")

    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
