#!/usr/bin/env python3

"""
Impliments correction for thermally-induced measurement offset
of the V2 P.I.N.D.A. inductive probe for the klipper printer firmware.
"""

from .probe import CalibrationData

if __name__ == "__main__":
    print("Running as script")
else:
    print("Running as package")
