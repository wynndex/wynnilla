from pathlib import Path
import shutil
import json
import os
import re

import compiler

BUILDERS_DIR = "build/sources/"
INFO_BOXES_DEST_DIR = "docs/generated/"

used_splayed_fonts = []

def do_builder():
    compiler.do_compiler()

    source_files = [f for f in list(Path(BUILDERS_DIR).rglob("*")) if f.is_file()]

    for item in Path(INFO_BOXES_DEST_DIR).iterdir():
        if item.is_file() or item.is_symlink():
            item.unlink()
        else:
            shutil.rmtree(item)

    for file in source_files:
        print(f"Builder: {file}")
        with file.open("r") as f:
            content: list = json.load(f)
            output = []
            wrappers = {}
            # Loop through
            content_pointer = 0
            while content_pointer < len(content):
                item = content[content_pointer]
                # If it is a wrapper
                if item["target"].startswith("incr:"):
                    wrapper_lit = item["target"].replace("incr:", "")
                    if wrapper_lit not in wrappers or wrappers[wrapper_lit] == 0:
                        wrappers[wrapper_lit] = 1
                        output.append(item["value"])
                    else:
                        wrappers[wrapper_lit] += 1
                elif item["target"].startswith("decr:"):
                    wrapper_lit = item["target"].replace("decr:", "")
                    if wrapper_lit not in wrappers or wrappers[wrapper_lit] == 0:
                        raise Exception
                    elif wrappers[wrapper_lit] == 1:
                        output.append(item["value"])
                    wrappers[wrapper_lit] -= 1
                # If it is another buildfile
                elif item["target"].endswith(".json"):
                    with open(os.path.join(BUILDERS_DIR, item["target"]), "r") as f2:
                        for sub_item in json.load(f2)[::-1]:
                            if "x" in sub_item and "y" in sub_item:
                                sub_item["x"] += item["x"]
                                sub_item["y"] += item["y"]
                            content.insert(content_pointer + 1, sub_item)
                # Else it is a compiled file
                else:
                    if item["x"] != 0:
                        output.append(f"{{$pan@{item["x"]}}};")
                    output.append(f"{{{item["target"]}({item["y"]})}};")
                    if item["x"] != 0:
                        output.append(f"{{$pan@{-item["x"]}}};")
                content_pointer += 1

            for i, item in enumerate(output):
                output[i] = compiler.parse_curly_expressions(
                    item,
                    compiler.global_function_map,
                    {})

        destination_path = Path(os.path.join(INFO_BOXES_DEST_DIR), str(file).replace("final", "").replace(".json",".infobox"))
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        evaluated_output_string = "".join(output)[:-1].replace(" ","").replace("|", " ")
        destination_path.write_text(f"{{with_font(concat_st({evaluated_output_string});\"wynnilla:ui\")}}")
        # destination_path.write_text(f"{{concat({evaluated_output_string})}}")

        pattern = r"wynnilla:.*?/offset_\d+"

        matches = re.findall(pattern, evaluated_output_string)

        used_splayed_fonts.extend(matches)

def trim_splayed_fonts():
    source_files = [f for f in list(Path("pack/Wynnilla UI/assets/wynnilla/font").rglob("*")) if f.is_file()]
    for fileobj in source_files:
        if fileobj.name == "ui.json":
            continue
        testing_name = f"wynnilla:{fileobj.parent.name}/{Path(fileobj.name)}".replace(".json","")
        if testing_name not in used_splayed_fonts:
            fileobj.unlink()

if __name__ == "__main__":
    do_builder()

    compiler.trim_font(Path("pack/Wynnilla UI/assets/wynnilla/font/ui.json"))
    trim_splayed_fonts()