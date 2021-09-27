from pathlib import Path
import os

home = str(Path.home())
storage = os.path.join(home, "medperf")
config = {
    "server": "http://localhost:8000",
    "storage": storage,
    "tmp_reg_prefix": "tmp_",
    "tmp_storage": os.path.join(storage, "tmp"),
    "data_storage": os.path.join(storage, "data"),
    "cubes_storage": os.path.join(storage, "cubes"),
    "results_storage": os.path.join(storage, "results"),
    "model_output": "outputs/predictions.csv",
    "workspace_path": "workspace",
    "cube_filename": "mlcube.yaml",
    "params_filename": "parameters.yaml",
    "additional_path": "workspace/additional_files",
    "tarball_filename": "tmp.tar.gz",
    "reg_file": "registration-info.yaml",
}
