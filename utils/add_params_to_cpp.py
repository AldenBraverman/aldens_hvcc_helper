import sys
import os
import json

# JSON reading and processing functionality
def read_json_parameters(json_file_path, cpp_file_path):
    """
    Read parameters from a JSON file and return them as a list.
    :param json_file_path: Path to the JSON file.
    :return: List of parameters or None if an error occurs.
    """
    print("Heavy Dir: "+json_file_path)
    try:
        if not os.path.exists(json_file_path):
            print(f"Error: File '{json_file_path}' not found.")
            return None
        
        with open(json_file_path, 'r') as file:
            print("Param JSON loaded")
            parameters = json.load(file)
        
        if not isinstance(parameters, list):
            print("Error: JSON file should contain a list of parameters.")
            return None
        
        print(f"Successfully loaded {len(parameters)} parameters from {json_file_path}")

        process_parameters(parameters, cpp_file_path)
        # return parameters
    
    except json.JSONDecodeError:
        print(f"Error: '{json_file_path}' is not a valid JSON file.")
        return None
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        return None

def process_parameters(parameters, cpp_file_path):
    """
    Process and display parameters.
    :param parameters: List of parameter dictionaries.
    """
    # Example 1: Iterate through each parameter
    # params_to_add_to_header = []
    # print("\nAll Parameters:")
    # for param in parameters:
    #     print(f"{param['name']} (Hash: {param['hash']}) - Range: {param['minVal']} to {param['maxVal']}, Default: {param['defaultVal']}")
    #     params_to_add_to_header.append("juce::AudioParameterFloat* "+f"{param['name']}"+"Param")
    
    # print("CPP_FILE_PATH: "+cpp_file_path)

    if(cpp_file_path.endswith(".h")):
        print("This is the .h file: "+cpp_file_path)

        params_to_add_to_header = []
        param_ids_to_add_to_header = []
        print("\nAll Parameters:")
        for param in parameters:
            print(f"{param['name']} (Hash: {param['hash']}) - Range: {param['minVal']} to {param['maxVal']}, Default: {param['defaultVal']}")
            params_to_add_to_header.append("juce::AudioParameterFloat* "+f"{param['name']}"+"Param;")
            param_ids_to_add_to_header.append("PARAMETER_ID("+f"{param['name']}"+")")

        add_lines_after_marker(cpp_file_path,"@_PARAM_IDS_GO_HERE", param_ids_to_add_to_header)
        add_lines_after_marker(cpp_file_path, "@_PLACE_PARAMS_HERE", params_to_add_to_header)
        

    if(cpp_file_path.endswith(".cpp")):
        print("This is the .cpp file: "+cpp_file_path)

       #  params_to_add_to_header = []
        print("\nAll Parameters:")
        for param in parameters:
            print(f"{param['name']} (Hash: {param['hash']}) - Range: {param['minVal']} to {param['maxVal']}, Default: {param['defaultVal']}")
            # params_to_add_to_header.append("juce::AudioParameterFloat* "+f"{param['name']}"+"Param;")
    
    # # Example 2: Filter parameters based on a condition
    # high_range_params = [p for p in parameters if p['maxVal'] > 100]
    # if high_range_params:
    #     print("\nParameters with max value > 100:")
    #     for param in high_range_params:
    #         print(f"{param['name']}: {param['maxVal']}")
    
    # Example 3: Create a dictionary mapping parameter names to their details
    # param_dict = {p['name']: p for p in parameters}
    # return param_dict

def add_lines_after_marker(file_path, marker, new_lines):
    """
    Add lines to a file after a specific marker.
    
    Args:
        file_path (str): Path to the file
        marker (str): The marker line to find
        new_lines (list): List of strings to add after the marker
    """
    # Read the existing content
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        # If file doesn't exist, create it with just the marker and new lines
        with open(file_path, 'w') as file:
            file.write(marker + '\n')
            for line in new_lines:
                file.write(line + '\n')
        return

    # Find the marker and insert new lines
    with open(file_path, 'w') as file:
        marker_found = False
        for line in lines:
            file.write(line)
            # Check if this line contains the marker
            if marker in line and not marker_found:
                marker_found = True
                print("Marker Found: "+marker+" in file: "+file_path)
                # Add the new lines right after the marker
                for new_line in new_lines:
                    file.write(new_line + '\n')
        
        # If marker wasn't found, append marker and new lines at the end
        # if not marker_found:
        #     file.write('\n' + marker + '\n')
        #     for new_line in new_lines:
        #         file.write(new_line + '\n')

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python add_params_to_cpp.py <file_path> <heavy_json_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    json_path = sys.argv[2]
    # heavy_dir = sys.argv[3]

    read_json_parameters(json_path, file_path)
    # replace_boilerplate(file_path, new_name)
    # read_json_parameters(heavy_dir)