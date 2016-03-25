from __future__ import division, print_function, absolute_import
import numpy as np


class RunningStats():

    def __init__(self, shape=1):
        self.shape = shape
        self.n = np.zeros(shape)
        self._mean = np.zeros(shape)
        self._M2 = np.zeros(shape)

    def add(self, data):
        idx = ~np.isnan(data)
        self._mean[self.n == 0] = 0
        self._delta[idx] = data[idx] - self._mean[idx]

        self.n[idx] += 1
        self._mean[idx] += self._delta[idx] / self.n[idx]
        self._M2[idx] += self._delta[idx] * (data[idx] - self._mean[idx])

    def add_slice(self, data, sl):
        #idx = ~np.isnan(data)
        #self._mean[self.n == 0] = 0
        delta = data - self._mean[sl]

        self.n[sl] += 1
        self._mean[sl] += delta / self.n[sl]
        self._M2[sl] += delta * (data - self._mean[sl])

    def addfoo(self, data, stop_cell):
        S = self.shape
        L = len(data)

        X = S - (stop_cell + L)
        if X >= 0:
            self.add_slice(
                data,
                slice(stop_cell, stop_cell + L)
            )
        else:
            self.add_slice(
                data[:X],
                slice(stop_cell, None)
            )
            self.add_slice(
                data[X:],
                slice(None, -X)
            )

    @property
    def mean(self):
        return self._mean

    @property
    def var(self):
        var = self._M2 / (self.n - 1)
        var[self.n <= 2] = np.nan
        return var

    @property
    def std(self):
        return np.sqrt(self.var)

    @property
    def sem(self):
        return 1 / np.sqrt(self.n) * self.std


def combine(many_running_stats):

    shapes = list(map(lambda stat: stat.shape, many_running_stats))
    the_shape = shapes[0]
    assert (x == the_shape for x in shapes)

    new_stat = RunningStats(shape=the_shape)

    new_stat._mean = None
    new_stat._delta = None
    new_stat._M2 = None

    N = None
    for s in many_running_stats:
        if new_stat._mean is None:
            new_stat._mean = s.mean * s.n
            N = s.n
        else:
            new_stat._mean += s.mean * s.n
            N += s.n
    new_stat._mean /= N

    return new_stat
