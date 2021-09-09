import os
import pandas as pd
import torch
import torchxrayvision as xrv
from torch.utils.data import DataLoader
import typer
import yaml
from tqdm import tqdm

from data.dataset import XRVDataset

app = typer.Typer()


class XRVInference(object):
    @staticmethod
    def run(data_path, params_file, out_path):
        with open(params_file, "r") as f:
            params = yaml.full_load(f)

        densenet = xrv.models.DenseNet
        out_filepath = os.path.join(out_path, params["out_filename"])
        available_models = set(
            ["all", "rsna", "nih", "pc", "chex", "mimic_nb", "mimic_ch"]
        )

        if params["model"] in available_models:
            model = densenet(weights=params["model"])
        else:
            print("The specified model couldn't be found")
            exit()

        preds = []
        data = XRVDataset(data_path)
        with torch.no_grad():
            for sample in tqdm(data):
                out = model(torch.from_numpy(sample["img"]).unsqueeze(0))
                preds.append([sample["Path"]] + out.tolist()[0])

        pred_cols = ["Path"] + model.pathologies
        preds_df = pd.DataFrame(data=preds, columns=pred_cols)
        preds_df.to_csv(out_filepath, index=False)


@app.command("infer")
def infer(
    data_dir: str = typer.Option(..., "--data_dir"),
    params_file: str = typer.Option(..., "--params_file"),
    out_dir: str = typer.Option(..., "--out_dir"),
):
    XRVInference.run(data_dir, params_file, out_dir)


if __name__ == "__main__":
    app()
