#!/usr/bin/env python
__author__ = 'solivr'

import os
from exps.evaluation.base import Metrics, compare_bin_prediction_to_label
from glob import glob
from scipy.misc import imread, imsave
import cv2
import numpy as np


def dibco_evaluate_folder(output_folder: str, validation_dir: str, verbose=False, debug_folder=None) -> dict:
    filenames_processed = glob(os.path.join(output_folder, '*.png'))

    if debug_folder is not None:
        os.makedirs(debug_folder, exist_ok=True)

    global_metrics = Metrics()
    for filename in filenames_processed:
        post_processed = imread(filename, mode='L')
        post_processed = post_processed / np.max(post_processed)

        basename = os.path.basename(filename).split('.')[0]
        label_image = imread(os.path.join(validation_dir, 'labels', '{}.png'.format(basename)), mode='L')
        label_image_normalized = label_image / np.max(label_image)

        target_shape = (label_image.shape[1], label_image.shape[0])
        bin_upscaled = cv2.resize(np.uint8(post_processed), target_shape, interpolation=cv2.INTER_NEAREST)

        # Compute errors
        metric = compare_bin_prediction_to_label(bin_upscaled, label_image_normalized)
        global_metrics += metric

        if debug_folder is not None:
            debug_image = np.zeros((*label_image.shape[:2], 3), np.uint8)
            debug_image[np.logical_and(bin_upscaled, label_image_normalized)] = [0, 255, 0]
            debug_image[np.logical_and(bin_upscaled, label_image_normalized == 0)] = [0, 0, 255]
            debug_image[np.logical_and(bin_upscaled == 0, label_image_normalized)] = [255, 0, 0]
            imsave(os.path.join(debug_folder, basename + '.png'), debug_image)

    global_metrics.compute_mse()
    global_metrics.compute_psnr()
    global_metrics.compute_prf()

    if verbose:
        print('EVAL --- PSNR : {}, R : {}, P : {}, FM : {}'.format(global_metrics.PSNR, global_metrics.recall,
                                                                   global_metrics.precision, global_metrics.f_measure))

    return {k: v for k, v in vars(global_metrics).items() if k in ['MSE', 'PSNR', 'precision', 'recall', 'f_measure']}

