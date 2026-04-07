from errors.parser_errors import *


def check_extension(filename):
    ext = filename.split(".")[-1]
    if ext != "jack":
        raise ERR_WRONG_EXTENSION


def open_file(filename):
    check_extension(filename)
    with open(filename, encoding="utf-8", mode="r") as f:
        try:
            text = f.read().strip()
        except Exception:
            raise ERR_PARSE_READING_FILE
    return text
