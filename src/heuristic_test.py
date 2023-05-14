import argparse
import csv
import shutil
from pathlib import Path
import numpy as np
from scipy.stats import chisquare

from packageland import handler
from PIL import Image, ImageStat

parser = argparse.ArgumentParser(description="Heuristic Filters, Filter images by histogram based heuristics")
parser.add_argument('--directory', '-d', metavar='-D', type=str, help='Initial directory to be processed.',
                    required=True)
parser.add_argument('--command', '-c', metavar='-C', type=str, required=True)
parser.add_argument('--parallel', '-p', metavar='-P', action=argparse.BooleanOptionalAction,
                    help='multicore processing')
parser.add_argument('--multiplier', '-m', metavar='-M', type=float, default=5,
                    help='if using multicore processing, job multiplier per core. default = 5')
# parser.add_argument('--tolerance', '-t', metavar='-T', type=float, default=10,
#                     help='absolute tolerance value between 0 and infinity, default = 10')
args = parser.parse_args()

np.seterr(all='raise')
Image.MAX_IMAGE_PIXELS = None


def save(image, path):
    path.parent.mkdir(exist_ok=True, parents=True)
    image.save(path.with_suffix('.png'), compress_level=1)


def make_path(path, d_suffix, tolerance):
    out_folder = Path(str(p.name) + "_" + d_suffix + "_" + str(tolerance).replace('.', '-'))
    out_path = Path.joinpath(out_folder, path.name)
    return out_path


def get_brightness(image):
    img_l = image.convert('L')
    stat = ImageStat.Stat(img_l)
    return stat.rms[0]


def get_channels(image):
    r = np.asarray(image.getchannel('R')).astype(int)
    g = np.asarray(image.getchannel('G')).astype(int)
    b = np.asarray(image.getchannel('B')).astype(int)
    result = r, g, b
    return result


def has_data(image):
    r = 1
    g = 1
    b = 1
    if len(image.getchannel('R').getcolors()) == 1:
        r = 0
    if len(image.getchannel('G').getcolors()) == 1:
        g = 0
    if len(image.getchannel('B').getcolors()) == 1:
        b = 0
    return [r, g, b]


def get_percent_same(r, g, b, tolerance):
    r_g = np.sum(np.isclose(r, g, atol=tolerance) / r.size)
    r_b = np.sum(np.isclose(r, b, atol=tolerance) / r.size)
    g_b = np.sum(np.isclose(g, b, atol=tolerance) / r.size)
    return r_g, r_b, g_b


def get_mse(r, g, b):
    r_g = np.mean((r - g) ** 2)
    r_b = np.mean((r - b) ** 2)
    g_b = np.mean((g - b) ** 2)
    return r_g, r_b, g_b


def get_same(r, g, b, tolerance):
    r_g = np.allclose(r, g, atol=tolerance, rtol=0)
    r_b = np.allclose(r, b, atol=tolerance, rtol=0)
    g_b = np.allclose(g, b, atol=tolerance, rtol=0)
    return r_g, r_b, g_b


def save_channel(channel, image_path, image, is_data, tolerance):
    channel_data = image.getchannel(channel)
    if is_data:
        suffix = channel + "_" + "D"
    else:
        suffix = channel + "_" + "E"
    # suffix = channel
    output_path = make_path(image_path, suffix, tolerance)
    output_path.parent.mkdir(exist_ok=True, parents=True)
    save(channel_data, output_path)
    return suffix


def sort_image(image_path, tolerance):
    """
    sort RGB into "Y_D, Y_E, R_D, R_E, G_D, G_E, B_D, B_E" based on a_tol
    :param tolerance:
    :param image_path:
    :return: tolerance value, bool[r_g, r_b, g_b], bool[data]
    """
    with Image.open(image_path) as image:
        r, g, b = get_channels(image)
        data = has_data(image)
    same = get_same(r, g, b, tolerance)
    # percent = get_percent_same(r, g, b)
    # mse = get_mse(r, g, b)
    # avg = np.mean(r - g), np.mean(g - b), np.mean(b - g)
    # std = np.std(r - g), np.std(g - b), np.std(b - g)
    del r, g, b
    status = []
    # don't use relative tolerance, except for the default which is 1e-05
    # don't use confint as will allow spec of color somewhere like : monsterm0053objbodyb0001texturev02_m0053b0001_c_s.png
    if all(same):
        if data == [0, 0, 0]:
            suffix = "Y_E"
        else:
            suffix = "Y_D"
        # suffix = "Y"
        output_path = make_path(image_path, suffix, tolerance)
        output_path.parent.mkdir(exist_ok=True, parents=True)
        shutil.copy(image_path, output_path)
        status.append(suffix)
    else:
        with Image.open(image_path) as image:
            status.append(save_channel('R', image_path, image, data[0], tolerance))
            status.append(save_channel('G', image_path, image, data[1], tolerance))
            status.append(save_channel('B', image_path, image, data[2], tolerance))
        # if data == [1, 1, 1]:
        #     suffix = "RGB_D"
        #     output_path = make_path(image_path, suffix, tolerance)
        #     output_path.parent.mkdir(exist_ok=True, parents=True)
        #     shutil.copy(image_path, output_path)
        # suffix = "RGB"
        # output_path = make_path(image_path, suffix, tolerance)
        # output_path.parent.mkdir(exist_ok=True, parents=True)
        # shutil.copy(image_path, output_path)
    return [tolerance, same[0], same[1], same[2], data[0], data[1], data[2], status]
    # return [percent[0], percent[1], percent[2], data[0], data[1], data[2], avg[0], avg[1], avg[2], std[0],
    #         std[1], std[2], mse[0], mse[1], mse[2], suffix]


def read_command(command):
    if "sort" == command.lower():
        return sort_image, "_sort_"


p = Path(args.directory)
parallel = args.parallel
multiplier = args.multiplier
command = read_command(args.command)
# tolerance = args.tolerance
dict_3d = {}


def image_handler(image_path):
    function = command[0]
    # for i in range(25):
    #     result = function(image_path, tolerance=i)
    result = function(image_path, tolerance=9)
    dict_3d[image_path.as_posix()] = result


if __name__ == '__main__':
    grabber = list(p.glob('**/*.*'))
    function = image_handler
    if parallel:
        handler.parallel_process(grabber, function, multiplier)
    else:
        handler.solo_process(grabber, function)
    with open('output_status.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(
            ['Path', 'tolerance', 'same r-g', 'same r-b', 'same g-b', 'data r-g', 'data r-b', 'data g-b',
             'Classification'])
        for name, values in dict_3d.items():
            writer.writerow([name] + values)
