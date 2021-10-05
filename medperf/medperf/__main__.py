import typer
import logging
from tabulate import tabulate

from medperf import DataPreparation
from medperf import BenchmarkExecution
from medperf.entities import Dataset
from medperf.config import config


app = typer.Typer()


@app.command("prepare")
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
    logging.info("Running the 'prepare' command")
    DataPreparation.run(benchmark_uid, data_path, labels_path)


@app.command("execute")
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
    logging.info("Running the 'execute' command")
    BenchmarkExecution.run(benchmark_uid, data_uid, model_uid)


@app.command("datasets")
def datasets():
    """Prints information about prepared datasets living locally
    """
    logging.info("Running the 'execute' command")
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
