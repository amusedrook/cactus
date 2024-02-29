#!/usr/bin/env python3

"""Adjust for thermal variablility of PINDA2 inductive probe"""

import logging

# import probe
# from . import probe
# from probe import PrinterProbe, ProbeEndstopWrapper
from .probe import PrinterProbe, ProbeEndstopWrapper


class CactusPrinterProbe(PrinterProbe):
    """(Override) Inductive probe"""

    def __init__(self, config, mcu_probe):
        logging.info("CactusPrinterProbe:")
        super().__init__(config, mcu_probe)


class CactusProbeEndstopWrapper(ProbeEndstopWrapper):
    """(Override) Endstop wrapper that enables probe specific features"""

    def __init__(self, config):
        logging.info("CactusPEW: init")
        super().__init__(config)
        self.gcode = self.printer.lookup_object("gcode")
        self.printer.register_event_handler(
            "klippy:mcu_identify", self._handle_mcu_identify
        )
        self.printer.register_event_handler("klippy:connect", self._handle_connect)
        self.printer.register_event_handler("klippy:ready", self._handle_ready)
        self.printer.register_event_handler(
            "stepper:sync_mcu_position",
            self._handle_sync_mcu_position,
        )
        self.printer.register_event_handler(
            "homing:home_rails_begin", self._handle_home_rails_begin
        )
        self.printer.register_event_handler(
            "homing:home_rails_end", self._handle_home_rails_end
        )
        self.printer.register_event_handler(
            "homing:homing_move_begin", self._handle_homing_move_begin
        )
        self.printer.register_event_handler(
            "homing:homing_move_end", self._handle_homing_move_end
        )

    def _handle_mcu_identify(self):
        logging.info('CactusPEW event: "klippy:mcu_identify"')

    def _handle_connect(self):
        logging.info('CactusPEW event: "klippy:connect"')

    def _handle_ready(self):
        logging.info('CactusPEW event: "klippy:ready"')

    def _handle_sync_mcu_position(self, stepper):
        #logging.info('CactusPEW event: "stepper:sync_mcu_position"')
        self.gcode.respond_info('CactusPEW event: "stepper:sync_mcu_position"')
        #logging.info("CactusPEW stepper: " + stepper.get_name())
        self.gcode.respond_info("CactusPEW stepper: " + stepper.get_name())

    def _handle_home_rails(self, homing_state, rails):
        #logging.info(f"CactusPEW homing_state axes: {homing_state.get_axes()}")
        self.gcode.respond_info(f"CactusPEW - homing_state axes: {homing_state.get_axes()}")
        for rail in rails:
            # Returns name of stepper (for cartesian - unknown for others)
            #logging.info(f"CactusPEW rail: {rail.get_name()}")
            self.gcode.respond_info(f"CactusPEW - rail: {rail.get_name()}")
            for stepper in rail.get_steppers():
                # Returns name of stepper (same name as above for cartesian)
                # Possibly corexy/delta do not have one stepper per rail?
                stepper_name = stepper.get_name()
                #logging.info(f'CactusPEW stepper: "{stepper_name}"')
                self.gcode.respond_info(f"CactusPEW - stepper: {stepper_name}")
                try:
                    # No idea what unit this value is in, nor what it represents
                    # Values fluctuate slightly
                    # x: -3256 (125mm): 3256/125 = 26.048 3dp
                    # y: -2850 (110mm): 2850/110 = 25.909 3dp
                    # z: -16545 (40mm?): 16545/40 = 413.625 3dp
                    #
                    trigger_pos = homing_state.get_trigger_position(stepper_name)
                    #logging.info(f"CactusPEW trigger_position: {trigger_pos}")
                    self.gcode.respond_info(f"CactusPEW - trigger_position: {trigger_pos}")
                except:
                    #logging.info("CactusPEW trigger_position: N/A")
                    self.gcode.respond_info("CactusPEW - trigger_position: N/A")
            for endstops in rail.get_endstops():
                #logging.info(f"CactusPEW endstops: {endstops}")
                self.gcode.respond_info(f"CactusPEW - endstops: {endstops}")
                try:
                    # Endstop position equals z_offset, which is distance between
                    # nozzle and bed-surface at probe's trigger point.
                    # i.e. "self.z_offset" in the "PrinterProbe" class or
                    # self.position_endstop in the "ProbeEndstopWrapper" class
                    # (parent of this class).
                    # ...so this is a silly way to get this value.
                    endstop_position = endstops[0].get_position_endstop()
                    #logging.info(f"CactusPEW endstop position: {endstop_position}")
                    self.gcode.respond_info(f"CactusPEW - endstop_position: {endstop_position}")
                except:
                    pass

    def _handle_home_rails_begin(self, homing_state, rails):
        #logging.info('CactusPEW event: "homing:home_rails_begin"')
        self.gcode.respond_info("CactusPEW event: homing:home_rails_begin")
        self._handle_home_rails(homing_state, rails)

    def _handle_home_rails_end(self, homing_state, rails):
        #logging.info('CactusPEW event: "homing:home_rails_end"')
        self.gcode.respond_info("CactusPEW event: homing:home_rails_end")
        self._handle_home_rails(homing_state, rails)

    def _handle_homing_move(self, homing_move):
        self.gcode.respond_info(f"CactusPEW - homing_move: {homing_move}")

    def _handle_homing_move_begin(self, homing_move):
        self.gcode.respond_info("CactusPEW event: homing:homing_move_begin")
        #logging.info('CactusPEW event: "homing:homing_move_begin"')
        self._handle_homing_move(homing_move)

    def _handle_homing_move_end(self, homing_move):
        self.gcode.respond_info("CactusPEW event: homing:homing_move_end")
        #logging.info('CactusPEW event: "homing:homing_move_end"')
        self._handle_homing_move(homing_move)


def load_config(config):
    """Load Cactus module and register as a 'probe'"""
    cactus_probe = CactusPrinterProbe(config, CactusProbeEndstopWrapper(config))
    config.get_printer().add_object("probe", cactus_probe)
    return cactus_probe
