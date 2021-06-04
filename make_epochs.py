#!/usr/local/bin/python3

import json
import mne
import numpy as np
import warnings
import shutil
import os 
import pandas as pd
import helper


def make_epochs(raw, events_matrix, param_event_id, param_tmin, param_tmax, param_baseline,
                param_picks_by_channel_types_or_names, param_picks_by_channel_indices, 
                param_preload, param_reject, param_flat, param_proj, param_decim,
                param_reject_tmin, param_reject_tmax, param_detrend, param_on_missing, 
                param_reject_by_annotation, param_metadata, param_event_repeated):
    """Create epochs from matrix events contained in a .tsv file.

    Parameters
    ----------
    raw: instance of mne.io.Raw
        Data from which the events will be extracted or created.
    events_matrix: np.array
        Matrix of events (2D array, shape (n_events, 3)).
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

    # Create epochs from events
    epoched_data = mne.Epochs(raw, events_matrix, event_id=param_event_id, tmin=param_tmin, tmax=param_tmax, baseline=param_baseline,
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

    # Read and save optional files
    config, cross_talk_file, calibration_file, events_file, head_pos_file, channels_file, destination = helper.read_optional_files(config, 'out_dir_make_epochs')
    
    # Convert empty strings values to None
    config = helper.convert_parameters_to_None(config)

    # Channels.tsv must be BIDS compliant
    if channels_file is not None:
        user_warning_message_channels = f'The channels file provided must be ' \
                                        f'BIDS compliant and the column "status" must be present. ' 
        warnings.warn(user_warning_message_channels)
        dict_json_product['brainlife'].append({'type': 'warning', 'msg': user_warning_message_channels})

        raw, user_warning_message_channels = helper.update_data_info_bads(raw, channels_file)
        if user_warning_message_channels is not None: 
            warnings.warn(user_warning_message_channels)
            dict_json_product['brainlife'].append({'type': 'warning', 'msg': user_warning_message_channels})


    ## Extract the matrix of events ##

    # Test if an events file is given 
    if events_file is None:
        value_error_message = f'You need to provide events.tsv to make epochs. ' \
                              f'Please use the app-get-events to create such file.'  
        # Raise exception
        raise ValueError(value_error_message) 
    # Get the matrix of events    
    elif events_file is not None:
            # Warning: events file must be BIDS compliant  
            user_warning_message_events = f'The events file provided must be ' \
                                          f'BIDS compliant.'        
            warnings.warn(user_warning_message_events)
            dict_json_product['brainlife'].append({'type': 'warning', 'msg': user_warning_message_events})
            ############### TO BE TESTED ON NO RESTING STATE DATA
            # Compute the events matrix #
            df_events = pd.read_csv(events_file, sep='\t')
            
            # Extract relevant info from df_events
            samples = df_events['sample'].values
            event_id = df_events['value'].values

            # Compute the values for events matrix 
            events_time_in_sample = [raw.first_samp + sample for sample in samples]
            values_of_trigger_channels = [0]*len(events_time_in_sample)

            # Create a dataframe
            df_events_matrix = pd.DataFrame([events_time_in_sample, values_of_trigger_channels, event_id])
            df_events_matrix = df_events_matrix.transpose()

            # Convert dataframe to numpy array
            events_matrix = df_events_matrix.to_numpy()


    ## Convert parameters ## 

    # Deal with param_baseline parameter # 
    # Convert baseline parameter into tuple when the app runs locally
    if isinstance(config['param_baseline'], list):
       config['param_baseline'] = tuple(config['param_baseline'])

    # Convert baseline parameter into tuple when the App runs on BL
    if isinstance(config['param_baseline'], str):
        param_baseline = list(map(str, config['param_baseline'].split(', ')))
        param_baseline = [None if i=='None' else i for i in param_baseline]
        param_baseline = [float(i) if isinstance(i, str) else i for i in param_baseline]
        config['param_baseline'] = tuple(param_baseline)

    # Deal with param_proj parameter #
    # Convert string into boolean when app runs on BL
    if config['param_proj'] == "True":
        config['param_proj'] = True
    elif config['param_proj'] == "False":
        config['param_proj'] = False

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

    # Deal with param metadata #
    # Convert it into a pd.Dataframe when the App runs locally
    if isinstance(config['param_metadata'], str):
        config['param_metadata'] = pd.read_csv(config['param_metadata'])
    elif isinstance(config['param_metadata'], dict):
        config['param_metadata'] = pd.DataFrame(list(config['param_metadata'].items())) 

    # Deal with param detrend #
    # Convert it into an int if not None
    if isinstance(config['param_detrend'], str):
        config['param_detrend'] = int(config['param_detrend'])

    # Delete keys values in config.json when this app is executed on Brainlife
    kwargs = helper.define_kwargs(config)

    # Epoch data
    epoched_data = make_epochs(raw, events_matrix, **kwargs)

    # Success message in product.json    
    dict_json_product['brainlife'].append({'type': 'success', 'msg': 'Data was successfully epoched.'})

    # Save the dict_json_product in a json file
    with open('product.json', 'w') as outfile:
        json.dump(dict_json_product, outfile)


if __name__ == '__main__':
    main()