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
handlers
"""

import logging

import bpy
from bpy.app.handlers import persistent


_logger = logging.getLogger(__name__)


# global vars
if "gbWkDebug" not in vars() and "gbWkDebug" not in globals():
    gbWkDebug = False

if gbWkDebug:
    if "gbWkDebug_DontDeleteTmpFiles" not in vars() and "gbWkDebug_DontDeleteTmpFiles" not in globals():
        gbWkDebug_DontDeleteTmpFiles = True

    if "gbWkDebug_DrawTextLines" not in vars() and "gbWkDebug_DrawTextLines" not in globals():
        gbWkDebug_DrawTextLines = True

else:
    if "gbWkDebug_DontDeleteTmpFiles" not in vars() and "gbWkDebug_DontDeleteTmpFiles" not in globals():
        gbWkDebug_DontDeleteTmpFiles = False

    if "gbWkDebug_DrawTextLines" not in vars() and "gbWkDebug_DrawTextLines" not in globals():
        gbWkDebug_DrawTextLines = False

