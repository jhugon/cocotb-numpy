from cocotbnumpy.signal import NumpySignal
import numpy as np


def test_NumpySignal_basics():
    in1 = [0, 1, 0, 1, 0, 1]
    s1 = NumpySignal(in1)
    assert str(s1) == str(in1).replace(",", "")[1:-1]
    assert s1.get_max_str_width() == 1
    assert len(s1) == len(in1)
    assert s1 == NumpySignal(in1)
    for i in range(len(in1)):
        assert s1[i] == in1[i]

    in2 = list(range(10))
    s2 = NumpySignal(in2)
    assert str(s2) == str(in2).replace(",", "")[1:-1]
    assert s2.get_max_str_width() == 1
    assert len(s2) == len(in2)
    assert (s2 == NumpySignal(in2)).all()
    for i in range(len(in2)):
        assert s2[i] == in2[i]

    assert s1[0] == s2[0]
    assert s1[5] != s2[5]
    assert s1 != s2

    ## Just checking some random other type
    assert s1 != "xxx"


def test_NumpySignal_masks():
    in1 = [0, 1, 0, 1, 0, 1]
    in2 = [1, 0, 0, 1, 0, 1]
    s1 = NumpySignal(in1, [1, 1])
    s2 = NumpySignal(in2)

    in1str = "- - 0 1 0 1"
    assert str(s1) == in1str
    assert repr(s1) == f"NumpySignal({in1},[1, 1, 0, 0, 0, 0])"

    for i in range(len(in1)):
        if i < 2:
            assert s1[i] != in2[i]
        else:
            assert s1[i] == in2[i]
    assert s1 == s2
    assert s2 != s1
