import cocotb
from cocotb.triggers import FallingEdge
from cocotb.clock import Clock
from .signal import NumpySignal
import numpy as np


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
        cocotb.start_soon(Clock(self.clock_sig, 10, units="ns").start())
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