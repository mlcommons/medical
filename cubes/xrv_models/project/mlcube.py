import typer
import subprocess

app = typer.Typer()


def exec_python(cmd: str) -> None:
    splitted_cmd = cmd.split()
    process = subprocess.Popen(splitted_cmd, cwd=".")
    process.wait()


class InferTask(object):
    """
    Task for generating inferences on data

    Arguments:
    - data_dir [str]: location of prepared data
    - params_file [str]: file containing parameters for inference
    - out_dir [str]: location for storing inferences
    """

    @staticmethod
    def run(data_dir: str, params_file: str, out_dir: str) -> None:
        cmd = f"python3 model.py --data_dir={data_dir} --params_file={params_file} --out_dir={out_dir}"
        exec_python(cmd)


@app.command("hotfix")
def hotfix():
    pass


@app.command("infer")
def infer(
    data_dir: str = typer.Option(..., "--data_dir"),
    params_file: str = typer.Option(..., "--parameters_file"),
    out_dir: str = typer.Option(..., "--out_dir"),
):
    InferTask.run(data_dir, params_file, out_dir)


if __name__ == "__main__":
    app()
