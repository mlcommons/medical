#!/bin/bash

MODEL_FILE="model.pth.tar"
MODEL_DIR="${MODEL_DIR:-./checkpoints}"
MODEL_PATH="${MODEL_DIR}/${MODEL_FILE}"

if [ ! -d "$MODEL_DIR" ]
then
    mkdir $MODEL_DIR
    chmod go+rx $MODEL_DIR
#     python utils/download_librispeech.py utils/librispeech.csv $DATA_DIR -e ${DATA_ROOT_DIR}/
fi
curl  https://raw.githubusercontent.com/gaetandi/cheXpert/master/model_ones_3epoch_densenet.tar --output ${MODEL_PATH}

