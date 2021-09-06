import requests
from pathlib import Path
import os

from .config import config
from .utils import pretty_error, get_file_sha1, cleanup


class Server:
    def __init__(self, server_url):
        self.server_url = server_url

    def get_benchmark(self, benchmark_uid: str) -> dict:
        """Retrieves the benchmark specification file from the server

        Args:
            benchmark_uid (str): uid for the desired benchmark

        Returns:
            dict: benchmark specification
        """
        res = requests.get(f"{self.server_url}/benchmarks/{benchmark_uid}")
        if res.status_code != 200:
            pretty_error("the specified benchmark doesn't exist")
        benchmark = res.json()
        return benchmark

    def get_cube_metadata(self, cube_uid: str):
        res = requests.get(f"{self.server_url}/cubes/{cube_uid}/metadata")
        if res.status_code != 200:
            pretty_error("the specified cube doesn't exist")
        metadata = res.json()
        return metadata

    def get_cube(self, url: str, uid: str):
        res = requests.get(url)
        if res.status_code != 200:
            pretty_error("The specified cube doesn't exist")

        tmp_cube_path = os.path.join(config["tmp_storage"], uid)
        if not os.path.isdir(tmp_cube_path):
            os.mkdir(tmp_cube_path)
        tmp_cube_manifest = os.path.join(tmp_cube_path, "mlcube.yaml")
        open(tmp_cube_manifest, "wb+").write(res.content)
        return tmp_cube_manifest

    def get_cube_params(self, cube_uid: str, workspace_path: str):
        res = requests.get(f"{self.server_url}/cubes/{cube_uid}/parameters-file")
        if res.status_code != 200:
            pretty_error("the specified cube doesn't exist")

        params_filepath = os.path.join(workspace_path, "parameters.yaml")
        open(params_filepath, "wb+").write(res.content)
        return params_filepath

    def upload_dataset(self, dataset_reg_path):
        parent_path = str(Path(dataset_reg_path).parent)
        reg_sha = get_file_sha1(dataset_reg_path)
        new_name = os.path.join(parent_path, reg_sha + ".yaml")
        os.rename(dataset_reg_path, new_name)
        files = {"file": open(new_name, "rb")}
        res = requests.post(f"{self.server_url}/datasets", files=files)
        if res.status_code != 200:
            pretty_error("Could not registrate the dataset")
