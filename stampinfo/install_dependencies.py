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
from .utils.utils_os import internet_on, module_can_be_imported, is_admin

import logging

_logger = logging.getLogger(__name__)


def install_dependencies():
    """Install external libraries: Pillow
    """
    error_messages = []
    # return ["Debug message"]

    # PIL (or pillow)
    ##########################
    module_name = "PIL"
    if not module_can_be_imported(module_name):

        outputMess = f"*** {module_name} Install Failed: "
        # NOTE: possible issue on Mac OS, check the content of the function internet_on()
        if not internet_on():
            errorMess = f"Err.{1}: No Internet connection"
            print(outputMess + errorMess)
            error_messages.append(errorMess)
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
                errorMess = f"Err.{2}: No Admin rights - Cannot write to Blender Python folder"
                print(outputMess + errorMess)
                error_messages.append(errorMess)
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
                    errorMess = f"Err.{3}: Library {module_name} installed but cannot be imported"
                    print(f"    subError: {subError}")
                    print(outputMess + errorMess)
                    print("    Possibly installed in a wrong Python instance folder - Contact the support")
                    error_messages.append(errorMess)
            else:
                errorMess = f"Err.{4}: Library {module_name} cannot be imported"
                print(f"    subError: {subError}")
                print(outputMess + errorMess)
                error_messages.append(errorMess)

                # send the error
                subError.check_returncode()

        except subprocess.CalledProcessError as e:
            print(e.output)
            if 0 == e.returncode:
                errorMess = f"Err.{5}: Error during installation of library {module_name}"
            else:
                errorMess = f"Err.{6}: Error during installation of library {module_name}"
            print(outputMess + errorMess)
            error_messages.append(errorMess)

    return error_messages
