from pathlib import Path


def get_file_line_by_line(filename):
    with open(filename, 'r', encoding="utf-8") as f:
        for line in f:
            yield line


def get_abs_path_for_file(filename):
    return Path(filename).absolute()
