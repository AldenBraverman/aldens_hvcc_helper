import re
import sys

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
parameter_info_regex = r"int Heavy_[a-zA-Z_][a-zA-Z_0-9]*::getParameterInfo\(.*?\) \{(.*?)return 1;"
parameter_info_match = re.search(parameter_info_regex, cpp_code, re.S)

if parameter_info_match:
    # Extracted function body
    parameter_info_body = parameter_info_match.group(1)

    # Regex to extract relevant data from each case block
    case_block_regex = (
        r"case\s+\d+:\s*\{.*?info->hash\s*=\s*(0x[0-9A-Fa-f]+);.*?"
        r"info->minVal\s*=\s*([\d\.f]+);.*?"
        r"info->maxVal\s*=\s*([\d\.f]+);.*?"
        r"info->defaultVal\s*=\s*([\d\.f]+);.*?\}"
    )

    # Use re.S in the re.findall call
    case_blocks = re.findall(case_block_regex, parameter_info_body, re.S)

    # Update the dictionary with minVal, maxVal, and defaultVal
    for hash_value, min_val, max_val, default_val in case_blocks:
        if hash_value in case_dict:
            case_dict[hash_value] = {
                'name': case_dict[hash_value],
                'minVal': float(min_val.rstrip('f')),
                'maxVal': float(max_val.rstrip('f')),
                'defaultVal': float(default_val.rstrip('f')),
            }

# Output the updated dictionary
print(case_dict)