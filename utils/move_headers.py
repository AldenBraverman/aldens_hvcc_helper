import os
import shutil
import sys

def move_header_files(src_dir):
    if not os.path.isdir(src_dir):
        print(f"Error: {src_dir} is not a valid directory.")
        sys.exit(1)

    # Compute destination folder: one level up + /h
    dest_dir = os.path.abspath(os.path.join(src_dir, "..", "h"))
    os.makedirs(dest_dir, exist_ok=True)

    moved_files = 0

    for filename in os.listdir(src_dir):
        file_path = os.path.join(src_dir, filename)

        if os.path.isfile(file_path) and filename.endswith(('.h', '.hpp')):
            dest_path = os.path.join(dest_dir, filename)
            shutil.move(file_path, dest_path)
            moved_files += 1
            print(f"Moved: {filename} → {dest_dir}")

    print(f"Done. {moved_files} file(s) moved to {dest_dir}.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python move_headers.py <path_to_folder>")
        sys.exit(1)

    move_header_files(sys.argv[1])