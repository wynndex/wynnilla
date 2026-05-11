from pathlib import Path
import shutil
import json
import os

import compiler

BUILDERS_DIR = "build/sources/"
INFO_BOXES_DEST_DIR = "generated/"

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
                    output.append(f"{{$pan@{item["x"]}}};")
                    output.append(f"{{{item["target"]}({item["y"]})}};")
                    output.append(f"{{$pan@{-item["x"]}}};")
                content_pointer += 1

            for i, item in enumerate(output):
                output[i] = compiler.parse_curly_expressions(
                    item,
                    compiler.global_function_map,
                    {})

        destination_path = Path(os.path.join(INFO_BOXES_DEST_DIR), str(file).replace("final", "").replace(".json",".infobox"))
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        destination_path.write_text(f"{{with_font(concat_st({"".join(output)[:-1].replace(" ","").replace("|", " ")});\"wynnilla:ui\")}}")

if __name__ == "__main__":
    do_builder()