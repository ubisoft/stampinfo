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

import subprocess

import bpy
from .utils.utils_os import internet_on, module_can_be_imported

import logging

_logger = logging.getLogger(__name__)


def install_dependencies():
    """Install external libraries: Pillow
    """
    error_messages = []

    # warning: on Mac OS this test failed and internet is considered to be accessible
    if not internet_on():
        error_messages.append("No Internet connection")
        return error_messages

    # PIL (or pillow)
    ##########################
    module_name = "PIL"
    if not module_can_be_imported(module_name):
        try:
            subError = subprocess.run([bpy.app.binary_path_python, "-m", "pip", "install", "pillow"])
            if 0 != subError:
                # Note: one possible returned error is "Requirement already satisfied". This case should not appear since
                # we test is the module is already there with the function module_can_be_imported
                print(f"*** Ubisoft Stamp Info Error: Failed to import Python library named {module_name}")
                print(f"subError: {subError}")
                error_messages.append(f"Module {module_name} cannot be imported")

                # send the error
                subError.check_returncode()
        except subprocess.CalledProcessError as e:
            print(e.output)
            print(f"*** Ubisoft Stamp Info Error: error in subprocess to import Python library named {module_name}")
            error_messages.append(f"Module {module_name}: No module with this name found for import")

        if 0 < len(error_messages):
            return error_messages

    # return []
    return error_messages
