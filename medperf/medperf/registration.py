import yaml
from datetime import datetime
from pathlib import Path
import typer
import os

from .config import config
from .utils import get_file_sha1


class Registration:
    def __init__(self, cube, owner, name=None, description=None, location=None):
        self.owner = owner
        self.cube = cube
        self.stats = self.__get_stats()
        dt = datetime.now()
        self.reg_time = int(datetime.timestamp(dt))
        self.name = name
        self.description = description
        self.location = location
        self.approved = False

    @property
    def uid(self):
        if self.name is None:
            return None
        return "_".join([self.owner, self.name])

    def __get_stats(self):
        stats_path = self.cube.get_default_output("statistics", "output_path")
        with open(stats_path, "r") as f:
            stats = yaml.full_load(f)

        return stats

    def todict(self):
        registration = {
            "name": self.name,
            "description": self.description,
            "location": self.location,
            "owner": self.owner,
            "split_seed": self.reg_time,
            "preparation_cube_uid": self.cube.uid,
            "metadata": {},
        }
        registration.update(self.stats)

        if self.uid is not None:
            registration.update({"uid": self.uid})

        return registration

    def retrieve_additional_data(self):
        self.name = input("Provide a dataset name: ")
        self.description = input("Provide a description:  ")
        self.location = input("Provide a location:     ")

    def request_approval(self):
        if self.approved:
            return

        typer.echo()
        typer.echo("=" * 20)
        reg_data = self.todict()
        reg_data = {k: v for (k, v) in reg_data.items() if v is not None}
        typer.echo(yaml.dump(reg_data))
        typer.echo("=" * 20)
        typer.echo(
            "Above is the information and statistics that will be registered to the database"
        )
        approval = None
        while approval not in ("Y", "N", "n"):
            approval = input(
                "Do you approve the registration of the presented data to the MLCommons server? [Y/n] "
            )

        self.approved = approval == "Y"
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

        return filepath

