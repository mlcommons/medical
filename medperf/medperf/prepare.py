import os
import typer
from yaspin import yaspin

from .config import config
from .server import Server
from .cube import Cube
from .registration import Registration
from .utils import (
    generate_tmp_datapath,
    get_file_sha1,
    init_storage,
    cleanup,
    pretty_error,
)


class DataPreparation:
    @staticmethod
    def run(benchmark_uid: str, data_path: str, labels_path: str):
        data_path = os.path.abspath(data_path)
        labels_path = os.path.abspath(labels_path)
        out_path, out_datapath = generate_tmp_datapath()
        server = Server(config["server"])
        init_storage()
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

            params_path = None
            if prep_meta["includes_parameters"]:
                sp.text = "Downloading parameters file..."
                params_path = server.get_cube_params(cube_uid)
                sp.write("> Paramaters file download complete")

            cube = Cube(cube_uid, cube_path, params_path)
            sp.text = "Running Cube"

            cube.run(
                task="prepare",
                data_path=data_path,
                labels_path=labels_path,
                output_path=out_datapath,
            )
            sp.write("> Cube execution complete")

            sp.text = "Running sanity checks"
            cube.run(task="sanity_check", data_path=out_datapath)
            sp.write("> Sanity checks complete")

            sp.text = "Generating statistics"
            cube.run(task="statistics", data_path=out_datapath)
            sp.write("> Statistics complete")

            sp.text = "Starting registration procedure"
            registration = Registration(cube, "testuser")
        if registration.request_approval():
            registration.retrieve_additional_data()
            reg_path = registration.write(out_path)
            out_path = registration.to_permanent_path(out_path, reg_path)
            typer.echo("Uploading")
            server.upload_dataset(out_path)
            typer.echo("✅ Done!")
        else:
            pretty_error("Registration operation cancelled")
        cleanup()
