import numpy as np


class DataNormalizer(object):

    def __init__(self, num_samples=200):
        self.num_samples = num_samples
        self._array = np.zeros(self.num_samples, dtype='f')
        self._idx = 0

    def __call__(self, data, min_norm=0.0):
        new_idx = (self._idx + 1) % self.num_samples
        self._array[self._idx] = data

        self._idx = new_idx

        norm = max(np.amax(self._array), min_norm) 

        if norm != 0.0:
            return data / norm
        return data



def ArrayNormalizer(data):
    norm = np.amax(np.absolute(data))
    print norm
    if norm != 0:
        return data/norm
    return data
