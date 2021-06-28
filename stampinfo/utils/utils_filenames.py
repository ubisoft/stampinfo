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
        - myPath.fullpath: "c:\temp\mySequence_####.png"
        - myPath.parent: "c:\temp\"
        - myPath.name: "mySequence_####.png"
        - myPath.stem: "mySequence_####"
        - myPath.seq_name: "mySequence"
        - myPath.seq_separators: "####"
        - myPath.suffix: ".png"
    """

    fullpath = None

    def __init__(self, filepath):
        self.fullpath = filepath

    # ------------------------------
    # standard filepath functions

    def parent(self):
        return str(Path(self.fullpath).parent) + "\\"

    def name(self):
        return str(Path(self.fullpath).name)

    def stem(self):
        return str(Path(self.fullpath).stem)

    def suffix(self):
        """
        If the file name extension contains a # its end will not be considered as an extension
        but as an index.
        """
        suf = str(Path(self.fullpath).suffix)
        if -1 != suf.find("#"):
            return ""
        return suf

    # ------------------------------
    # sequence filepath functions

    def sequence_name(self):
        return str(Path(self.fullpath).name)

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

    def sequence_stem(self):
        """
        If the file name extension contains a # its end will not be considered as an extension
        but as an index.
        """
        suf = str(Path(self.fullpath).suffix)
        if -1 != suf.find("#"):
            return str(Path(self.fullpath).name)
        return str(Path(self.fullpath).stem)

    def sequence_indices(self):
        if self.fullpath is None:
            return ""

        indices = ""
        lastInd = self.fullpath.rfind("#")
        while lastInd > 0 and "#" == self.fullpath[lastInd]:
            indices += "#"
            lastInd -= 1

        return indices

    def print(self, spacer=""):
        outStr = ""
        outStr += f"{spacer}fullpath:          {self.fullpath}\n"
        outStr += f"{spacer}parent:            {self.parent()}\n"
        outStr += f"{spacer}name:              {self.name()}\n"
        outStr += f"{spacer}stem:              {self.stem()}\n"
        outStr += f"{spacer}suffix:            {self.suffix()}\n"

        # outStr += "\n"
        outStr += f"{spacer}sequence_name:     {self.sequence_name()}\n"
        outStr += f"{spacer}sequence_stem:     {self.sequence_stem()}\n"
        outStr += f"{spacer}sequence_basename: {self.sequence_basename()}\n"
        outStr += f"{spacer}sequence_indices:  {self.sequence_indices()}\n"

        print(outStr)


def run_sequence_path_tests():

    print("\nrun_sequence_path_tests:")

    filenames = []
    filenames.append("c:\\root\\seq\\singleImage.jpg")
    filenames.append("c:\\root\\seq\\seqWitDot.###.jpg")
    filenames.append("c:\\root\\seq\\seqWithUnderscore_###.jpg")
    filenames.append("c:\\root\\seq\\seqNoExt.###")

    for f in filenames:
        print(f"File path: {f}")
        myPath = SequencePath(f)
        myPath.print(spacer="   ")


run_sequence_path_tests()

# """ Find the name template for the specified images sequence in order to create it
#    """
#    import re
#    from pathlib import Path

#    seq = None
#    p = Path(images_path)
#    folder, name = p.parent, str(p.name)

#    mov_name = ""
#    # Find frame padding. Either using # formating or printf formating
#    file_re = ""
#    padding_match = re.match(".*?(#+).*", name)
#    if not padding_match:
#        padding_match = re.match(".*?%(\d\d)d.*", name)
#        if padding_match:
#            padding_length = int(padding_match[1])
#            file_re = re.compile(
#                r"^{1}({0}){2}$".format(
#                    "\d" * padding_length, name[: padding_match.start(1) - 1], name[padding_match.end(1) + 1 :]
#                )
#            )
#            mov_name = (
#                str(p.stem)[: padding_match.start(1) - 1] + str(p.stem)[padding_match.end(1) + 1 :]
#            )  # Removes the % and d which are not captured in the re.
#    else:
#        padding_length = len(padding_match[1])
#        file_re = re.compile(
#            r"^{1}({0}){2}$".format(
#                "\d" * padding_length, name[: padding_match.start(1)], name[padding_match.end(1) :]
#            )
#        )
#        mov_name = str(p.stem)[: padding_match.start(1)] + str(p.stem)[padding_match.end(1) :]

#    if padding_match:
#        # scene.render.filepath = str(folder.joinpath(mov_name))

#        frames = dict()
#        max_frame = 0
#        min_frame = 999999999
#        for f in sorted(list(folder.glob("*"))):
#            _folder, _name = f.parent, f.name
#            re_match = file_re.match(_name)
#            if re_match:
#                frame_nb = int(re_match[1])
#                max_frame = max(max_frame, frame_nb)
#                min_frame = min(min_frame, frame_nb)

#                frames[frame_nb] = f

#        frame_keys = list(frames.keys())  # As of python 3.7 should be in the insertion order.
#        if frames:
#            seq = scene.sequence_editor.sequences.new_image(
#                clipName, str(frames[frame_keys[0]]), channelInd, atFrame
#            )

#            for i in range(min_frame + 1, max_frame + 1):
#                pp = frames.get(i, Path(""))
#                seq.elements.append(pp.name)

#
#


_classes = (SequencePath,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
