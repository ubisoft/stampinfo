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
Classes and functions dedicated to filenames management such as sequence names.
"""


from pathlib import Path
import bpy


class SequencePath:
    # to do: suppôrt / and \, support creation with file name already with an index (have a parameter
    # to get generic infos or index specific infos)
    """
    Split a file path into parts. Dedicated to sequence filename management.
    
    Returns an instance made of:
        - fullpath: the file path and name
        - parent: the file path without the file name AND with a "\" at the end
        - name: the name of the file with extention
        - stem: the name of the file without extention
        - seq_name: the name of the sequence when # are removed
        - suffix: the file extention

    Eg.: myPath = SequencePath("c:\temp\mySequence_####.png")
        - myPath.fullpath(): "c:\temp\mySequence_####.png"
        - myPath.parent(): "c:\temp\"
        - myPath.name(): "mySequence_####.png"
        - myPath.stem(): "mySequence_####"
        - myPath.sequence_name(): "mySequence"
        - myPath.sequence_indices: "####"
        - myPath.suffix: ".png"     or myPath.extention(): ".png"
    """

    fullpath = None

    def __init__(self, filepath):
        self.fullpath = filepath

    def isValidFileExtension(self):
        """
        Return False if the extension is empty, containts only digits or contains at least one # character
        """
        suf = str(Path(self.fullpath).suffix)
        if 0 == len(suf):
            return False
        if "." == suf[0]:
            suf = suf[1:]
            try:
                # if suf can be converted to an int then the extention is not valid
                int(suf)
                return False
            except Exception:
                pass

        # case where there is no file extention but filename ends with '.###'
        if -1 != suf.find("#"):
            return False

        return True

    # ------------------------------
    # standard filepath functions

    def parent(self):
        return str(Path(self.fullpath).parent) + "\\"

    def name(self):
        return str(Path(self.fullpath).name)

    def stem(self):
        return str(Path(self.fullpath).stem)

    def extension(self):
        """
        Same as function self.suffix(). Available for consistensy with operating systems.
        """
        return self.suffix()

    def suffix(self):
        """
        Same as function self.extension(). Available for consistensy with Python pathlib terminology.
        If the file name extension contains a # its end will not be considered as an extension
        but as an index.
        """
        suf = str(Path(self.fullpath).suffix)
        if self.isValidFileExtension():
            return suf
        return ""

    # ------------------------------
    # sequence filepath functions

    def sequence_fullpath(self, at_frame=None):
        if at_frame is None:
            return self.fullpath

        fullp = f"{self.parent()}{self.sequence_name(at_frame=at_frame)}"
        return fullp

    def sequence_name(self, at_frame=None):
        if at_frame is None:
            return str(Path(self.fullpath).name)

        indices_pattern = self.sequence_indices(at_frame=at_frame)
        seq_name = f"{self.sequence_basename()}{indices_pattern}{self.suffix()}"
        return seq_name

    def sequence_stem(self, at_frame=None):
        """
        If the file name extension contains a # its end will not be considered as an extension
        but as an index.
        """
        # case where there is no file extention but filename ends with '.###'
        if self.isValidFileExtension():
            seq_stem = self.sequence_basename() + self.sequence_indices(at_frame=at_frame)
        else:
            seq_stem = self.sequence_basename()
            indices = self.sequence_indices(at_frame=at_frame)
            seq_stem += indices

        return seq_stem

    def sequence_basename(self):
        if self.fullpath is None:
            return None

        lastInd = self.fullpath.rfind("#")
        if -1 == lastInd:
            name = self.stem()
        else:
            while lastInd > 0 and "#" == self.fullpath[lastInd]:
                lastInd -= 1
            name = str(Path(self.fullpath[0 : lastInd + 1]).stem)

        return name

    def sequence_indices(self, at_frame=None):
        """
        at_frame: frame infex at which the indices should be set.
            Returns an empty string if there is no indice pattern in the filename.
        """
        if self.fullpath is None:
            return ""

        indices = ""
        lastInd = self.fullpath.rfind("#")
        while lastInd > 0 and "#" == self.fullpath[lastInd]:
            indices += "#"
            lastInd -= 1

        if at_frame is not None and 0 < len(indices):
            at_frame_str = str(at_frame)
            while len(at_frame_str) < len(indices):
                at_frame_str = "0" + at_frame_str
            indices = at_frame_str

        return indices

    def print(self, at_frame=None, spacer=""):
        outStr = ""
        outStr += f"{spacer}fullpath:           {self.fullpath}\n"
        outStr += f"{spacer}parent:             {self.parent()}\n"
        outStr += f"{spacer}name:               {self.name()}\n"
        outStr += f"{spacer}stem:               {self.stem()}\n"
        outStr += f"{spacer}extension (suffix): {self.extension()}\n"

        outStr += "\n"
        outStr += f"{spacer}sequence_fullpath:  {self.sequence_fullpath()}\n"
        outStr += f"{spacer}sequence_name:      {self.sequence_name()}\n"
        outStr += f"{spacer}sequence_stem:      {self.sequence_stem()}\n"
        outStr += f"{spacer}sequence_basename:  {self.sequence_basename()}\n"
        outStr += f"{spacer}sequence_indices:   {self.sequence_indices()}\n"

        if at_frame is not None:
            outStr += f"\n - At frame {at_frame}:\n"
            outStr += f"{spacer}sequence_fullpath: {self.sequence_fullpath(at_frame=at_frame)}\n"
            outStr += f"{spacer}sequence_name:     {self.sequence_name(at_frame=at_frame)}\n"
            outStr += f"{spacer}sequence_stem:     {self.sequence_stem(at_frame=at_frame)}\n"
            outStr += f"{spacer}sequence_basename: {self.sequence_basename()}\n"
            outStr += f"{spacer}sequence_indices:  {self.sequence_indices(at_frame=at_frame)}\n"

        print(outStr)


def run_sequence_path_tests(at_frame=None):

    print("\nrun_sequence_path_tests:")

    filenames = []
    filenames.append("c:\\root\\seq\\singleImage.jpg")
    filenames.append("c:\\root\\seq\\seqNoExt.###")
    filenames.append("c:\\root\\seq\\seqWithUnderscore_###.jpg")
    filenames.append("c:\\root\\seq\\seqWitDot.###.jpg")

    for f in filenames:
        print(f"File path: {f}")
        myPath = SequencePath(f)
        myPath.print(at_frame=at_frame, spacer="   ")


# display test paths for debug and unit tests
# run_sequence_path_tests(at_frame=25)


_classes = (SequencePath,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
