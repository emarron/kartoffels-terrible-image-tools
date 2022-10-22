import argparse
import sys
from pathlib import Path

from PIL import Image, ImageChops

from packageland import handler

parser = argparse.ArgumentParser(description="ICADM, Image Channel and Directory Modifier")
parser.add_argument('--directory', metavar='-D', type=str, help='Initial directory to be processed.', required=True)
parser.add_argument('--command', metavar='-C', type=str,
                    help='split, merge, 4split, 4merge, flatten, unflatten, tga_png (tga_png is destructive!)', required=True)
parser.add_argument('--output', metavar='-O', type=str, help='output image type, png=default or tga.')
args = parser.parse_args()

if args.directory.endswith('/') or args.directory.endswith('\\'):
    folder = args.directory[:-1]
else:
    folder = args.directory
p = Path(folder)
command = args.command


def save(image, path):
    path.parent.mkdir(exist_ok=True, parents=True)
    if args.output is not None and args.output.lower() == 'tga':
        image.save(path.with_suffix('.tga'))
    else:
        image.save(path.with_suffix('.png'), compress_level=1)


def flatten_path(path):
    flattened_path = Path(str(path.parent).replace('\\', '') + path.stem + ".png")
    return flattened_path


def unflatten_path(path):
    unflattened_path = Path(str(path.parent).replace('😊', '\\') + path.name)
    return unflattened_path


def do_thing_flatten(path):
    """
    flatten dir and save to PNG
    """
    with Image.open(path) as image:
        out_folder = Path(str(folder) + '_RGBA')
        out_path = Path.joinpath(out_folder, flatten_path(path))
        save(image.convert('RGBA'), out_path)


def do_thing_unflatten(path):
    flattened_folder = Path(str(folder) + '_RGBA')
    flattened_path = Path.joinpath(flattened_folder, flatten_path(path))
    try:
        with Image.open(flattened_path) as image:
            merged_path = Path.joinpath(Path('./output'), Path(*path.parts[1:]).with_suffix(".tga"))
            save(image, merged_path)
    except FileNotFoundError:
        pass


def do_thing_split_RGB_A(path):
    """
    flatten dir, separate RGB and A, and save to PNG
    """
    with Image.open(path) as image:
        rgb_folder, alpha_folder = [Path(str(folder) + '_RGB'), Path(str(folder) + '_A')]
        rgb_path = Path.joinpath(rgb_folder, flatten_path(path))
        alpha_path = Path.joinpath(alpha_folder, flatten_path(path))
        save(image.convert('RGB'), rgb_path)
        try:
            with image.getchannel('A') as alpha:
                if ImageChops.invert(alpha).getbbox():
                    save(alpha, alpha_path)
        except ValueError:
            pass


def do_thing_split_R_G_B_A(path):
    """
    flatten dir, separate R, G, B, A, and save to PNG
    """
    with Image.open(path) as image:
        # todo: first part to function.
        red_folder, green_folder, blue_folder, alpha_folder = [Path(str(folder) + 'R'), Path(str(folder) + 'G'),
                                                               Path(str(folder) + 'B'), Path(str(folder) + 'A')]
        red_path, green_path, blue_path, alpha_path = [Path.joinpath(red_folder, flatten_path(path)),
                                                       Path.joinpath(green_folder, flatten_path(path)),
                                                       Path.joinpath(blue_folder, flatten_path(path)),
                                                       Path.joinpath(alpha_folder, flatten_path(path))]
        save(image.getchannel('R'), red_path)
        save(image.getchannel('G'), green_path)
        save(image.getchannel('B'), blue_path)
        try:
            with image.getchannel('A') as alpha:
                if ImageChops.invert(alpha).getbbox():
                    save(alpha, alpha_path)
        except ValueError:
            pass


def do_thing_TGA_PNG(path):
    """
    convert TGA to PNG
    """
    if path.suffix == '.tga':
        with Image.open(path) as image:
            image.save(path.with_suffix('.png'), compress_level=1)
        path.unlink()


def do_thing_merge_R_G_B_A(path):
    red_folder, green_folder, blue_folder, alpha_folder = [Path(str(folder) + 'R'), Path(str(folder) + 'G'),
                                                           Path(str(folder) + 'B'), Path(str(folder) + 'A')]
    red_path, green_path, blue_path, alpha_path = [Path.joinpath(red_folder, flatten_path(path)),
                                                   Path.joinpath(green_folder, flatten_path(path)),
                                                   Path.joinpath(blue_folder, flatten_path(path)),
                                                   Path.joinpath(alpha_folder, flatten_path(path))]
    try:
        with Image.merge('RGB', [Image.open(red_path).convert('L'), Image.open(green_path).convert('L'),
                                 Image.open(blue_path).convert('L')]) as image:
            merged_path = Path.joinpath(Path('./output'), Path(*path.parts[1:]))
            try:
                with Image.open(alpha_path).convert('L') as alpha:
                    image.putalpha(alpha)
                    save(image, merged_path)
            except FileNotFoundError:
                # could just copy rather than open and save
                save(image, merged_path)
    except FileNotFoundError:
        pass


def do_thing_merge_RGB_A(path):
    rgb_folder, alpha_folder = [Path(str(folder) + '_RGB'), Path(str(folder) + '_A')]
    rgb_path = Path.joinpath(rgb_folder, flatten_path(path))
    alpha_path = Path.joinpath(alpha_folder, flatten_path(path))
    try:
        with Image.open(rgb_path) as image:
            merged_path = Path.joinpath(Path('./output'), Path(*path.parts[1:]))
            try:
                with Image.open(alpha_path).convert('L') as alpha:
                    image.putalpha(alpha)
                    save(image, merged_path)
            except FileNotFoundError:
                # could just copy rather than open and save
                save(image, merged_path)
    except FileNotFoundError:
        pass


def read_command(command):
    if "flatten" == command.lower():
        return do_thing_flatten
    if "split" == command.lower():
        return do_thing_split_RGB_A
    if "merge" == command.lower():
        return do_thing_merge_RGB_A
    if "tga_png" == command.lower():
        return do_thing_TGA_PNG
    if "4split" == command.lower():
        return do_thing_split_R_G_B_A
    if "4merge" == command.lower():
        return do_thing_merge_R_G_B_A
    if "unflatten" == command.lower():
        return do_thing_unflatten


if __name__ == '__main__':
    grabber = list(p.glob('**/*.*'))
    function = read_command(command)
    parallel = True
    if parallel:
        handler.parallel_process(grabber, function, 5)
    else:
        handler.solo_process(grabber, function)
