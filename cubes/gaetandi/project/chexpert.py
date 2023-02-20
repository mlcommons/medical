import os
import argparse
import yaml
import pandas as pd
from tqdm import tqdm

import torch
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
from data.dataset import CheXpertDataSet
from model import DenseNet121
from collections import OrderedDict

use_gpu = torch.cuda.is_available()


class CheXpertRunner:
    def __init__(self, params):
        self.params = params
        device = "gpu" if torch.cuda.is_available() else "cpu"
        self.device = torch.device(device)
        self.dataloader = self.__get_dataloader()
        self.model = self.__build_model()

    def __get_dataloader(self):
        transformSequence = self.__get_transforms(self.params["imgtransCrop"])
        dataset = CheXpertDataSet(
            self.params["data_path"],
            self.params["data_file"],
            transformSequence,
            policy="ones",
        )

        return DataLoader(dataset=dataset)

    def __get_transforms(self, imgtransCrop):
        normalize = transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        transformList = []
        transformList.append(transforms.Resize(imgtransCrop))
        transformList.append(transforms.ToTensor())
        transformList.append(normalize)
        return transforms.Compose(transformList)

    def __build_model(self):
        model = DenseNet121(self.params["nnClassCount"])
        model = self.__load_model(model)
        model = model.to(self.device)
        return model

    def __load_model(self, model):
        model_checkpoint = torch.load(
            self.params["checkpoint"], map_location=self.device
        )
        model_checkpoint = self.__fix_state_dict(model_checkpoint)
        model.load_state_dict(model_checkpoint["state_dict"])
        return model

    def __fix_state_dict(self, modelCheckpoint):
        new_state_dict = OrderedDict()
        for key, value in modelCheckpoint["state_dict"].items():

            new_key = ".".join(key.split(".")[1:])
            new_state_dict[new_key] = value

        modelCheckpoint["state_dict"] = new_state_dict
        return modelCheckpoint

    def predict(self):
        out_pred = torch.FloatTensor().to(self.device)

        self.model.eval()
        image_names = []

        with torch.no_grad():
            for i, (x, _, image_name) in tqdm(enumerate(self.dataloader)):

                _, c, h, w = x.size()
                var_x = x.view(-1, c, h, w)

                out = self.model(var_x)
                out_pred = torch.cat((out_pred, out), 0)
                image_names.append(image_name[0])

        return out_pred, image_names


def main():
    with open("config.yaml", "r") as f:
        params = yaml.full_load(f)
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data_path",
        "--data-path",
        type=str,
        required=True,
        help="Path where the data is stored",
    )
    parser.add_argument(
        "--out_path",
        "--out-path",
        type=str,
        required=True,
        help="Path to store the predictions",
    )
    parser.add_argument(
        "--model_path",
        "--model-path",
        type=str,
        required=True,
        help="location and name of the checkpoint file",
    )
    args = parser.parse_args()

    params["data_path"] = args.data_path
    params["checkpoint"] = os.path.join(args.model_path, "model.pth.tar")
    runner = CheXpertRunner(params)
    preds, names = runner.predict()
    preds_df = pd.DataFrame(data=preds.tolist(), columns=params["class_names"])
    preds_df["Path"] = names
    out_path = os.path.join(args.out_path)
    preds_df.to_csv(out_path, index=False)


if __name__ == "__main__":
    main()
