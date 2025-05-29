import sys
import os

def exclude_missing_files(cmake_file_path, source_dir):
    # Get list of .c and .cpp files in directory (basename only)
    valid_extensions = {".c", ".cpp"}
    existing_files = set(
        f for f in os.listdir(source_dir)
        if os.path.isfile(os.path.join(source_dir, f)) and os.path.splitext(f)[1] in valid_extensions
    )

    with open(cmake_file_path, 'r') as f:
        lines = f.readlines()

    start_tag = "# @_HEAVY_SOURCES_START_@"
    end_tag = "# @_HEAVY_SOURCES_END_@"
    new_lines = []
    inside_block = False

    for line in lines:
        stripped = line.strip()
        if stripped == start_tag:
            inside_block = True
            new_lines.append(line)
            continue
        if stripped == end_tag:
            inside_block = False
            new_lines.append(line)
            continue

        if inside_block:
            # Extract the filename
            filename = os.path.basename(stripped)
            if (filename.endswith(".c") or filename.endswith(".cpp")):
                if filename not in existing_files and not stripped.startswith("#"):
                    # Comment out missing file
                    line = f"# {line}"
        new_lines.append(line)

    with open(cmake_file_path, 'w') as f:
        f.writelines(new_lines)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 exclude_hvcc_c_files.py <CMakeLists.txt path> <source directory>")
        sys.exit(1)

    cmake_file = sys.argv[1]
    source_dir = sys.argv[2]
    exclude_missing_files(cmake_file, source_dir)