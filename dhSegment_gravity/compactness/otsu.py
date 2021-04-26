import cv2
import numpy as np
from matplotlib import pyplot as plt

from PIL import Image

import argparse

parser = argparse.ArgumentParser(description='Otsu Binarization')
parser.add_argument('-imgpath', type=str, required=True,
                   help='a path to the input image')

parser.add_argument('-save', type=str, required=True,
                   help='a path to the output image')

args = parser.parse_args()

IMAGE_PATH = args.imgpath
SAVE_PATH  = args.save

# read image
greyscaleImage = cv2.imread(IMAGE_PATH, 0)

# Otsu's thresholding
ret2,binaryImage = cv2.threshold(greyscaleImage,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

binaryImage_ = Image.fromarray(binaryImage)
binaryImage_ = binaryImage_.convert('1')
    
binaryImage_.save(SAVE_PATH, format='TIFF', dpi=(300.,300.), compression='tiff_lzw')