'''
Usage:
    time_vs_value.py <inputfile>
'''
from dragonboard import EventGenerator
from tqdm import tqdm
from docopt import docopt
import numpy as np
import matplotlib.pyplot as plt


def relative2physical(cap_id, stop_cell, num_caps=4096):
    return (cap_id + stop_cell) % num_caps


def physical2relative(cap_id, stop_cell, roi, num_caps=4096):
    assert cap_id < num_caps

    if stop_cell <= cap_id < stop_cell + roi:
        return cap_id - stop_cell

    if cap_id < (stop_cell + roi) % num_caps:
        return num_caps - stop_cell + cap_id

    raise ValueError('Physical capacitor not in data')


def capicator_in_data(cap_id, stop_cell, roi, num_caps=4096):

    assert cap_id < num_caps

    # cap directly in roi
    if stop_cell <= cap_id < stop_cell + roi:
        return True

    # overlapping readout region
    if cap_id < stop_cell + roi - num_caps:
        return True

    return False


def main():

    args = docopt(__doc__)

    inputfile = args['<inputfile>']

    pixel = 0
    channel = 'high'
    cap_id = 0

    delta_ts = []
    charges = []

    eg = EventGenerator(inputfile)

    for event in eg:
        last_event = event
        last_stop_cell = event.header.stop_cells[pixel][channel]
        if capicator_in_data(cap_id, last_stop_cell, last_event.roi, 4096):
            break

    for event in tqdm(eg):
        stop_cell = event.header.stop_cells[pixel][channel]
        last_stop_cell = last_event.header.stop_cells[pixel][channel]

        if capicator_in_data(cap_id, stop_cell, event.roi):
            rel_id = physical2relative(cap_id, stop_cell, event.roi)

            delta_ts.append(
                event.header.counter_133MHz - last_event.header.counter_133MHz
            )
            charges.append(event.data[pixel][channel][rel_id])

            last_event = event
            last_stop_cell = stop_cell

    plt.plot(np.array(delta_ts) / 133e3, charges, 'k.')
    plt.xlabel('$\delta t$ / ms')
    plt.show()

if __name__ == '__main__':
    main()
