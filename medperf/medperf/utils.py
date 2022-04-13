import hashlib
import os
from .config import config
from shutil import rmtree
import typer


def get_file_sha1(path):
    BUF_SIZE = 65536
    sha1 = hashlib.sha1()
    with open(path, "rb") as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha1.update(data)

    return sha1.hexdigest()


def init_storage():
    storage = config["tmp_storage"]
    if not os.path.isdir(storage):
        os.mkdir(storage)


def cleanup():
    storage = config["tmp_storage"]
    rmtree(storage)


def pretty_error(msg):
    msg = "❌ " + msg
    msg = typer.style(msg, fg=typer.colors.RED, bold=True)
    typer.echo(msg)
    cleanup()
    exit()
