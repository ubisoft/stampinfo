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
Dependencies installation
"""

import bpy
from ..utils.utils_os import internet_on, module_can_be_imported, is_admin
from . import addon_error_prefs

import logging

_logger = logging.getLogger(__name__)


def install_libraries():
    """Install external libraries: Pillow
    """
    error_messages = []
    # return ["Debug message"]

    # PIL (or pillow)
    ##########################
    module_name = "PIL"
    if not module_can_be_imported(module_name):

        outputMess = f"   # {module_name} Install Failed: "
        # NOTE: possible issue on Mac OS, check the content of the function internet_on()
        if not internet_on():
            errorInd = 1
            errorMess = f"Err.{errorInd}: No Internet connection"
            print(outputMess + errorMess)
            error_messages.append((errorMess, errorInd))
            return error_messages

        import subprocess
        import os
        import sys
        import subprocess
        from pathlib import Path

        pyExeFile = sys.executable
        localPyDir = str(Path(pyExeFile).parent) + "\\lib\\site-packages\\"

        if not is_admin():
            if not os.access(localPyDir, os.W_OK):
                errorInd = 2
                errorMess = f"Err.{errorInd}: No Admin rights - Cannot write to Blender Python folder"
                print(outputMess + errorMess)
                error_messages.append((errorMess, errorInd))
                return error_messages

        try:
            # NOTE: to prevent a strange situation where pip finds and/or installs the library in the OS Python directory
            # we force the installation in the current Blender Python \lib\site-packages with the use of "--ignore-installed"
            subError = subprocess.run(
                [bpy.app.binary_path_python, "-m", "pip", "install", "pillow", "--ignore-installed"]
            )
            # print(f"    - subError.returncode: {subError.returncode}")
            if 0 == subError.returncode:
                # NOTE: one possible returned error is "Requirement already satisfied". This case should not appear since
                # we test is the module is already there with the function module_can_be_imported
                if module_can_be_imported(module_name):
                    print("  Pillow Imaging Library (PIL) correctly installed for Ubisoft Stamp Info")
                else:
                    errorInd = 3
                    errorMess = f"Err.{errorInd}: Library {module_name} installed but cannot be imported"
                    print(f"    subError: {subError}")
                    print(outputMess + errorMess)
                    print("    Possibly installed in a wrong Python instance folder - Contact the support")
                    error_messages.append((errorMess, errorInd))
            else:
                errorInd = 4
                errorMess = f"Err.{errorInd}: Library {module_name} cannot be imported"
                print(f"    subError: {subError}")
                print(outputMess + errorMess)
                error_messages.append((errorMess, errorInd))

                # send the error
                subError.check_returncode()

        except subprocess.CalledProcessError as e:
            print(e.output)
            if 0 == e.returncode:
                errorInd = 5
                errorMess = f"Err.{errorInd}: Error during installation of library {module_name}"
            else:
                errorInd = 6
                errorMess = f"Err.{errorInd}: Error during installation of library {module_name}"
            print(outputMess + errorMess)
            error_messages.append((errorMess, errorInd))

    return error_messages


def install_dependencies():
    """Install the add-on dependecies
    Return 0 if everything went well, the error code >0 otherwise
    """
    installation_errors = install_libraries()
    # installation_errors = []

    if 0 < len(installation_errors):
        print(
            "   !!! Something went wrong during the installation of the add-on - Check the Stamp Info add-on Preferences panel !!!"
        )
        addon_error_prefs.register()
        prefs_addon = bpy.context.preferences.addons["stampinfo"].preferences
        prefs_addon.error_message = installation_errors[0][0]
        return installation_errors[0][1]
    return 0


def unregister_from_failed_install():
    # unregistering add-on in the case it has been registered with install errors
    prefs_addon = bpy.context.preferences.addons["stampinfo"].preferences
    if hasattr(prefs_addon, "install_failed") and prefs_addon.install_failed:
        from . import addon_error_prefs

        print("      **************** Uninstall failed addon ***************")
        addon_error_prefs.unregister()
        return True
    return False
