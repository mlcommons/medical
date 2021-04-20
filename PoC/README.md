# Proof-of-Concept 
This is early work to demonstrate the use of MLCube on medical ML benchmarking for Medical ML Working Group at MLCommons.

### Background
The Medical ML Working Group at MLCommons aims to build a benchmark suite which will help facilitate
fair, transparent and clinically meaningful benchmarking in medical space. A detailed description of the goals 
and vision can be found in the Working Group's [document](https://docs.google.com/document/d/1EzylJ4a3cMs8miR6Ads9skpkMoggxrQqdetTpnJ__WY/edit?usp=sharing). 


Towards this end, the Working Group is planning 
to use MLCube as the core technology for its benchmarking suite. As initial effort, the Working Group is developing a Proof-of-Concept (PoC) based on the following specifications:
* Model evaluation scenarios on a publicly available medical imaging dataset and a publicly available ML model
* Integration of MLCube as a containerization approach to execute model evaluation scenarios

### Purpose
The purpose of the PoC is to **simulate** in a simple way how benchmarks can operate within the proposed benchmarking suite on real clinical settings. 
Moreover, it aims to demonstrate how MLCube can successfully help with subsequent development.

### Design Philosophy
The current design philosophy of the PoC is simple. It consists of 3 components:
- Data: The data to operate/benchmark on. This component contains metadata information about the data. Specifically it utilizes `yaml` format to describe the metadata.
- Model: The model code. This component describes the model architecture as well as any pre-processing/post-processing code as provided by model author/researcher. It contains the model architecture as well as the weights of the model.
- Benchmark: This component describes the benchmark pipeline. It contains the model evaluation scenarios to execute on the data using the model. It utilized `yaml` format to describe benchmark specifications.
### Model Evaluation Scenarios
For the PoC we have identified 2 meaningful model evaluation scenarios for simulation purposes on a publicly available dataset.
 
 The public dataset is partitioned (sharded) into non-iid partitions (e.g. different hospitals, different manufacturers) and all partitions are hosted locally in a single node. 

- Scenario 1 - Decentralized evaluation: 
An ML model already trained on one data partition of the public dataset is evaluated on each of the rest of the data partitions. 

- Scenario 2 - Decentralized fine-tuning/evaluation:
An pre-trained ML model is fine-tuned and evaluated on each of the data partitions. The only difference with Scenario 1 is that there is a fine-tuning step before evaluation. This scenario is useful when the model is refined to a new clinical client.

In both scenarios the model is NOT shared between multiple clinical clients. Only metrics are returned back. This is important and intentional as model/data privacy is one of the main requirements of our benchmarking suite. 


### Description (WIP as of April 2021) 
This is a preliminary work-in-progress implementation of the PoC based on MLCube. Please bear in mind that this implementation is undergoing heavy development and it will change in the future.

This version has the following specifications:
- It uses [BraTS dataset 2016/17](http://medicaldecathlon.com)
- The trained model is based on [MONAI's implementation](https://github.com/Project-MONAI/tutorials/blob/master/3d_segmentation/brats_segmentation_3d.ipynb)

Following the Design Philosophy the PoC has: 

Code structure:
- [MLCube/workspace/data/](MLCube/workspace/data/) contains testing images for the model evaluation scenarios. This data is one partition.  
- [MLCube/workspace/model](MLCube/workspace/model) contains model code (i.e. architecture, preprocessing transformation, weights) 
- [MLCube/src/benchmark](MLCube/src/benchmark) contains the benchmark pipeline. This pipeline contains loads the model and infers the images. Metrics

with `yaml` structure:
- Data: Metadata of the data partition are stored in [MLCube/workspace/parameters/partition.yaml](MLCube/workspace/parameters/partition.yaml)
- Model: Model description is stored in [MLCube/workspace/model/model.yaml](MLCube/workspace/model/model.yaml)
- Benchmark: Benchmark description is stored in [MLCube/workspace/parameters/benchmark.yaml](MLCube/workspace/parameters/benchmark.yaml)

### How to run
Make sure you follow these [instructions](https://github.com/mlcommons/mlcube) to install MLCube on your virtual environment.
- Navigate to `platforms` folder and build the MLCube container by executing: `docker build -t mlcommons/poc_benchmark:0.0.1 .` 
- To execute Scenario 1 of model evaluation run the following command from the `PoC` folder run : 
`mlcube_docker run --mlcube=. --platform=platforms/docker.yaml --task=run/scenario_1.yaml` 
- If all is gone well, metrics (i.e. DICE) will be stored in `/Results` folder.


Note: Scenario 2 under development
