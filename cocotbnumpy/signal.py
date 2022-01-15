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

        The mask is only taken into account on the first member of an equality
        check, that is:

        in1 = [0,1,0,1,0,1]
        in2 = [1,0,0,1,0,1]
        s1 = NumpySignal(in1,[1,1])
        s2 = NumpySignal(in2)
        assert s1 == s2
        assert s2 != s1

        """
        waveform = np.array(waveform)
        if dontcaremask is None:
            dontcaremask = np.zeros(waveform.size, dtype=np.uint8)
        dontcaremask = np.array(dontcaremask)

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
                result += ("{:" + str(width) + "} ").format("-")
            else:
                result += ("{:" + str(width) + "} ").format(x)
        if len(result) > 0:
            result = result[:-1]
        return result

    def __repr__(self):
        return (
            f"NumpySignal({list(self.waveform)},dontcaremask={list(self.dontcaremask)})"
        )

    def get_max_str_width(self):
        l = list(self.waveform)
        l = ["{}".format(x) for x in l]
        width = max([len(x) for x in l])
        return width

    def __len__(self):
        return len(self.waveform)

    def __eq__(self, other):
        """
        Only use the dontcaremask of self, not other.
        This means in a comparison `a == b` that a.dontcaremask will be used.
        """
        try:
            equal_elements = np.equal(self.waveform, other.waveform)
            result = np.logical_or(equal_elements, self.dontcaremask)
            return result.all()
        except AttributeError:
            return False
        except ValueError:
            return False

    def __getitem__(self, i):
        return self.waveform[i]
