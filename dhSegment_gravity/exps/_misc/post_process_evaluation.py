#!/usr/bin/env python
__author__ = 'solivr'

import argparse
import json
import os
from glob import glob
from hashlib import sha1
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from exps import cbad_post_processing_fn, dibco_binarization_fn, cini_post_processing_fn, \
    page_post_processing_fn, diva_post_processing_fn, ornaments_post_processing_fn
from exps import cbad_evaluate_folder, dibco_evaluate_folder, cini_evaluate_folder, \
    page_evaluate_folder, diva_evaluate_folder, ornament_evaluate_folder, evaluate_epoch
from dh_segment.utils import parse_json
from tqdm import tqdm
from functools import partial

POST_PROCESSING_DIR_NAME = 'post_processing'

POST_PROCESSING_EVAL_FN_DICT = {
    'cbad': (cbad_post_processing_fn, cbad_evaluate_folder),
    'dibco': (dibco_binarization_fn, dibco_evaluate_folder),
    'cini': (cini_post_processing_fn, cini_evaluate_folder),
    'page': (page_post_processing_fn, page_evaluate_folder),
    'diva': (diva_post_processing_fn, diva_evaluate_folder),
    'ornaments': (ornaments_post_processing_fn, ornament_evaluate_folder)
}


def _hash_dict(params):
    return sha1(json.dumps(params, sort_keys=True).encode()).hexdigest()


def evaluate_one_model(model_dir, validation_dir, post_processing_pair, post_processing_params,
                       verbose=False, save_params=True, n_selected_epochs=None) -> None:
    """
    Evaluate a combination model/post-process
    :param model_dir:
    :param validation_dir:
    :param post_processing_pair:
    :param post_processing_params:
    :param verbose:
    :param save_params:
    :return:
    """
    eval_outputs_dir = os.path.join(model_dir, 'eval', 'epoch_*')
    list_saved_epochs = glob(eval_outputs_dir)
    list_saved_epochs.sort()
    if n_selected_epochs is not None:
        list_saved_epochs = list_saved_epochs[-n_selected_epochs:]
    if len(list_saved_epochs) == 0:
        print('No file found in : {}'.format(eval_outputs_dir))
        return

    post_process_dir = os.path.join(model_dir, POST_PROCESSING_DIR_NAME, _hash_dict(post_processing_params))
    os.makedirs(post_process_dir, exist_ok=True)

    validation_scores = dict()
    for saved_epoch in tqdm(list_saved_epochs, desc='Epoch dir'):
        epoch_dir_name = saved_epoch.split(os.path.sep)[-1]
        epoch, timestamp = (int(s) for s in epoch_dir_name.split('_')[1:3])
        validation_scores[epoch_dir_name] = {**evaluate_epoch(saved_epoch, validation_dir,
                                                              post_process_fn=partial(post_processing_pair[0],
                                                                                      **post_processing_params),
                                                              evaluation_fn=post_processing_pair[1]
                                                              ),
                                             "epoch": epoch,
                                             "timestamp": timestamp
                                             }

    with open(os.path.join(post_process_dir, 'validation_scores.json'), 'w') as f:
        json.dump(validation_scores, f)

    if save_params:
        with open(os.path.join(post_process_dir, 'post_process_params.json'), 'w') as f:
            json.dump({'post_process_fn': post_processing_pair[0].__name__, 'params': post_processing_params}, f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--model-dir', type=str, required=True, nargs='+')
    parser.add_argument('-p', '--params-json-file', type=str, required=True)
    parser.add_argument('-t', '--task-type', type=str, required=True,
                        help="Choose among : 'cbad', 'dibco', 'page', 'cini'")
    parser.add_argument('-v', '--verbose', type=bool, default=False)
    parser.add_argument('-ne', '--n_epochs', type=int, default=None, help='Number of selected epochs to evaluate')
    # Labels dir is not necessary anymore, can be obtained directly from model config
    # parser.add_argument('-l', '--labels-dir', type=str, required=True)
    args = vars(parser.parse_args())

    # get the pair post-process fn and post-process eval
    post_processing_pair = POST_PROCESSING_EVAL_FN_DICT[args['task_type']]
    with open(args.get('params_json_file'), 'r') as f:
        configs_data = json.load(f)
        # If the file contains a list of configurations
        if 'configs' in configs_data.keys():
            params_list = configs_data['configs']
            assert isinstance(params_list, list)
        # Or if there is a single configuration
        else:
            params_list = [configs_data]

    model_dirs = args.get('model_dir')
    print('Found {} configs and {} model directories'.format(len(params_list), len(model_dirs)))

    for params in tqdm(params_list, desc='Params'):
        for model_dir in tqdm(model_dirs, desc='Model directory'):
            eval_data_dir = parse_json(os.path.join(model_dir, 'config.json'))['eval_dir']
            evaluate_one_model(model_dir, eval_data_dir,
                               post_processing_pair,
                               params, args.get('verbose'),
                               n_selected_epochs=args.get('n_epochs'))
