def get_file_line_by_line(filename):
    with open(filename, 'r', encoding="utf-8") as f:
        for line in f:
                yield line

