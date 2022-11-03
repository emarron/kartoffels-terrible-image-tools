import argparse
import shutil
from pathlib import Path
import numpy as np

from packageland import handler
from PIL import Image, ImageStat

Image.MAX_IMAGE_PIXELS = None

parser = argparse.ArgumentParser(description="Heuristic Filters, Filter images by histogram based heuristics")
parser.add_argument('--directory', '-d', metavar='-D', type=str, help='Initial directory to be processed.',
                    required=True)
parser.add_argument('--command', '-c', metavar='-C', type=str,
                    help='variance_range, mean_range, stddev_mean',
                    required=True)
parser.add_argument('--parallel', '-p', metavar='-P', action=argparse.BooleanOptionalAction,
                    help='multicore processing')
parser.add_argument('--threshold', '-t', metavar='-T', type=float, default=0.5,
                    help='threshold for mean and var range, scalar for stddev, default=0.5')
parser.add_argument('--multiplier', '-m', metavar='-M', type=float, default=5,
                    help='if using multicore processing, job multiplier per core. default = 5')
args = parser.parse_args()
"""some operations to hopefully find interesting images when they are not labeled properly. 
mean_range: A large difference between the means of each channel can indicate that the channels are being used for 
different purposes. threshold should be around 0.1-1.0
var_range: A large difference between the variances of each channel can indicate the the channels are being used for
different purposes. threshold should be from 0.1-1.0
stdev_greater_than_mean: If the stddev of any channel is greater than the mean of that channel, then the image may have 
channel(s) being used for opacity. mean scalar should be from 1-5

basically some cost-effective F-tests
"""


def make_path(path, d_suffix):
    out_folder = Path(str(p.name) + d_suffix)
    out_path = Path.joinpath(out_folder, path.name)
    return out_path


def get_variance_range(image_path):
    with Image.open(image_path) as image:
        histogram = image.histogram()
        variance = ImageStat.Stat(histogram).var
        normalized_variance = variance / np.linalg.norm(variance)
        variance_range = (max(normalized_variance) - min(normalized_variance))
        result = is_range_greater_than_threshold(variance_range)
    return result


def get_mean_range(image_path):
    with Image.open(image_path) as image:
        histogram = image.histogram()
        mean = ImageStat.Stat(histogram).mean
        normalized_mean = mean / np.linalg.norm(mean)
        mean_range = (max(normalized_mean) - min(normalized_mean))
        result = is_range_greater_than_threshold(mean_range)
    return result


def is_range_greater_than_threshold(range):
    if range >= threshold:
        return True


def is_stddev_greater_than_mean(image_path):
    with Image.open(image_path) as image:
        histogram = image.histogram()
        mean, stddev = np.asarray(ImageStat.Stat(histogram).mean), np.asarray(ImageStat.Stat(histogram).stddev)
        result = (stddev > threshold * mean)
        # is equiv to stddev/mean > threshold, but faster
        return result


def is_med_greater_than_mean(image_path):
    with Image.open(image_path) as image:
        histogram = image.histogram()
        mean, median = np.asarray(ImageStat.Stat(histogram).mean), np.asarray(ImageStat.Stat(histogram).median)
        result = (median > threshold * mean)
        return result


def do_f_test(image_path):
    with Image.open(image_path) as image:
        histogram = image.histogram()
        variance = ImageStat.Stat(histogram).var
        normalized_variance = variance / np.linalg.norm(variance)
        f_value = (max(normalized_variance) / min(normalized_variance))
        result = is_range_greater_than_threshold(f_value)
    return result


def get_unique_colors(image_path):
    # https://stackoverflow.com/questions/59669715/fastest-way-to-find-the-rgb-pixel-color-count-of-image/59671950#59671950
    with Image.open(image_path).convert('RGB') as img:
        na = np.array(img)
    try:
        f = np.dot(na.astype(np.uint32), [1, 256, 65536])
        colors = len(np.unique(f))
    except np.core._exceptions._ArrayMemoryError:
        colors = np.unique(na.reshape(-1, na.shape[2]), axis=0)
        # waaaaaaaaaaaaaaaaaaaaaay slower
    result = colors > threshold
    return result


def read_command(command):
    if "variance_range" == command.lower():
        return get_variance_range, "_variance_range_"
    if "mean_range" == command.lower():
        return get_mean_range, "_mean_range_"
    if "stddev_mean" == command.lower():
        return is_stddev_greater_than_mean, "_sttdev_mean_"
    if "f_test" == command.lower():
        return do_f_test, "_f_test_"
    if "median_mean" == command.lower():
        return is_med_greater_than_mean, "_med_mean_"
    if "unique_colors" == command.lower():
        return get_unique_colors, "_unique_colors_"


p = Path(args.directory)
parallel = args.parallel
multiplier = args.multiplier
threshold = args.threshold
command = read_command(args.command)


def image_handler(image_path):
    function = command[0]
    suffix = command[1] + str(threshold).replace('.', '-')
    output_path = make_path(image_path, suffix)
    output_path.parent.mkdir(exist_ok=True, parents=True)
    result = function(image_path)
    try:
        if 1 in result:
            shutil.copy(image_path, output_path)
    except TypeError:
        if result == 1:
            shutil.copy(image_path, output_path)


if __name__ == '__main__':

    grabber = list(p.glob('**/*.*'))
    function = image_handler
    if parallel:
        handler.parallel_process(grabber, function, multiplier)

    else:
        handler.solo_process(grabber, function)
