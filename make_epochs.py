#!/usr/local/bin/python3

import json
import mne
import numpy as np
import warnings
import shutil
import os 

def make_epochs(raw, events_file, param_event_id, param_tmin, param_tmax, param_baseline,
                param_picks, param_preload, param_reject, param_flat, param_proj, param_decim,
                param_reject_tmin, param_reject_tmax, param_detrend, param_on_missing, param_reject_by_annotation,
                param_metadata, param_event_repeated):
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
    param_picks: str, list, slice, or None
        Channels to include. Default is None.
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

    # Check for None parameters

    # event id
    if config['param_event_id'] == "":
        config['param_event_id'] = None  # when App is run on Bl, no value for this parameter corresponds to ''

    # Baseline
    if config['param_baseline'] == "":
        config['param_baseline'] = None  # when App is run on Bl, no value for this parameter corresponds to ''

    # picks
    if config['param_picks'] == "":
        config['param_picks'] = None  # when App is run on Bl, no value for this parameter corresponds to ''    

    # reject
    if config['param_reject'] == "":
        config['param_reject'] = None  # when App is run on Bl, no value for this parameter corresponds to '' 

    # flat
    if config['param_flat'] == "":
        config['param_flat'] = None  # when App is run on Bl, no value for this parameter corresponds to '' 

    # reject tmin
    if config['param_reject_tmin'] == "":
        config['param_reject_tmin'] = None  # when App is run on Bl, no value for this parameter corresponds to '' 

    # reject tmax
    if config['param_reject_tmax'] == "":
        config['param_reject_tmax'] = None  # when App is run on Bl, no value for this parameter corresponds to ''

    # reject detrend
    if config['param_detrend'] == "":
        config['param_param_detrend'] = None  # when App is run on Bl, no value for this parameter corresponds to ''

    # reject metadata
    if config['param_metadata'] == "":
        config['param_metadata'] = None  # when App is run on Bl, no value for this parameter corresponds to ''

    # Convert list parameter into tuple
    if isinstance(config['param_baseline'], list):
       config['param_baseline'] = tuple(config['param_baseline'])
       print('aaa')

    # Define kwargs

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