from cocotb.handle import ModifiableObject
from cocotb.utils import get_sim_time


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
