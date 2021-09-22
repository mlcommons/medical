from yaspin.core import Yaspin
from typing import List, Tuple
from datetime import datetime
import hashlib
import os
from .config import config
from shutil import rmtree
import tarfile
import typer
import yaml
from pathlib import Path

from .cube import Cube


def get_file_sha1(path: str) -> str:
    """Calculates the sha1 hash for a given file.

    Args:
        path (str): Location of the file of interest.

    Returns:
        str: Calculated hash
    """
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
    """Builds the general medperf folder structure.
    """
    parent = config["storage"]
    data = config["data_storage"]
    cubes = config["cubes_storage"]
    results = config["results_storage"]
    tmp = config["tmp_storage"]

    dirs = [parent, data, cubes, results, tmp]
    for dir in dirs:
        if not os.path.isdir(dir):
            os.mkdir(dir)


def cleanup():
    """Removes clutter and unused files from the medperf folder structure.
    """
    rmtree(config["tmp_storage"])
    dsets = get_dsets()
    prefix = config["tmp_reg_prefix"]
    unreg_dsets = [dset for dset in dsets if dset.startswith(prefix)]
    for dset in unreg_dsets:
        dset_path = os.path.join(config["data_storage"], dset)
        rmtree(dset_path)


def get_dsets() -> List[str]:
    """Retrieves the UID of all the datasets stored locally.

    Returns:
        List[str]: UIDs of prepared datasets.
    """
    data = config["data_storage"]
    dsets_path = os.path.join(config["storage"], data)
    dsets = next(os.walk(dsets_path))[1]
    return dsets


def pretty_error(msg: str, clean: bool = True):
    """Prints an error message with typer protocol and exits the script

    Args:
        msg (str): Error message to show to the user
        clean (bool, optional): Wether to run the cleanup process before exiting. Defaults to True.
    """
    msg = "❌ " + msg
    msg = typer.style(msg, fg=typer.colors.RED, bold=True)
    typer.echo(msg)
    if clean:
        cleanup()
    exit()


def cube_path(uid: str) -> str:
    """Gets the path for a given cube.

    Args:
        uid (str): Cube UID.

    Returns:
        str: Location of the cube folder structure.
    """
    return os.path.join(config["storage"], "cubes", uid)


def generate_tmp_datapath() -> Tuple[str, str]:
    """Builds a temporary folder for prepared but yet-to-register datasets.

    Returns:
        str: General temporary folder location
        str: Specific data path for the temporary dataset
    """
    dt = datetime.now()
    ts = str(int(datetime.timestamp(dt)))
    tmp = config["tmp_reg_prefix"] + ts
    out_path = os.path.join(config["storage"], "data", tmp)
    out_path = os.path.abspath(out_path)
    out_datapath = os.path.join(out_path, "data")
    if not os.path.isdir(out_datapath):
        os.makedirs(out_datapath)
    return out_path, out_datapath


def check_cube_validity(cube: Cube, sp: Yaspin):
    """Helper function for pretty printing the cube validity process.

    Args:
        cube (Cube): Cube to check for validity
        sp (Yaspin): yaspin instance being used
    """
    sp.text = "Checking cube MD5 hash..."
    if not cube.is_valid():
        pretty_error("MD5 hash doesn't match")
    sp.write("> Cube MD5 hash check complete")


def untar_additional(add_filepath: str) -> str:
    """Untars and removes the additional_files.tar.gz file

    Args:
        add_filepath (str): Path where the additional_files.tar.gz file can be found.

    Returns:
        str: location where the untared files can be found.
    """
    addpath = str(Path(add_filepath).parent)
    tar = tarfile.open(add_filepath)
    tar.extractall(addpath)
    tar.close()
    os.remove(add_filepath)
    return addpath


def approval_prompt(msg: str) -> bool:
    """Helper function for prompting the user for things they have to explicitly approve.

    Args:
        msg (str): What message to ask the user for approval.

    Returns:
        bool: Wether the user explicitly approved or not.
    """
    approval = None
    while approval not in ("Y", "N", "n"):
        approval = input(msg)

    return approval == "Y"


def dict_pretty_print(in_dict: dict):
    """Helper function for distinctively printing dictionaries with yaml format.

    Args:
        in_dict (dict): dictionary to print
    """
    typer.echo()
    typer.echo("=" * 20)
    in_dict = {k: v for (k, v) in in_dict.items() if v is not None}
    typer.echo(yaml.dump(in_dict))
    typer.echo("=" * 20)
