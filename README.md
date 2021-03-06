# dragonboard_testbench
[![Build Status](https://travis-ci.org/cta-observatory/dragonboard_testbench.svg?branch=master)](https://travis-ci.org/cta-observatory/dragonboard_testbench)

A collection of programs to help with drs calibration of the LST test data of the dragon_cam.


## Installation

`pip install git+https://github.com/cta-observatory/dragonboard_testbench`

or, if you are developing

```
git clone http://github.com/cta-observatory/dragonboard_testbench
pip install -e dragonboard_testbench
```

## Usage


### DragonViewer

Use the `dragonviewer` executable to view some data, it is in your `$PATH` after
you installed this module.

`dragoviewer [<inputfile>]`

If you do not provide `<inputfile>`, a file dialog will open

![Alt text](/dragonviewer.png?raw=true "Optional Title")

### Calculate Calibration Constants

Use `python offset_calculation.py <inputdirectory> <outputdirectory>` to calculate offsets.

`<inoutdirectory>` is the /path/to/pedestal_files.py

`<outputdirectory>` is the directory to which a generated `offsets.csv` will be written

### Apply Calibration Constants

Use `offset_calibration.py <raw_datafile_directory> <calibration_constants_directory> <output_directory>`

`<raw_datafile_directory>` can be any type of readable raw_file.dat 

`<calibration_constants_directory>` is the /path/to/offsets.csv generated by `offset_calculation.py`

`<output_directory>` is the path where the raw_files.dat will be written to `raw_files_calibrated.dat`


## Running the tests

We are using `pytest`, install with

```
$ conda install pytest
```
or, if you are not using anaconda,
```
pip install pytest
```

You can then run the tests using:

```
py.test
```

in the base directory, the output could look like this if everything goes well:

```
$ py.test
===================== test session starts ============================
platform linux -- Python 3.5.1, pytest-2.8.5, py-1.4.31, pluggy-0.3.1
rootdir: /home/maxnoe/Uni/CTA/dragonboard_testbench, inifile: 
collected 2 items 

dragonboard/tests/test_runningstats.py ..

================== 2 passed in 0.28 seconds ==========================
```



