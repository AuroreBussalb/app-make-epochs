#!/usr/local/bin/python3

import json
import mne
import numpy as np

def make_epochs(raw):

	print(raw.info['events'])
	if raw.info['events'] is True:
	    print('events')
	else:
		print('no events')
    
    # create fixed length events
    array_events = mne.make_fixed_length_events(raw, duration=10)

    # create epochs
    epoched_data = mne.Epochs(raw, array_events)

    # Save file
    epoched_data.save("out_dir_make_epochs/meg.fif", overwrite=True)

    return epoched_data


def main():

    # Generate a json.product to display messages on Brainlife UI
    dict_json_product = {'brainlife': []}

    # Load inputs from config.json
    with open('config.json') as config_json:
        config = json.load(config_json)

    # Read the files
    data_file = config.pop('fif')
    raw = mne.io.read_raw_fif(data_file, allow_maxshield=True)

    # Epoch data
    epoched_data = make_epochs(raw)

    # Success message in product.json    
    dict_json_product['brainlife'].append({'type': 'success', 'msg': 'Data was successfully epoched.'})

    # Save the dict_json_product in a json file
    with open('product.json', 'w') as outfile:
        json.dump(dict_json_product, outfile)


if __name__ == '__main__':
    main()