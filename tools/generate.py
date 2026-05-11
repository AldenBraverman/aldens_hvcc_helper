#!/usr/bin/env python3
"""
Project generator: hvcc (Heavy) or libpd JUCE backend.
Run from repository root: python3 tools/generate.py -c config.json
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def load_config(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def validate_common(cfg: dict) -> None:
    for key in ("folder_name", "project_name", "pd_paths"):
        if key not in cfg or cfg[key] in (None, ""):
            raise SystemExit(f"Missing required config key: {key}")
    pd_paths = cfg["pd_paths"]
    if "patch_path" not in pd_paths or not pd_paths["patch_path"]:
        raise SystemExit("pd_paths.patch_path is required")


def run(cmd: list[str], *, cwd: Path | None = None) -> None:
    print("+", " ".join(cmd))
    r = subprocess.run(cmd, cwd=cwd or REPO_ROOT)
    if r.returncode != 0:
        raise SystemExit(f"Command failed ({r.returncode}): {' '.join(cmd)}")


def run_optional(cmd: list[str], *, cwd: Path | None = None) -> bool:
    print("+", " ".join(cmd))
    r = subprocess.run(cmd, cwd=cwd or REPO_ROOT)
    if r.returncode != 0:
        print(f"Warning: command exited {r.returncode} (continuing): {' '.join(cmd)}")
        return False
    return True


def run_py(script: Path, args: list[str]) -> None:
    run([sys.executable, str(script)] + args, cwd=REPO_ROOT)


def install_git_submodules() -> None:
    gitmodules = REPO_ROOT / ".gitmodules"
    if not gitmodules.is_file():
        print("No .gitmodules; skipping submodule init.")
        return
    print("Initializing git submodules...")
    ok = run_optional(["git", "submodule", "init"], cwd=REPO_ROOT)
    if ok:
        run_optional(["git", "submodule", "update", "--recursive", "--remote"], cwd=REPO_ROOT)


def init_libpd_submodule() -> None:
    if not (REPO_ROOT / ".git").exists():
        print("Not a git checkout; ensure libs/libpd is populated (see README).")
        return
    print("Ensuring libpd submodule is initialized...")
    run_optional(["git", "submodule", "update", "--init", "--recursive", "libs/libpd"], cwd=REPO_ROOT)
    libpd_root = REPO_ROOT / "libs" / "libpd"
    pd_h = libpd_root / "pure-data" / "src" / "m_pd.h"
    if libpd_root.is_dir() and not pd_h.is_file():
        print("Initializing nested libpd submodules (pure-data)...")
        run_optional(["git", "submodule", "update", "--init", "--recursive"], cwd=libpd_root)


def apply_juce_cmake_plugin_settings(cmake_path: Path, cfg: dict) -> None:
    """Patch juce_add_plugin(...) lines from cmake_settings and is_synth."""
    cs = cfg.get("cmake_settings") or {}
    is_synth = str(cfg.get("is_synth", "N")).upper() == "Y"
    text = cmake_path.read_text(encoding="utf-8")
    text = _replace_cmake_line(text, "COMPANY_NAME", cs.get("company_name", "aldenbraverman"))
    text = _replace_cmake_line(text, "IS_SYNTH", "TRUE" if is_synth else "FALSE")
    text = _replace_cmake_line(
        text, "NEEDS_MIDI_INPUT", str(cs.get("needs_midi_input", "FALSE")).upper()
    )
    text = _replace_cmake_line(
        text, "NEEDS_MIDI_OUTPUT", str(cs.get("needs_midi_output", "FALSE")).upper()
    )
    text = _replace_cmake_line(
        text, "PLUGIN_MANUFACTURER_CODE", cs.get("plugin_manufacturer_code", "ALDB")
    )
    text = _replace_cmake_line(text, "PLUGIN_CODE", cs.get("plugin_code", "ALDB"))
    text = _replace_cmake_line(
        text, "NEEDS_WEBVIEW2", str(cs.get("needs_webview2", "TRUE")).upper()
    )
    fmts = cs.get("formats")
    if isinstance(fmts, list) and fmts:
        text = _replace_cmake_line(text, "FORMATS", " ".join(str(x) for x in fmts))
    cmake_path.write_text(text, encoding="utf-8")


def _replace_cmake_line(text: str, key: str, value: str) -> str:
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith(key + " "):
            indent = line[: len(line) - len(stripped)]
            out.append(f"{indent}{key} {value}\n")
        else:
            out.append(line)
    return "".join(out)


def apply_project_version(cmake_path: Path, version: str) -> None:
    text = cmake_path.read_text(encoding="utf-8")
    # project(Name VERSION x.y.z)
    import re

    text, n = re.subn(
        r"project\s*\(\s*[^\s]+\s+VERSION\s+[^\s)]+\s*\)",
        lambda m: re.sub(r"VERSION\s+[^\s)]+", f"VERSION {version}", m.group(0)),
        text,
        count=1,
    )
    if n:
        cmake_path.write_text(text, encoding="utf-8")


def run_hvcc_flow(cfg: dict, new_dir: Path, name: str, patch_path: Path, web_gen: str) -> None:
    heavy_dir = new_dir / "Heavy"
    new_dir.mkdir(parents=True, exist_ok=True)
    heavy_dir.mkdir(parents=True, exist_ok=True)

    if not patch_path.is_file():
        raise SystemExit(f"Patch not found: {patch_path}")

    shutil.copy2(patch_path, new_dir / patch_path.name)
    shutil.copy2(cfg["_config_path"], new_dir / cfg["_config_path"].name)

    hvcc_input = new_dir / patch_path.name
    generator_arg = "js" if str(web_gen).upper() == "Y" else "c"

    run(
        [
            "hvcc",
            str(hvcc_input),
            "-o",
            str(heavy_dir),
            "-n",
            name,
            "-g",
            generator_arg,
            "-p",
            str(REPO_ROOT / "libs" / "heavylib"),
        ]
    )
    run_py(REPO_ROOT / "utils" / "parse_params.py", [str(heavy_dir), name])


def juce_cmake_copy(
    cfg: dict,
    new_dir: Path,
    name: str,
    *,
    template_subdir: str,
) -> None:
    tmpl = REPO_ROOT / template_subdir
    plugin_dst = new_dir / "plugin"
    plugin_dst.mkdir(parents=True, exist_ok=True)
    (plugin_dst / "include" / name).mkdir(parents=True, exist_ok=True)

    shutil.copytree(tmpl / "plugin" / "src", plugin_dst / "src", dirs_exist_ok=True)
    ui_src = tmpl / "plugin" / "ui"
    if ui_src.is_dir():
        shutil.copytree(ui_src, plugin_dst / "ui", dirs_exist_ok=True)
    shutil.copy2(tmpl / "CMakeLists.txt", new_dir / "CMakeLists.txt")
    shutil.copy2(tmpl / "plugin" / "CMakeLists.txt", plugin_dst / "CMakeLists.txt")

    inc_src = tmpl / "plugin" / "include" / "Boiler_plate"
    inc_dst = plugin_dst / "include" / name
    for f in inc_src.iterdir():
        shutil.copy2(f, inc_dst / f.name)

    targets = [
        plugin_dst / "src" / "PluginEditor.cpp",
        plugin_dst / "src" / "PluginProcessor.cpp",
        plugin_dst / "include" / name / "PluginEditor.h",
        plugin_dst / "include" / name / "PluginProcessor.h",
        plugin_dst / "CMakeLists.txt",
        new_dir / "CMakeLists.txt",
    ]
    rb = REPO_ROOT / "utils" / "replace_boilerplate.py"
    for p in targets:
        if p.is_file():
            run_py(rb, [str(p), name])

    ver = cfg.get("project_version", "0.1.0")
    apply_project_version(new_dir / "CMakeLists.txt", str(ver))
    apply_juce_cmake_plugin_settings(plugin_dst / "CMakeLists.txt", cfg)


def hvcc_postprocess(cfg: dict, new_dir: Path, name: str, is_synth: str) -> None:
    plugin_dst = new_dir / "plugin"
    cpp_path = plugin_dst / "src" / "PluginProcessor.cpp"
    params_json = new_dir / "Heavy" / f"Heavy_{name}_params.json"
    add_cpp = REPO_ROOT / "utils" / "add_params_to_cpp.py"
    for rel in (
        "src/PluginProcessor.cpp",
        "src/PluginProcessor.h",
        "include/" + name + "/PluginEditor.h",
        "include/" + name + "/PluginProcessor.h",
    ):
        p = plugin_dst / rel
        if p.is_file():
            run_py(add_cpp, [str(p), str(params_json)])

    run_py(REPO_ROOT / "utils" / "add_params_to_layout.py", [str(params_json), str(cpp_path)])
    run_py(REPO_ROOT / "utils" / "add_params_to_update.py", [str(cpp_path), str(params_json)])
    run_py(REPO_ROOT / "utils" / "is_synth_note_on_off.py", [is_synth, str(cpp_path)])
    run_py(REPO_ROOT / "utils" / "init_prepare_to_play.py", [str(cpp_path), name])
    run_py(
        REPO_ROOT / "utils" / "exclude_hvcc_c_files.py",
        [str(plugin_dst / "CMakeLists.txt"), str(new_dir / "Heavy" / "c")],
    )
    run_py(REPO_ROOT / "utils" / "move_headers.py", [str(new_dir / "Heavy" / "c")])


def libpd_prepare_pd_files(cfg: dict, new_dir: Path, patch_path: Path) -> None:
    pd_dir = new_dir / "plugin" / "pd"
    if pd_dir.exists():
        shutil.rmtree(pd_dir)
    pd_dir.mkdir(parents=True)

    shutil.copy2(patch_path, pd_dir / "main.pd")

    libpd_cfg = cfg.get("libpd") or {}
    paths = libpd_cfg.get("search_paths") or []
    if paths:
        print(
            "Note: libpd search_paths are copied under plugin/pd/extra/ for bundling; "
            "ensure patches only reference relative abstractions there."
        )
    for i, rel in enumerate(paths):
        p = (REPO_ROOT / rel).resolve() if not os.path.isabs(rel) else Path(rel)
        dest = pd_dir / "extra" / f"path_{i}"
        if p.is_dir():
            shutil.copytree(p, dest, dirs_exist_ok=True)
        elif p.is_file():
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dest / p.name)


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate JUCE project from config JSON.")
    ap.add_argument("-c", "--config", required=True, help="Path to config JSON")
    args = ap.parse_args()
    cfg_path = Path(args.config).resolve()
    if not cfg_path.is_file():
        raise SystemExit(f"Config not found: {cfg_path}")

    cfg = load_config(cfg_path)
    cfg["_config_path"] = cfg_path
    validate_common(cfg)

    engine = str(cfg.get("audio_engine", "hvcc")).lower()
    if engine not in ("hvcc", "libpd"):
        raise SystemExit(f"Unknown audio_engine: {engine!r} (use hvcc or libpd)")

    tag = cfg["folder_name"]
    name = cfg["project_name"]
    patch_path = (REPO_ROOT / cfg["pd_paths"]["patch_path"]).resolve()
    is_synth = str(cfg.get("is_synth", "N"))
    web_gen = str(cfg.get("web_gen", "N"))

    if engine == "libpd" and str(web_gen).upper() == "Y":
        print("Warning: web_gen=Y is ignored for audio_engine=libpd (WASM still requires hvcc).")

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    new_dir = REPO_ROOT / "outputs" / f"{ts}_{tag}"
    new_dir.mkdir(parents=True, exist_ok=True)
    os.environ["new_dir_export"] = str(new_dir)

    install_git_submodules()

    if engine == "hvcc":
        run_hvcc_flow(cfg, new_dir, name, patch_path, web_gen)
        juce_cmake_copy(cfg, new_dir, name, template_subdir="plugin_template")
        hvcc_postprocess(cfg, new_dir, name, is_synth)
        (new_dir / "Heavy" / "h").mkdir(parents=True, exist_ok=True)
    else:
        init_libpd_submodule()
        if not patch_path.is_file():
            raise SystemExit(f"Patch not found: {patch_path}")
        shutil.copy2(cfg_path, new_dir / cfg_path.name)
        juce_cmake_copy(cfg, new_dir, name, template_subdir="plugin_template_libpd")
        libpd_prepare_pd_files(cfg, new_dir, patch_path)

    print("-" * 50)
    print(f"Generated project in: {new_dir}")
    print("-" * 50)


if __name__ == "__main__":
    main()
