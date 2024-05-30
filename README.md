# RKNN Converter
## Table of Contents
<!-- TOC -->
* [RKNN Converter](#rknn-converter)
  * [Table of Contents](#table-of-contents)
  * [About](#about)
  * [Installation](#installation)
    * [System dependencies](#system-dependencies)
    * [Cloning the repository and install](#cloning-the-repository-and-install)
  * [Conversion](#conversion)
    * [Preparing](#preparing)
      * [Creating dataset](#creating-dataset)
    * [Executing](#executing)
  * [Other versions of Python](#other-versions-of-python)
    * [Python 3.10](#python-310)
    * [Python 3.6 - 3.9](#python-36---39)
    * [Python <3.6 or >3.11](#python-36-or-311)
  * [Support](#support)
    * [Discussions and featurerequests](#discussions-and-featurerequests)
    * [Bugfixes](#bugfixes)
  * [References](#references)
<!-- TOC -->

## About
This tool provides to convert YOLO models (or ONNX models) to RKNN format.

> [!IMPORTANT]  
> This tool is based on [rknn-toolkit2](https://github.com/airockchip/rknn-toolkit2) version [1.6.0](https://github.com/airockchip/rknn-toolkit2/tree/v1.6.0).
> You should be using **rknn-toolkit-lite2** on an SBC of the same version.

## Installation
### System dependencies
System dependencies must be installed for a successful installation.
```shell
sudo apt install -y libgl1-mesa-dev
```

### Cloning the repository and install
The following steps are for **Python 3.11**. If you have a different version, [refer to this section first](#other-versions-of-python).
```shell
cd ~
git clone https://github.com/denisbondar/rknn-converter.git
cd rknn-converter
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Conversion
### Preparing
You will need a YOLO format model — usually the `best.pt` file.
You will also need a dataset of 20 photos matching your model for the quantization process.

You don't have to place all these files inside the current rknn-converter directory, you can place them wherever you like.
However, for simplicity and reliability, the instructions below will assume that the files are in the model subdirectory of the current rknn-converter directory:

Create the necessary directories:
```shell
mkdir -p model/images
```
And then copy your model file `best.pt` to the `model` directory.

#### Creating dataset
Create a model directory and navigate to it. In the model directory, create the images directory and copy your images there.
While in the model directory, run the command that creates an image index, a text file that lists the paths to each of the image files.
```shell
cd model
ls ./images/* > images.txt
cd ..
```
The content of the images.txt file should be (you can see it with the cat model/images.txt command).
```text
./images/01.jpg
./images/02.jpg
./images/03.jpg

... etc ...
```

---
In general, the file tree will be something like this:
```text
.
├── model
│   ├── best.pt
│   ├── images
│   │   ├── 01.jpg
│   │   ├── 02.jpg
│   │   ├── 03.jpg
│   │   ├── . . .
│   │   └── 20.jpg
│   └── images.txt
├── pt2rknn.py
├── README.md
├── requirements.txt
└── rknn-toolkit2_pkgs
```

### Executing
Make sure you are still in an active virtual environment - your command line prompt prefix should be `(venv)`, and run the following command:
```shell
python3 pt2rknn.py -m model/best.pt -d model/images.txt
```
As a result, two new files should be created: `model/best.onnx` and `model/best-rk3588.rknn`.

The command also contains optional parameters such as image size (default 640x640) and target platform (default kr3588).
You can run the command with the -h flag to see all available options.

Alternatively, you can specify a model of type ONNX as a source model and get a model in RKNN format.

```text
$ python3 pt2rknn.py -h
usage: pt2rknn.py [-h] -m MODEL -d DATASET [-s IMGSIZE] [-p PLATFORM]

YOLOv8 to RKNN converter tool

options:
  -h, --help            show this help message and exit
  -m MODEL, --model MODEL
                        File mame of YOLO model (PyTorch format .pt)
  -d DATASET, --dataset DATASET
                        Path to dataset .txt file for quantization
  -s IMGSIZE, --imgsize IMGSIZE
                        Image size of the side of the square or H:W. (default: 640 or 640:640)
  -p PLATFORM, --platform PLATFORM
                        RKNN target platform (default: rk3588)
```

## Other versions of Python
### Python 3.10
If you are using Python version 3.10, before installing, edit the requirements.txt file by replacing the first line with
```text
./rknn-toolkit2_pkgs/rknn_toolkit2-1.6.0+81f21f4d-cp311-cp311-linux_x86_64.whl
```
by replacing the first line
```text
./rknn-toolkit2_pkgs/rknn_toolkit2-1.6.0+81f21f4d-cp310-cp310-linux_x86_64.whl
```
And only after that, run the `pip install` command.

### Python 3.6 - 3.9
If your version of Python is between 3.6 and 3.9, you will first need to repackage the original **rknn-toolkit2** package.
To do this, add the desired version, such as `"cp39"`, to the `PYTHON_VERSIONS` list of the `rknn-toolkit2_pkgs/repack-whl.sh` file.
Then run this file, and it will create a package for your version of Python.
Now modify `requirements.txt` as [above](#python-310) with the name of your package.

You can now run the `pip install ...`command as shown in the [installation section](#cloning-the-repository-and-install).

### Python <3.6 or >3.11
rknn-toolkit2 v1.6.0 only supports Python in the 3.6 to 3.11 version range.

## Support
Given the instability and persistent problems of the original rknn-toolkit package, there are likely to be future problems that simply did not exist when the converter was written.

### Discussions and featurerequests
For questions and discussions, it is best to use [discussions board](../../discussions) so as not to clutter the issues with questions.
If you're not sure, it's always best to start with discussions, as your issue may have already been or is currently being discussed.

### Bugfixes
If you find a clear bug that can be fixed, [see if there is an issue](../../issues) with a similar bug before [creating a new one](../../issues/new).

## References
* <https://docs.ultralytics.com/>
* <https://onnx.ai/>
* <https://github.com/airockchip/rknn-toolkit2/>
