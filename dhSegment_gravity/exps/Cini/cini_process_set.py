#!/usr/bin/env python
__author__ = 'solivr'

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir)))
from doc_seg.loader import LoadedModel
from cini_post_processing import cini_post_processing_fn
from cini_evaluation import cini_evaluate_folder

import tensorflow as tf
from tqdm import tqdm
import numpy as np
import argparse
from glob import glob
from scipy.misc import imread, imresize, imsave
import tempfile
import json
from doc_seg.post_processing import PAGE
from doc_seg.utils import hash_dict, dump_json


def predict_on_set(filenames_to_predict, model_dir, output_dir):
    """

    :param filenames_to_predict:
    :param model_dir:
    :param output_dir:
    :return:
    """
    with tf.Session():
        m = LoadedModel(model_dir, 'filename')
        for filename in tqdm(filenames_to_predict, desc='Prediction'):
            pred = m.predict(filename)['probs'][0]
            np.save(os.path.join(output_dir, os.path.basename(filename).split('.')[0]),
                    np.uint8(255 * pred))


def find_elements(img_filenames, dir_predictions, post_process_params, output_dir, debug=False, mask_dir: str=None):
    """

    :param img_filenames:
    :param dir_predictions:
    :param post_process_params:
    :param output_dir:
    :return:
    """

    os.makedirs(output_dir, exist_ok=True)

    for filename in tqdm(img_filenames, 'Post-processing'):
        orig_img = imread(filename, mode='RGB')
        basename = os.path.basename(filename).split('.')[0]

        filename_pred = os.path.join(dir_predictions, basename + '.npy')
        pred = np.load(filename_pred)/255  # type: np.ndarray

        contours, lines_mask = cini_post_processing_fn(pred, **post_process_params,
                                                       output_basename=os.path.join(output_dir, basename))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--model-dir', type=str, required=True,
                        help='Directory of the model (should be of type ''*/export/<timestamp>)')
    parser.add_argument('-i', '--input-files', type=str, required=True, nargs='+',
                        help='Folder containing the images to evaluate the model on')
    parser.add_argument('-o', '--output-dir', type=str, required=True,
                        help='Folder containing the outputs (.npy predictions and visualization errors)')
    parser.add_argument('-gt', '--ground_truth_dir', type=str, required=True,
                        help='Ground truth directory containing the labeled images')
    parser.add_argument('--params-file', type=str, default=None,
                        help='JSOn file containing the params for post-processing')
    parser.add_argument('--gpu', type=str, default='0', help='Which GPU to use')
    parser.add_argument('-pp', '--post-process-only', default=False, action='store_true',
                        help='Whether to make or not the prediction')
    args = parser.parse_args()
    args = vars(args)

    os.environ["CUDA_VISIBLE_DEVICES"] = args.get('gpu')
    model_dir = args.get('model_dir')
    input_files = args.get('input_files')
    if len(input_files) == 0:
        raise FileNotFoundError

    output_dir = args.get('output_dir')
    os.makedirs(output_dir, exist_ok=True)

    # Prediction
    npy_directory = output_dir
    if not args.get('post_process_only'):
        predict_on_set(input_files, model_dir, npy_directory)

    npy_files = glob(os.path.join(npy_directory, '*.npy'))

    if args.get('params_file') is None:
        print('No params file found')
        params_list = [{"clean_predictions": True, "advanced": True}]
    else:
        with open(args.get('params_file'), 'r') as f:
            configs_data = json.load(f)
            # If the file contains a list of configurations
            if 'configs' in configs_data.keys():
                params_list = configs_data['configs']
                assert isinstance(params_list, list)
            # Or if there is a single configuration
            else:
                params_list = [configs_data]

    gt_dir = args.get('ground_truth_dir')

    for params in tqdm(params_list, desc='Params'):
        print(params)
        exp_dir = os.path.join(output_dir, '_' + hash_dict(params))
        find_elements(input_files, npy_directory, params, exp_dir, debug=False)

        if gt_dir is not None:
            scores = cini_evaluate_folder(exp_dir, gt_dir, debug_folder=os.path.join(exp_dir, '_debug'))
            dump_json(os.path.join(exp_dir, 'post_process_config.json'), params)
            dump_json(os.path.join(exp_dir, 'scores.json'), scores)
            print('Scores : {}'.format(scores))



