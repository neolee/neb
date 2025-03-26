from pathlib import Path


def list_files(parent: str, ext: str) -> list[Path]:
    p = Path(parent)
    files = [f for f in p.iterdir() if f.is_file() and f.suffix.lower() == ext]
    return files

def list_files_as_strs(parent: str, ext: str) -> list[str]:
    strs = [str(f) for f in list_files(parent, ext)]
    return strs


if __name__ == "__main__":
    files = list_files_as_strs("books", ".pdf")
    print(files)
