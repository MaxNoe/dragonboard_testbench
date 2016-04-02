"""
#######################################################
*          Dragon board readout software              *
* calculate time-lapse dependence from pedestal files *
#######################################################

annotations:

- inputdirectory is the path to the directory of your pedestal files


Usage:
  offset_calculation.py <inputdirectory> [options]
  offset_calculation.py (-h | --help)
  offset_calculation.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --outpath N   Outputfile path [default: calibration_constants.pickle]

"""

import numpy as np
import matplotlib.pyplot as plt
from dragonboard import EventGenerator
from dragonboard.runningstats import RunningStats
import dragonboard
from tqdm import tqdm
import glob
import os
from docopt import docopt
import sys
import pickle

def timelapse_calc(inputdirectory):
    """ calculate time lapse dependence for a given capacitor """

    glob_expression = os.path.join(inputdirectory, '*.dat')
    for filename in sorted(glob.glob(glob_expression)):
        try:
            capno = 2424
            gaintype = "low"
            pixelindex = 0

            time = []
            adc_counts = []

            for event in tqdm(
                    iterable=dragonboard.EventGenerator(filename),
                    desc=os.path.basename(filename),
                    leave=True,
                    unit=" events"):
                stop_cell = event.header.stop_cells[gaintype][pixelindex]
                if stop_cell <= capno < (stop_cell + event.roi):
                    time.append(event.header.counter_133MHz / 133e6)
                    adc_counts.append(int(event[2][pixelindex][gaintype][capno - stop_cell]))
        except Exception as e:
            print(e)

    delta_t_in_ms = np.diff(time)*1e3

    plt.scatter(delta_t_in_ms, adc_counts[1:])
    plt.xlabel("time between consecutive events / ms")
    plt.ylabel("ADC counts")
    plt.xscale("log")
    plt.title("Time dependence: cap {} @ {} {} ({})".format(capno, pixelindex, gaintype, os.path.basename(filename)))

if __name__ == '__main__':
    arguments = docopt(__doc__, version='Dragon Board Time-Dependent Offset Calculation v.1.0')

    if not glob.glob(os.path.join(arguments["<inputdirectory>"], '*.dat')):
        sys.exit("Error: no files found to perform time-lapse calculation")

    timelapse_calc(arguments["<inputdirectory>"])
    plt.show()