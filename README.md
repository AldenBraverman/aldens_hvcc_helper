# Alden's hvcc helper

This repo turns a [Pure Data](https://puredata.info/) patch into either:

- **hvcc / Heavy**: a [Heavy-compatible](https://wasted-audio.github.io/hvcc/) patch compiled to C or JavaScript plus a [JUCE](https://juce.com/) CMake plugin (and optional WebAssembly when `web_gen` is `Y`).
- **libpd** (JUCE desktop only): the same patch runs inside the real Pd engine via [libpd](https://github.com/libpd/libpd), linked as a native plugin (no hvcc-generated Heavy sources, no WASM in v1).

Orchestration is implemented in [tools/generate.py](tools/generate.py) (Python 3, stdlib only). [setup_env_with_hvcc.sh](setup_env_with_hvcc.sh) is a thin wrapper that calls that script.

### Requirements

- [git](https://git-scm.com/downloads) (submodules: JUCE, and libpd if you use `audio_engine: libpd`)
- [docker](https://www.docker.com/) and [VS Code](https://code.visualstudio.com/) with the [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension (optional)
- [CMake](https://cmake.org/) 3.22+ for hvcc outputs; **3.25+** for libpd outputs (required by upstream libpd)
- [hvcc](https://wasted-audio.github.io/hvcc/) on `PATH` when using `audio_engine: hvcc`

### Getting started

1. `git clone https://github.com/AldenBraverman/aldens_hvcc_helper.git`
2. `cd aldens_hvcc_helper`
3. Initialize submodules (first clone):

```bash
git submodule update --init --recursive
```

For libpd, ensure `libs/libpd/pure-data/src/m_pd.h` exists; if `pure-data` is empty, run:

```bash
cd libs/libpd && git submodule update --init --recursive && cd ../..
```

### Configuration

Copy [config_template.json](config_template.json) or edit it. Important keys:

| Key | Meaning |
|-----|--------|
| `audio_engine` | `"hvcc"` (default) or `"libpd"` |
| `folder_name` | Output folder tag under `outputs/<timestamp>_<folder_name>/` |
| `project_name` | C++/CMake symbol prefix (replaces `Boiler_plate` in templates) |
| `pd_paths.patch_path` | Path to the `.pd` file (repo-relative or absolute) |
| `is_synth` | `Y` / `N` — drives MIDI note hooks for **hvcc** plugins |
| `web_gen` | `Y` generates hvcc JS/WASM; **`Y` is ignored with a warning when `audio_engine` is `libpd`** |
| `cmake_settings` | `company_name`, `needs_midi_input`, `needs_midi_output`, `plugin_manufacturer_code`, `plugin_code`, `formats`, `needs_webview2`, etc. These are written into the generated `plugin/CMakeLists.txt`. |
| `libpd.search_paths` | Optional list of extra directories or files copied under `plugin/pd/extra/` and embedded with the patch (abstractions must resolve from those paths) |

Example (hvcc):

```json
{
	"audio_engine": "hvcc",
	"folder_name": "my_folder",
	"project_name": "osc_test",
	"manufacturer_settings": {
		"name": "my_manufacturer",
		"code": "manu"
	},
	"project_version": "1.0.0",
	"is_synth": "Y",
	"web_gen": "Y",
	"generic_ui": {
		"use_web_ui": "N",
		"react_project_path": ""
	},
	"pd_paths": {
		"patch_path": "./aldens_polysynth.pd",
		"heavylib_path": "./libs/heavylib"
	},
	"libpd": {
		"search_paths": []
	},
	"cmake_settings": {
		"plugin_name": "MyPlugin",
		"company_name": "aldenbraverman",
		"needs_midi_input": "TRUE",
		"needs_midi_output": "FALSE",
		"plugin_manufacturer_code": "ALDB",
		"plugin_code": "ALDB",
		"formats": [
			"VST3",
			"AU",
			"Standalone"
		],
		"needs_webview2": "TRUE"
	}
}
```

**hvcc note:** In the generated `PluginProcessor.cpp`, the line after `//@_ADD_HEAVY_CONTEXT_HERE` is a placeholder until [utils/init_prepare_to_play.py](utils/init_prepare_to_play.py) rewrites it to match your patch name.

### Usage

1. (Optional) Open the repo in the dev container.
2. Edit or copy `config_template.json` as above.
3. Run either:

```bash
./setup_env_with_hvcc.sh -c config_template.json
```

or:

```bash
python3 tools/generate.py -c config_template.json
```

4. Open the new directory under `outputs/<timestamp>_<folder_name>/` and configure/build CMake from there (so relative paths to `libs/juce` and `libs/libpd` resolve).

**macOS (example):** `cmake -G "Xcode" -B build .` then `cmake --build build`  
**Windows:** use a supported Visual Studio generator and see libpd’s CMake notes for MSVC/pthreads if you use `audio_engine: libpd`.

### Artifact locations

- Native (hvcc or libpd): `<output_dir>/build/plugin/<target>_artifacts/...` (layout depends on generator and config).
- WebAssembly (hvcc only): `<output_dir>/Heavy/js/index.html`

### libpd limitations (v1)

- Desktop JUCE targets only; there is no libpd-backed WASM path yet.
- Audio is advanced in multiples of `libpd_blocksize()` (64 samples); shorter tails at the end of a host buffer are passed through unchanged.
- Windows MSVC builds need extra setup for libpd (pthreads); see upstream libpd documentation.
