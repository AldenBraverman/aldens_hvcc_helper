#!/bin/bash

#
# ./setup_env_with_hvcc.sh -t my_reorg -p aldens_polysynth.pd -n aldens_synth -s Y -g juce
#

# Running on windows
# https://stackoverflow.com/questions/71111124/running-sh-script-with-wsl-returns-command-not-found
# wsl -e setup_env_with_hvcc.sh -t wsl_windows -p osc2.pd  -n mySynth -s Y  -g juce

# Initialize variables
TAG=""
FILE_PATH=""
NAME=""
IS_SYNTH=""
GENERATOR=""

# Parse arguments
while getopts "t:p:n:s:g:" opt; do
  case $opt in
    t) TAG=$OPTARG ;;
    p) FILE_PATH=$OPTARG ;;
    n) NAME=$OPTARG ;;
    s) IS_SYNTH=$OPTARG ;;
    g) GENERATOR=$OPTARG ;;
    *)
      echo "Usage: bash ./setup_env_with_hvcc.sh -t <tag> -p <file_path> -n <name> -s <isSynth> -g <generator>"
      exit 1
      ;;
  esac
done

# Validate arguments
validate_args() {
  if [[ -z "$TAG" || -z "$FILE_PATH" || -z "$NAME" || -z "$IS_SYNTH" || -z "$GENERATOR" ]]; then
      echo "All arguments (-t, -p, -n, -s, -g) are required."
      exit 1
  fi

  if [[ "$IS_SYNTH" != "Y" && "$IS_SYNTH" != "N" ]]; then
      echo "Error: -s argument must be 'Y' or 'N'."
      exit 1
  fi

  if [[ "$GENERATOR" != "juce" && "$GENERATOR" != "web" ]]; then
      echo "Error: -g argument must be 'juce' or 'web'."
      exit 1
  fi

  if [[ ! "$FILE_PATH" =~ \.pd$ ]]; then
      echo "Error: The file must be a .pd file."
      exit 1
  fi

  if [[ ! "$TAG" =~ ^[a-zA-Z0-9_-]+$ ]]; then
      echo "Error: TAG contains invalid characters."
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
  hvcc "$hvcc_input_file" -o "$heavy_dir" -n "$NAME" -g "$generator_arg" -p "./libs/heavylib"
  # hvcc "$hvcc_input_file" -o "$heavy_dir" -n "$NAME" -g "js" -p "./heavylib"

  # Run Python script with the new directory
  python3 ./utils/parse_params.py "$heavy_dir" "$NAME"
}

# Copy CMake files
juce_cmake() {
  mkdir "$new_dir_export/plugin"
  # mkdir "$new_dir_export/juce_build"
  # mkdir "$new_dir_export/libs"
  cp -r plugin_template/plugin "$new_dir_export/"
  cp plugin_template/CMakeLists.txt "$new_dir_export/"

  # Copy Juce library into dir
  # cp -r libs/juce "$new_dir_export/"
  # Create alias for juce library for Cmake
  # ln -s libs/juce "$new_dir_export/libs"

  # Array of target files (adjust as needed)
  TARGET_FILES=("PluginEditor.cpp" "PluginProcessor.cpp" "PluginEditor.h" "PluginProcessor.h")

  # Replace placeholder in each target file
  for file in "${TARGET_FILES[@]}"; do
      TARGET_PATH="$new_dir_export/CMake/src/$file"
      if [[ -f "$TARGET_PATH" ]]; then
          python3 replace_boilerplate.py "$TARGET_PATH" "$NAME"
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

  # Replace placeholder in each target file
  for file in "${TARGET_FILES[@]}"; do
      TARGET_PATH="$new_dir_export/CMake/src/$file"
      if [[ -f "$TARGET_PATH" ]]; then
          python3 add_params_to_cpp.py "$TARGET_PATH" "$new_dir_export/Heavy/Heavy_"$NAME"_params.json"
      else
          echo "Warning: File '$TARGET_PATH' does not exist. Skipping."
      fi
  done
}

# Main execution
validate_args
install_git_submodules
# setup_venv
run_hvcc
juce_cmake
replace_boilerplate

# deactivate
echo "--------------------------------------------------"
echo "hvcc command executed successfully."
echo "Output directory: outputs"
echo "--------------------------------------------------"

# cmake -G "Visual Studio 17 2022" -B build .
# cmake -G "Xcode" -B build .