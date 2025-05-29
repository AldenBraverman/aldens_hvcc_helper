# insert_params.py
import json
import sys

def insert_parameter_blocks(json_path, cpp_path):
    with open(json_path, 'r') as f:
        parameters = json.load(f)

    cpp_blocks = []
    for param in parameters:
        name = param["name"]
        min_val = param["minVal"]
        max_val = param["maxVal"]
        default_val = param["defaultVal"]
        step_val = max_val / 100.0
        
        cpp_block = f"""    layout.add(std::make_unique<juce::AudioParameterFloat>(
        ParameterID::{name},
        "{name}",
        juce::NormalisableRange<float>({min_val}f, {max_val}f, {step_val:.6f}f),
        {default_val}f
));"""
        cpp_blocks.append(cpp_block)

    with open(cpp_path, 'r') as f:
        cpp_code = f.read()

    marker = '@_LAYOUT_PARAM_IDS_GO_HERE'
    if marker not in cpp_code:
        raise ValueError(f"Marker '{marker}' not found in the C++ file.")
    
    updated_cpp_code = cpp_code.replace(marker, marker + '\n' + '\n\n'.join(cpp_blocks))

    with open(cpp_path, 'w') as f:
        f.write(updated_cpp_code)

    print(f"Inserted {len(cpp_blocks)} parameter blocks into {cpp_path}.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python insert_params.py <path_to_json> <path_to_cpp>")
        sys.exit(1)
    insert_parameter_blocks(sys.argv[1], sys.argv[2])