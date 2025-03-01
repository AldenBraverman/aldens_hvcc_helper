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
    print("\nAll Parameters:")
    for param in parameters:
        print(f"{param['name']} (Hash: {param['hash']}) - Range: {param['minVal']} to {param['maxVal']}, Default: {param['defaultVal']}")
    
    print("CPP_FILE_PATH: "+cpp_file_path)
    
    # # Example 2: Filter parameters based on a condition
    # high_range_params = [p for p in parameters if p['maxVal'] > 100]
    # if high_range_params:
    #     print("\nParameters with max value > 100:")
    #     for param in high_range_params:
    #         print(f"{param['name']}: {param['maxVal']}")
    
    # Example 3: Create a dictionary mapping parameter names to their details
    # param_dict = {p['name']: p for p in parameters}
    # return param_dict

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