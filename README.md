# Alden's hvcc helper
aldens_hvcc_helper converts a [heavy compatible](https://wasted-audio.github.io/hvcc/) [pure data](https://puredata.info/) patch into [WebAssembly](https://emscripten.org/) and [JUCE](https://juce.com/) [CMake](https://cmake.org/) project. It's usage enables rapid iteration, generating the WebAssembly and JUCE code in a matter of seconds. With the WebAssembly code and the JUCE CMake project, you can deliver the audio application to a game engine, web, VST3, mobile or native exactly how the application was designed in pure data.
### Requirements
- [git](https://git-scm.com/downloads)
- [docker](https://www.docker.com/)
- [vscode](https://code.visualstudio.com/)
	- [Dev Containers Extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
- [cmake]()
	- Generators (Otherwise, you can the `Unix Makefiles` generator with the dev container)
		- MacOS: [Xcode]()
		- Windows: [Visual Studio]()
### Getting Started
1. Clone the repo
	- `git clone https://github.com/AldenBraverman/aldens_hvcc_helper.git`
2. Open the repo is vscode
	- `cd aldens_hvcc_helper`
	- `code .`
#### Verify Requirements Installs
1. In your terminal/command prompt, make sure the following commands are found:
	- `git`
	- `docker`
	- `code`
	- `cmake --help`
		- Here you should see your generators listed; `Xcode` for MacOS, `Visual Studio 16 2019` for Windows (you may have a different Visual Studio version, use whatever version you have installed)
### Usage
1. Open the repo in the dev container
2. Make a copy (`cp config_template.json <config_name>.json`), or update the contents of the `config_template.json` file
	  - set `patch_path` to the path of your puredata patch
	  - if your patch uses a `notein` object/is a synthesizer, set `is_synth=Y` and `needs_midi_input=TRUE` 
	  - if your patch is an audio effect, set `is_synth=N` and `needs_midi_input=FALSE`
```json
{
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
3. Run the generate command: `./setup_env_with_hvcc -c config_template.json`
4. Reopen the repo locally, this will make the CMake builds for native targets easier/faster
5. Open the output directory in an integrated terminal
6. Build the cmake project
	- On MacOS, use `cmake -G "Xcode" -B build .`
	- On Windows, use `cmake -G "Visual Studio 16 2019" -B build .`
7. When the build complete, build the artifacts: `cmake --build build`
### Artifact locations and testing
- Native files can be found at the following:
	- Standalone: `<output_dir>/build/plugin/<project_name>_artifacts/Debug/Standalone/`
	- VST3: `<output_dir>/build/plugin/<project_name>_artifacts/Debug/VST3/`
- WebAssembly Index file can be found here: `<output_dir>/Heavy/js/index.html`
