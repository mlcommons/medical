"""MLCube handler file"""
import os
import yaml
import typer
import shutil
import subprocess
from pathlib import Path


app = typer.Typer()


class DownloadModelTask(object):
    """
    Downloads model config and checkpoint files
    Arguments:
    - model_path [str]: path for storing the model.
    """

    @staticmethod
    def run(model_path: str) -> None:

        env = os.environ.copy()
        env.update(
            {"MODEL_DIR": model_path,}
        )

        process = subprocess.Popen("./download_model.sh", cwd=".", env=env)
        process.wait()


class InferTask(object):
    """
    Inference task for generating predictions on the CheXpert dataset.

    Arguments:
    - log_path [str]: logging location.
    - data_path [str]: data location.
    - model_path [str]: model location.
    - out_path [str]: location for storing the predictions.
    """

    @staticmethod
    def run(data_path: str, model_path: str, out_path) -> None:
        cmd = f"python3 chexpert.py --data_path={data_path} --model_path={model_path} --out_path={out_path}"
        splitted_cmd = cmd.split()

        process = subprocess.Popen(splitted_cmd, cwd=".")
        process.wait()


@app.command("download_model")
def download_model(model_path: str = typer.Option(..., "--model_path")):
    DownloadModelTask.run(model_path)


@app.command("infer")
def infer(
    data_path: str = typer.Option(..., "--data_path"),
    model_path: str = typer.Option(..., "--model_path"),
    out_path: str = typer.Option(..., "--output_path"),
):
    InferTask.run(data_path, model_path, out_path)


if __name__ == "__main__":
    app()
