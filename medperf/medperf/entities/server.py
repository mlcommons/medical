import requests
import yaml
import os
from shutil import copyfile

from medperf.utils import pretty_error, get_file_sha1, cube_path
from medperf.config import config


class Server:
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.token = None

    def login(self, username: str, password: str):
        """Authenticates the user with the server. Required for most endpoints

        Args:
            username (str): Username
            password (str): password
        """
        body = {"username": username, "password": password}
        res = requests.post(f"{self.server_url}/auth-token", data=body)
        if res.status_code != 200:
            pretty_error("Unable to authentica user with provided credentials")

        self.token = res.json()["token"]

    def __auth_get(self, url, **kwargs):
        return self.__auth_req(url, requests.get, **kwargs)

    def __auth_post(self, url, **kwargs):
        return self.__auth_req(url, requests.post, **kwargs)

    def __auth_req(self, url, req_func, **kwargs):
        if self.token is None:
            pretty_error("Must be authenticated")
        return req_func(url, headers={"Authorization": f"Token {self.token}"}, **kwargs)

    def get_benchmark(self, benchmark_uid: str) -> dict:
        """Retrieves the benchmark specification file from the server

        Args:
            benchmark_uid (str): uid for the desired benchmark

        Returns:
            dict: benchmark specification
        """
        res = self.__auth_get(f"{self.server_url}/benchmarks/{benchmark_uid}")
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
        res = self.__auth_get(f"{self.server_url}/cubes/{cube_uid}/metadata")
        if res.status_code != 200:
            pretty_error("the specified cube doesn't exist")
        metadata = res.json()
        return metadata

    def __create_cube_fs(self, uid: str) -> str:
        """Creates the required folder structure for a cube

        Args:
            uid (str): Cube UID.

        Returns:
            str: Path to the cube folder structure.
        """
        c_path = cube_path(uid)
        ws = config["workspace_path"]
        if not os.path.isdir(c_path):
            os.mkdir(c_path)
            ws_path = os.path.join(c_path, ws)
            os.mkdir(ws_path)
        return c_path

    def get_cube(self, url: str, uid: str) -> str:
        """Downloads and writes an mlcube.yaml file from the server

        Args:
            url (str): URL where the mlcube.yaml file can be downloaded.
            uid (str): Cube UID.

        Returns:
            str: location where the mlcube.yaml file is stored locally.
        """
        cube_file = config["cube_filename"]
        return self.__get_cube_file(url, uid, "", cube_file)

    def get_cube_params(self, url: str, cube_uid: str) -> str:
        """Retrieves the cube parameters.yaml file from the server

        Args:
            url (str): URL where the parameters.yaml file can be downloaded.
            cube_uid (str): Cube UID.

        Returns:
            str: Location where the parameters.yaml file is stored locally.
        """
        ws = config["workspace_path"]
        params_file = config["params_filename"]
        return self.__get_cube_file(url, cube_uid, ws, params_file)

    def get_cube_additional(self, url: str, cube_uid: str) -> str:
        """Retrieves and stores the additional_files.tar.gz file from the server

        Args:
            url (str): URL where the additional_files.tar.gz file can be downloaded.
            cube_uid (str): Cube UID.

        Returns:
            str: Location where the additional_files.tar.gz file is stored locally.
        """
        add_path = config["additional_path"]
        tball_file = config["tarball_filename"]
        return self.__get_cube_file(url, cube_uid, add_path, tball_file)

    def __get_cube_file(self, url: str, cube_uid: str, path: str, filename: str):
        res = requests.get(url)
        if res.status_code != 200:
            pretty_error("There was a problem retrieving the specified file at " + url)

        c_path = cube_path(cube_uid)
        path = os.path.join(c_path, path)
        if not os.path.isdir(path):
            os.makedirs(path)
        filepath = os.path.join(path, filename)
        open(filepath, "wb+").write(res.content)
        return filepath

    def upload_dataset(self, parent_path: str, filename: str = config["reg_file"]):
        """Uploads registration data to the server, under the sha name of the file.

        Args:
            parent_path (str): Path to the registration data.
            filename (str, optional): Name of the registration file. Defaults to config["reg_file"].
        """
        dataset_reg_path = os.path.join(parent_path, filename)
        reg_sha = get_file_sha1(dataset_reg_path)
        new_name = os.path.join(parent_path, reg_sha + ".yaml")
        copyfile(dataset_reg_path, new_name)
        files = {"file": open(new_name, "rb")}
        res = self.__auth_post(f"{self.server_url}/datasets", files=files)
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
        res = self.__auth_post(f"{self.server_url}/results", json=data)
        if res.status_code != 200:
            pretty_error("Could not upload the results")
