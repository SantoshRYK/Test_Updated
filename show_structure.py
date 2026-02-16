import os
from pathlib import Path

def print_tree(directory, prefix="", ignore_dirs={'.git', '__pycache__', 'venv', 'env', '.venv'}):
    contents = sorted(Path(directory).iterdir(), key=lambda x: (x.is_file(), x.name))
    for i, path in enumerate(contents):
        if path.name in ignore_dirs or path.name.startswith('.'):
            continue
        is_last = i == len(contents) - 1
        print(f"{prefix}{'└── ' if is_last else '├── '}{path.name}")
        if path.is_dir():
            extension = "    " if is_last else "│   "
            print_tree(path, prefix + extension, ignore_dirs)

print_tree(".")