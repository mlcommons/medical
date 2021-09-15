import subprocess
import yaml
import os
from pathlib import Path


class Cube(object):
    def __init__(self, uid, cube_path, params_path):
        self.uid = uid
        self.cube_path = cube_path
        self.params_path = params_path

    def run(self, **kwargs):
        cmd = f"mlcube run --mlcube={self.cube_path}"
        for k, v in kwargs.items():
            if k == "task":
                cmd_arg = f"--{k}={v}"
            else:
                cmd_arg = f"{k}={v}"
            cmd = " ".join([cmd, cmd_arg])

        splitted_cmd = cmd.split()

        subprocess.check_call(splitted_cmd, cwd=".")
        # process.wait()

    def get_default_output(self, task: str, out_key: str, param_key: str = None) -> str:
        """Returns the output parameter specified in the mlcube.yaml file

        Args:
            task (str): the task of interest
            out_key (str): key used to identify the desired output in the yaml file
            param_key (str): OPTIONAL. key inside the parameters file that completes the output path

        Returns:
            str: the path as specified in the mlcube.yaml file for the desired
                output for the desired task
        """
        with open(self.cube_path, "r") as f:
            cube = yaml.full_load(f)

        out_path = cube["tasks"][task]["parameters"]["outputs"][out_key]
        if type(out_path) == dict:
            # output is specified as a dict with type and default values
            out_path = out_path["default"]
        cube_loc = str(Path(self.cube_path).parent)
        out_path = os.path.join(cube_loc, "workspace", out_path)

        if self.params_path is not None and param_key is not None:
            with open(self.params_path, "r") as f:
                params = yaml.full_load(f)

            out_path = os.path.join(out_path, params[param_key])

        return out_path
