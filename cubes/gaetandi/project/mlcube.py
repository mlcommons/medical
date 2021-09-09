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
    - model_dir [str]: path for storing the model.
    """

    @staticmethod
    def run(model_dir: str) -> None:

        env = os.environ.copy()
        env.update(
            {
                "MODEL_DIR": model_dir,
            }
        )

        process = subprocess.Popen("./download_model.sh", cwd=".", env=env)
        process.wait()


class InferTask(object):
    """
    Inference task for generating predictions on the CheXpert dataset.

    Arguments:
    - log_dir [str]: logging location.
    - data_dir [str]: data location.
    - model_dir [str]: model location.
    - out_dir [str]: location for storing the predictions.
    """

    @staticmethod
    def run(data_dir: str, model_dir: str, out_dir) -> None:
        cmd = f"python3 chexpert.py --data_path={data_dir} --model_path={model_dir} --out_path={out_dir}"
        splitted_cmd = cmd.split()

        process = subprocess.Popen(splitted_cmd, cwd=".")
        process.wait()


@app.command("download_model")
def download_model(model_dir: str = typer.Option(..., "--model_dir")):
    DownloadModelTask.run(model_dir)


@app.command("infer")
def infer(
    data_dir: str = typer.Option(..., "--data_dir"),
    model_dir: str = typer.Option(..., "--model_dir"),
    out_dir: str = typer.Option(..., "--out_dir"),
):
    InferTask.run(data_dir, model_dir, out_dir)


if __name__ == "__main__":
    app()
