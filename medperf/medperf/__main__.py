import typer
import logging
from tabulate import tabulate

from medperf import DataPreparation
from medperf import BenchmarkExecution
from medperf.entities import Dataset
from medperf.config import config
from medperf.utils import clean_except
from medperf import DatasetBenchmarkAssociation


app = typer.Typer()


@app.command("prepare")
@clean_except
def prepare(
    benchmark_uid: int = typer.Option(
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
        benchmark_uid (int): UID of the desired benchmark.
        data_path (str): Location of the data to be prepared.
        labels_path (str): Labels file location.
    """
    data_uid = DataPreparation.run(benchmark_uid, data_path, labels_path)
    DatasetBenchmarkAssociation.run(data_uid, benchmark_uid)


@app.command("execute")
@clean_except
def execute(
    benchmark_uid: int = typer.Option(
        ..., "--benchmark", "-b", help="UID of the desired benchmark"
    ),
    data_uid: int = typer.Option(
        ..., "--data_uid", "-d", help="Registered Dataset UID"
    ),
    model_uid: int = typer.Option(
        ..., "--model_uid", "-m", help="UID of model to execute"
    ),
):
    """Runs the benchmark execution step for a given benchmark, prepared dataset and model

    Args:
        benchmark_uid (int): UID of the desired benchmark.
        data_uid (int): Registered Dataset UID.
        model_uid (int): UID of model to execute.
    """
    BenchmarkExecution.run(benchmark_uid, data_uid, model_uid)


@app.command("associate")
@clean_except
def associate(
    data_uid: int = typer.Option(
        ..., "--data_uid", "-d", help="Registered Dataset UID"
    ),
    benchmark_uid: int = typer.Option(
        ..., "-benchmark_uid", "-b", help="Benchmark UID"
    ),
):
    DatasetBenchmarkAssociation.run(data_uid, benchmark_uid)


@app.command("datasets")
@clean_except
def datasets():
    """Prints information about prepared datasets living locally
    """
    dsets = Dataset.all()
    headers = ["UID", "Name", "Data Preparation Cube UID"]
    dsets_data = [
        [dset.data_uid, dset.name, dset.preparation_cube_uid] for dset in dsets
    ]
    tab = tabulate(dsets_data, headers=headers)
    print(tab)


@app.callback()
def main(log: str = "INFO", log_file: str = config["log_file"]):
    """Manage global configuration and options, like logging or shared initial prints

    Args:
        log (str, optional): Logging level to use. Defaults to "INFO".
        log_file (str, optional): File to use for logging. Defaults to the path defined in config.
    """
    log = log.upper()
    log_lvl = getattr(logging, log)
    log_fmt = "%(asctime)s | %(levelname)s: %(message)s"
    logging.basicConfig(filename=log_file, level=log_lvl, format=log_fmt)
    logging.info(f"Running MedPerf v{config['version']} on {log} logging level")
    typer.echo(f"MedPerf {config['version']}")


if __name__ == "__main__":
    app()
