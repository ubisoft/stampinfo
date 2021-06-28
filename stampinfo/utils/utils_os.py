# GPLv3 License
#
# Copyright (C) 2020 Ubisoft
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
Utility functions that may require os/platform specific adjustments
"""

import subprocess
from pathlib import Path
import sys


def open_folder(path):
    """
    Open a path or an URL with the application specified by the os
    """
    if sys.platform == "darwin":
        subprocess.check_call(["open", "--", path])
    elif sys.platform == "linux":
        subprocess.check_call(["xdg-open", path])
    elif sys.platform == "win32":
        subprocess.Popen(f'explorer "{Path(path)}"')


# to do: support of / and \, make abs?
def decompose_path(filepath):
    """
    Split a file path into parts. Dedicated to 
    Returns a dictionnary made of:
        - fullpath: the file path and name
        - parent: the file path without the file name AND with a "\" at the end
        - name: the name of the file with extention
        - stem: the name of the file without extention
        - seq_name: the name of the sequence when # are removed
        - suffix: the file extention

    Eg.: res = decompose_path("c:\temp\mySequence_####.png")
        - res.fullpath: "c:\temp\mySequence_####.png"
        - res.parent: "c:\temp\"
        - res.name: "mySequence_####.png"
        - res.stem: "mySequence_####"
        - res.seq_name: "mySequence"
        - res.seq_separators: "####"
        - res.suffix: ".png"
    """

