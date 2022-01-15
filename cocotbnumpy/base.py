import cocotb

# from cocotb.triggers import Timer
# from cocotb.triggers import FallingEdge
# from cocotb.clock import Clock
from cocotb.handle import ModifiableObject
from cocotb.utils import get_sim_time

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


class NumpyTest:
    def __init__(self, dut, in_dict, expected_dict, clock_name):
        self.in_dict = self._convert_dict_to_npsigs(in_dict)
        self.expected_dict = self._convert_dict_to_npsigs(expected_dict)
        self.obs_dict = None
        self.clock_name = clock_name
        self.clock_sig = getattr(clock, clock_name)

        # defines self.sig_len
        self._get_and_check_lengths(self)

        self.dut = dut

    async def run(self):
        self.obs_dict = {}
        for exp_key in self.expected_dict:
            self.obs_dict[exp_key] = np.zeros(self.sig_len)
        for iClock in range(self.sig_len):
            for obs_key in self.obs_dict:
                obs_val = self.dut.get_sig_val(obs_key)
                self.obs_dict[obs_key][iClock] = obs_val
            for sig_key in self.in_dict:
                self.dut.set_sig_val(sig_key, self.in_dict[sig_key])
            await FallingEdge(self.clock_sig)
        ## Done running, now to just check obs vs exp
        for exp_key in self.expected_dict:
            exp = self.expected_dict[exp_key]
            obs = self.obs_dict[exp_key]
            assert exp == obs

    def _convert_to_npsig(self, sig):
        if isinstance(sig, NumpySignal):
            return sig
        else:
            return NumpySignal(sig)

    def _convert_dict_to_npsigs(self, d):
        result = {}
        for key in d:
            result[key] = self._convert_to_npsig(d[key])
        return result

    def _get_and_check_lengths(self, d):
        for d in [self.in_dict, self.expected_dict]:
            for key in d:
                n = len(d[key])
                try:
                    if self.sig_len != n:
                        raise ValueError(
                            f"Every input waveform doesn't have the same length. Previous lengths: {self.sig_len} but signame: {key} length: {n}"
                        )
                except AttributeError:
                    self.sig_len = n

    def get_waveform_listing_string(self):
        clock_width = max(len(str(self.sig_len)), 4)
        result = ("{:" + str(clock_width) + "}").format("iClk")
        in_widths = []
        for key in sorted(self.in_dict):
            width = self.in_dict[key].get_max_str_width()
            width = max(len(key), width)
            in_widths.append(width)
            result += (" {" + str(width) + "}").format(key)
        obs_widths = []
        for key in sorted(self.obs_dict):
            width = self.obs_dict[key].get_max_str_width()
            width = max(len(key), width)
            obs_widths.append(width)
            result += (" {" + str(width) + "}").format(key)
        result += "\n"
        for iClock in range(self.sig_len):
            result += ("{:" + str(clock_width) + "}").format(iClock)
            for key, width in zip(sorted(self.in_dict), in_widths):
                result += (" {" + str(width) + "}").format(self.in_dict[key][iClock])
            for key, width in zip(sorted(self.obs_dict), obs_widths):
                result += (" {" + str(width) + "}").format(self.obs_dict[key][iClock])
            result += "\n"
        return result


class BaseDUT:
    def __init__(self, dut, in_names: list, out_names: list, clock_name: str):
        self.dut = dut
        self.in_names = in_names
        self.out_names = out_names
        self.clock_name = clock_name
        self.in_sigs = []
        self.out_sigs = []
        self.internal_sigs = []
        self.in_sig_dict = {}
        self.out_sig_dict = {}
        self.internal_sig_dict = {}
        self.all_sig_dict = {}
        self.clock_sig = None
        for attr_name in dir(dut):
            attr = getattr(dut, attr_name)
            if not isinstance(attr, ModifiableObject):
                continue
            self.all_sig_dict[attr_name] = attr
            if attr_name == clock_name:
                self.clock_sig = attr
            elif attr_name in in_names:
                self.in_sigs.append(attr)
                self.in_sig_dict[attr_name] = attr
            elif attr_name in out_names:
                self.out_sigs.append(attr)
                self.out_sig_dict[attr_name] = attr
            else:
                self.internal_sigs.append(attr)
                self.internal_sig_dict[attr_name] = attr

    def get_signal(self, signname):
        return self.all_sig_dict(signame)

    def get_sig_val(self, signame):
        return self.get_signal(signame).value

    def set_sig_val(self, signame, val):
        self.get_signal(signame).value = val

    def format_sig(self, sig):
        return sig.value

    def __str__(self):
        return self.get_str(show_internal=False)

    def get_str(self, show_internal=False):
        result = ""
        result += self.clock_sig._name + ": {0}".format(self.format_sig(self.clock_sig))
        for sig in self.in_sigs:
            result += " " + sig._name + ": {0}".format(self.format_sig(sig))
        if show_internal:
            for sig in self.internal_sigs:
                result += " " + sig._name + ": {0}".format(self.format_sig(sig))
        for sig in self.out_sigs:
            result += " " + sig._name + ": {0}".format(self.format_sig(sig))
        return result

    def log(self, other_info="", show_internal=False):
        self.dut._log.info(
            f"At {get_sim_time('ns'):4.0f} ns {other_info} {self.get_str(show_internal)}"
        )
