import yaml
import torch
# from model.model import Architecture
from benchmark.metrics import Metrics
from benchmark.dataset import DataSet
# from model.transforms import Tranforms
from benchmark.dataloader import DataLoader
import importlib.util
import json
import os
import numpy as np
import argparse
import logging
import logging.config
from enum import Enum
import sys

logger = logging.getLogger(__name__)

#Check device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


class Task(str, Enum):
    scenario_1 = 'scenario_1'


class Scenario1():
    def __init__(self, benchmark_config, data_config, model_config, output_folder):

        self.data_config = data_config
        self.model_config = model_config
        self.benchmark_config = benchmark_config

        # Get random seed from benchmark_ configuration file
        np.random.seed(seed=benchmark_config['random_seed'])

        # Import model modules
        model = import_module('model.model',
                os.path.join(model_config['root_folder'], 'model.py'))
        self.transforms = import_module('model.transforms',
                os.path.join(model_config['root_folder'], 'transforms.py'))

        # Load model architecture
        self.model = model.Architecture().to(device)
        # Load model weights
        model_weights_file = os.path.join(model_config['root_folder'], model_config['weights'])
        self.model.load_state_dict(torch.load(model_weights_file))
        # Load scenario metrics
        self.metrics = Metrics(self.benchmark_config['scenario_1']['metrics'])
        self.output_folder=output_folder
        # Create scenario output folder
        os.makedirs(self.output_folder, exist_ok=True)
        # Load preprocessing transformations as specified by model owner
        self.preprocessing_transforms = self.transforms.Tranforms(
                self.model_config['scenario_1']['preprocessing_tranformations'])


    def __load_partition__(self):
        '''
        Loads dataset from data configuration file for a particular partition id.
        Applies benchmark_'s default validation split
        :param partition: partition id string
        :return: list of images, labels
        '''
        root_folder = self.data_config['root_folder']
        if self.data_config['validation data'] is not None:
            partition = self.data_config['validation data']
            fraction = 1
        else:
            partition = self.data_config['data']
            fraction = int(self.benchmark_config['scenario_1']['validation_fraction'])

        length = len(partition)
        indices = np.arange(length)
        np.random.shuffle(indices)

        val_length = int(length * fraction)

        val_indices = indices[:val_length]

        datalist = []
        for i in val_indices:
            dictionary = partition[i]
            for key in dictionary.keys():
                dictionary[key] = os.path.join(root_folder, dictionary[key])
            datalist.append(dictionary)
        return datalist


    def execute(self):

        # Load partition dataset
        datalist = self.__load_partition__()

        # Attach preprocessing transformations to dataset
        dataset = DataSet(datalist, self.preprocessing_transforms)

        # Create data loader
        val_loader = DataLoader(dataset)

        metric_values = []
        metric_values_tc = []
        metric_values_wt = []
        metric_values_et = []

        self.model.eval()

        metrics_results = []
        #Code below taken as is from MONAI's example: https://github.com/Project-MONAI/tutorials/blob/master/3d_segmentation/brats_segmentation_3d.ipynb
        with torch.no_grad():
            #Load post-processing tranformations
            post_processing_transforms = self.transforms.Tranforms(
                    self.model_config['scenario_1']['postprocessing_transformations'])

            metric_sum = metric_sum_tc = metric_sum_wt = metric_sum_et = 0.0
            metric_count = metric_count_tc = metric_count_wt = metric_count_et = 0
            for val_data in val_loader:


                val_inputs, val_labels = (
                    val_data["image"].to(device),
                    val_data["label"].to(device),
                )

                val_outputs = self.model(val_inputs)
                val_outputs = post_processing_transforms(val_outputs)

                for metric, metric_name in self.metrics:

                    # compute overall mean dice
                    value, not_nans = metric(y_pred=val_outputs, y=val_labels)
                    not_nans = not_nans.item()
                    metric_count += not_nans
                    metric_sum += value.item() * not_nans
                    # compute mean dice for TC
                    value_tc, not_nans = metric(y_pred=val_outputs[:, 0:1], y=val_labels[:, 0:1])
                    not_nans = not_nans.item()
                    metric_count_tc += not_nans
                    metric_sum_tc += value_tc.item() * not_nans
                    # compute mean dice for WT
                    value_wt, not_nans = metric(y_pred=val_outputs[:, 1:2], y=val_labels[:, 1:2])
                    not_nans = not_nans.item()
                    metric_count_wt += not_nans
                    metric_sum_wt += value_wt.item() * not_nans
                    # compute mean dice for ET
                    value_et, not_nans = metric(y_pred=val_outputs[:, 2:3], y=val_labels[:, 2:3])
                    not_nans = not_nans.item()

                    metric_count_et += not_nans
                    metric_sum_et += value_et.item() * not_nans


                    metric = metric_sum / (metric_count+1e-10)
                    metric_values.append(metric)
                    metric_tc = metric_sum_tc / (metric_count_tc+1e-10)
                    metric_values_tc.append(metric_tc)
                    metric_wt = metric_sum_wt / (metric_count_wt+1e-10)
                    metric_values_wt.append(metric_wt)
                    metric_et = metric_sum_et / (metric_count_et+1e-10)
                    metric_values_et.append(metric_et)
                    
                    metrics_dictionary = {'image':val_data['image_meta_dict']['filename_or_obj'][0],'metric_name':metric_name, 'results':{'mean':value.item(),'TC':value_tc.item(),'WT':value_wt.item(),'ET':value_et.item()}}
                    metrics_results.append(metrics_dictionary)
        return metrics_results

    def export_metric_results(self, results):
        with open(os.path.join(self.output_folder,'results.json'), "w") as outfile:
            json.dump(results, outfile, indent=4)
        outfile.close()

def parse_ml_args(task_args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', '--data_dir', type=str, default='../workspace/data',
                        help="Data root directory")
    parser.add_argument('--model_dir', '--model_dir', type=str, default='../workspace/model',
                        help="Model directory")
    parser.add_argument('--benchmark_parameters_file', '--benchmark_parameters_file', type=str, default='../workspace/parameters/benchmark.yaml', help="Benchmark parameters file.")
    parser.add_argument('--model_parameters_file', '--model_parameters_file', type=str, default='../workspace/model/model.yaml',
                        help="Model parameters file. User defined.")
    parser.add_argument('--data_parameters_file', '--data_parameters_file', type=str, default='../workspace/parameters/partition.yaml',
                        help="Data parameters values.")
    parser.add_argument('--output_dir', '--output-dir', type=str, default='results',
                        help="Output directory.")
    args = parser.parse_args(args=task_args)

    print("Benchmark parameters file : ", args.benchmark_parameters_file)
    print("Model parameters file : ", args.model_parameters_file)
    print("Data parameters file: ", args.data_parameters_file)
    print("Output Dir : ", args.output_dir)

    return args

def import_module(module_name, module_path):
    spec = importlib.util.spec_from_file_location(
            module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def scenario_1(task_args):
    # Read arguments
    args = parse_ml_args(task_args)
    # Benchmark configuration file
    benchmark_config = yaml.load(open(args.benchmark_parameters_file), Loader=yaml.FullLoader)
    # Data configuration file
    data_config = yaml.load(open(args.data_parameters_file), Loader=yaml.FullLoader)
    # Set/override the data root dir
    data_config["root_folder"] = args.data_dir
    # Model configuration file (SPECIFIED BY USER)
    model_config = yaml.load(open(args.model_parameters_file), Loader=yaml.FullLoader)
    # Set/override the model root dir
    model_config["root_folder"] = args.model_dir

    scenario1 = Scenario1(benchmark_config,data_config,model_config, args.output_dir)
    results = scenario1.execute()
    scenario1.export_metric_results(results)



def main():
    """
    main.py task task_specific_parameters...
    """
    # noinspection PyBroadException
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('mlcube_task', type=str, help="Task for this MLCube.")
        parser.add_argument('--log_dir', '--log-dir', type=str, required=True, help="Logging directory.")
        ml_box_args, task_args = parser.parse_known_args()
        os.makedirs(ml_box_args.log_dir, exist_ok=True)
        logger_config = {
            "version": 1,
            "disable_existing_loggers": True,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s - %(name)s - %(threadName)s - %(levelname)s - %(message)s"},
            },
            "handlers": {
                "file_handler": {
                    "class": "logging.FileHandler",
                    "level": "INFO",
                    "formatter": "standard",
                    "filename": os.path.join(ml_box_args.log_dir,
                                             f"mlbox_sciml_{ml_box_args.mlcube_task}.log")
                }
            },
            "loggers": {
                "": {"level": "INFO", "handlers": ["file_handler"]},
                "__main__": {"level": "NOTSET", "propagate": "yes"},
            }
        }
        logging.config.dictConfig(logger_config)

        if ml_box_args.mlcube_task == Task.scenario_1:
            scenario_1(task_args)
        else:
            raise ValueError(f"Unknown task: {task_args}")
    except Exception as err:
        logger.exception(err)


if __name__ == '__main__':
    main()