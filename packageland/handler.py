import gc
import os
from multiprocessing import Pool

from tqdm import tqdm
# from tqdm.contrib.concurrent import process_map


def chunks(arr, size):
    """
    split an array into chunks
    :param arr: the array
    :param size: size of each chunk
    :return: yields one chunk of size `size` of `arr`
    """
    for i in range(0, len(arr), size):
        yield arr[i: i + size]


def parallel_process(items, function, multiplier):
    core_count = os.cpu_count()
    with tqdm(total=len(items)) as pb:
        for chunk in chunks(items, round(core_count * multiplier)):
            with Pool(core_count) as p:
                p.map(function, chunk)
                gc.collect()
            pb.update(len(chunk))


#    process_map() could work but there is some safety nets in here I need.

def solo_process(items, function):
    list(map(function, tqdm(items)))
