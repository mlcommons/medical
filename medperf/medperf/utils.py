from datetime import datetime
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
    parent = config["storage"]
    data = os.path.join(parent, "data")
    cubes = os.path.join(parent, "cubes")
    results = os.path.join(parent, "results")
    tmp = config["tmp_storage"]
    dirs = [parent, data, cubes, results, tmp]
    for dir in dirs:
        if not os.path.isdir(dir):
            os.mkdir(dir)


def cleanup():
    storage = config["tmp_storage"]
    rmtree(storage)


def pretty_error(msg, clean=True):
    msg = "❌ " + msg
    msg = typer.style(msg, fg=typer.colors.RED, bold=True)
    typer.echo(msg)
    if clean:
        cleanup()
    exit()


def cube_path(uid: str):
    return os.path.join(config["storage"], "cubes", uid)


def generate_tmp_datapath():
    dt = datetime.now()
    ts = str(int(datetime.timestamp(dt)))
    out_path = os.path.join(config["storage"], "data", ts)
    out_path = os.path.abspath(out_path)
    out_datapath = os.path.join(out_path, "data")
    if not os.path.isdir(out_datapath):
        os.makedirs(out_datapath)
    return out_path, out_datapath

