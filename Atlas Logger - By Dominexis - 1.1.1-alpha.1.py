import os
import json
import shutil

from pathlib import Path
from enum import Enum
from typing import Dict, List, Set, Tuple

ATLAS_LOGGER_VERSION = "1.1.1-alpha.1"
FOLDER_PATH = Path(__file__).parent
PACK_FORMAT = 12


class State(Enum):
    MAIN_MENU = "Main Menu"
    SETTINGS = "Settings"
    SETTINGS_FOLDER_MODE = "Settings Folder-mode"
    RESOURCE_PACK = "Resourcepack"
    RESOURCE_PACK_NAME = "Resource pack's name"
    RESOURCE_PACK_LIST = "Resource pack list"
    FIX_RESOURCE_PACK = "Fix resource pack"
    EXIT = "Exit"


class FolderMode(Enum):
    SINGLES = "Singles"
    FOLDERS = "Folders"


class Program:
    __slots__ = (
        'state',
        'folder_mode',
        'message',
        'resource_pack_file_name',
        'pack_entry_type',
        'pack_directory')
    state: State
    """State of the program"""
    folder_mode: FolderMode
    """Current mode of the folder"""
    message: str
    """Message to send to screen"""
    resource_pack_file_name: str
    """Resource pack file string"""
    pack_entry_type: State
    """Type of entry given by user"""
    pack_directory: Path
    """FILEPATH + resource_pack"""

    def __init__(self):
        STATE_HANDLER = {
            # Main menu
            State.MAIN_MENU: self.__handle_main_menu,
            # Settings
            State.SETTINGS: self.__handle_settings,
            State.SETTINGS_FOLDER_MODE: self.__handle_settings_folder_mode,
            # Resource pack menu
            State.RESOURCE_PACK: self.__handle_resource_pack,
            State.RESOURCE_PACK_NAME: self.__handle_resource_pack_name,
            State.RESOURCE_PACK_LIST: self.__handle_resource_pack_list,
            State.FIX_RESOURCE_PACK: self.__handle_fix_resource_pack,
            # Exit
            State.EXIT: exit
        }

        self.state = State.MAIN_MENU
        self.folder_mode = FolderMode.SINGLES
        self.message = ""
        self.resource_pack_file_name = ""
        self.pack_entry_type = State.RESOURCE_PACK_NAME

        while True:
            STATE_HANDLER[self.state]()

    def __handle_main_menu(self):
        while True:
            # Display menu
            display_title()
            display_settings(self.folder_mode)
            print(""" Actions:
  1) Fix resource pack
  2) Change settings
  3) Exit program
            """)

            # Process action
            action, error, self.message = check_action(
                input(self.message + " Action: "), 1, 3)
            if error:
                continue
            self.state = {
                1: State.RESOURCE_PACK,
                2: State.SETTINGS,
                3: State.EXIT
            }[action]
            self.message = ""
            return

    def __handle_settings(self):
        while True:
            # Display settings menu
            display_title()
            print(f""" Edit settings:
  0) Go back
  1) Folder Mode: {self.folder_mode.value}
""")

            # Process action
            action, error, self.message = check_action(
                input(self.message + " Action: "), 0, 1)
            if error:
                continue
            self.state = [
                State.MAIN_MENU,
                State.SETTINGS_FOLDER_MODE
            ][action]
            self.message = ""
            return

    def __handle_settings_folder_mode(self):
        while True:
            # Display options
            print("""
 Folder Mode:
  1) Singles - Processes each file individually. This prevents unwanted textures from getting through, but makes it harder to edit.
  2) Folders - Logs entire directories. This makes it easier to edit, but can include unwanted files in the block atlas.
""")

            # Process action
            action, error, self.message = check_action(
                input(self.message + " Folder Mode: "), 0, 2)
            if error:
                continue
            if 1 <= action <= 2:
                self.folder_mode = {
                    1: FolderMode.SINGLES,
                    2: FolderMode.FOLDERS
                }[action]
            self.state = State.SETTINGS
            self.message = ""
            return

    def __handle_resource_pack(self):
        while True:
            # Display resource pack menu
            display_title()
            print(""" Fix resource pack:
  0) Go back
  1) Fix resource pack by name
  2) Fix resource pack from a list
""")

            # Process action
            action, error, self.message = check_action(
                input(self.message + " Action: "), 0, 2)
            if error:
                continue
            self.state = [
                State.MAIN_MENU,
                State.RESOURCE_PACK_NAME,
                State.RESOURCE_PACK_LIST
            ][action]
            return

    def __handle_resource_pack_name(self):
        while True:
            # Display menu
            display_title()
            print(
                ' Fix resource pack by name. Enter "0" to go back.\n'
            )

            # Set entry type
            self.pack_entry_type = State.RESOURCE_PACK_NAME

            # Process action
            file_name, error, self.message = check_file(
                input(self.message + " Resource pack: "))
            if file_name == "0":
                self.message = ""
                self.state = State.RESOURCE_PACK
                return
            if error:
                continue
            self.state = State.FIX_RESOURCE_PACK
            self.resource_pack_file_name = file_name
            return

    def __handle_resource_pack_list(self):
        while True:
            # Display menu
            display_title()
            print(""" Fix resource pack:
  0) Go back""")

            # Set entry type
            self.pack_entry_type = State.RESOURCE_PACK_LIST

            # List off resource packs
            packs: List[str] = []
            for path in FOLDER_PATH.iterdir():
                if (
                    # Folder with pack.mcmeta
                    (path.is_dir() and (path / 'pack.mcmeta').is_file())
                    or
                    # File with .zip suffix
                    (path.is_file() and path.suffix == ".zip")
                ):
                    packs.append(path.name)

            for index, pack in enumerate(packs):
                print(f"  {index+1}) {pack}")
            print()

            # Process action
            action, error, self.message = check_action(
                input(self.message + " Action: "), 0, len(packs))
            if error:
                continue
            if action == 0:
                self.state = State.RESOURCE_PACK
                return
            self.state = State.FIX_RESOURCE_PACK
            self.resource_pack_file_name = packs[action - 1]
            return

    def __handle_fix_resource_pack(self):
        # Unzip pack if it is a zip
        is_zip = Path(self.resource_pack_file_name).suffix == ".zip"
        # Whether the file is a zip
        if is_zip:
            (FOLDER_PATH / "atlas_logger_temp").mkdir(exist_ok=True)
            shutil.unpack_archive(
                FOLDER_PATH / self.resource_pack_file_name,
                FOLDER_PATH / "atlas_logger_temp",
                "zip"
            )
            self.pack_directory = FOLDER_PATH / "atlas_logger_temp"
        else:
            self.pack_directory = FOLDER_PATH / self.resource_pack_file_name

        # Check that needed folders/directories exist
        for test in ("pack.mcmeta", "assets"):
            if not (self.pack_directory / test).exists():
                self.message = f" Error: {test} does not exist!"
                self.state = self.pack_entry_type
                return

        # Check if there is already an atlas file
        if (self.pack_directory / "assets" / "minecraft" /
                "atlases" / "block.json").exists():
            while True:
                print("""
 "minecraft:atlases/blocks.json" already exists, do you wish to overwrite it?
  0) No
  1) Yes
""")
                # Process action
                action, error, self.message = check_action(
                    input(self.message + " Action: "), 0, 1)
                if error:
                    continue
                if action == 0:
                    self.state = self.pack_entry_type
                    self.remove_temp_directory()
                    return
                break

        # Update resource pack
        self.update_resource_pack()

        # Zip up folder
        if is_zip:
            # len(".zip") = 4
            shutil.make_archive(
                (
                    FOLDER_PATH /
                    self.resource_pack_file_name[:-4]
                ).as_posix(),
                "zip",
                FOLDER_PATH / "atlas_logger_temp"
            )

        self.remove_temp_directory()
        self.state = self.pack_entry_type
        return

    def remove_temp_directory(self):
        if (FOLDER_PATH / "atlas_logger_temp").exists():
            shutil.rmtree(FOLDER_PATH / "atlas_logger_temp")

    def update_resource_pack(self):
        self.message = ""

        # Change pack format in pack.mcmeta
        try:
            with (self.pack_directory / "pack.mcmeta").open("r", encoding="utf-8") as file:
                contents = json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            self.message += " Warning: pack.mcmeta is not formatted correctly!\n"
        else:
            if contents["pack"]["pack_format"] < PACK_FORMAT:
                contents["pack"]["pack_format"] = PACK_FORMAT
            with (self.pack_directory / "pack.mcmeta").open("w", encoding="utf-8") as file:
                contents = json.dump(contents, file, indent=4)

        textures = self.get_texture_set()

        if textures:
            self.create_atlas_file(textures)

        self.message += " Atlas successfully compiled!\n"

    def get_texture_set(self) -> Set[str]:
        textures: Set[str] = set()

        # Iterate through namespaces
        for namespace_path in (self.pack_directory / "assets").iterdir():
            if not namespace_path.is_dir():
                continue

            # Skip namespace if it has no models
            if not (namespace_path / "models").exists():
                continue

            # Iterate through models
            for file_path in (namespace_path / "models").glob("**/*.json"):
                model_id = file_path.name

                try:
                    with file_path.open("r", encoding="utf-8") as file:
                        model_json: Dict[str, Dict[str, str]] = json.load(file)
                except json.JSONDecodeError:
                    self.message += f" Warning: {model_id} is not properly formatted!\n"
                    continue

                if "textures" not in model_json:
                    continue

                if not isinstance(model_json["textures"], dict):
                    self.message += f" Warning: {model_id} has an incorrect texture listed!\n"
                    continue

                # Log any textures that exist
                for key, texture in model_json["textures"].items():
                    if not (isinstance(key, str) and isinstance(texture, str)):
                        self.message += f" Warning: {model_id} has an incorrect texture listed!\n"
                        continue

                    if ":" not in texture:
                        texture = "minecraft:" + texture

                    # Add to list if it isn't in the block or item folder
                    # and isn't already on the list
                    if (
                        (
                            "/" not in texture
                            or
                            texture.split(":")[1].split(
                            "/")[0] not in {"block", "item"}
                        )
                        and
                        texture not in textures
                    ):
                        textures.add(texture)

        return textures

    def create_atlas_file(self, textures: Set[str]):
        # Compile set of folders
        folders: Set[str] = set()
        if self.folder_mode == FolderMode.FOLDERS:
            new_textures: Set[str] = set()
            for texture in textures:
                # Get folder name
                if "/" in texture:
                    folder = texture.split(":")[1].split("/")[0]
                    if folder not in folders:
                        folders.add(folder)
                else:
                    new_textures.add(texture)

            textures = new_textures

        # Compile sources
        sources: List[Dict[str, str]] = []
        for folder in folders:
            # Add source
            sources.append(
                {
                    "type": "directory",
                    "source": folder,
                    "prefix": folder + "/"
                }
            )
        for texture in textures:
            # Add source
            sources.append(
                {
                    "type": "single",
                    "resource": texture
                }
            )

        # Create atlas file
        (self.pack_directory / "assets" /
         "minecraft" / "atlases").mkdir(exist_ok=True)
        with (self.pack_directory / "assets" / "minecraft" / "atlases" / "blocks.json").open("w", encoding="utf-8") as file:
            json.dump({"sources": sources}, file, indent=4)


# Define check functions
def check_action(action_str: str, minimum: int,
                 maximum: int) -> Tuple[int, bool, str]:
    """
    Check if action is valid

    :param action_str: User given string on action
    :param minimum: Minimum numuber action can be
    :param maximum: Maximum numuber action can be
    :return: Tuple of action, whether there is an error, and message to display
    """
    if not action_str.isnumeric():
        return 0, True, " Error: Input must be a number!\n"

    action = int(action_str)

    if not (minimum <= action <= maximum):
        return action, True, " Error: Input is out of range!\n"

    return action, False, ""


def check_file(file_name: str) -> Tuple[str, bool, str]:
    """
    Check if file name is valid

    :param file_name: User given string on file_name
    :return: Tuple of file_name, whether there is an error, and message to display
    """
    if not file_name:
        return file_name, True, " Error: Cannot use an empty string!\n"

    # Halt if there are any illegal characters in the string
    for char in ("/", "\\", "?", "<", ">", ":", "\"", "|"):
        if char in file_name:
            return file_name, True, " Error: Cannot use illegal characters in file names!\n"

    if not (FOLDER_PATH / file_name).exists():
        return file_name, True, " Error: Resource pack does not exist!\n"

    return file_name, False, ""


def display_title():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")
    print(f"\n\n Atlas Logger - By Dominexis - {ATLAS_LOGGER_VERSION}\n")


def display_settings(folder_mode: FolderMode):
    print(f""" Settings:
  Folder Mode: {folder_mode.value}
""")


# Execute program
if __name__ == "__main__":
    Program()
