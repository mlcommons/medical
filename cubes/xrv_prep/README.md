# TorchXRayVision Data Preparation Cube
Example of a data preparation cube based on the `torchxrayvision` library. This cube takes advantage of the fact that the library provides data preprocessing for multiple chest xray data formats.

## Purpose of a Data Preparation Cube
Ideally, data preparation cubes are written for a specific benchmark in mind, and are intended to accept multiple common data formats and transforms them into a single standard format. Data preparation cubes are expected to create a new version of the data, leaving the original input data untouched.

## Project Setup
```
# Create Python environment 
virtualenv -p python3 ./env && source ./env/bin/activate

# Install prerequired packages
pip install wheel

# Install MLCube and MLCube docker runner from GitHub repository (normally, users will just run `pip install mlcube mlcube_docker`)
git clone https://github.com/sergey-serebryakov/mlbox.git && cd mlbox && git checkout feature/configV2
cd ./mlcube && python setup.py bdist_wheel  && pip install --force-reinstall ./dist/mlcube-* && cd ..
cd ./runners/mlcube_docker && python setup.py bdist_wheel  && pip install --force-reinstall --no-deps ./dist/mlcube_docker-* && cd ../../..
rm -fr mlbox
```

## Get the cube
This folder contains all the required files to build the cube. Therefore, to get the cube, run this:
```
git clone https://github.com/mlcommons/medical.git && cd ./cubes
git fetch origin pull/XX/head:cubes && git checkout cubes
cd ./cubes/xrv_prep
```

## Get the data
Given the nature of the data, no dataset can be easily obtained without user interaction. Most (if not all) require at least signing a user license agreement. It is expected that you've already obtained one of the common datasets for chest xray modelling, and placed it inside the cube's `workspace`. Then, modified the `mlcube.yaml` respectively so that the `preprocess` task points to the location of the data. In this repo we provide two `mlcube.yaml` examples for:
- CheXpert Dataset
- NIH Dataset

Where the following file structure is expected:
```
.
├── mlcube
│   └── workspace
│       ├── CheXpert-v1.0-small
│       │   ├── valid
│       │  	└── valid.csv
│       ├── NIH
│       │   ├── images
│       │  	└── Data_Entry_2017_v2020.csv
│       └── parameters.yaml
└── project
```
Please rename the desired example to `mlcube.yaml` for execution

# Run cube on a local machine with Docker runner
```
mlcube run --task preprocess # Creates new version of the data into /data
mlcube run --task sanity_check # checks that the output format is okay
mlcube run --task statistics # Calculates data statistics into statistics.yaml
```
Parameters defined in mlcube.yaml can be overridden using: param=input, example:
```
mlcube run --task preprocess data_path=path_to_custom_dir
```
We are targeting pull-type installation, so MLCubes should be available on docker hub. If not, try this:

```
mlcube run ... -Pdocker.build_strategy=auto
```