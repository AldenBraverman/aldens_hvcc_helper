import sys
import os

def replace_heavy_context_call(cpp_path, new_context_name):
    with open(cpp_path, 'r') as f:
        lines = f.readlines()

    updated_lines = []
    i = 0
    while i < len(lines):
        updated_lines.append(lines[i])
        if '@_ADD_HEAVY_CONTEXT_HERE' in lines[i]:
            if i + 1 < len(lines):
                line = lines[i + 1]
                updated_line = line.replace('osc_one_d_one', new_context_name)
                updated_lines.append(updated_line)
                i += 1
        i += 1

    with open(cpp_path, 'w') as f:
        f.writelines(updated_lines)

    print(f"Updated context name to '{new_context_name}' in {cpp_path}.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 ./utils/replace_heavy_context.py <path_to_cpp> <new_context_name>")
        sys.exit(1)

    cpp_path = sys.argv[1]
    context_name = sys.argv[2]

    if not os.path.exists(cpp_path):
        print(f"File not found: {cpp_path}")
        sys.exit(1)

    replace_heavy_context_call(cpp_path, context_name)
