#!/usr/local/bin/python3

import json
import mne
import numpy as np
import warnings
import shutil
import os 

def make_epochs(raw, events_file, param_event_id, param_tmin, param_tmax, param_baseline,
                param_picks_by_channel_types_or_names, param_picks_by_channel_indices, 
                param_preload, param_reject, param_flat, param_proj, param_decim,
                param_reject_tmin, param_reject_tmax, param_detrend, param_on_missing, 
                param_reject_by_annotation, param_metadata, param_event_repeated):
    """Create epochs from matrix events contained in a .tsv file.

    Parameters
    ----------
    raw: instance of mne.io.Raw
        Data from which the events will be extracted or created.
    events_file: str
        Path to the .tsv events file containing the matrix of events.
    param_event_id: int, list of int, or None
        The id of the event to consider. Default is None.
    param_tmin: float
        Start time before event. Default is -0.2.
    param_tmax: float
        End time after event. Default is 0.5.
    param_baseline: tuple of length 2 or None
        The time interval to consider as “baseline” when applying baseline correction. 
        Default is (None, 0).
    param_picks_by_channel_types_or_names: str, list of str, or None 
        Channels to include. In lists, channel type strings (e.g., ["meg", "eeg"]) will pick channels of those types, channel name 
        strings (e.g., ["MEG0111", "MEG2623"]) will pick the given channels. Can also be the string values “all” 
        to pick all channels, or “data” to pick data channels. None (default) will pick all data channels. Note 
        that channels in info['bads'] will be included if their names are explicitly provided.
    param_picks_by_channel_indices: list of int, slice, or None
        Channels to include. Slices (e.g., "0, 10, 2" or "0, 10" if you don't want a step) and lists of integers 
        are interpreted as channel indices. None (default) will pick all data channels. This parameter must be set 
        to None if param_picks_by_channel_types_or_names is not None. Note that channels in info['bads'] will 
        be included if their indices are explicitly provided.
    param_preload: bool
        Load all epochs from disk when creating the object or wait before accessing each epoch.
        Default is False.
    param_reject: dict or None
        Reject epochs based on peak-to-peak signal amplitude, i.e. the absolute difference between 
        the lowest and the highest signal value. Default is None.
    param_flat: dict or None
        Rejection parameters based on flatness of signal. Valid keys are 'grad', 'mag', 'eeg', 'eog', 'ecg'. 
        The values are floats that set the minimum acceptable peak-to-peak amplitude. Default is None.
    param_proj: bool or str
        Apply SSP projection vectors. If proj is ‘delayed’ and reject is not None the single epochs will be 
        projected before the rejection decision, but used in unprojected state if they are kept. Default is True.
    param_decim: int
        Factor by which to subsample the data. Default is 1.
    param_reject_tmin: scalar or None
        Start of the time window used to reject epochs (with the default None, the window will start with tmin).
    param_reject_tmax: scalar or None
        End of the time window used to reject epochs (with the default None, the window will end with tmax).  
    param_detrend: int or None
        If 0 or 1, the data channels (MEG and EEG) will be detrended when loaded. 0 is a constant (DC) detrend, 1 
        is a linear detrend. None (default) is no detrending.
    param_on_missing: str
        What to do if one or several event ids are not found in the recording. Valid keys are ‘raise’, ‘warn’, or
        ‘ignore’. Default is ‘raise’.
    param_reject_by_annotation: bool
        Whether to reject based on annotations. If True (default), epochs overlapping with segments whose description 
        begins with 'bad' are rejected. 
    param_metadata: instance of pandas.DataFrame or None
        A pandas.DataFrame specifying metadata about each epoch. Default is None.
    param_event_repeated: str
        How to handle duplicates in events[:, 0]. Can be 'error' (default), to raise an error, ‘drop’ to only retain 
        the row occurring first in the events, or 'merge' to combine the coinciding events (=duplicates) into a new event.

    Returns
    -------
    epoched_data: instance of mne.Epochs
        The epoched data.
    """

    # Raise error if both param picks are not None
    if param_picks_by_channel_types_or_names is not None and param_picks_by_channel_indices is not None:
        value_error_message = f"You can't provide values for both " \
                              f"param_picks_by_channel_types_or_names and " \
                              f"param_picks_by_channel_indices. One of them must be " \
                              f"set to None."
        raise ValueError(value_error_message)
    # Define param_picks
    elif param_picks_by_channel_types_or_names is None and param_picks_by_channel_indices is not None:
        param_picks = param_picks_by_channel_indices
    elif param_picks_by_channel_types_or_names is not None and param_picks_by_channel_indices is None:
        param_picks = param_picks_by_channel_types_or_names
    else:
        param_picks = None  
    
    # Convert tsv file into a numpy array of integers
    array_events = np.loadtxt(fname=events_file, delimiter="\t")
    events = array_events.astype(int)

    # Create epochs from events
    epoched_data = mne.Epochs(raw, events, event_id=param_event_id, tmin=param_tmin, tmax=param_tmax, baseline=param_baseline,
                              picks=param_picks, preload=param_preload, reject=param_reject, flat=param_flat, proj=param_proj, 
                              decim=param_decim, reject_tmin=param_reject_tmin, reject_tmax=param_reject_tmax, detrend=param_detrend, 
                              on_missing=param_on_missing, reject_by_annotation=param_reject_by_annotation,
                              metadata=param_metadata, event_repeated=param_event_repeated)

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
        value_error_message = f'You need to provide events.tsv to make epochs. ' \
                              f'Please use the app-get-events to create such file.'
        # Raise exception
        raise ValueError(value_error_message)
    else:
    	shutil.copy2(events_file, 'out_dir_make_epochs/events.tsv')  # required to run a pipeline on BL

    # Read the crosstalk file
    cross_talk_file = config.pop('crosstalk')
    if os.path.exists(cross_talk_file) is True:
        shutil.copy2(cross_talk_file, 'out_dir_make_epochs/crosstalk_meg.fif')  # required to run a pipeline on BL

    # Read the calibration file
    calibration_file = config.pop('calibration')
    if os.path.exists(calibration_file) is True:
        shutil.copy2(calibration_file, 'out_dir_make_epochs/calibration_meg.dat')  # required to run a pipeline on BL

    # Read destination file 
    destination_file = config.pop('destination')
    if os.path.exists(destination_file) is True:
        shutil.copy2(destination_file, 'out_dir_make_epochs/destination.fif')  # required to run a pipeline on BL

    # Read head pos file
    head_pos = config.pop('headshape')
    if os.path.exists(head_pos) is True:
        shutil.copy2(head_pos, 'out_dir_make_epochs/headshape.pos')  # required to run a pipeline on BL

    # Convert all "" into None when the App runs on BL
    tmp = dict((k, None) for k, v in config.items() if v == "")
    config.update(tmp)

    # # event id
    # if config['param_event_id'] == "":
    #     config['param_event_id'] = None  # when App is run on Bl, no value for this parameter corresponds to ''

    # # Baseline
    # if config['param_baseline'] == "":
    #     config['param_baseline'] = None  # when App is run on Bl, no value for this parameter corresponds to ''

    # # picks
    # if config['param_picks'] == "":
    #     config['param_picks'] = None  # when App is run on Bl, no value for this parameter corresponds to ''    

    # # reject
    # if config['param_reject'] == "":
    #     config['param_reject'] = None  # when App is run on Bl, no value for this parameter corresponds to '' 

    # # flat
    # if config['param_flat'] == "":
    #     config['param_flat'] = None  # when App is run on Bl, no value for this parameter corresponds to '' 

    # # reject tmin
    # if config['param_reject_tmin'] == "":
    #     config['param_reject_tmin'] = None  # when App is run on Bl, no value for this parameter corresponds to '' 

    # # reject tmax
    # if config['param_reject_tmax'] == "":
    #     config['param_reject_tmax'] = None  # when App is run on Bl, no value for this parameter corresponds to ''

    # # reject detrend
    # if config['param_detrend'] == "":
    #     config['param_param_detrend'] = None  # when App is run on Bl, no value for this parameter corresponds to ''

    # # reject metadata
    # if config['param_metadata'] == "":
    #     config['param_metadata'] = None  # when App is run on Bl, no value for this parameter corresponds to ''

    ## Convert parameters ## 

    # Deal with param baseline #
    # Convert baseline parameter into tuple when the App is run locally
    if config['param_baseline'] is not None:
       config['param_baseline'] = tuple(config['param_baseline'])

    # Deal with param_baseline parameter

    # Convert baseline parameter into tuple when the app runs locally
    if isinstance(config['param_baseline'], list):
       config['param_baseline'] = tuple(config['param_baseline'])

    # Convert baseline parameter into tuple when the App runs on BL
    if isinstance(config['param_baseline'], str):
        param_baseline = list(map(str, config['param_baseline'].split(', ')))
        param_baseline = [None if i=='None' else i for i in param_baseline]
        param_baseline = [float(i) if isinstance(i, str) else i for i in param_baseline]
        print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
        config['param_baseline'] = tuple(param_baseline)

    # Deal with param_proj parameter when app runs on BL
    # if config['param_proj'] == "True":
    #     config['param_proj'] = True
    # elif config['param_proj'] == "False":
    #     config['param_proj'] = False

    # Deal with param_picks_by_channel_indices parameter #
    # Convert it into a slice When the App is run locally and on BL
    picks = config['param_picks_by_channel_indices']
    if isinstance(picks, str) and picks.find(",") != -1 and picks.find("[") == -1 and picks is not None:
        picks = list(map(int, picks.split(', ')))
        if len(picks) == 2:
            config['param_picks_by_channel_indices'] = slice(picks[0], picks[1])
        elif len(picks) == 3:
            config['param_picks_by_channel_indices'] = slice(picks[0], picks[1], picks[2])
        else:
            value_error_message = f"If you want to select channels using a slice, you must give two or three elements."
            raise ValueError(value_error_message)

    # Convert it into a list of integers when the App is run on BL
    if isinstance(picks, str) and picks.find(",") != -1 and picks.find("[") != -1 and picks is not None:
        picks = picks.replace('[', '')
        picks = picks.replace(']', '')
        config['param_picks_by_channel_indices'] = list(map(int, picks.split(', ')))

    # Deal with param_picks_by_channel_types_or_name parameter #
    # Convert it into a list of str when the App is run on BL
    picks = config['param_picks_by_channel_types_or_names']
    if isinstance(picks, str) and picks.find("[") != -1 and picks is not None:
        picks = picks.replace('[', '')
        picks = picks.replace(']', '')
        config['param_picks_by_channel_types_or_names'] = list(map(str, picks.split(', ')))

    # Deal with event id #    
    # Convert it into a list of int or an int When it is run on BL
    if config['param_event_id'] is not None:
        if config['param_event_id'].find("[") != -1: 
            config['param_event_id'] = config['param_event_id'].replace('[', '')
            config['param_event_id'] = config['param_event_id'].replace(']', '')
            config['param_event_id'] = list(map(int, config['param_event_id'].split(', ')))  
        else:
            config['param_event_id'] = int(config['param_event_id']) 

    # Deal with param proj
    

    ## Define kwargs ##

    # Delete keys values in config.json when this app is executed on Brainlife
    if '_app' and '_tid' and '_inputs' and '_outputs' in config.keys():
        del config['_app'], config['_tid'], config['_inputs'], config['_outputs'] 
    kwargs = config  

    # Epoch data
    epoched_data = make_epochs(raw, events_file, **kwargs)

    # Success message in product.json    
    dict_json_product['brainlife'].append({'type': 'success', 'msg': 'Data was successfully epoched.'})

    # Save the dict_json_product in a json file
    with open('product.json', 'w') as outfile:
        json.dump(dict_json_product, outfile)


if __name__ == '__main__':
    main()