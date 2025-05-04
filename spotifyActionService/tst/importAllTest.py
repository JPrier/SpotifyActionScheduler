import importlib
import os
import sys


def test_import_all_modules() -> None:
    here = os.path.dirname(__file__)
    src_dir = os.path.abspath(os.path.join(here, "..", "src"))
    sys.path.insert(0, src_dir)

    for root, _, files in os.walk(src_dir):
        for fn in files:
            if not fn.endswith(".py") or fn.startswith("__"):
                continue
            full_path = os.path.join(root, fn)
            rel_path = os.path.relpath(full_path, src_dir)
            module_name = os.path.splitext(rel_path)[0].replace(os.sep, ".")
            importlib.import_module(module_name)
