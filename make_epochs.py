#!/usr/local/bin/python3

import json
import mne
import numpy as np
import warnings
import os 

def make_epochs(raw, events):

    if events is not None:
        # Convert tsv file into an numpy array of integers
        array_events = np.loadtxt(fname=events, delimiter="\t")
        events = array_events.astype(int)

    else:
        events = mne.find_events(raw)

    # Create epochs from events
    epoched_data = mne.Epochs(raw, events)

    # Save file
    epoched_data.save("out_dir_make_epochs/meg.fif", overwrite=True)

    return epoched_data


def main():

    # Generate a json.product to display messages on Brainlife UI
    dict_json_product = {'brainlife': []}

    # Load inputs from config.json
    with open('config.json') as config_json:
        config = json.load(config_json)

    # Read the MEG file 
    data_file = config.pop('fif')
    raw = mne.io.read_raw_fif(data_file, allow_maxshield=True)

    # Read the events file
    events_file = config.pop('events')

    # Test if events file exist
    if os.path.exists(events_file) is False:
        events_file = None
        user_warning_message = f'You are going to create epochs from events ' \
                               f'contained in your fif file.'
        warnings.warn(user_warning_message)
        dict_json_product['brainlife'].append({'type': 'info', 'msg': user_warning_message})
    else:
        user_warning_message = f'You are going to create epochs from events ' \
                               f'created beforehand.'
        warnings.warn(user_warning_message)
        dict_json_product['brainlife'].append({'type': 'info', 'msg': user_warning_message})

    # Epoch data
    epoched_data = make_epochs(raw, events_file)

    # Success message in product.json    
    dict_json_product['brainlife'].append({'type': 'success', 'msg': 'Data was successfully epoched.'})

    # Save the dict_json_product in a json file
    with open('product.json', 'w') as outfile:
        json.dump(dict_json_product, outfile)


if __name__ == '__main__':
    main()