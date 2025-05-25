#!/bin/bash

#
# ./setup_env_with_hvcc.sh -t my_reorg -p aldens_polysynth.pd -n aldens_synth -s Y -g juce
#

# USE LF LINE ENDINGS - CLRF -> LF
# https://unix.stackexchange.com/questions/721844/linux-bash-shell-script-error-cannot-execute-required-file-not-found
# https://willi.am/blog/2016/08/11/docker-for-windows-dealing-with-windows-line-endings/

# Running on windows
# https://stackoverflow.com/questions/71111124/running-sh-script-with-wsl-returns-command-not-found
# wsl -e setup_env_with_hvcc.sh -t wsl_windows -p osc2.pd  -n mySynth -s Y  -g juce

# Initialize variables
TAG=""
FILE_PATH=""
NAME=""
IS_SYNTH=""
GENERATOR=""

# # Parse arguments
# while getopts "t:p:n:s:g:" opt; do
#   case $opt in
#     t) TAG=$OPTARG ;;
#     p) FILE_PATH=$OPTARG ;;
#     n) NAME=$OPTARG ;;
#     s) IS_SYNTH=$OPTARG ;;
#     g) GENERATOR=$OPTARG ;;
#     *)
#       echo "Usage: bash ./setup_env_with_hvcc.sh -t <tag> -p <file_path> -n <name> -s <isSynth> -g <generator>"
#       exit 1
#       ;;
#   esac
# done

#!/bin/bash

# Parse arguments
while getopts "c:" opt; do
  case $opt in
    c) CONFIG_FILE="$OPTARG"
    ;;
    \?) echo "Invalid option -$OPTARG" >&2
        exit 1
    ;;
  esac
done

if [ -z "$CONFIG_FILE" ]; then
  echo "Usage: $0 -c <config_file.json>"
  exit 1
fi

# Extract variables from JSON
TAG=$(jq -r '.folder_name' "$CONFIG_FILE")
FILE_PATH=$(jq -r '.pd_paths.patch_path' "$CONFIG_FILE")
NAME=$(jq -r '.project_name' "$CONFIG_FILE")
IS_SYNTH=$(jq -r '.is_synth' "$CONFIG_FILE")

# The rest of your script can use $tag, $file_path, $name, $is_synth as before
echo "Tag: $TAG"
echo "File Path: $FILE_PATH"
echo "Project Name: $NAME"
echo "Is Synth: $IS_SYNTH"

# Validate arguments
validate_args() {
  # if [[ -z "$TAG" || -z "$FILE_PATH" || -z "$NAME" || -z "$IS_SYNTH" || -z "$GENERATOR" ]]; then
  #     echo "All arguments (-t, -p, -n, -s, -g) are required."
  #     exit 1
  # fi

  # if [[ "$IS_SYNTH" != "Y" && "$IS_SYNTH" != "N" ]]; then
  #     echo "Error: -s argument must be 'Y' or 'N'."
  #     exit 1
  # fi

  # if [[ "$GENERATOR" != "juce" && "$GENERATOR" != "web" ]]; then
  #     echo "Error: -g argument must be 'juce' or 'web'."
  #     exit 1
  # fi

  # if [[ ! "$FILE_PATH" =~ \.pd$ ]]; then
  #     echo "Error: The file must be a .pd file."
  #     exit 1
  # fi

  # if [[ ! "$TAG" =~ ^[a-zA-Z0-9_-]+$ ]]; then
  #     echo "Error: TAG contains invalid characters."
  #     exit 1
  # fi
  if [ -z "$TAG" ] || [ -z "$FILE_PATH" ] || [ -z "$NAME" ]; then
    echo "Missing required config values: tag, file_path, or name."
    exit 1
  fi
}

# Install Git submodules
install_git_submodules() {
  if [[ -f .gitmodules ]]; then
    echo "Initializing and updating Git submodules..."
    git submodule init
    # git submodule update --remote
    git submodule update --init --recursive
    echo "Git submodules initialized and updated."
  else
    echo "No Git submodules found."
  fi
}

# Virtual environment setup
setup_venv() {
  local venv_dir="hvcc_juce_helper_venv"

  if [ ! -d "$venv_dir" ]; then
      echo "Creating virtual environment: $venv_dir"
      python3 -m venv "$venv_dir"
  fi

  source "$venv_dir/bin/activate"

  # # pwd
  # cd hvcc/
  # pip3 install -e .
  # cd ../

  # if ! python3 -c "import hvcc" &>/dev/null; then
  #     echo "Installing Python library: hvcc"
  #     pip3 install hvcc
  # fi
  pip3 install hvcc
}

# Run hvcc
run_hvcc() {
  local outputs_dir="outputs"
  local timestamp=$(date +"%Y-%m-%d_%H%M%S")
  local new_dir="${outputs_dir}/${timestamp}_${TAG}"
  export new_dir_export="$new_dir"
  local heavy_dir="${new_dir}/Heavy"

  # Create required directories
  mkdir -p "$outputs_dir"
  mkdir -p "$heavy_dir"

  # Validate and copy .pd file
  if [[ -f "$FILE_PATH" ]]; then
      cp "$FILE_PATH" "$new_dir/"
  else
      echo "Error: File '$FILE_PATH' does not exist."
      exit 1
  fi

  local hvcc_input_file="$new_dir/$(basename "$FILE_PATH")"
  local generator_arg=""

  # Map generator argument
  if [[ "$GENERATOR" == "juce" ]]; then
      generator_arg="c"
  elif [[ "$GENERATOR" == "web" ]]; then
      echo "Web support coming soon!"
      exit 1
  fi

  # Run hvcc command
  # hvcc "$hvcc_input_file" -o "$heavy_dir" -n "$NAME" -g "$generator_arg" -p "./libs/heavylib"
  hvcc "$hvcc_input_file" -o "$heavy_dir" -n "$NAME" -g "c" -p "./libs/heavylib"

  # Run Python script with the new directory
  python3 ./utils/parse_params.py "$heavy_dir" "$NAME"
}

# Copy CMake files
juce_cmake() {
  mkdir "$new_dir_export/plugin"
  mkdir "$new_dir_export/plugin/include"
  mkdir "$new_dir_export/plugin/include/$NAME/"
  # mkdir "$new_dir_export/juce_build"
  # mkdir "$new_dir_export/libs"
  cp -r plugin_template/plugin/src "$new_dir_export/plugin"

  cp plugin_template/CMakeLists.txt "$new_dir_export/CMakeLists.txt"
  cp plugin_template/plugin/CMakeLists.txt "$new_dir_export/plugin/CMakeLists.txt"

  # We may want to specify in config a different path for the UI code
  cp -r plugin_template/plugin/ui "$new_dir_export/plugin"

  cp -r plugin_template/plugin/include/Boiler_plate/* "$new_dir_export/plugin/include/$NAME"

  # Copy Juce library into dir
  # cp -r libs/juce "$new_dir_export/"
  # Create alias for juce library for Cmake
  # ln -s libs/juce "$new_dir_export/libs"

  # Array of target files (adjust as needed)
  TARGET_FILES=("src/PluginEditor.cpp" "src/PluginProcessor.cpp" "include/$NAME/PluginEditor.h" "include/$NAME/PluginProcessor.h" "CMakeLists.txt" "../CMakeLists.txt")

  # Replace placeholder in each target file
  for file in "${TARGET_FILES[@]}"; do
      TARGET_PATH="$new_dir_export/plugin/$file"
      echo "$TARGET_PATH"
      if [[ -f "$TARGET_PATH" ]]; then
          pwd
          python3 ./utils/replace_boilerplate.py "$TARGET_PATH" "$NAME"
      else
          echo "Warning: File '$TARGET_PATH' does not exist. Skipping."
      fi
  done

  # cd "$new_dir_export/CMake"
  # cmake -G "Xcode" -B build .
}

# Replace JUCE boilerplate code
replace_boilerplate() {
  # Array of target files (adjust as needed)
  TARGET_FILES=("PluginProcessor.cpp" "PluginProcessor.h")
  TARGET_HEADER_FILES=("PluginEditor.h" "PluginProcessor.h")

  # Replace placeholder in each target file
  for file in "${TARGET_FILES[@]}"; do
      TARGET_PATH="$new_dir_export/plugin/src/$file"
      if [[ -f "$TARGET_PATH" ]]; then
          python3 ./utils/add_params_to_cpp.py "$TARGET_PATH" "$new_dir_export/Heavy/Heavy_"$NAME"_params.json"
      else
          echo "Warning: File '$TARGET_PATH' does not exist. Skipping."
      fi
  done

    # Replace placeholder in each target file
  for file in "${TARGET_HEADER_FILES[@]}"; do
      TARGET_PATH="$new_dir_export/plugin/include/$NAME/$file"
      if [[ -f "$TARGET_PATH" ]]; then
          python3 ./utils/add_params_to_cpp.py "$TARGET_PATH" "$new_dir_export/Heavy/Heavy_"$NAME"_params.json"
      else
          echo "Warning: File '$TARGET_PATH' does not exist. Skipping."
      fi
  done
}

add_params_to_layout() {
  # Paths to input files
  JSON_PATH="$new_dir_export/Heavy/Heavy_"$NAME"_params.json"
  CPP_PATH="$new_dir_export/plugin/src/PluginProcessor.cpp"

  # Call the Python script
  python3 ./utils/add_params_to_layout.py "$JSON_PATH" "$CPP_PATH"
}

is_synth_note_on_off() { 
  python3 ./utils/is_synth_note_on_off.py "$IS_SYNTH" "$CPP_PATH"
}

init_prepare_to_play() {
  # Paths to input files
  JSON_PATH="$new_dir_export/Heavy/Heavy_"$NAME"_params.json"
  CPP_PATH="$new_dir_export/plugin/src/PluginProcessor.cpp"

  # Call the Python script
  python3 ./utils/init_prepare_to_play.py "$CPP_PATH" "$NAME"
}

add_params_to_update() { 
  JSON_PATH="$new_dir_export/Heavy/Heavy_"$NAME"_params.json"
  CPP_PATH="$new_dir_export/plugin/src/PluginProcessor.cpp"
  
  python3 ./utils/insert_param_updates.py "$CPP_PATH" "$JSON_PATH"
}

reorg_heavy_source() {
  # Paths to input files
  HEAVY_OUT_PATH="$new_dir_export/Heavy"

  mkdir -p "$HEAVY_OUT_PATH/h"

  # Call the Python script
  python3 ./utils/move_headers.py "$HEAVY_OUT_PATH/c"
}

# Main execution
validate_args
install_git_submodules
# setup_venv
run_hvcc
juce_cmake
replace_boilerplate
add_params_to_layout
is_synth_note_on_off
init_prepare_to_play
reorg_heavy_source

# deactivate
echo "--------------------------------------------------"
echo "hvcc command executed successfully."
echo "Output directory: outputs"
echo "--------------------------------------------------"

# cmake -G "Visual Studio 17 2022" -B build .
# cmake -G "Xcode" -B build .