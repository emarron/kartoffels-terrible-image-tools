from math import ceil
from pathlib import Path
from typing import Tuple

import cv2
from PIL import Image
import numpy as np


def get_h_w_c(image: np.ndarray) -> Tuple[int, int, int]:
    """Returns the height, width, and number of channels."""
    h, w = image.shape[:2]
    c = 1 if image.ndim == 2 else image.shape[2]
    return h, w, c


def AverageColorFix(input_img, ref_img, scale_factor: float):
    if scale_factor != 100.0:
        # Make sure reference image dims are not resized to 0
        h, w, _ = get_h_w_c(ref_img)
        out_dims = (
            max(ceil(w * (scale_factor / 100)), 1),
            max(ceil(h * (scale_factor / 100)), 1),
        )

        ref_img = cv2.resize(
            ref_img,
            out_dims,
            interpolation=cv2.INTER_AREA,
        )
        input_h, input_w, input_c = get_h_w_c(input_img)
        ref_h, ref_w, ref_c = get_h_w_c(ref_img)

        assert (
                ref_w < input_w and ref_h < input_h
        ), "Image must be larger than Reference Image"
        assert input_c in (3, 4), "The input image must be an RGB or RGBA image"
        assert ref_c in (3, 4), "The reference image must be an RGB or RGBA image"

        # adjust channels
        alpha = None
        if input_c > ref_c:
            alpha = input_img[:, :, 3:4]
            input_img = input_img[:, :, :ref_c]
        elif ref_c > input_c:
            ref_img = ref_img[:, :, :input_c]

        # Find the diff of both images

        # Downscale the input image
        downscaled_input = cv2.resize(
            input_img,
            (ref_w, ref_h),
            interpolation=cv2.INTER_AREA,
        )

        # Get difference between the reference image and downscaled input
        downscaled_diff = ref_img - downscaled_input  # type: ignore

        # Upsample the difference
        diff = cv2.resize(
            downscaled_diff,
            (input_w, input_h),
            interpolation=cv2.INTER_CUBIC,
        )

        result = input_img + diff

        # add alpha back in
        if alpha is not None:
            result = np.concatenate([result, alpha], axis=2)

        return np.clip(result, 0, 1)


references_path = Path('./reference')
inputs_path = Path('./input')
reference_list = list(references_path.glob('**/*.*'))
input_list = list(inputs_path.glob('**/*.*'))
if len(reference_list) == len(input_list):
    # extremely bare-bones verification of content, ideally would check each item to have same sub-path and name.
    for reference_path, input_path in zip(reference_list, input_list):
        if reference_path.stem == input_path.stem:
            print("ref: " + reference_path.name)
            print("in:  " + input_path.name)
            input_image = Image.open(input_path)
            reference_image = Image.open(reference_path)
            if input_image.mode == "L":
                input_array = np.asarray(input_image.convert('RGB')) / 255
            else:
                input_array = np.asarray(input_image) / 255
            if reference_image.mode == "L":
                reference_array = np.asarray(reference_image.convert('RGB')) / 255
            else:
                reference_array = np.asarray(reference_image) / 255
            output_array = AverageColorFix(input_array, reference_array, 25)
            output_image = Image.fromarray((output_array * 255).astype(np.uint8))
            output_path = Path.joinpath(
                Path('./output'), (input_path.relative_to(*inputs_path.parts[:1]).with_name(input_path.stem + '.png')))
            output_path.parent.mkdir(exist_ok=True, parents=True)
            output_image.save(output_path)
        else:
            print("ref: " + reference_path.name + ", doesn't match input: " + input_path.name)
            break
    else:
        print("ref images count and input images count are not equal.")
