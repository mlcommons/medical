import yaml
from datetime import datetime
from pathlib import Path
import typer
import os

from .config import config
from .server import Server
from .cube import Cube
from .utils import get_file_sha1, approval_prompt, dict_pretty_print


class Registration:
    def __init__(
        self,
        cube: Cube,
        owner: str,
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
        self.owner = owner
        self.cube = cube
        self.stats = self.__get_stats()
        dt = datetime.now()
        self.reg_time = int(datetime.timestamp(dt))
        self.name = name
        self.description = description
        self.location = location
        self.approved = False
        self.path = None

    @property
    def uid(self) -> str:
        """Auto-generates an UID given the user and name of the registration

        Returns:
            str: generated UID
        """
        if self.name is None:
            return None
        return "_".join([self.owner, self.name])

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
            "owner": self.owner,
            "split_seed": 0,
            "preparation_cube_uid": self.cube.uid,
            "metadata": {},
        }
        registration.update(self.stats)

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
        if self.approved:
            return True

        dict_pretty_print(self.todict())
        typer.echo(
            "Above is the information and statistics that will be registered to the database"
        )
        self.approved = approval_prompt(
            "Do you approve the registration of the presented data to the MLCommons server? [Y/n] "
        )
        return self.approved

    def to_permanent_path(self, out_path: str, reg_path: str) -> str:
        """Renames the temporary data folder to permanent one using the hash of
        the registration file

        Args:
            out_path (str): current temporary location of the data
            reg_path (str): path to registration file

        Returns:
            str: renamed location of the data.
        """
        sha = get_file_sha1(reg_path)
        new_path = os.path.join(str(Path(out_path).parent), sha)
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

    def upload(self):
        """Uploads the registration information to the server.
        """
        server = Server(config["server"])
        server.upload_dataset(self.path)
