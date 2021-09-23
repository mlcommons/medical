from medperf.config import config
from medperf.entities import Server


class Benchmark:
    def __init__(self, uid: str, benchmark_dict: dict):
        """Creates a new benchmark instance

        Args:
            uid (str): The benchmark UID
            benchmark_dict (dict): key-value representation of the benchmark.
        """
        self.uid = uid
        self.name = benchmark_dict["name"]
        self.description = benchmark_dict["description"]
        self.owner = benchmark_dict["owner"]
        self.data_preparation = benchmark_dict["data_preparation"]
        self.models = benchmark_dict["models"]
        self.evaluator = benchmark_dict["evaluator"]

    @classmethod
    def get(cls, benchmark_uid: str) -> "Benchmark":
        """Retrieves and creates a Benchmark instance from the server

        Args:
            benchmark_uid (str): UID of the benchmark.

        Returns:
            Benchmark: a Benchmark instance with the retrieved data
        """
        server = Server(config["server"])
        benchmark_dict = server.get_benchmark(benchmark_uid)
        return cls(benchmark_uid, benchmark_dict)
