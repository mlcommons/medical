import typer
from .prepare import DataPreparation

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
    DataPreparation.run(benchmark_uid, data_path, labels_path)


@app.command("execute")
def execute(
    benchmark_uid: str = typer.Option(
        ..., "--benchmark", "-b", help="UID of the desired benchmark"
    ),
    data_uid: str = typer.Option(
        ..., "--data_uid", "-d", help="Registered Dataset UID"
    ),
):
    pass


if __name__ == "__main__":
    app()
