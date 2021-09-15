from pathlib import Path
import os

home = str(Path.home())
storage = os.path.join(home, "medperf")
tmp = os.path.join(storage, "tmp")
config = {
    "server": "http://localhost:8000",
    "storage": storage,
    "tmp_storage": tmp,
}
