import glob

from pathlib import Path

# there's also iglob for an iterator, which might be better depending on the use-case
py_files = glob.glob("../*/*.py")
# print(py_files)

for f in py_files:
    p = Path(f)
    print(f"found file {f} and full path is {p.absolute()}")
