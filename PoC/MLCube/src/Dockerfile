FROM ubuntu:18.04
LABEL maintainer="MLCommons Medical Working Group"

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
            software-properties-common \
            build-essential \
            python3-dev \
            python3-pip \
            curl

WORKDIR /mlcube

COPY requirements.txt /mlcube/requirements.txt

RUN pip3 install --no-cache-dir setuptools
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /mlcube

ENTRYPOINT ["python3", "main.py"]
