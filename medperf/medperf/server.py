import requests
from pathlib import Path
import os
from shutil import copyfile

from .config import config
from .utils import pretty_error, get_file_sha1, cleanup, cube_path


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

        c_path = self.__create_cube_fs(uid)
        cube_manifest = os.path.join(c_path, "mlcube.yaml")
        open(cube_manifest, "wb+").write(res.content)
        return cube_manifest

    def __create_cube_fs(self, uid: str):
        c_path = cube_path(uid)
        if not os.path.isdir(c_path):
            os.mkdir(c_path)
            ws_path = os.path.join(c_path, "workspace")
            os.mkdir(ws_path)
        return c_path

    def get_cube_params(self, cube_uid: str):
        res = requests.get(f"{self.server_url}/cubes/{cube_uid}/parameters-file")
        if res.status_code != 200:
            pretty_error("the specified cube doesn't exist")

        c_path = cube_path(cube_uid)
        params_filepath = os.path.join(c_path, "workspace/parameters.yaml")
        open(params_filepath, "wb+").write(res.content)
        return params_filepath

    def upload_dataset(self, parent_path, filename="registration-info.yaml"):
        """Uploads registration data to server, under the sha name of the file

        Args:
            parent_path ([str]): path to the registration data
            filename (str, optional): name of the registration file. Defaults to "registration-info.yaml".
        """
        dataset_reg_path = os.path.join(parent_path, filename)
        reg_sha = get_file_sha1(dataset_reg_path)
        new_name = os.path.join(parent_path, reg_sha + ".yaml")
        copyfile(dataset_reg_path, new_name)
        files = {"file": open(new_name, "rb")}
        res = requests.post(f"{self.server_url}/datasets", files=files)
        os.remove(new_name)
        if res.status_code != 200:
            pretty_error("Could not registrate the dataset")
