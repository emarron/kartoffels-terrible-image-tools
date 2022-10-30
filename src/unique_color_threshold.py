import shutil
from pathlib import Path
import numpy as np
from PIL import Image
from packageland import handler


def get_unique_colors(path):
    # https://stackoverflow.com/questions/59669715/fastest-way-to-find-the-rgb-pixel-color-count-of-image/59671950#59671950
    with Image.open(path).convert('RGB') as img:
        na = np.array(img)
        f = np.dot(na.astype(np.uint32), [1, 256, 65536])
        nColours = len(np.unique(f))
        return nColours


def unique_color_threshold(path):
    # value = 2e6 for jank, 200-ish for not ffxiv color-maps
    value = 1000
    if get_unique_colors(path) > value:
        shutil.copy(path, ("./threshold_matched/" + path.name))


if __name__ == '__main__':
    output_path = Path('./threshold_matched')
    output_path.mkdir(exist_ok=True, parents=True)
    inputs_path = Path('./channel_variance')
    input_list = list(inputs_path.glob('**/*.*'))
    parallel = True
    if parallel:
        handler.parallel_process(input_list, unique_color_threshold, 10)
    else:
        handler.solo_process(input_list, unique_color_threshold)