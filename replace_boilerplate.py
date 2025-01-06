import sys
import os

def replace_boilerplate(file_path, new_name):
    """
    Replaces the hardcoded placeholder 'Boiler_plate' in a .h or .cpp file with the provided name.

    :param file_path: Path to the file.
    :param new_name: The new name to replace 'Boiler_plate'.
    """
    placeholder = "Boiler_plate"
    
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        sys.exit(1)

    try:
        with open(file_path, 'r') as file:
            content = file.read()

        updated_content = content.replace(placeholder, new_name)

        with open(file_path, 'w') as file:
            file.write(updated_content)

        # print(f"Successfully replaced '{placeholder}' with '{new_name}' in '{file_path}'.")

    except Exception as e:
        print(f"Error: Unable to process the file. {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python replace_boilerplate.py <file_path> <new_name>")
        sys.exit(1)

    file_path = sys.argv[1]
    new_name = sys.argv[2]

    replace_boilerplate(file_path, new_name)
