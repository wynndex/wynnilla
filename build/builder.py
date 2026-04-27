from pathlib import Path
import shutil
import json
import os

import compiler

BUILDERS_DIR = "build/sources/"
INFO_BOXES_DEST_DIR = "generated/"

def do_builder():
    compiler.do_compiler()

    font_files = list(Path(BUILDERS_DIR).rglob("*"))

    for item in Path(INFO_BOXES_DEST_DIR).iterdir():
        if item.is_file() or item.is_symlink():
            item.unlink()
        else:
            shutil.rmtree(item)

    for file in font_files:
        with file.open("r") as f:
            content = json.load(f)
            output = []
            for item in content:
                output.append(f"{{$pan@{item["x"]}}};")
                output.append(f"{{{item["target"]}({item["y"]})}};")
                output.append(f"{{$pan@{-item["x"]}}};")

            for i, item in enumerate(output):
                output[i] = compiler.parse_curly_expressions(
                    item,
                    compiler.global_function_map,
                    {})

        destination_path = Path(os.path.join(INFO_BOXES_DEST_DIR), str(file).replace("final", "").replace(".json",""))
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        destination_path.write_text(f"{{with_font(concat_st({"".join(output)[:-1].replace(" ","").replace("|", " ")});\"wynnilla:ui\")}}")

if __name__ == "__main__":
    do_builder()