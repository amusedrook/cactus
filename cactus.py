#!/usr/bin/env python3

"""Adjust for thermal variablility of PINDA2 inductive probe"""

import logging
import probe


class CactusPrinterProbe(probe.PrinterProbe):
    """(Override) Inductive probe"""

    def __init__(self, config, mcu_probe):
        logging.info("CactusPrinterProbe:")
        super().__init__(config, mcu_probe)


class CactusProbeEndstopWrapper(probe.ProbeEndstopWrapper):
    """(Override) Endstop wrapper that enables probe specific features"""

    def __init__(self, config):
        logging.info("CactusProbeEndstopWrapper:")
        super().__init__(config)


def load_config(config):
    """This is a docstring"""
    return CactusPrinterProbe(config, CactusProbeEndstopWrapper(config))
