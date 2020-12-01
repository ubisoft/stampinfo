import logging

import os
from pathlib import Path
import subprocess

import bpy
import bpy.utils.previews
from bpy.types import Operator
from bpy.props import StringProperty, PointerProperty

# for file browser:
from bpy_extras.io_utils import ImportHelper


import importlib

from .config import config

from .utils.utils_render import Utils_LaunchRender
from .utils.utils import display_addon_registered_version

from . import handlers
from . import stamper
from . import stampInfoSettings

from .ui import si_ui

from .operators import prefs
from .operators import about

from .operators import debug

importlib.reload(stampInfoSettings)
importlib.reload(stamper)
importlib.reload(handlers)
importlib.reload(debug)


bl_info = {
    "name": "UAS_StampInfo",
    "author": "Julien Blervaque (aka Werwack)",
    "description": "Stamp scene information on the rendered images - Ubisoft Animation Studio"
    "\nRequiers (and automatically install if not found) the Python library named Pillow",
    "blender": (2, 83, 0),
    "version": (0, 9, 36),
    "location": "Right panel in the 3D View",
    "wiki_url": "https://mdc-web-tomcat17.ubisoft.org/confluence/display/UASTech/UAS+StampInfo",
    # "warning": "BETA Version",
    "category": "UAS",
}

__version__ = f"v{bl_info['version'][0]}.{bl_info['version'][1]}.{bl_info['version'][2]}"


###########
# Logging
###########

_logger = logging.getLogger(__name__)
_logger.propagate = False
MODULE_PATH = Path(__file__).parent.parent
logging.basicConfig(level=logging.INFO)
_logger.setLevel(logging.DEBUG)  # CRITICAL ERROR WARNING INFO DEBUG NOTSET

pil_logger = logging.getLogger("PIL")
pil_logger.setLevel(logging.INFO)

# _logger.info(f"Logger {}")
# _logger.warning(f"logger {}")
# _logger.error(f"error {}")
# _logger.debug(f"debug {}")


class Formatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def format(self, record: logging.LogRecord):
        """
        The role of this custom formatter is:
        - append filepath and lineno to logging format but shorten path to files, to make logs more clear
        - to append "./" at the begining to permit going to the line quickly with VS Code CTRL+click from terminal
        """
        s = super().format(record)
        # s = record
        pathname = Path(record.pathname).relative_to(MODULE_PATH)
        s += f" [{os.curdir}{os.sep}{pathname}:{record.lineno}]"
        return s


# def get_logs_directory():
#     def _get_logs_directory():
#         import tempfile

#         if "MIXER_USER_LOGS_DIR" in os.environ:
#             username = os.getlogin()
#             base_shared_path = Path(os.environ["MIXER_USER_LOGS_DIR"])
#             if os.path.exists(base_shared_path):
#                 return os.path.join(os.fspath(base_shared_path), username)
#             logger.error(
#                 f"MIXER_USER_LOGS_DIR env var set to {base_shared_path}, but directory does not exists. Falling back to default location."
#             )
#         return os.path.join(os.fspath(tempfile.gettempdir()), "mixer")

#     dir = _get_logs_directory()
#     if not os.path.exists(dir):
#         os.makedirs(dir)
#     return dir


# def get_log_file():
#     from mixer.share_data import share_data

#     return os.path.join(get_logs_directory(), f"mixer_logs_{share_data.run_id}.log")


# This operator requires   from bpy_extras.io_utils import ImportHelper
# See https://sinestesia.co/blog/tutorials/using-blenders-filebrowser-with-python/
class UAS_OpenFileBrowser(Operator, ImportHelper):
    bl_idname = "stampinfo.openfilebrowser"
    bl_label = "Open"
    bl_description = (
        "Open the file browser to define the image to stamp\n"
        "Relative path must be set directly in the text field and must start with ''//''"
    )

    filter_glob: StringProperty(default="*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.tga,*.bmp", options={"HIDDEN"})

    def execute(self, context):
        """Use the selected file as a stamped logo"""
        filename, extension = os.path.splitext(self.filepath)
        #   print('Selected file:', self.filepath)
        #   print('File name:', filename)
        #   print('File extension:', extension)
        bpy.context.scene.UAS_StampInfo_Settings.logoFilepath = self.filepath

        return {"FINISHED"}


class UAS_OpenExplorer(Operator):
    bl_idname = "stampinfo.openexplorer"
    bl_label = "Open Explorer"
    bl_description = "Open an Explorer window located at the render output directory"

    # wkip use icon FILEBROWSER

    def execute(self, context):
        """Open an Explorer window located at the render output directory"""

        renderPath = stamper.getInfoFileFullPath(context.scene, -1)[0]

        # cf https://stackoverflow.com/questions/281888/open-explorer-on-a-file
        import subprocess

        # subprocess.Popen(r'explorer "C:\tmp"')
        subprocess.Popen('explorer "' + renderPath + '"')

        _logger.debug(f" UAS_OpenExplorer: Open {renderPath}")

        return {"FINISHED"}


class UAS_ResetHandlers(Operator):
    bl_idname = "stampinfo.resethandlers"
    bl_label = "Reset Handlers"
    bl_description = (
        "Y if handlers are installed, N if not.\nRed if the status of the handlers is not the expected one according to\n"
        "the stateof Use Stamp Info.\nButton pressed: Reset Handlers to the expected state"
    )

    def execute(self, context):
        """Clear Compo Nodes"""
        _logger.debug(f" UAS_ResetHandlersAndCompoNodes")

        # stamper.clearInfoCompoNodes(context.scene)

        # context.scene.UAS_StampInfo_Settings.clearRenderHandlers()     # not needed cause also called in registerRenderHandlers
        context.scene.UAS_StampInfo_Settings.registerRenderHandlers()

        return {"FINISHED"}


class UAS_ResetHandlersAndCompoNodes(Operator):
    bl_idname = "stampinfo.resethandlersandcomponodes"
    bl_label = "Reset Handlers and Compo"
    bl_description = "Clear and register again the handlers and clear the Compo Nodes"

    def execute(self, context):
        """Clear Compo Nodes"""
        _logger.debug(f" UAS_ResetHandlersAndCompoNodes")

        context.scene.UAS_StampInfo_Settings.clearRenderHandlers()

        stamper.clearInfoCompoNodes(context.scene)

        context.scene.UAS_StampInfo_Settings.registerRenderHandlers()

        return {"FINISHED"}


classes = (
    stampInfoSettings.UAS_StampInfoSettings,
    Utils_LaunchRender,
    UAS_OpenFileBrowser,
    UAS_OpenExplorer,
    UAS_ResetHandlersAndCompoNodes,
    UAS_ResetHandlers,
)
# debug:
#   handlers.UAS_StampInfoCreateHandlers,
#   handlers.UAS_StampInfoClearHandlers,


def module_can_be_imported(name):
    try:
        __import__(name)
        return True
    except ModuleNotFoundError:
        return False


def register():

    display_addon_registered_version("UAS_StampInfo")

    config.initGlobalVariables()

    ###################
    # logging
    ###################

    if len(_logger.handlers) == 0:
        _logger.setLevel(logging.WARNING)
        formatter = Formatter("{asctime} {levelname[0]} {name:<36}  - {message:<80}", style="{")
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        _logger.addHandler(handler)

        # handler = logging.FileHandler(get_log_file())
        # handler.setFormatter(formatter)
        # _logger.addHandler(handler)

    ###################
    # Pillow lib installation
    ###################

    if not module_can_be_imported("PIL"):
        subprocess.run([bpy.app.binary_path_python, "-m", "pip", "install", "pillow"])

    for cls in classes:
        bpy.utils.register_class(cls)

    about.register()
    prefs.register()
    si_ui.register()

    # debug tools
    if config.uasDebug:
        debug.register()

    bpy.types.Scene.UAS_StampInfo_Settings = PointerProperty(type=stampInfoSettings.UAS_StampInfoSettings)

    # declaration of properties that will not be saved in the scene

    # stampInfoSettings.registerRenderHandlers()

    # handlers.registerPostLoadHandler()


def unregister():

    si_ui.unregister()
    prefs.unregister()
    about.unregister()

    # debug tools
    if config.uasDebug:
        debug.unregister()

    for cls in reversed(classes):
        # print(str(cls) + " being unregistered...")
        bpy.utils.unregister_class(cls)

    # clearing handlers
    # https://blender.stackexchange.com/questions/53894/how-to-avoid-multiple-running-instances-of-same-handler-function-when-running-it
    # bpy.app.handlers.render_init.clear()
    # bpy.app.handlers.render_pre.clear()
    # bpy.app.handlers.render_complete.clear()
    # bpy.app.handlers.render_cancel.clear()
    # bpy.app.handlers.render_init.remove(my_handlder)

    config.releaseGlobalVariables()
