#!/usr/bin/env python3

import logging
import os
import sys
from argparse import ArgumentParser

from rknn.api import RKNN
from ultralytics import YOLO

logging.getLogger("rknn-converter")


def yolo_to_onnx(
    yolo_model_file: str,
    img_size: tuple[int, int],
) -> str:
    """
    Converts YOLO model to ONNX model.

    :param yolo_model_file: filename of YOLO model
    :param img_size: Size of input image (height, width)

    :return: File name of ONNX model
    """
    logging.info(f"Converting {yolo_model_file} to ONNX model")
    yolo = YOLO(yolo_model_file)
    yolo.export(format="onnx", imgsz=[img_size[0], img_size[1]], opset=12)
    base_name, _ = os.path.splitext(yolo_model_file)
    onnx_file_name = f"{base_name}.onnx"
    logging.info(f"ONNX model saved to {onnx_file_name}")
    return onnx_file_name


def onnx_to_rknn(
    onnx_model_file: str,
    dataset_file: str,
    rknn_model_file: str,
    target_platform: str,
) -> None:
    """
    Converts ONNX model to RKNN model.

    :param onnx_model_file: filename of ONNX model for load
    :param dataset_file: filename of dataset file
    :param rknn_model_file: filename of RKNN model for save
    :param target_platform: target platform name
    """
    logging.info(f"Converting {onnx_model_file} to RKNN model")
    rknn = RKNN(verbose=False)

    rknn.config(
        mean_values=[[0, 0, 0]],
        std_values=[[255, 255, 255]],
        target_platform=target_platform,
        optimization_level=2,
        quantized_dtype="asymmetric_quantized-8",
        # quant_img_RGB2BGR=True,
        # quantized_algorithm="normal",
        # quantized_method="channel",
        # float_dtype="float16",
        # custom_string=None,
        # remove_weight=None,
        # compress_weight=False,
        # single_core_mode=False,
        # model_pruning=False,
        # op_target=None,
        # dynamic_input=None,
    )

    logging.info(f"Loading {onnx_model_file}")
    ret = rknn.load_onnx(
        model=onnx_model_file,
        # outputs=["", "", ""],
    )
    if ret != 0:
        logging.error(f"Failed to load ONNX model: {onnx_model_file}")
        raise IOError(f"ONNX load error: {ret}")

    logging.info("Building RKNN model")
    if rknn.build(do_quantization=bool(dataset_file), dataset=dataset_file) != 0:
        logging.error(f"Failed to build RKNN model: {onnx_model_file}")
        raise RuntimeError("Build model error")

    logging.info(f"Exporting RKNN model: {rknn_model_file}")
    if rknn.export_rknn(rknn_model_file) != 0:
        logging.error(f"Failed to export RKNN model: {rknn_model_file}")
        raise IOError("RKNN export error")

    rknn.release()


def read_args() -> tuple[str, str, tuple[int, int], str]:
    parser = ArgumentParser(
        description="YOLOv8 to RKNN converter tool",
        add_help=True,
    )
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        required=True,
        help="File mame of YOLO model (PyTorch format .pt)",
    )
    parser.add_argument(
        "-d",
        "--dataset",
        type=str,
        required=True,
        default=None,
        help="Path to dataset .txt file for quantization",
    )
    parser.add_argument(
        "-s",
        "--imgsize",
        type=str,
        required=False,
        default="640",
        help="Image size of the side of the square or H:W. (default: 640 or 640:640)",
    )
    parser.add_argument(
        "-p",
        "--platform",
        type=str,
        default="rk3588",
        help="RKNN target platform (default: rk3588)",
    )

    args = parser.parse_args()

    try:
        if ":" in args.imgsize:
            img_h, img_w = map(int, args.imgsize.split(":"))
        else:
            img_h, img_w = int(args.imgsize), int(args.imgsize)
    except ValueError as e:
        raise ValueError(f"Invalid image size format: {args.imgsize}") from e

    return (
        args.model,
        args.dataset,
        (img_h, img_w),
        args.platform,
    )


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    try:
        model, dataset, imgsize, platform = read_args()
    except ValueError as e:
        logging.error(e)
        logging.exception(e)
        return 1

    if not os.path.isfile(model):
        logging.error(f"File {model} does not exist")
        return 1

    if platform not in [
        "rk3562",
        "rk3566",
        "rk3568",
        "rk3588",
        "rk1808",
        "rv1109",
        "rv1126",
    ]:
        logging.error(f"Platform {platform} is not supported")
        return 1

    model_base_name, model_extension = os.path.splitext(model)
    rknn_model_name = f"{model_base_name}-{platform}.rknn"

    logging.info("Converting PyTorch or ONNX model to RKNN model.")
    logging.info(f"Input model: {model}")
    logging.info(f"Output model: {rknn_model_name}")
    logging.info(f"Target platform: {platform}")
    if dataset:
        logging.info(f"Quantization using dataset file: {dataset}")
    else:
        logging.warning("Without quantization!")

    if model_extension.lower() == ".pt":
        onnx_model_file = yolo_to_onnx(
            yolo_model_file=model,
            img_size=imgsize,
        )
    elif model_extension.lower() == ".onnx":
        onnx_model_file = model
    else:
        logging.error(f"Unknown model type {model_extension}")
        return 1

    onnx_to_rknn(
        onnx_model_file=onnx_model_file,
        dataset_file=dataset,
        rknn_model_file=rknn_model_name,
        target_platform=platform,
    )

    logging.info("Done")

    return 0


def console_main() -> int:
    try:
        code = main()
        sys.stdout.flush()
        return code
    except BrokenPipeError:
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        return 1


if __name__ == "__main__":
    main()
