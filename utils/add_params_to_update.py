import json
import os
import sys


def _load_params(json_path: str) -> list:
    if not os.path.exists(json_path):
        print(f"Error: JSON file not found: {json_path}")
        sys.exit(1)
    with open(json_path, "r", encoding="utf-8") as f:
        params = json.load(f)
    if not isinstance(params, list):
        print("Error: JSON file should contain a list of parameters.")
        sys.exit(1)
    return params


def _read_cpp_lines(cpp_path: str) -> list[str]:
    if not os.path.exists(cpp_path):
        print(f"Error: C++ file not found: {cpp_path}")
        sys.exit(1)
    with open(cpp_path, "r", encoding="utf-8") as f:
        return f.readlines()


def _write_cpp_lines(cpp_path: str, lines: list[str]) -> None:
    with open(cpp_path, "w", encoding="utf-8") as f:
        f.writelines(lines)


def _insert_after_markers(lines: list[str], marker: str, insert_lines_for_param):
    out: list[str] = []
    i = 0
    while i < len(lines):
        out.append(lines[i])
        if marker in lines[i]:
            for extra in insert_lines_for_param():
                out.append(extra)
        i += 1
    return out


def insert_param_updates(cpp_path: str, json_path: str) -> None:
    params = _load_params(json_path)
    lines = _read_cpp_lines(cpp_path)

    def gen_updates():
        for param in params:
            name = param["name"]
            hash_val = param["hash"]
            yield f"        float _{name} = {name}Param->get();\n"
            yield f"        hv_sendFloatToReceiver(context, {hash_val}, _{name});\n"

    updated = _insert_after_markers(lines, "@_ADD_PARAMS_TO_UPDATE_HERE", lambda: list(gen_updates()))
    _write_cpp_lines(cpp_path, updated)
    print(f"Parameter update code inserted into {cpp_path}.")


def insert_cast_param(cpp_path: str, json_path: str) -> None:
    params = _load_params(json_path)
    lines = _read_cpp_lines(cpp_path)

    def gen_casts():
        for param in params:
            name = param["name"]
            yield f"castParameter(apvts, ParameterID::{name}, {name}Param);\n"

    updated = _insert_after_markers(lines, "@_ADD_CAST_PARAMETERS_HERE", lambda: list(gen_casts()))
    _write_cpp_lines(cpp_path, updated)
    print(f"Cast parameter code inserted into {cpp_path}.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 utils/add_params_to_update.py <path_to_cpp> <path_to_json>")
        sys.exit(1)

    insert_param_updates(sys.argv[1], sys.argv[2])
    insert_cast_param(sys.argv[1], sys.argv[2])
