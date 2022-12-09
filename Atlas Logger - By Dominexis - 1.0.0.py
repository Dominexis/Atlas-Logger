# Import things

import os
import json



# Initialize variables

global_path = os.path.dirname(os.path.realpath(__file__))
atlas_logger_version = "1.0.0"

folder_mode = "Singles"

error = False
message = ""



# Define functions

def clear():
    os.system("cls") if os.name == "nt" else os.system("clear")
def action_check(string, minumum, maximum):
    # Halt if string contains non-number characters
    try:
        action = int(string)
    except:
        return 0, True, " Error: Input must be a number!\n"
    else:
        if minumum <= action and action <= maximum:
            return action, False, ""
        else:
            return 0, True, " Error: Input is out of range!\n"
def file_check(string):
    # Halt if string is empty
    if len(string) == 0:
        return "", True, " Error: Cannot use an empty string!\n"
    # Halt if there are any illegal characters in the string
    for char in ["/", "\\", "?", "<", ">", ":", "\"", "|"]:
        if char in string:
            return "", True, " Error: Cannot use illegal characters in file names!\n"
    # Halt if the resource pack does not exist
    if not os.path.exists(os.path.join(global_path, string)):
        return "", True, " Error: Resource pack does not exist!\n"
    # Return
    return string, False, ""




while True:
    # Display menu
    clear()
    print(
        "\n Atlas Logger - By Dominexis - " + atlas_logger_version + "\n" +
        "\n Settings:" +
        "\n  Folder Mode: " + folder_mode + "\n" +
        "\n Actions:" +
        "\n  1) Generate atlas file for resource pack" +
        "\n  2) Change settings" +
        "\n  3) Exit program" +
        "\n"
    )

    # Get action input
    action, error, message = action_check(input(message + " Action: "), 1, 3)
    if not error:
        if action == 1:
            while True:
                # Display menu
                clear()
                print(
                    "\n Atlas Logger - By Dominexis - " + atlas_logger_version + "\n" +
                    "\n Settings:" +
                    "\n  Folder Mode: " + folder_mode + "\n"
                )

                # Get action input
                resource_pack, error, message = file_check(input(message + " Resource pack: "))
                if not error:
                    # Check if the atlas file already exists
                    write_bool = True
                    if os.path.exists(os.path.join(global_path, resource_pack, "assets", "minecraft", "atlases", "blocks.json")):
                        # Display menu
                        print(
                            "\n \"minecraft:atlases/blocks.json\" already exists, do you wish to overwrite it?" +
                            "\n  0) No" +
                            "\n  1) Yes" +
                            "\n"
                        )

                        # Get action input
                        action, error, message = action_check(input(message + " Action: "), 0, 1)
                        if not error:
                            if action == 0:
                                write_bool = False
                    
                    # Write atlas file
                    if write_bool:
                        # Compile list of textures                        
                        textures = []
                        # Get list of namespaces
                        if os.path.exists(os.path.join(global_path, resource_pack, "assets")):
                            for subdir, dirs, files in os.walk(os.path.join(global_path, resource_pack, "assets")):
                                namespaces = dirs.copy()
                                break
                            # Iterate through namespaces
                            for namespace in namespaces:
                                if os.path.exists(os.path.join(global_path, resource_pack, "assets", namespace, "models")):
                                    for subdir, dirs, files in os.walk(os.path.join(global_path, resource_pack, "assets", namespace, "models")):
                                        # Iterate through model files
                                        for file in files:
                                            # Check that the file is a model
                                            if file.split(".")[-1] == "json":
                                                # Open file
                                                with open(os.path.join(subdir, file), "r", encoding="utf-8") as f:
                                                    contents = f.read()
                                                # Convert contents to json
                                                model = json.loads(contents)
                                                # Log any textures that exist
                                                if "textures" in model:
                                                    for key in model["textures"].keys():
                                                        texture = model["textures"][key]
                                                        # Apply namespace to it if it doesn't exist
                                                        if ":" not in texture:
                                                            texture = "minecraft:" + texture
                                                        # Add to list if it isn't in the block or item folder and isn't already on the list
                                                        if ( texture.split(":")[1].split("/")[0] not in ["block", "item"] or "/" not in texture ) and texture not in textures:
                                                            textures.append(texture)

                        # Compile list of folders
                        folders = []
                        if folder_mode == "Folders":
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

                        # Create atlas file
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
                        if not os.path.exists(os.path.join(global_path, resource_pack, "assets", "minecraft", "atlases")):
                            os.makedirs(os.path.join(global_path, resource_pack, "assets", "minecraft", "atlases"))
                        with open(os.path.join(global_path, resource_pack, "assets", "minecraft", "atlases", "blocks.json"), "w", encoding="utf-8") as file:
                            file.write(
                                json.dumps({"sources": sources}, indent = 4)
                            )

                        # Send message
                        message = " Atlas successfully compiled!\n"
                        break


        elif action == 2:
            while True:
                # Display settings menu
                clear()
                print(
                    "\n Atlas Logger - By Dominexis - " + atlas_logger_version + "\n" +
                    "\n Edit settings:" +
                    "\n  0) Go back" +
                    "\n  1) Folder Mode: " + folder_mode +
                    "\n"
                )

                # Get action input
                action, error, message = action_check(input(message + " Action: "), 0, 1)
                if not error:
                    if action == 0:
                        break
                    elif action == 1:
                        print(
                            "\n 1) Singles - Processes each file individually. This prevents unwanted textures from getting through, but makes it harder to edit." +
                            "\n 2) Folders - Logs entire directories. This makes it easier to edit, but can include unwanted files in the block atlas." +
                            "\n"
                        )
                        value, error, message = action_check(input(message + " Folder Mode: "), 1, 2)
                        if not error:
                            folder_mode = "Singles" if value == 1 else "Folders"

        elif action == 3:
            exit()