from cocotbnumpy.signal import NumpySignal
from cocotbnumpy.test import NumpyTest
import numpy as np
import cocotb


@cocotb.test()
async def NumpyTest_basics(dut):
    in_sigs = {
        "sig_in": [0, 1, 0, 1, 0, 1, 0, 0, 0, 0],
    }
    exp_sigs = {
        "sig_out": NumpySignal([0, 0, 1, 0, 1, 0, 1, 0, 0, 0], [1, 1]),
        # "sig_out": [0, 0, 1, 0, 1, 0, 1, 0, 0, 0],
    }
    nptest = NumpyTest(dut, in_sigs, exp_sigs, "clock")
    await nptest.run(True)
