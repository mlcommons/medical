import os
import typer
from yaspin import yaspin

from medperf.entities import Benchmark, Cube, Registration, Server
from medperf.config import config
from medperf.utils import (
    check_cube_validity,
    generate_tmp_datapath,
    init_storage,
    cleanup,
    pretty_error,
)


class DataPreparation:
    @staticmethod
    def run(benchmark_uid: str, data_path: str, labels_path: str):
        """Data Preparation flow.

        Args:
            benchmark_uid (str): UID of the desired benchmark.
            data_path (str): Location of the data to be prepared.
            labels_path (str): Labels file location.
        """
        server = Server(config["server"])
        # TODO: find a way to store authentication credentials
        server.login("admin", "admin")
        data_path = os.path.abspath(data_path)
        labels_path = os.path.abspath(labels_path)
        out_path, out_datapath = generate_tmp_datapath()
        init_storage()
        benchmark = Benchmark.get(benchmark_uid, server)
        typer.echo(f"Benchmark: {benchmark.name}")

        cube_uid = benchmark.data_preparation
        with yaspin(
            text=f"Retrieving data preparation cube: '{cube_uid}'", color="green"
        ) as sp:
            cube = Cube.get(cube_uid, server)
            sp.write("> Preparation cube download complete")

            check_cube_validity(cube, sp)

            sp.text = "Running Cube"
            cube.run(
                task="prepare",
                data_path=data_path,
                labels_path=labels_path,
                # TODO: no need to do all the tmp output logic. Can be moved
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
            with sp.hidden():
                approved = registration.request_approval()
                if approved:
                    registration.retrieve_additional_data()
                    reg_path = registration.write(out_path)
                    sp.write("Uploading")
                    data_uid = registration.upload(server)
                    registration.to_permanent_path(out_path, data_uid)
                    sp.write("✅ Done!")
                else:
                    pretty_error("Registration operation cancelled")
            cleanup()
