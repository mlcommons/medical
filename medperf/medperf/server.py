import requests
import yaml
import os
from shutil import copyfile

from .utils import pretty_error, get_file_sha1, cleanup, cube_path


class Server:
    def __init__(self, server_url: str):
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

    def get_cube_metadata(self, cube_uid: str) -> dict:
        """Retrieves metadata about the specified cube

        Args:
            cube_uid (str): UID of the desired cube.

        Returns:
            dict: Dictionary containing url and hashes for the cube files
        """
        res = requests.get(f"{self.server_url}/cubes/{cube_uid}/metadata")
        if res.status_code != 200:
            pretty_error("the specified cube doesn't exist")
        metadata = res.json()
        return metadata

    def get_cube(self, url: str, uid: str) -> str:
        """Downloads and writes an mlcube.yaml file from the server

        Args:
            url (str): URL where the mlcube.yaml file can be downloaded.
            uid (str): Cube UID.

        Returns:
            str: location where the mlcube.yaml file is stored locally.
        """
        res = requests.get(url)
        if res.status_code != 200:
            pretty_error("The specified cube doesn't exist")

        c_path = self.__create_cube_fs(uid)
        cube_manifest = os.path.join(c_path, "mlcube.yaml")
        open(cube_manifest, "wb+").write(res.content)
        return cube_manifest

    def __create_cube_fs(self, uid: str) -> str:
        """Creates the required folder structure for a cube

        Args:
            uid (str): Cube UID.

        Returns:
            str: Path to the cube folder structure.
        """
        c_path = cube_path(uid)
        if not os.path.isdir(c_path):
            os.mkdir(c_path)
            ws_path = os.path.join(c_path, "workspace")
            os.mkdir(ws_path)
        return c_path

    def get_cube_params(self, url: str, cube_uid: str) -> str:
        """Retrieves the cube parameters.yaml file from the server

        Args:
            url (str): URL where the parameters.yaml file can be downloaded.
            cube_uid (str): Cube UID.

        Returns:
            str: Location where the parameters.yaml file is stored locally.
        """
        res = requests.get(url)
        if res.status_code != 200:
            pretty_error("the specified cube doesn't exist")

        c_path = cube_path(cube_uid)
        params_filepath = os.path.join(c_path, "workspace/parameters.yaml")
        open(params_filepath, "wb+").write(res.content)
        return params_filepath

    def get_cube_additional(self, url: str, cube_uid: str) -> str:
        """Retrieves and stores the additional_files.tar.gz file from the server

        Args:
            url (str): URL where the additional_files.tar.gz file can be downloaded.
            cube_uid (str): Cube UID.

        Returns:
            str: Location where the additional_files.tar.gz file is stored locally.
        """
        res = requests.get(url)
        if res.status_code != 200:
            pretty_error("the specified files don't exist")

        c_path = cube_path(cube_uid)
        addpath = os.path.join(c_path, "workspace/additional_files")
        if not os.path.isdir(addpath):
            os.mkdir(addpath)
        add_filepath = os.path.join(addpath, "tmp.tar.gz")
        open(add_filepath, "wb+").write(res.content)
        return add_filepath

    def upload_dataset(
        self, parent_path: str, filename: str = "registration-info.yaml"
    ):
        """Uploads registration data to the server, under the sha name of the file.

        Args:
            parent_path (str): Path to the registration data.
            filename (str, optional): Name of the registration file. Defaults to "registration-info.yaml".
        """
        dataset_reg_path = os.path.join(parent_path, filename)
        reg_sha = get_file_sha1(dataset_reg_path)
        new_name = os.path.join(parent_path, reg_sha + ".yaml")
        copyfile(dataset_reg_path, new_name)
        files = {"file": open(new_name, "rb")}
        res = requests.post(f"{self.server_url}/datasets", files=files)
        os.remove(new_name)
        if res.status_code != 200:
            pretty_error("Could not upload the dataset")

    def upload_results(
        self, results_path: str, benchmark_uid: str, model_uid: str, dataset_uid: str
    ):
        """Uploads results to the server.

        Args:
            results_path (str): Location where the results.yaml file can be found.
            benchmark_uid (str): UID of the used benchmark.
            model_uid (str): UID of the used model.
            dataset_uid (str): UID of the used dataset.
        """
        with open(results_path, "r") as f:
            scores = yaml.full_load(f)
        data = {
            "benchmark_uid": benchmark_uid,
            "model_uid": model_uid,
            "dataset_uid": dataset_uid,
            "scores": scores,
        }
        res = requests.post(f"{self.server_url}/results", json=data)
        if res.status_code != 200:
            pretty_error("Could not upload the results")
