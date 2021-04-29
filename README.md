# app-make-epochs

This is a draft of a future Brainlife App using MNE Python to epoch the data ([`mne.Epochs`](hhttps://mne.tools/stable/generated/mne.Epochs.html).

# app-make-epochs documentation

1) Epoch the data. 
2) Input files are:
    * a MEG file in `.fif` format,
    * an events file in `.tsv` format,
    * an optional fine calibration file in `.dat`,
    * an optional crosstalk compensation file in `.fif`,
    * an optional head position file in `.pos`,
    * an optional destination file in `.fif`,
3) Input parameters are:
    * `param_event_id`: `int`, `list of int`, optional, the id of the event to consider. Default is None.
    * `param_tmin`: `float`, start time before event. Default is -0.2.
    * `param_tmax`: `float`, end time after event. Default is 0.5.
    * `param_baseline`: `tuple` of length 2, optional, the time interval to consider as “baseline” when applying baseline correction. Default is (None, 0).
    * `param_picks`: `str`, `list`, `slice`, optional, channels to include. Default is None.
    * `param_preload`: `bool`, load all epochs from disk when creating the object or wait before accessing each epoch. Default is False.
    * `param_reject`: `dict`, optional, reject epochs based on peak-to-peak signal amplitude, i.e. the absolute difference between the lowest and the highest signal value. 
       Default is None.
    * `param_flat`: `dict`, optional, rejection parameters based on flatness of signal. Valid keys are 'grad', 'mag', 'eeg', 'eog', 'ecg'. 
The values are floats that set the minimum acceptable peak-to-peak amplitude. Default is None.
    * `param_proj`: `bool` or `str`, apply SSP projection vectors. If proj is "delayed" and reject is not None the single epochs will be 
projected before the rejection decision, but used in unprojected state if they are kept. Default is True.
    * `param_decim`: `int`, factor by which to subsample the data. Default is 1.
    * `param_reject_tmin`: `scalar`, optional, start of the time window used to reject epochs (with the default None, the window will start with tmin).
    * `param_reject_tmax`: `scalar` or None, end of the time window used to reject epochs (with the default None, the window will end with tmax). 
    * `param_detrend`: `int`, optional, if 0 or 1, the data channels (MEG and EEG) will be detrended when loaded. 0 is a constant (DC) detrend, 1 
        is a linear detrend. Default is None (no detrending).
    * `param_on_missing`: `str`, what to do if one or several event ids are not found in the recording. Valid keys are 'raise', 'warn', or
'ignore'. Default is 'raise'.
    * `param_reject_by_annotation`: `bool`, whether to reject based on annotations. If True, epochs overlapping with segments whose description begins with 'bad' are rejected. Default is True.
    * `param_metadata`: `str`, `dict` or None, path to a csv file specifying metadata about each epoch. Default is None.
    * `param_event_repeated`: `str`, how to handle duplicates in events[:, 0]. Can be 'error', to raise an error, ‘drop’ to only retain 
the row occurring first in the events, or 'merge' to combine the coinciding events (=duplicates) into a new event. Default is 'error'.
      
This list along with the default values correspond to the parameters of MNE Python version 0.22.0.

4) Ouput file is an epoched MEG data in a .fif file

### Authors
- [Aurore Bussalb](aurore.bussalb@icm-institute.org)

### Contributors
- [Aurore Bussalb](aurore.bussalb@icm-institute.org)
- [Maximilien Chaumon](maximilien.chaumon@icm-institute.org)

### Funding Acknowledgement
brainlife.io is publicly funded and for the sustainability of the project it is helpful to Acknowledge the use of the platform. We kindly ask that you acknowledge the funding below in your code and publications. Copy and past the following lines into your repository when using this code.

[![NSF-BCS-1734853](https://img.shields.io/badge/NSF_BCS-1734853-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=1734853)
[![NSF-BCS-1636893](https://img.shields.io/badge/NSF_BCS-1636893-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=1636893)
[![NSF-ACI-1916518](https://img.shields.io/badge/NSF_ACI-1916518-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=1916518)
[![NSF-IIS-1912270](https://img.shields.io/badge/NSF_IIS-1912270-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=1912270)
[![NIH-NIBIB-R01EB029272](https://img.shields.io/badge/NIH_NIBIB-R01EB029272-green.svg)](https://grantome.com/grant/NIH/R01-EB029272-01)

### Citations
1. Avesani, P., McPherson, B., Hayashi, S. et al. The open diffusion data derivatives, brain data upcycling via integrated publishing of derivatives and reproducible open cloud services. Sci Data 6, 69 (2019). [https://doi.org/10.1038/s41597-019-0073-y](https://doi.org/10.1038/s41597-019-0073-y)
2. Taulu S. and Kajola M. Presentation of electromagnetic multichannel data: The signal space separation method. Journal of Applied Physics, 97 (2005). [https://doi.org/10.1063/1.1935742](https://doi.org/10.1063/1.1935742)
3. Taulu S. and Simola J. Spatiotemporal signal space separation method for rejecting nearby interference in MEG measurements. Physics in Medicine and Biology, 51 (2006). [https://doi.org/10.1088/0031-9155/51/7/008](https://doi.org/10.1088/0031-9155/51/7/008)


## Running the App 

### On Brainlife.io

This App is still private.

### Running Locally (on your machine)

1. git clone this repo
2. Inside the cloned directory, create `config.json` with the same keys as in `config.json.example` but with paths to your input 
   files and values of the input parameters. For instance:

```json
{
  "fif": "rest1-raw.fif"
}
```

3. Launch the App by executing `main`

```bash
./main
```

## Output

The output file is .fif file.
