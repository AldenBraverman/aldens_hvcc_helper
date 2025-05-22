import sys
import json
import os

def insert_param_updates(cpp_path, json_path):
    if not os.path.exists(cpp_path):
        print(f"Error: C++ file not found: {cpp_path}")
        sys.exit(1)

    if not os.path.exists(json_path):
        print(f"Error: JSON file not found: {json_path}")
        sys.exit(1)

    with open(json_path, 'r') as f:
        params = json.load(f)

    with open(cpp_path, 'r') as f:
        lines = f.readlines()

    updated_lines = []
    i = 0
    while i < len(lines):
        updated_lines.append(lines[i])
        if '@_ADD_PARAMS_TO_UPDATE_HERE' in lines[i]:
            for param in params:
                name = param["name"]
                hash_val = param["hash"]
                updated_lines.append(f"        // float _{name} = {name}->get();\n")
                updated_lines.append(f"        // hv_sendFloatToReceiver(context, {hash_val}, _{name});\n")
        i += 1

    with open(cpp_path, 'w') as f:
        f.writelines(updated_lines)

    print(f"Parameter update code inserted into {cpp_path}.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 ./utils/insert_param_updates.py <path_to_cpp> <path_to_json>")
        sys.exit(1)

    insert_param_updates(sys.argv[1], sys.argv[2])
