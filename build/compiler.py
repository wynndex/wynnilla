import os
from pathlib import Path
import json
import shutil
import math
import re as regex

FUNCTIONS_DIR = "compile/sources/function/"
FONTS_DIR = "compile/sources/font/"
FONTS_DEST_DIR = "pack/Wynnilla UI/assets/wynnilla/font/"
FUNCTIONS_DEST_DIR = "generated/"
FONT_TEMPLATE = "compile/sources/template/font.json"
SPLAY_DEPTH = 100

global_character_map = {}
global_function_map = {}

class Logging: depth = 0

def log(msg):
    print(f"{"  " * Logging.depth}{msg}")

def compile_font(font_file: Path):
    local_character_map = {}

    class ID: _v = 2048

    def id():
        ID._v += 1
        return ID._v
    
    with font_file.open("r") as handle:
        content = json.load(handle)

        with open(FONT_TEMPLATE, "r") as f:
            template = json.load(f)

        for entry, value in content["spaces"].items():
            match value["function"]:
                case "static_character":
                    template["providers"][1]["advances"][chr(value["character"])] = value["value"]
                    local_character_map[entry] = value["character"]
                case "add_1" | "subtract_1" | "add_half" | "subtract_half":
                    op = lambda a, b: a
                    if value["function"] == "add_1":
                        op = lambda a, b: a + b
                    elif value["function"] == "subtract_1":
                        op = lambda a, b: a - b
                    elif value["function"] == "add_half":
                        op = lambda a, b: a + math.floor(b / 2)
                    elif value["function"] == "subtract_half":
                        op = lambda a, b: a - math.floor(b / 2)
                    for i in range(value["limit"]):
                        this_id = id()
                        template["providers"][1]["advances"][chr(this_id)] = op(value["start"], i)
                        if i == 0:
                            local_character_map[entry] = (this_id, 1)

        for entry, value in content["textures"].items():
            if "function" in value:
                if value["function"] == "override":
                    injection = {
                        "ascent": 0,
                        "chars": value["chars"],
                        "file": value["path"],
                        "height": value["height"],
                        "type": "bitmap"
                    }
                    template["providers"].append(injection)
            else:
                for i in range(SPLAY_DEPTH):
                    w, h = value["chars"]
                    these_id = [id() for _ in range(w * h)]
                    injection = {
                        "ascent": -i,
                        "chars": ["".join(chr(these_id[a + b * w]) for a in range(w)) for b in range(h)],
                        "file": value["path"],
                        "height": value["height"],
                        "type": "bitmap"
                    }
                    template["providers"].append(injection)
                    if i == 0:
                        local_character_map[entry] = (these_id[0], w * h)

        if "meta" in content:
            if "function" in content["meta"]:
                if content["meta"]["function"] == "splay":
                    dir_path = os.path.join(FONTS_DEST_DIR, str(font_file).replace(FONTS_DIR, "").replace(".json", ""))
                    os.mkdir(dir_path)
                    for i in range(SPLAY_DEPTH):
                        if i != 0:
                            for entry in template["providers"][2:]:
                                entry["ascent"] -= 1
                        with open(os.path.join(dir_path, f"offset_{i}.json"), "w+") as f:
                            json.dump(template, f, indent=2)
        else:
            dest = os.path.join(FONTS_DEST_DIR, str(font_file).replace(FONTS_DIR, ""))
            global_character_map[dest.replace(FONTS_DEST_DIR,"").replace(".json","")] = local_character_map
            with open(dest, "w+") as f:
                json.dump(template, f, indent=2)

def echo_and_print(match):
    print(match.group(1))
    return match.group(1)

def split_at_next(literal, match):
    for i, char in enumerate(literal[1:]):
        if char in match:
            return literal[:i+1], literal[i+1:]
    return literal, ""

def parse_curly_expressions(literal, function_map, argument_pool) -> str:
    output = []
    depth = 0
    ptr = 0
    for i, char in enumerate(literal):
        if char == "{":
            if depth == 0:
                output.append(literal[ptr:i])
                ptr = i + 1
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                expval = parse_curly_expressions(literal[ptr:i], function_map, argument_pool)
                ptr = i + 1

                if "{" in expval or "}" in expval:
                    output.append(f"{{{expval}}}")
                    continue

                if expval[0] == ":":
                    value_parts = expval[1:].split("+")
                    if value_parts[0] in argument_pool:
                        if len(value_parts) > 1:
                            output.append(str(int(argument_pool[value_parts[0]])+int(value_parts[1])))
                        else:
                            output.append(argument_pool[value_parts[0]])
                    else:
                        output.append(f"{{{expval}}}")
                elif expval[0] == "$":
                    continuation = expval
                    texture_spec = {}
                    while continuation:
                        select, continuation = split_at_next(continuation, ["@", "^", "."])
                        if select[0] == "$":
                            texture_spec["id"] = select[1:]
                        elif select[0] == "^":
                            texture_spec["offset"] = int(select[1:])
                        elif select[0] == ".":
                            texture_spec["mod"] = select[1:]
                        elif select[0] == "@":
                            texture_spec["slot"] = int(select[1:])
                    char_id = global_character_map["ui"][texture_spec["id"]][0]
                    if "slot" in texture_spec:
                        char_id += texture_spec["slot"]
                    if "offset" in texture_spec:
                        char_id += texture_spec["offset"] * global_character_map["ui"][texture_spec["id"]][1]
                    if "mod" in texture_spec:
                        if texture_spec["mod"] == "V":
                            output.append(f"{char_id}")
                    else:
                        # output.append(f"styled_text(\"{chr(char_id)}\")")
                        output.append(f"st(from_codepoint({char_id}))")
                else:
                    function_call_name = expval[0:expval.index("(")]
                    function_call_args = expval[expval.index("(")+1:-1].split(", ")

                    if isinstance(function_map[function_call_name], Path):
                        compile_function(
                            function_map[function_call_name],
                            function_call_name,
                            function_map
                        )

                    arg_pool_copy = argument_pool.copy()
                    for k, v in zip(function_map[function_call_name][1], function_call_args):
                        arg_pool_copy[k] = v
                    target_content = parse_curly_expressions(
                        function_map[function_call_name][0], function_map, arg_pool_copy
                    )

                    output.append(target_content)
    
    output.append(literal[ptr:])

    return "".join(output)

def compile_function(file, name, function_map):
    print(f"Compiler: {name}")
    with file.open("r") as f:
        content = f.read().split("\n")
        arguments = content[0].split(" ")
        function_raw = "".join(content[1:])

        function_raw = parse_curly_expressions(function_raw, function_map, {})

        function_map[name] = (function_raw, arguments)

def strip_filename(fp, parent):
    return str(fp).replace(parent, "").replace(".wynn", "")

def do_compiler():
    font_files = list(Path(FONTS_DIR).rglob("*"))

    for item in Path(FONTS_DEST_DIR).iterdir():
        if item.is_file() or item.is_symlink():
            item.unlink()
        else:
            shutil.rmtree(item)

    for file in font_files:
        compile_font(file)

    function_files = [f for f in list(Path(FUNCTIONS_DIR).rglob("*")) if f.is_file()]

    for item in Path(FUNCTIONS_DEST_DIR).iterdir():
        if item.is_file() or item.is_symlink():
            item.unlink()
        else:
            shutil.rmtree(item)

    function_map = global_function_map

    for file in function_files:
        file_id = strip_filename(file, FUNCTIONS_DIR)
        function_map[file_id] = file

    while True:
        fid_found = False
        for file, value in function_map.items():
            if isinstance(value, Path):
                compile_function(value, file, function_map)
                fid_found = True
                break
        if not fid_found:
            break

    # for k, v in function_map.items():
    #     print(f"{k}: {v}\n")

if __name__ == "__main__":
    do_compiler()