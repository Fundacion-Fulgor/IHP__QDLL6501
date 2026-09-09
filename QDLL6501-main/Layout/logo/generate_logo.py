import argparse
import math
from pathlib import Path
import runpy

import gdspy
import numpy as np
from PIL import Image


def generate(width, image_path, output):
    if not math.isfinite(width) or width < 24:
        raise ValueError("Width must be finite and at least 24 um")
    width = round(width / 0.005) * 0.005
    with Image.open(image_path) as source:
        image = source.convert("RGB").convert("L")
    image = image.point(lambda value: 255 if value < 240 else 0)
    bounds = image.getbbox()
    if bounds is None:
        raise ValueError("Image contains no logo")
    image = image.crop(bounds)
    pixels = int(width / 2) - 4
    height = max(1, round(pixels * image.height / image.width))
    image = image.resize((pixels, height), Image.Resampling.LANCZOS)
    bitmap = np.pad(np.asarray(image) / 127.5 - 1, 4, constant_values=-1)

    artistic = Path(__file__).parent / "artistic" / "scripts" / "meerkat.py"
    meerkat = runpy.run_path(str(artistic))
    kernels = np.asarray(meerkat["KERNELS"])
    primitives = gdspy.Cell("fulgor_primitives", exclude_from_current=True)
    for col in range(0, bitmap.shape[1] - 4, 3):
        for row in range(0, bitmap.shape[0] - 4, 3):
            patch = bitmap[row : row + 4, col : col + 4]
            match = np.sum(kernels * patch, axis=(1, 2)).argmax()
            meerkat["FUNCS"][match](primitives, row, col)

    bounds = primitives.get_bounding_box()
    if bounds is None:
        raise ValueError("Width is too small to resolve the logo")
    scale = width / (bounds[1, 0] - bounds[0, 0])
    cell = gdspy.Cell("FULGOR_LOGO", exclude_from_current=True)
    for polygon in primitives.get_polygons():
        points = np.rint((polygon - bounds[0]) * scale / 0.005) * 0.005
        cell.add(gdspy.Polygon(points, layer=134, datatype=0))
    library = gdspy.GdsLibrary(unit=1e-6, precision=5e-9)
    library.add(cell)
    library.write_gds(str(output))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("width", type=float, help="Width in um")
    parser.add_argument(
        "-i",
        "--image",
        type=Path,
        default=Path.home() / "Downloads" / "fulgor_edited_medium.jpg",
    )
    parser.add_argument("-o", "--output", type=Path, default=Path("fulgor.gds"))
    args = parser.parse_args()
    try:
        generate(args.width, args.image.expanduser(), args.output.expanduser())
    except (ValueError, OSError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
