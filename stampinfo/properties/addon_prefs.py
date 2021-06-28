import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, IntProperty, BoolProperty, EnumProperty


class UAS_StampInfo_AddonPrefs(AddonPreferences):
    """
        Use this to get these prefs:
        prefs = context.preferences.addons["stampinfo"].preferences
    """

    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package
    bl_idname = "stampinfo"

    mediaFirstFrameIsZero: BoolProperty(
        name="Output Media First Frame is 0",
        description="If checked (most common approach) then the first frame of the output\nmedia has index 0 (last then have index (seq. number of frames - 1).\n"
        "If not checked then it has index 1 and the last frame has the index equal to the media duration",
        default=True,
        options=set(),
    )

    write_still: BoolProperty(
        name="Write rendered still images on disk",
        description="If checked then writes rendered still images on disk.\n"
        "If not checked (most common approach) then the images are written with a name starting with '_Still_' in order to prevent modification on a single frame"
        "in an already rendered image sequences",
        default=False,
        options=set(),
    )

    def draw(self, context):
        layout = self.layout
        prefs = context.preferences.addons["stampinfo"].preferences

        box = layout.box()
        box.use_property_decorate = False

        box.prop(self, "mediaFirstFrameIsZero")
        box.prop(self, "write_still")


_classes = (UAS_StampInfo_AddonPrefs,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)

