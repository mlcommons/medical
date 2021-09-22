import typer

from .prepare import DataPreparation
from .benchmark_execution import BenchmarkExecution
from .dataset import Dataset
from tabulate import tabulate

app = typer.Typer()


@app.command("prepare")
def prepare(
    benchmark_uid: str = typer.Option(
        ..., "--benchmark", "-b", help="UID of the desired benchmark"
    ),
    data_path: str = typer.Option(
        ..., "--data_path", "-d", help="Location of the data to be prepared"
    ),
    labels_path: str = typer.Option(
        ..., "--labels_path", "-l", help="Labels file location"
    ),
):
    """Runs the Data preparation step for a specified benchmark and raw dataset

    Args:
        benchmark_uid (str): UID of the desired benchmark.
        data_path (str): Location of the data to be prepared.
        labels_path (str): Labels file location.
    """
    typer.echo("MedPerf 0.0.0")
    DataPreparation.run(benchmark_uid, data_path, labels_path)


@app.command("execute")
def execute(
    benchmark_uid: str = typer.Option(
        ..., "--benchmark", "-b", help="UID of the desired benchmark"
    ),
    data_uid: str = typer.Option(
        ..., "--data_uid", "-d", help="Registered Dataset UID"
    ),
    model_uid: str = typer.Option(
        ..., "--model_uid", "-m", help="UID of model to execute"
    ),
):
    """Runs the benchmark execution step for a given benchmark, prepared dataset and model

    Args:
        benchmark_uid (str): UID of the desired benchmark.
        data_uid (str): Registered Dataset UID.
        model_uid (str): UID of model to execute.
    """
    typer.echo("MedPerf 0.0.0")
    BenchmarkExecution.run(benchmark_uid, data_uid, model_uid)


@app.command("datasets")
def datasets():
    """Prints information about prepared datasets living locally
    """
    typer.echo("MedPerf 0.0.0")
    dsets = Dataset.all()
    headers = ["UID", "Name", "Data Preparation Cube UID"]
    dsets_data = [
        [dset.data_uid, dset.name, dset.preparation_cube_uid] for dset in dsets
    ]
    tab = tabulate(dsets_data, headers=headers)
    print(tab)


if __name__ == "__main__":
    app()
