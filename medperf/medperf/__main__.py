import os
import yaml
import typer
import requests
from pathlib import Path
from yaspin import yaspin
import subprocess

from .config import config
from .server import Server
from .utils import get_file_sha1, init_storage, cleanup, pretty_error

app = typer.Typer()


@app.command("prepare")
def prepare(
    benchmark_uid: str = typer.Option(
        ..., "--benchmark", "-b", help="UID of the desired benchmark"
    ),
    data_path: str = typer.Option(
        ..., "--data_path", "-d", help="Location of the data to be prepared"
    ),
):
    workspace_path = str(Path(data_path).parent)
    server = Server(config["server"])
    init_storage()
    typer.echo("MedPerf 0.0.0")
    benchmark = server.get_benchmark(benchmark_uid)
    typer.echo(f"Benchmark: {benchmark['name']}")

    cube_uid = benchmark["preprocessor"]
    with yaspin(
        text=f"Retrieving data preparation cube: '{cube_uid}'", color="green"
    ) as sp:
        prep_meta = server.get_cube_metadata(cube_uid)
        cube_path = server.get_cube(prep_meta["url"], cube_uid)
        sp.write("> Preparation cube download complete")

        sp.text = "Checking cube MD5 hash..."
        if get_file_sha1(cube_path) != prep_meta["sha1"]:
            pretty_error("MD5 hash doesn't match")
        sp.write("> Cube MD5 hash check complete")

        if prep_meta["includes_parameters"]:
            sp.text = "Downloading parameters file..."
            params_path = server.get_cube_params(cube_uid, workspace_path)
            sp.write("> Paramaters file download complete")

        sp.text = "Running Cube"
        execute_cube(
            cube_path, workspace=workspace_path, task="preprocess", data_path=data_path
        )
        sp.write("> Cube execution complete")

        sp.text = "Running sanity checks"
        execute_cube(cube_path, workspace=workspace_path, task="sanity_check")
        sp.write("> Sanity checks complete")

        sp.text = "Generating statistics"
        execute_cube(cube_path, workspace=workspace_path, task="statistics")
        sp.write("> Statistics complete")

        sp.text = "Starting registration procedure"
        reg_path = generate_registration_info(
            cube_path, workspace_path, params_path, cube_uid
        )
    approval = registration_approval(reg_path)
    if approval:
        typer.echo("Uploading")
        server.upload_dataset(reg_path)
        typer.echo("✅ Done!")
    else:
        pretty_error("Registration operation cancelled")
    cleanup()


def execute_cube(cube: str, **kwargs):
    cmd = f"mlcube run --mlcube={cube}"
    for k, v in kwargs.items():
        cmd_arg = f"--{k}={v}"
        cmd = " ".join([cmd, cmd_arg])

    splitted_cmd = cmd.split()

    process = subprocess.Popen(splitted_cmd, cwd=".")
    process.wait()


def generate_registration_info(cube_path, workspace_path, params_path, cube_uid):
    with open(cube_path, "r") as f:
        cube = yaml.full_load(f)

    with open(params_path, "r") as f:
        params = yaml.full_load(f)

    out_path = cube["tasks"]["statistics"]["parameters"]["outputs"]["out_path"]
    stats_path = os.path.join(workspace_path, out_path, params["output_statsfile"])

    with open(stats_path, "r") as f:
        stats = yaml.full_load(f)

    params_sha1 = get_file_sha1(params_path)
    registration = {
        "user_uid": "mock user",
        "cube uid": cube_uid,
        "parameters sha1": params_sha1,
        "metadata": stats,
    }

    out_path = os.path.join(config["tmp_storage"], cube_uid, "registration.yaml")

    with open(out_path, "w") as f:
        yaml.dump(registration, f)

    return out_path


def registration_approval(registration_path: str) -> bool:

    typer.echo()
    typer.echo("=" * 20)
    with open(registration_path, "r") as f:
        typer.echo(f.read())
    typer.echo("=" * 20)
    typer.echo(
        "Above is the information and statistics that will be registered to the database"
    )
    approval = None
    while approval not in ["Y", "N", "n"]:
        approval = input(
            "Do you approve the registration of the presented data to the MLCommons server? [Y/n] "
        )

    return approval == "Y"


if __name__ == "__main__":
    app()
