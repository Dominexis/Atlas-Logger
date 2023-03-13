# Import things

import os
import json
import shutil
import sys
from pathlib import Path
from enum import Enum



# Check that correct Python version is running

if not (
    (sys.version_info[0] == 3 and sys.version_info[1] >= 9)
    or
    (sys.version_info[0] > 3)
):
    print("\n\n ERROR: Atlas Logger requires Python 3.9 or newer!")
    input()
    exit()



# Initialize variables

ATLAS_LOGGER_VERSION = "1.2.1"
PROGRAM_PATH = Path(__file__).parent
PACK_FORMAT = 12

class State(Enum):
    """Enumeration which stores the IDs of the program states.

    Using plain strings to store these sorts of values risks typos breaking the system.

    An enumeration ensures that the values are accurate because the IDE can flag typos."""

    MAIN_MENU = "main_menu"
    SETTINGS = "settings"
    SETTINGS_FOLDER_MODE = "settings_folder_mode"
    RESOURCE_PACK_MENU = "resource_pack_menu"
    RESOURCE_PACK_NAME = "resource_pack_name"
    RESOURCE_PACK_LIST = "resource_pack_list"
    FIX_RESOURCE_PACK = "fix_resource_pack"
    EXIT = "exit"

class FolderMode(Enum):
    """Enumeration which stores the possible values of the folder mode.

    Using plain strings to store these sorts of values risks typos breaking the system.

    An enumeration ensures that the values are accurate because the IDE can flag typos."""

    SINGLES = "Singles"
    FOLDERS = "Folders"



# Define program class

class Program:
    """The main class which runs the program.

    Most of the program is handled by a single class so that object variables
    can be accessed by the wide array of functions without having to make global variable calls."""

    __slots__ = (
        "state",
        "folder_mode",
        "message",
        "resource_pack_file_name",
        "pack_entry_type",
        "pack_directory"
    )

    state: State
    """State of the program."""
    folder_mode: FolderMode
    """Folder mode, determines whether it lists off folders or individual files."""
    message: str
    """Message to display on the terminal."""
    resource_pack_file_name: str
    """Name of the resource pack."""
    pack_entry_type: State
    """Whether the user is fixing the pack by name or by list."""
    pack_directory: Path
    """Full directory of the resource pack."""

    def __init__(self):
        STATE_HANDLER = {
            # Main menu
            State.MAIN_MENU: self.__handle_main_menu,
            # Settings
            State.SETTINGS: self.__handle_settings,
            State.SETTINGS_FOLDER_MODE: self.__handle_settings_folder_mode,
            # Resource pack menu
            State.RESOURCE_PACK_MENU: self.__handle_resource_pack_menu,
            State.RESOURCE_PACK_NAME: self.__handle_resource_pack_name,
            State.RESOURCE_PACK_LIST: self.__handle_resource_pack_list,
            State.FIX_RESOURCE_PACK: self.__handle_fix_resource_pack,
            # Exit
            State.EXIT: exit
        }

        # Initialize variables
        self.state = State.MAIN_MENU
        self.folder_mode = FolderMode.SINGLES
        self.message = ""
        self.resource_pack_file_name = ""
        self.pack_entry_type = State.RESOURCE_PACK_NAME

        # Execute state
        while True:
            STATE_HANDLER[self.state]()

    def __handle_main_menu(self):
        # Display menu
        display_title()
        display_settings(self.folder_mode)
        print_lines(
            " Actions:",
            "  1) Fix resource pack",
            "  2) Change settings",
            "  3) Exit program",
            ""
        )

        # Process action
        action, error, self.message = check_action(
            input(self.message + " Action: "), 1, 3)
        if error:
            return
        self.state = {
            1: State.RESOURCE_PACK_MENU,
            2: State.SETTINGS,
            3: State.EXIT
        }[action]
        self.message = ""
        return

    def __handle_settings(self):
        # Display settings menu
        display_title()
        print_lines(
            " Edit settings:",
            "  0) Go back",
            f"  1) Folder Mode: {self.folder_mode.value}",
            ""
        )

        # Process action
        action, error, self.message = check_action(
            input(self.message + " Action: "), 0, 1)
        if error:
            return
        self.state = [
            State.MAIN_MENU,
            State.SETTINGS_FOLDER_MODE
        ][action]
        self.message = ""
        return

    def __handle_settings_folder_mode(self):
        # Display options
        print_lines(
            "",
            " Folder Mode:",
            "  1) Singles - Processes each file individually. This prevents unwanted textures from getting through, but makes it harder to edit.",
            "  2) Folders - Logs entire directories. This makes it easier to edit, but can include unwanted files in the block atlas.",
            ""
        )

        # Process action
        action, error, self.message = check_action(
            input(self.message + " Folder Mode: "), 0, 2)
        if error:
            return
        if 1 <= action <= 2:
            self.folder_mode = {
                1: FolderMode.SINGLES,
                2: FolderMode.FOLDERS
            }[action]
        self.state = State.SETTINGS
        self.message = ""
        return

    def __handle_resource_pack_menu(self):
        # Display resource pack menu
        display_title()
        print_lines(
            " Fix resource pack:",
            "  0) Go back",
            "  1) Fix resource pack by name",
            "  2) Fix resource pack from a list",
            ""
        )

        # Process action
        action, error, self.message = check_action(
            input(self.message + " Action: "), 0, 2)
        if error:
            return
        self.state = [
            State.MAIN_MENU,
            State.RESOURCE_PACK_NAME,
            State.RESOURCE_PACK_LIST
        ][action]
        return

    def __handle_resource_pack_name(self):
        # Display menu
        display_title()
        print(
            ' Fix resource pack by name. Enter "0" to go back.\n'
        )

        # Set entry type
        self.pack_entry_type = State.RESOURCE_PACK_NAME

        # Process action
        action, error, self.message = check_file(input(self.message + " Resource pack: "))
        if action == "0":
            self.message = ""
            self.state = State.RESOURCE_PACK_MENU
            return
        if error:
            return
        self.state = State.FIX_RESOURCE_PACK
        self.resource_pack_file_name = action
        return

    def __handle_resource_pack_list(self):
        # Display menu
        display_title()
        print_lines(
            " Fix resource pack:",
            "  0) Go back"
        )

        # Set entry type
        self.pack_entry_type = State.RESOURCE_PACK_LIST

        # List off resource packs
        packs: list[str] = []
        for path in PROGRAM_PATH.iterdir():
            if (
                # Is a folder resource pack with pack.mcmeta
                (path.is_dir() and (path / "pack.mcmeta").is_file())
                or
                # Is a ZIP file
                (path.is_file() and path.suffix == ".zip")
            ):
                packs.append(path.name)

        # Print off resource packs
        for index, pack in enumerate(packs):
            print(f"  {index+1}) {pack}")
        print()

        # Process action
        action, error, self.message = check_action(
            input(self.message + " Action: "), 0, len(packs))
        if error:
            return
        if action == 0:
            self.state = State.RESOURCE_PACK_MENU
            return
        self.state = State.FIX_RESOURCE_PACK
        self.resource_pack_file_name = packs[action - 1]
        return

    def __handle_fix_resource_pack(self):
        # Unzip pack if it is a zip
        zip_bool = Path(self.resource_pack_file_name).suffix == ".zip"
        if zip_bool:
            (PROGRAM_PATH / "atlas_logger_temp").mkdir(exist_ok=True)
            shutil.unpack_archive(
                PROGRAM_PATH / self.resource_pack_file_name,
                PROGRAM_PATH / "atlas_logger_temp",
                "zip"
            )
            self.pack_directory = PROGRAM_PATH / "atlas_logger_temp"
        else:
            self.pack_directory = PROGRAM_PATH / self.resource_pack_file_name

        # Check that needed folders/directories exist
        for test in ["pack.mcmeta", "assets"]:
            if not (self.pack_directory / test).exists():
                self.message = f' ERROR: "{test}" does not exist!'
                self.state = self.pack_entry_type
                return

        # Check if there is already an atlas file
        if (self.pack_directory / "assets" / "minecraft" / "atlases" / "blocks.json").exists():
            while True:
                # Display menu
                print_lines(
                    "",
                    ' "minecraft:atlases/blocks.json" already exists, do you wish to overwrite it?',
                    "  0) No",
                    "  1) Yes",
                    ""
                )

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
        if zip_bool:
            shutil.make_archive(
                PROGRAM_PATH / self.resource_pack_file_name[:-4],
                "zip",
                PROGRAM_PATH / "atlas_logger_temp"
            )

        # Return
        self.remove_temp_directory()
        self.state = self.pack_entry_type
        return

    def remove_temp_directory(self):
        """A temporary directory is used as the destination for zipped resource packs.
        This method removes it."""
        # Remove temp directory
        if (PROGRAM_PATH / "atlas_logger_temp").exists():
            shutil.rmtree(PROGRAM_PATH / "atlas_logger_temp")

    def update_resource_pack(self):
        """Updates the resource pack by gathering the texture list from the models and creating the atlas file."""
        # Reset message
        self.message = ""

        # Change pack format in pack.mcmeta
        try:
            with (self.pack_directory / "pack.mcmeta").open("r", encoding="utf-8") as file:
                contents: dict[str, dict[str, str]] = json.loads(file.read().encode(encoding="utf-8", errors="backslashreplace"))
        except (json.JSONDecodeError, FileNotFoundError):
            self.message += " WARNING: pack.mcmeta is not formatted correctly!\n"
        else:
            if contents["pack"]["pack_format"] < PACK_FORMAT:
                contents["pack"]["pack_format"] = PACK_FORMAT
            with (self.pack_directory / "pack.mcmeta").open("w", encoding="utf-8") as file:
                json.dump(contents, file, indent=4)

        # Get textures list
        textures = self.get_texture_list()

        # Create atlas file
        if (self.pack_directory / "assets" / "minecraft" / "atlases" / "blocks.json").exists():
            os.remove(self.pack_directory / "assets" / "minecraft" / "atlases" / "blocks.json")
        if textures:
            self.create_atlas_file(textures)

        # Send message
        self.message += " Atlas successfully compiled!\n"

    def get_texture_list(self) -> list[str]:
        """Gathers up the list of textures from all block and item models and puts them in a list."""
        # Initialize list of textures
        textures: list[str] = []

        # Iterate through namespaces
        for namespace in (self.pack_directory / "assets").iterdir():
            # Skip namespace if it doesn't exist or has no models
            if not namespace.is_dir():
                continue
            if not (namespace / "models").exists():
                continue

            # Iterate through models
            for file_path in (namespace / "models").glob("**/*.json"):
                # Set model ID
                model_id = file_path.name

                # Open file
                try:
                    with file_path.open("r", encoding="utf-8") as file:
                        model_json: dict[str, dict[str, str]] = json.loads(file.read().encode(encoding="utf-8", errors="backslashreplace"))
                except json.JSONDecodeError:
                    self.message += f" WARNING: {model_id} is not properly formatted!\n"
                    continue

                # Skip if textures don't exist
                if not "textures" in model_json:
                    continue

                # Skip if textures isn't a compound
                if not isinstance(model_json["textures"], dict):
                    self.message += f" WARNING: {model_id} has incorrectly listed textures!\n"
                    continue

                # Log any textures that exist
                for key, texture in model_json["textures"].items():
                    if not (isinstance(key, str) and isinstance(texture, str)):
                        self.message += f" WARNING: {model_id} has an incorrect texture listed!\n"
                        continue

                    # Skip if the texture is a reference
                    if texture[0] == "#":
                        continue

                    # Apply namespace to it if it doesn't exist
                    if ":" not in texture:
                        texture = "minecraft:" + texture

                    # Add to list if it isn't in the block or item folder
                    # and isn't already on the list
                    if (
                        (
                            "/" not in texture
                            or
                            texture.split(":")[1].split("/")[0] not in ["block", "item"]
                        )
                        and
                        texture not in textures
                    ):
                        textures.append(texture)

        return textures

    def create_atlas_file(self, textures: list[str]):
        """Creates the atlas file from the list of textures."""
        # Compile list of folders
        folders: list[str] = []
        if self.folder_mode == FolderMode.FOLDERS:
            new_textures: list[str] = []
            for texture in textures:
                # Get folder name
                if "/" in texture:
                    folder = texture.split(":")[1].split("/")[0]
                    if folder not in folders:
                        folders.append(folder)
                else:
                    new_textures.append(texture)
            # Push textures
            textures = new_textures

        # Compile sources
        sources: list[dict[str, str]] = []
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
        (self.pack_directory / "assets" / "minecraft" / "atlases").mkdir(parents=True, exist_ok=True)
        with (self.pack_directory / "assets" / "minecraft" / "atlases" / "blocks.json").open("w", encoding="utf-8") as file:
            json.dump({"sources": sources}, file, indent=4)

            





# Check functions

def check_action(action_string: str, minimum: int, maximum: int) -> tuple[int, bool, str]:
    """Checks if a numeric action command is a number and within range."""
    # Halt if string is not a number
    if not action_string.isnumeric():
        return 0, True, " ERROR: Input must be a number!\n"
    action = int(action_string)

    # Halt if number is out of range
    if not minimum <= action <= maximum:
        return action, True, " ERROR: Input is out of range!\n"
    return action, False, ""

def check_file(file_name: str) -> tuple[str, bool, str]:
    """Checks if a user-inputted string is a valid file directory string."""
    # Halt if string is empty
    if len(file_name) == 0:
        return file_name, True, " ERROR: Cannot use an empty string!\n"

    # Halt if there are any illegal characters in the string
    for char in ["/", "\\", "?", "<", ">", ":", "\"", "|"]:
        if char in file_name:
            return file_name, True, " ERROR: Cannot use illegal characters in file names!\n"

    # Halt if the resource pack does not exist
    if not (PROGRAM_PATH / file_name).exists():
        return file_name, True, " ERROR: Resource pack does not exist!\n"
    return file_name, False, ""



# Display functions

def display_title():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")
    print_lines(
        "\n",
        f" Atlas Logger - By Dominexis - {ATLAS_LOGGER_VERSION}",
        ""
    )

def display_settings(folder_mode: FolderMode):
    """Displays the title on the terminal."""
    print_lines(
        " Settings:",
        f"  Folder Mode: {folder_mode.value}",
        ""
    )

def print_lines(*lines: str):
    """Prints several lines on the terminal from a series of arguments."""
    print("\n".join(lines))



# Run program

if __name__ == "__main__":
    Program()