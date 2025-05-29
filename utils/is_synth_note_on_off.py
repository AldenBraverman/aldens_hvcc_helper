import sys

def uncomment_note_lines(toggle, cpp_path):
    if toggle.upper() != 'Y':
        print("Toggle is not 'Y'. No changes made.")
        return

    with open(cpp_path, 'r') as file:
        lines = file.readlines()

    updated_lines = []
    i = 0
    while i < len(lines):
        updated_lines.append(lines[i])

        if '@_UNCOMMENT_NOTE_ON_HERE' in lines[i] and i + 1 < len(lines):
            note_on_line = lines[i + 1].lstrip('// ').rstrip('\n')
            updated_lines.append(note_on_line + '\n')
            i += 1  # Skip next line (already handled)

        elif '@_UNCOMMENT_NOTE_OFF_HERE' in lines[i] and i + 1 < len(lines):
            note_off_line = lines[i + 1].lstrip('// ').rstrip('\n')
            updated_lines.append(note_off_line + '\n')
            i += 1

        i += 1

    with open(cpp_path, 'w') as file:
        file.writelines(updated_lines)

    print(f"Note-on/off lines uncommented in {cpp_path}.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python is_synth_note_on_off.py <Y_or_N> <path_to_cpp>")
        sys.exit(1)

    uncomment_note_lines(sys.argv[1], sys.argv[2])