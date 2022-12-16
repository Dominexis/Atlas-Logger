# Import things

import os
import json
import shutil



# Initialize variables

global atlas_logger_version
global global_path
global pack_format
atlas_logger_version = "1.1.0"
global_path = os.path.dirname(os.path.realpath(__file__))
pack_format = 12



# Define program class

class Program:
    def __init__(self):
        # Initialize variables
        self.state = "main_menu"
        self.folder_mode = "Singles"
        self.message = ""
        self.rp = ""
        self.pack_entry_type = "resource_pack_name"

        # Execute state
        while True:
            # Main menu
            if self.state == "main_menu":
                self.main_menu()

            # Settings
            elif self.state == "settings":
                self.settings()
            elif self.state == "settings_folder_mode":
                self.settings_folder_mode()

            # Resource pack menu
            elif self.state == "resource_pack":
                self.resource_pack()
            elif self.state == "resource_pack_name":
                self.resource_pack_name()
            elif self.state == "resource_pack_list":
                self.resource_pack_list()
            elif self.state == "fix_resource_pack":
                self.fix_resource_pack()

            # Exit
            elif self.state == "exit":
                exit()
            else:
                self.state = "main_menu"
                self.message = " Error: Invalid state! Sending back to main menu.\n"

    def main_menu(self):
        while True:
            # Display menu
            Display.clear()
            Display.title()
            Display.settings(self.folder_mode)
            print(
                " Actions:\n" +
                "  1) Fix resource pack\n" +
                "  2) Change settings\n" +
                "  3) Exit program\n"
            )

            # Process action
            action, error, self.message = Check.action(input(self.message + " Action: "), 1, 3)
            if error:
                continue
            self.state = ["resource_pack", "settings", "exit"][action - 1]
            self.message = ""
            return

    def settings(self):
        while True:
            # Display settings menu
            Display.clear()
            Display.title()
            print(
                " Edit settings:\n" +
                "  0) Go back\n" +
                "  1) Folder Mode: " + self.folder_mode + "\n"
            )

            # Process action
            action, error, self.message = Check.action(input(self.message + " Action: "), 0, 1)
            if error:
                continue
            self.state = ["main_menu", "settings_folder_mode"][action]
            self.message = ""
            return

    def settings_folder_mode(self):
        while True:
            # Display options
            print(
                "\n Folder Mode:\n" +
                "  1) Singles - Processes each file individually. This prevents unwanted textures from getting through, but makes it harder to edit.\n" +
                "  2) Folders - Logs entire directories. This makes it easier to edit, but can include unwanted files in the block atlas.\n"
            )

            # Process action
            action, error, self.message = Check.action(input(self.message + " Folder Mode: "), 0, 2)
            if error:
                continue
            if 1 <= action <= 2:
                self.folder_mode = ["Singles", "Folders"][action - 1]
            self.state = "settings"
            self.message = ""
            return

    def resource_pack(self):
        while True:
            # Display resource pack menu
            Display.clear()
            Display.title()
            print(
                " Fix resource pack:\n" +
                "  0) Go back\n" +
                "  1) Fix resource pack by name\n" +
                "  2) Fix resource pack from a list\n"
            )

            # Process action
            action, error, self.message = Check.action(input(self.message + " Action: "), 0, 2)
            if error:
                continue
            self.state = ["main_menu", "resource_pack_name", "resource_pack_list"][action]
            return

    def resource_pack_name(self):
        while True:
            # Display menu
            Display.clear()
            Display.title()
            print(
                " Fix resource pack by name. Enter \"0\" to go back.\n"
            )

            # Set entry type
            self.pack_entry_type = "resource_pack_name"

            # Process action
            action, error, self.message = Check.file(input(self.message + " Resource pack: "))
            if action == "0":
                self.message = ""
                self.state = "resource_pack"
                return
            if error:
                continue
            self.state = "fix_resource_pack"
            self.rp = action
            return

    def resource_pack_list(self):
        while True:
            # Display menu
            Display.clear()
            Display.title()
            print(
                " Fix resource pack:\n" +
                "  0) Go back"
            )

            # Set entry type
            self.pack_entry_type = "resource_pack_list"

            # List off resource packs
            packs = []
            for subdir, dirs, files in os.walk(os.path.join(global_path)):
                # Iterate through directories
                for dir in dirs:
                    if os.path.exists(os.path.join(global_path, dir, "pack.mcmeta")):
                        packs.append(dir)
                # Iterate through files
                for file in files:
                    if len(file.split(".")) >= 2 and file.split(".")[-1] == "zip":
                        packs.append(file)
                break
            for i in range(len(packs)):
                pack = packs[i]
                print("  " + str(i+1) + ") " + pack)
            print("")

            # Process action
            action, error, self.message = Check.action(input(self.message + " Action: "), 0, len(packs))
            if error:
                continue
            if action == 0:
                self.state = "resource_pack"
                return
            self.state = "fix_resource_pack"
            self.rp = packs[action - 1]
            return

    def fix_resource_pack(self):
        # Unzip pack if it is a zip
        self.zip_bool = len(self.rp.split(".")) >= 2 and self.rp.split(".")[-1] == "zip"
        if self.zip_bool:
            if not os.path.exists(os.path.join(global_path, "atlas_logger_temp")):
                os.makedirs(os.path.join(global_path, "atlas_logger_temp"))
            shutil.unpack_archive(os.path.join(global_path, self.rp), os.path.join(global_path, "atlas_logger_temp"), "zip")
            self.pack_directory = os.path.join(global_path, "atlas_logger_temp")
        else:
            self.pack_directory = os.path.join(global_path, self.rp)

        # Check that needed folders/directories exist
        for test in ["pack.mcmeta", "assets"]:
            if not os.path.exists(os.path.join(self.pack_directory, test)):
                self.message = " Error: " + test + " does not exist!"
                self.state = self.pack_entry_type
                return

        # Check if there is already an atlas file
        if os.path.exists(os.path.join(self.pack_directory, "assets", "minecraft", "atlases", "blocks.json")):
            while True:
                # Display menu
                print(
                    "\n \"minecraft:atlases/blocks.json\" already exists, do you wish to overwrite it?\n" +
                    "  0) No\n" +
                    "  1) Yes\n"
                )

                # Process action
                action, error, self.message = Check.action(input(self.message + " Action: "), 0, 1)
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
        if self.zip_bool:
            shutil.make_archive(os.path.join(global_path, self.rp[:-4]), "zip", os.path.join(global_path, "atlas_logger_temp"))

        # Return
        self.remove_temp_directory()
        self.state = self.pack_entry_type
        return

    def remove_temp_directory(self):
        # Remove temp directory
        if os.path.exists(os.path.join(global_path, "atlas_logger_temp")):
            shutil.rmtree(os.path.join(global_path, "atlas_logger_temp"))

    def update_resource_pack(self):
        # Reset message
        self.message = ""

        # Change pack format in pack.mcmeta
        try:
            with open(os.path.join(self.pack_directory, "pack.mcmeta"), "r", encoding="utf-8") as f:
                contents = json.loads(f.read().encode(encoding="utf-8"))
            if contents["pack"]["pack_format"] < pack_format:
                contents["pack"]["pack_format"] = pack_format
            with open(os.path.join(self.pack_directory, "pack.mcmeta"), "w", encoding="utf-8") as f:
                f.write( json.dumps(contents, indent = 4) )
        except:
            self.message += " Warning: pack.mcmeta is not formatted correctly!\n"

        # Get textures list
        textures = self.get_texture_list()

        # Create atlas file
        if len(textures) > 0:
            self.create_atlas_file(textures)

        # Send message
        self.message += " Atlas successfully compiled!\n"

    def get_texture_list(self):
        # Get list of namespaces
        for subdir, dirs, files in os.walk(os.path.join(self.pack_directory, "assets")):
            namespaces = dirs.copy()
            break

        # Initialize list of textures
        textures = []

        # Iterate through namespaces
        for namespace in namespaces:
            # Skip namespace if it has no models
            if not os.path.exists(os.path.join(self.pack_directory, "assets", namespace, "models")):
                continue

            # Iterate through models
            for subdir, dirs, files in os.walk(os.path.join(self.pack_directory, "assets", namespace, "models")):
                # Iterate through model files
                for file in files:
                    # Set model ID
                    model_id = os.path.join(subdir, file)[len(self.pack_directory) + 1:]

                    # Skip file if not a JSON file
                    if not (len(file.split(".")) >= 2 and file.split(".")[-1] == "json"):
                        continue

                    # Open file
                    try:
                        with open(os.path.join(subdir, file), "r", encoding="utf-8") as f:
                            model = json.loads(f.read().encode(encoding="utf-8"))
                    except:
                        self.message += " Warning: " + model_id + " is not properly formatted!\n"
                        continue

                    # Skip if textures don't exist
                    if not "textures" in model:
                        continue

                    # Log any textures that exist
                    for key in model["textures"].keys():
                        texture = model["textures"][key]
                        # Apply namespace to it if it doesn't exist
                        try:
                            if ":" not in texture:
                                texture = "minecraft:" + texture
                        except:
                            self.message += " Warning: " + model_id + " has an incorrect texture listed!\n"
                            continue

                        # Add to list if it isn't in the block or item folder and isn't already on the list
                        if ( texture.split(":")[1].split("/")[0] not in ["block", "item"] or "/" not in texture ) and texture not in textures:
                            textures.append(texture)
        # Return
        return textures

    def create_atlas_file(self, textures):
        # Compile list of folders
        folders = []
        if self.folder_mode == "Folders":
            new_textures = []
            for texture in textures:
                # Get folder name
                if "/" in texture:
                    folder = texture.split(":")[1].split("/")[0]
                    if folder not in folders:
                        folders.append(folder)
                else:
                    new_textures.append(texture)
            # Push textures
            textures = new_textures.copy()

        # Compile sources
        sources = []
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
        if not os.path.exists(os.path.join(self.pack_directory, "assets", "minecraft", "atlases")):
            os.makedirs(os.path.join(self.pack_directory, "assets", "minecraft", "atlases"))
        with open(os.path.join(self.pack_directory, "assets", "minecraft", "atlases", "blocks.json"), "w", encoding="utf-8") as file:
            file.write( json.dumps({"sources": sources}, indent = 4) )

            





# Define check class

class Check:

    @staticmethod
    def action(string, minumum, maximum):
        # Halt if string contains non-number characters
        try:
            action = int(string)
        except:
            return 0, True, " Error: Input must be a number!\n"
        else:
            if minumum <= action <= maximum:
                return action, False, ""
            return action, True, " Error: Input is out of range!\n"

    @staticmethod
    def file(string):
        # Halt if string is empty
        if len(string) == 0:
            return string, True, " Error: Cannot use an empty string!\n"
        # Halt if there are any illegal characters in the string
        for char in ["/", "\\", "?", "<", ">", ":", "\"", "|"]:
            if char in string:
                return string, True, " Error: Cannot use illegal characters in file names!\n"
        # Halt if the resource pack does not exist
        if not os.path.exists(os.path.join(global_path, string)):
            return string, True, " Error: Resource pack does not exist!\n"
        # Return
        return string, False, ""



# Define display class

class Display:

    @staticmethod
    def clear():
        os.system("cls") if os.name == "nt" else os.system("clear")
        print("\n")

    @staticmethod
    def title():
        print( " Atlas Logger - By Dominexis - " + atlas_logger_version + "\n" )

    @staticmethod
    def settings(folder_mode):
        print(
            " Settings:" +
            "\n  Folder Mode: " + folder_mode + "\n"
        )



# Execute program

Program()