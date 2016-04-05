'''
Usage:
    fit_delta_t.py <inputfile> <pixel> <gain> [options]

Options:
    -p, --plot              Show plots while fitting
    -n <n>, --n-jobs=<n>    How many threads to use [default: 1]
'''
import pandas as pd
from scipy.optimize import curve_fit
from joblib import Parallel, delayed
import numpy as np
import matplotlib.pyplot as plt
import logging
from docopt import docopt


def f(x, a, b, c):
    return a * x ** b + c


def fit(df, cell, plot=False):
    df = df[(5 <= df['sample']) & (df['sample'] < 35)]

    try:
        (a, b, c), cov = curve_fit(
            f,
            df['delta_t'],
            df['adc_counts'],
            p0=[2,  -0.3, 230],
        )
    except RuntimeError:
        logging.error('Could not fit cell {}'.format(cell))
        return np.full(4, np.nan)

    if plot:

        x = np.logspace(-4, 0, 250)

        fig = plt.gcf()
        ax = plt.gca()
        ax.cla()
        ax.set_xscale('log')
        ax.set_xlim(1e-4, 1)
        ax.scatter(
            x='delta_t', y='adc_counts', c='sample',
            cmap='rainbow', linewidth=0, s=4,
            data=df,
        )
        ax.plot(x, f(x, a, b, c))

        fig.tight_layout()
        fig.canvas.draw()

    ndf = len(df.index) - 3
    residuals = df['adc_counts'] - f(df['delta_t'], a, b, c)
    chisquare = np.sum(residuals**2) / ndf

    return a, b, c, chisquare


if __name__ == '__main__':
    args = docopt(__doc__)

    plt.rcParams['figure.figsize'] = (4, 3)
    plt.ion()

    pixel = args['<pixel>']
    gain = args['<gain>']

    data = pd.read_hdf(args['<inputfile>'], 'pixel_{}_{}'.format(pixel, gain))
    by_cell = data.groupby('cell')

    with Parallel(int(args['--n-jobs']), verbose=5) as pool:
        result = pd.DataFrame(
            pool(delayed(fit)(df, name, plot=args['--plot']) for name, df in by_cell),
            columns=['a', 'b', 'c', 'chisq_ndf']
        )

    result.to_hdf('fit_results_{}_{}.hdf5'.format(pixel, gain), 'fit_result')