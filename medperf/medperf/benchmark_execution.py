from medperf.utils import check_cube_validity
import typer
import os
from pathlib import Path
from yaspin import yaspin

from medperf.entities import Benchmark
from medperf.entities import Dataset
from medperf.entities import Cube
from medperf.utils import check_cube_validity, init_storage, pretty_error, cleanup
from medperf.config import config
from medperf.entities import Result


class BenchmarkExecution:
    @staticmethod
    def run(benchmark_uid: str, data_uid: str, model_uid: str):
        """Benchmark execution flow.

        Args:
            benchmark_uid (str): UID of the desired benchmark
            data_uid (str): Registered Dataset UID
            model_uid (str): UID of model to execute
        """
        init_storage()
        benchmark = Benchmark.get(benchmark_uid)
        dataset = Dataset(data_uid)

        if dataset.preparation_cube_uid != benchmark.data_preparation:
            pretty_error(
                "The provided dataset is not compatible with the specified benchmark."
            )

        if model_uid not in benchmark.models:
            pretty_error("The provided model is not part of the specified benchmark.")

        cube_uid = benchmark.evaluator
        with yaspin(
            text=f"Retrieving evaluator cube: '{cube_uid}'", color="green"
        ) as sp:
            evaluator = Cube.get(cube_uid)
            sp.write("> Evaluator cube download complete")

            check_cube_validity(evaluator, sp)

            sp.write(f"> Initiating model execution: '{model_uid}'")
            model_cube = Cube.get(model_uid)
            check_cube_validity(model_cube, sp)

            sp.write("Running model inference on dataset")
            out_path = config["model_output"]
            with sp.hidden():
                model_cube.run(
                    task="infer", data_path=dataset.data_path, output_path=out_path
                )
            sp.write("> Model execution complete")

            cube_root = str(Path(model_cube.cube_path).parent)
            workspace_path = os.path.join(cube_root, "workspace")
            abs_preds_path = os.path.join(workspace_path, out_path)
            labels_path = os.path.join(dataset.data_path, "data.csv")

            sp.write("Evaluating results")
            out_path = config["results_storage"]
            out_path = os.path.join(
                out_path, benchmark.uid, model_uid, dataset.data_uid
            )
            out_path = os.path.join(out_path, "results.yaml")
            with sp.hidden():
                evaluator.run(
                    task="evaluate",
                    preds_csv=abs_preds_path,
                    labels_csv=labels_path,
                    output_path=out_path,
                )

            result = Result(out_path, benchmark.uid, dataset.data_uid, model_uid)
            with sp.hidden():
                approved = result.request_approval()
            if approved:
                typer.echo("Uploading")
                result.upload()
                typer.echo("✅ Done!")
            else:
                pretty_error("Results upload operation cancelled")
            cleanup()

