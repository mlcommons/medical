import yaml
from datetime import datetime
from pathlib import Path
import typer
import os

from medperf.config import config
from medperf.utils import get_file_sha1, approval_prompt, dict_pretty_print
from medperf.entities import Server, Cube


class Registration:
    def __init__(
        self,
        cube: Cube,
        name: str = None,
        description: str = None,
        location: str = None,
    ):
        """Creates a registration instance

        Args:
            cube (Cube): Instance of the cube used for creating the registration.
            owner (str): UID of the user
            name (str, optional): Assigned name. Defaults to None.
            description (str, optional): Assigned description. Defaults to None.
            location (str, optional): Assigned location. Defaults to None.
        """
        self.cube = cube
        self.stats = self.__get_stats()
        dt = datetime.now()
        self.reg_time = int(datetime.timestamp(dt))
        self.name = name
        self.description = description
        self.location = location
        self.status = "PENDING"
        self.path = None

    @property
    def uid(self) -> str:
        """Auto-generates an UID given the user and name of the registration

        Returns:
            str: generated UID
        """
        if self.name is None:
            return None
        return "_".join([self.name])

    def __get_stats(self) -> dict:
        """Unwinds the cube output statistics location and retrieves the statistics data

        Returns:
            dict: dataset statistics as key-value pairs.
        """
        stats_path = self.cube.get_default_output("statistics", "output_path")
        with open(stats_path, "r") as f:
            stats = yaml.full_load(f)

        return stats

    def todict(self) -> dict:
        """Dictionary representation of the registration

        Returns:
            dict: dictionary containing information pertaining the registration.
        """
        registration = {
            "name": self.name,
            "description": self.description,
            "location": self.location,
            "split_seed": 0,
            "data_preparation_mlcube": self.cube.uid,
            "generated_uid": self.uid,
            "metadata": self.stats,
            "status": self.status,
        }

        if self.uid is not None:
            registration.update({"uid": self.uid})

        return registration

    def retrieve_additional_data(self):
        """Prompts the user for the name, description and location
        """
        self.name = input("Provide a dataset name: ")
        self.description = input("Provide a description:  ")
        self.location = input("Provide a location:     ")

    def request_approval(self) -> bool:
        """Prompts the user for approval concerning uploading the registration to the server.

        Returns:
            bool: Wether the user gave consent or not.
        """
        if self.status == "APPROVED":
            return True

        dict_pretty_print(self.todict())
        typer.echo(
            "Above is the information and statistics that will be registered to the database"
        )
        approved = approval_prompt(
            "Do you approve the registration of the presented data to the MLCommons server? [Y/n] "
        )
        return approved

    def to_permanent_path(self, out_path: str, uid: int) -> str:
        """Renames the temporary data folder to permanent one using the hash of
        the registration file

        Args:
            out_path (str): current temporary location of the data
            uid (int): UID of registered dataset. Obtained after uploading to server

        Returns:
            str: renamed location of the data.
        """
        new_path = os.path.join(str(Path(out_path).parent), str(uid))
        os.rename(out_path, new_path)
        self.path = new_path
        return new_path

    def write(self, out_path: str, filename: str = "registration-info.yaml") -> str:
        """Writes the registration into disk

        Args:
            out_path (str): path where the file will be created
            filename (str, optional): name of the file. Defaults to "registration-info.csv".

        Returns:
            str: path to the created registration file
        """
        data = self.todict()
        filepath = os.path.join(out_path, filename)
        with open(filepath, "w") as f:
            yaml.dump(data, f)

        self.path = filepath
        return filepath

    def upload(self, benchmark_uid: int, server: Server) -> int:
        """Uploads the registration information to the server.

        Args:
            benchmark_uid (int): UID of the benchmark used to create the dataset
            server (Server): Instance of the server interface.
        
        Returns:
            int: UID of registered dataset
        """
        dataset_uid = server.upload_dataset(self.todict())
        server.associate_dataset(dataset_uid, benchmark_uid)

        return
