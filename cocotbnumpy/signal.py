import numpy as np


class NumpySignal:
    def __init__(self, waveform, dontcaremask=None, badmask=None):
        """
        waveform is a numpy array of signal values at each successive clock.

        npsig = NumpySignal([0,1,0,0,1,1,0,0,1])

        If there are some clocks where you don't care what the value is, you
        can put 1's in those positions in the array given to dontcaremask. The
        array will be extended with zeros to the size of waveform. ex:

        npsigdc = NumpySignal([0,0,1,1,1],dontcaremask=[1,1])

        The dontcaremask is only taken into account on the first member of an equality
        check, that is:

        in1 = [0,1,0,1,0,1]
        in2 = [1,0,0,1,0,1]
        s1 = NumpySignal(in1,[1,1])
        s2 = NumpySignal(in2)
        assert s1 == s2
        assert s2 != s1

        The bad mask is for undefined and uncertain values. It will fail an
        equality test unless the dontcaremask stops it.
        """
        flag_type = np.uint8
        waveform_type = np.uint64
        waveform = np.array(waveform, dtype=waveform_type)
        if dontcaremask is None:
            dontcaremask = np.zeros(waveform.size, dtype=flag_type)
        if badmask is None:
            badmask = np.zeros(waveform.size, dtype=flag_type)
        dontcaremask = np.array(dontcaremask, dtype=flag_type)
        badmask = np.array(badmask, dtype=flag_type)

        if len(waveform) > len(dontcaremask):
            tmp = np.zeros(waveform.size, dtype=flag_type)
            tmp[: len(dontcaremask)] = dontcaremask
            dontcaremask = tmp
        if len(waveform) > len(badmask):
            tmp = np.zeros(waveform.size, dtype=flag_type)
            tmp[: len(badmask)] = badmask
            badmask = tmp

        self.waveform = waveform
        self.dontcaremask = dontcaremask
        self.badmask = badmask

    def __str__(self):
        l = list(self.waveform)
        l = ["{}".format(x) for x in l]
        width = max([len(x) for x in l])
        result = ""
        for x, dc, bad in zip(self.waveform, self.dontcaremask, self.badmask):
            if dc:
                result += ("{:" + str(width) + "} ").format("-")
            elif bad:
                result += ("{:" + str(width) + "} ").format("U")
            else:
                result += ("{:" + str(width) + "} ").format(x)
        if len(result) > 0:
            result = result[:-1]
        return result

    def __repr__(self):
        return f"NumpySignal({list(self.waveform)},{list(self.dontcaremask)})"

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
            selfgoodmask = np.logical_not(self.badmask)
            othergoodmask = np.logical_not(other.badmask)
            goodmask = np.logical_and(selfgoodmask, othergoodmask)
            result = np.logical_and(equal_elements, goodmask)
            result = np.logical_or(result, self.dontcaremask)
            return result.all()
        except AttributeError:
            return False
        except ValueError:
            return False

    def __getitem__(self, i):
        if self.badmask[i]:
            return "U"
        elif self.dontcaremask[i]:
            return "-"
        else:
            return self.waveform[i]

    def __setitem__(self, i, x):
        try:
            self.waveform[i] = int(x)
        except ValueError as e:
            x = str(x)
            if x == "U" or x == "X":
                self.badmask[i] = 1
