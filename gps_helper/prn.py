import json
import os
from collections import deque

prn_json = open(os.path.join(os.path.dirname(__file__), 'prn_info.json')).read()
prn_info = json.loads(prn_json)


class ShiftRegister:

    def __init__(self, poly_taps, prn_taps):
        """

        :param poly_taps: The polynomial taps to be used for the shift register. Usually G1, or G2 as specified in the
        ICD 200.
        :param prn_taps: The taps for the output, generally 10 for G1, or the sv taps listed in the ICD 200.
        """
        self.G = deque([1 for i in range(10)])  # Needs to be ints for binary addition)
        self.poly_taps = poly_taps
        self.prn_taps = prn_taps

    def next(self):
        """
        Generate the next output and return it. This method includes the feedback step.
        :return: Bit
        """
        out = self.get_output()
        self.do_feedback()
        return out

    def do_feedback(self):
        """
        Generate the feedback, and shift the values.
        :return:
        """
        fb = [self.G[i - 1] for i in self.poly_taps]
        fb = sum(fb) % 2
        self.G.pop()
        self.G.appendleft(fb)

    def get_output(self):
        """
        Generate the next output value for the sequence.
        :return: Bit
        """
        out = [self.G[i - 1] for i in self.prn_taps]
        out = sum(out) % 2
        return out


class PRN:

    def __init__(self, prn):
        """

        :param prn: SV ID No. as described in the ICD 200.
        """
        sv_range_message = "prn must be 1-63"
        self.prn = prn
        if prn < 1 or prn > 63:
            ValueError(sv_range_message)
        self.sv_prn = prn % 37 if prn > 37 else prn
        self.sv_taps = prn_info['taps'][str(self.sv_prn)]
        self.g1 = ShiftRegister(prn_info['taps']['G1'], [10])
        self.g2 = ShiftRegister(prn_info['taps']['G2'], self.sv_taps)
        if prn > 38:
            delays = prn_info['delays'][str(self.prn)]
            # TODO: Apply shifts to the X2 array before starting sequence
        self.iteration = 0
        self.ca = []

    def next(self):
        """
        Get the next chip in the sequence.
        :return:
        """
        if self.iteration < 1023:
            g1 = self.g1.next()
            g2 = self.g2.next()
            ca = (g1 + g2) % 2
            self.ca.append(ca)
            return ca