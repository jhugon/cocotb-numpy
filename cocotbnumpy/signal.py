import numpy as np


class NumpySignal:
    def __init__(self, waveform, dontcaremask=None):
        """
        waveform is a numpy array of signal values at each successive clock.

        npsig = NumpySignal([0,1,0,0,1,1,0,0,1])

        if there are some clocks where you don't care what the value is, you
        can put 1's in those positions in the array given to dontcaremask. The
        array will be extended with zeros to the size of waveform. ex:

        npsigdc = NumpySignal([0,0,1,1,1],dontcaremask=[1,1])

        """
        waveform = np.array(waveform)
        try:
            dontcaremask = np.array(dontcaremask)
        except ValueError:
            dontcaremask = np.zeros(waveform.size)

        if len(waveform) > len(dontcaremask):
            tmp = np.zeros(waveform.size)
            tmp[: len(dontcaremask)] = dontcaremask
            dontcaremask = tmp

        self.waveform = waveform
        self.dontcaremask = dontcaremask

    def __str__(self):
        l = list(self.waveform)
        l = ["{}".format(x) for x in l]
        width = max([len(x) for x in l])
        result = ""
        for x, m in zip(self.waveform, self.dontcaremask):
            if m:
                result += "{:" + str(width) + "}".format("-")
            else:
                result += "{:" + str(width) + "}".format(x)
        return result

    def get_max_str_width(self):
        l = list(self.waveform)
        l = ["{}".format(x) for x in l]
        width = max([len(x) for x in l])
        return width

    def __len__(self):
        return len(self.waveform)

    def __eq__(self, other):
        try:
            return self.waveform == other.waveform
        except AttributeError:
            return False
