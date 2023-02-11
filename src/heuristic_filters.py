import argparse
import shutil
from pathlib import Path
import numpy as np

from packageland import handler
from PIL import Image, ImageStat

Image.MAX_IMAGE_PIXELS = None
# todo: make this less stupid with the operators and commands in general. subparsers I think?
parser = argparse.ArgumentParser(description="Heuristic Filters, Filter images by histogram based heuristics")
parser.add_argument('--directory', '-d', metavar='-D', type=str, help='Initial directory to be processed.',
                    required=True)
parser.add_argument('--command', '-c', metavar='-C', type=str,
                    help='variance_range, mean_range, stddev_mean. threshold_mean, median_mean, unique_colors, f_test',
                    required=True)
parser.add_argument('--parallel', '-p', metavar='-P', action=argparse.BooleanOptionalAction,
                    help='multicore processing')
parser.add_argument('--threshold', '-t', metavar='-T', type=float, default=128,
                    help='threshold between 0 to 255, default=128')
parser.add_argument('--multiplier', '-m', metavar='-M', type=float, default=5,
                    help='if using multicore processing, job multiplier per core. default = 5')
parser.add_argument('--operator', '-o', metavar='-O', type=str, default="gt",
                    help='use bash integer comparison style, i.e "gt","lt", default = "gt"')
args = parser.parse_args()

np.seterr(all='raise')


def compare_with_threshold(variable):
    if operator == "ge":
        return variable >= threshold
    if operator == "le":
        return variable <= threshold
    if operator == "gt":
        return variable > threshold
    if operator == "lt":
        return variable < threshold


def make_path(path, d_suffix):
    out_folder = Path(str(p.name) + d_suffix)
    out_path = Path.joinpath(out_folder, path.name)
    return out_path


def is_variance_range(image_path):
    """
    sort of like an f test, if the range is between channels' variance is high it tells us that the image is likely a
    composite/multi image.
    """
    with Image.open(image_path) as image:
        histogram = image.histogram()
        variance = ImageStat.Stat(histogram).var
        if np.any(variance):
            #normalized_variance = variance / np.linalg.norm(variance)
            #variance_range = (max(normalized_variance) - min(normalized_variance))
            variance_range = max(variance) - min(variance)
        else:
            variance_range = 0
        result = compare_two_values(variance_range, threshold)
    return result


def is_mean_range(image_path):
    with Image.open(image_path) as image:
        histogram = image.histogram()
        mean = ImageStat.Stat(histogram).mean
        if np.any(mean):
            #normalized_variance = mean / np.linalg.norm(mean)
            #mean_range = (max(normalized_variance) - min(normalized_variance))
            mean_range = max(mean)-min(mean)
        else:
            mean_range = 0
        result = compare_two_values(mean_range, threshold)
    return result


def compare_two_values(var1, var2):
    if operator == "ge":
        return var1 >= var2
    if operator == "le":
        return var1 <= var2
    if operator == "gt":
        return var1 > var2
    if operator == "lt":
        return var1 < var2
    if operator == 'eq':
        return var1 == var2
    if operator == "ne":
        return var1 != var2


def stddev_mean(image_path):
    with Image.open(image_path) as image:
        histogram = image.histogram()
        mean, stddev = np.asarray(ImageStat.Stat(histogram).mean), np.asarray(ImageStat.Stat(histogram).stddev)
        result = compare_two_values(stddev, mean)
        return result


def median_mean(image_path):
    with Image.open(image_path) as image:
        histogram = image.histogram()
        mean, median = np.asarray(ImageStat.Stat(histogram).mean), np.asarray(ImageStat.Stat(histogram).median)
        result = compare_two_values(median, mean)
        return result


def mode_mean(image_path):
    with Image.open(image_path) as image:
        histogram = image.histogram()
        mean, mode = np.asarray(ImageStat.Stat(histogram).mean), np.asarray(ImageStat.Stat(histogram).mode)
        result = compare_two_values(mode, mean)
        return result


def threshold_mean(image_path):
    with Image.open(image_path) as image:
        histogram = image.histogram()
        mean = np.asarray(ImageStat.Stat(histogram).mean)
        result = compare_two_values(threshold, mean)
        return result


def do_f_test(image_path):
    """
    normally you would use this instead of ranges but division is expensive, and I'm already using python.
    """
    with Image.open(image_path) as image:
        histogram = image.histogram()
        variance = ImageStat.Stat(histogram).var
        normalized_variance = variance / np.linalg.norm(variance)
        f_value = (max(normalized_variance) / min(normalized_variance))
        result = compare_two_values(f_value)
    return result


def get_unique_colors(image_path):
    """
    I just googled some fast ways to do this. method 1 is fast, but sometimes gets a memory error, so if that happens
    we use method 2, which is like 4x slower.
    """
    # https://stackoverflow.com/questions/59669715/fastest-way-to-find-the-rgb-pixel-color-count-of-image/59671950#59671950
    with Image.open(image_path).convert('RGB') as img:
        na = np.array(img)
        # size = np.average([img.width, img.height])
    try:
        f = np.dot(na.astype(np.uint32), [1, 256, 65536])
        colors = len(np.unique(f))
    except np.core._exceptions._ArrayMemoryError:
        colors = np.unique(na.reshape(-1, na.shape[2]), axis=0)
        # waaaaaaaaaaaaaaaaaaaaaay slower
    # result = size < threshold * colors
    result = colors > threshold
    return result


def read_command(command):
    if "variance_range" == command.lower():
        return is_variance_range, "_variance_range_"
    if "mean_range" == command.lower():
        return is_mean_range, "_mean_range_"
    if "stddev_mean" == command.lower():
        return stddev_mean, "_stddev_mean_"
    if "threshold_mean" == command.lower():
        return threshold_mean, "_mean_"
    if "f_test" == command.lower():
        return do_f_test, "_f_test_"
    if "median_mean" == command.lower():
        return median_mean, "_median_mean_"
    if "unique_colors" == command.lower():
        return get_unique_colors, "_unique_colors_"


p = Path(args.directory)
parallel = args.parallel
multiplier = args.multiplier
threshold = args.threshold
operator = args.operator
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
