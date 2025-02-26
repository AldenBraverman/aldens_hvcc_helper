import re
import sys
import json

# Check if the directory argument is provided
# if len(sys.argv) != 2:
#     print("Usage: python3 parse_params.py <directory>")
#     sys.exit(1)

new_dir = sys.argv[1]
# print(f"Processing directory: {new_dir}")
synth_name = sys.argv[2]

# Add your processing logic here
# For example, listing files in the directory
# import os
# for file_name in os.listdir(new_dir):
#     print(f"Found file: {file_name}")

# Path to your C++ file
cpp_file_path = new_dir+f"/c/Heavy_{synth_name}.cpp"
# cpp_file_path = "/Users/aldenbraverman/Downloads/Quantum-B-1-VST-AU-plugin-main/Source/Heavy/Heavy_B1.cpp"

# Read the C++ file as a string
with open(cpp_file_path, "r", encoding="utf-8") as file:
    cpp_code = file.read()

# Debug: Confirm file content is loaded
print("File content loaded.")

# Regex to extract the function body for scheduleMessageForReceiver
function_regex = r"void Heavy_[a-zA-Z_][a-zA-Z_0-9]*::scheduleMessageForReceiver\(.*?\) \{(.*?)default: return;"
function_match = re.search(function_regex, cpp_code, re.S)

if function_match:
    # Extracted function body
    function_body = function_match.group(1)

    # Regex to extract cases within the isolated function
    case_regex = r"case\s+(0x[0-9A-Fa-f]+):\s*\{.*?//\s*(.*)"
    cases = re.findall(case_regex, function_body)

    # Convert the cases into a dictionary
    case_dict = {case_value: comment for case_value, comment in cases}

    # Output the dictionary
    print(case_dict)
else:
    print("Function not found.")

# Regex to extract the body of getParameterInfo
parameter_info_regex = r"int Heavy_[a-zA-Z_][a-zA-Z_0-9]*::getParameterInfo\(.*?\) \{(.*?)"
parameter_info_match = re.search(parameter_info_regex, cpp_code, re.S)
print("parameter info match: "+str(parameter_info_match))

if parameter_info_match:
    # Extracted function body
    parameter_info_body = parameter_info_match.group(0)
    print("Function Body: "+str(parameter_info_body))

case_pattern = r'case\s+(\d+):\s*\{\s*' \
                r'info->name\s*=\s*"([^"]+)";\s*' \
                r'info->hash\s*=\s*(0x[0-9A-F]+);\s*' \
                r'info->type\s*=\s*HvParameterType::([^;]+);\s*' \
                r'info->minVal\s*=\s*([^;]+);\s*' \
                r'info->maxVal\s*=\s*([^;]+);\s*' \
                r'info->defaultVal\s*=\s*([^;]+);\s*' \
                r'break;'

# Find all matches
parameters = []
matches = re.finditer(case_pattern, cpp_code, re.DOTALL)

for match in matches:
    # Skip the default case (usually has index as "default")
    if match.group(1) != "default":
        parameter = {
            "index": int(match.group(1)),
            "name": match.group(2),
            "hash": match.group(3),
            "type": match.group(4),
            "minVal": float(match.group(5).strip('f')),
            "maxVal": float(match.group(6).strip('f')),
            "defaultVal": float(match.group(7).strip('f'))
        }
        parameters.append(parameter)

# Print extracted parameters
print("Extracted Parameters:")
for param in parameters:
    print(f"Index: {param['index']}")
    print(f"  Name: {param['name']}")
    print(f"  Hash: {param['hash']}")
    print(f"  Min Value: {param['minVal']}")
    print(f"  Max Value: {param['maxVal']}")
    print(f"  Default Value: {param['defaultVal']}")
    print()

# Example of how to use the extracted data
print("Parameter Names and Ranges:")
for param in parameters:
    print(f"{param['name']}: {param['minVal']} to {param['maxVal']} (default: {param['defaultVal']})")



# Output the updated dictionary
# print("My case_dict: "+str(case_dict))

# Define the JSON output file path
json_file_path = new_dir + f"/Heavy_{synth_name}_params.json"

# Write the dictionary to a JSON file
with open(json_file_path, "w", encoding="utf-8") as json_file:
    json.dump(parameters, json_file, indent=4)

print(f"Dictionary saved to {json_file_path}")
