"""
##################################################
*          Dragon board readout software         *
* calculate offset constants from pedestal files *
##################################################

annotations:

- inputdirectory is the path to the directory of your pedestal files
- outputpath is the file path where the calibration constants are written to


Usage:
  offset_calculation.py <inputdirectory> [options]
  offset_calculation.py (-h | --help)
  offset_calculation.py --version

Options:
  -h --help       Show this screen.
  --version       Show version.
  -o --output P   output path. [default: calibration_constants.pickle]
  -m --multi N    use multiprocessing [default: False]

"""

import numpy as np
import matplotlib.pyplot as plt
from dragonboard import EventGenerator
from dragonboard.runningstats import RunningStats, combine
import dragonboard
from tqdm import tqdm
import glob
import os
from docopt import docopt
import sys
import pickle
from multiprocessing import Pool

disable_tqdm = False

def offsets(path):
    calibration_constants = {}
    for pixel in range(dragonboard.io.num_channels):
        for gain in dragonboard.io.gaintypes:
            calibration_constants[(pixel, gain)] = RunningStats(shape=dragonboard.io.max_roi)

    for event in tqdm(
            iterable=EventGenerator(
                open(path, "rb"),
                max_events=None,
                buffer_size=1000),
            desc=os.path.basename(path),
            leave=True,
            unit="events",
            disable=disable_tqdm):

        for (pixel, gain), stats in calibration_constants.items():
            stop_cell = event.header.stop_cells[gain][pixel]
            data = event.data[gain][pixel]
            stats.addfoo(data, stop_cell)

    return calibration_constants

def new_combine(file_offsets):
    stuff = {}
    for calibration_constants in file_offsets:
        for key in calibration_constants:
            if not key in stuff:
                stuff[key] = []
            stuff[key].append(calibration_constants[key])

    for key in stuff:
        stuff[key] = combine(stuff[key])

    return stuff


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Dragon Board Offset Calculation v.1.1')
    print(arguments)

    glob_expression = os.path.join(arguments["<inputdirectory>"], '*.dat')
    if not glob.glob(glob_expression):
        sys.exit("Error: no files found to perform offset calculation")


    try:
        arguments["--multi"] = int(arguments["--multi"])
    except ValueError:
        arguments["--multi"] = False

    if arguments["--multi"]:
        #disable_tqdm = True
        with Pool(arguments["--multi"]) as p:
            file_offsets = p.map(offsets, sorted(glob.glob(glob_expression)))
    else:
        file_offsets = list(map(offsets, sorted(glob.glob(glob_expression))))
    
    calibration_constants = new_combine(file_offsets)
    pickle.dump(calibration_constants, open(arguments["--output"], 'wb'))