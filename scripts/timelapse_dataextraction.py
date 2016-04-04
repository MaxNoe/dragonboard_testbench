'''
#######################################################
*          Dragon board readout software              *
* calculate time-lapse dependence from pedestal files *
#######################################################

annotations:

- inputdirectory is the path to the directory of your pedestal files


Usage:
  offset_calculation.py <inputfiles> ... [options]
  offset_calculation.py (-h | --help)
  offset_calculation.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --outpath N   Outputfile path [default: calibration_constants.pickle]

'''

import dragonboard
from tqdm import tqdm
import os
from docopt import docopt
import pandas as pd
from collections import defaultdict


def f(x, a, m, b):
    return a * x**m + b


def extract_data(inputfiles):
    ''' calculate time lapse dependence for a given capacitor '''

    with pd.HDFStore('data.hdf5', mode='a') as store:
        for filename in sorted(inputfiles):
            try:
                cell_id = 2424
                gaintype = 'low'
                pixelindex = 0

                data = defaultdict(list)

                for event in tqdm(
                        iterable=dragonboard.EventGenerator(filename),
                        desc=os.path.basename(filename),
                        leave=True,
                        unit=' events',
                        ):

                    stop_cell = event.header.stop_cells[gaintype][pixelindex]
                    if stop_cell <= cell_id < (stop_cell + event.roi):
                        data['time'].append(event.header.counter_133MHz / 133e6)
                        data['adc_counts'].append(
                            event[2][pixelindex][gaintype][cell_id - stop_cell]
                        )
                        data['sample_id'].append(cell_id - stop_cell)

                df = pd.DataFrame(data)
                df['delta_t'] = df.time.diff()
                store.append('cell{}/gain{}'.format(cell_id, gaintype), df)

            except Exception as e:
                print(e)


if __name__ == '__main__':
    arguments = docopt(
        __doc__, version='Dragon Board Time-Dependent Offset Calculation v.1.0'
    )
    extract_data(arguments['<inputfiles>'])
