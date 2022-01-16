from cocotb_test.simulator import run
import os


def test_ff():
    os.environ["SIM"] = "ghdl"
    run(
        vhdl_sources=["ff.vhd"],
        toplevel="ff",
        # python_search=[],
        module="ff",
        toplevel_lang="vhdl",
        force_compile=True,
    )
