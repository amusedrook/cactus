#!/usr/bin/env python3

"""Adjust for thermal variablility of PINDA2 inductive probe"""

import logging

# import probe
from . import probe
# from probe import PrinterProbe, ProbeEndstopWrapper


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
        #self.printer.register_event_handler(
        #    "toolhead:sync_print_time", self._handle_sync_print_time
        #)
        #self.printer.register_event_handler(
        #    "toolhead:set_position", self._handle_set_position
        #)
        #self.printer.register_event_handler(
        #    "toolhead:manual_move", self._handle_manual_move
        #)

    def _handle_mcu_identify(self):
        logging.info('CactusProbeEndstopWrapper event: "klippy:mcu_identify"')

    def _handle_connect(self):
        logging.info('CactusProbeEndstopWrapper event: "klippy:connect"')

    def _handle_ready(self):
        logging.info('CactusProbeEndstopWrapper event: "klippy:ready"')

    def _handle_sync_mcu_position(self, stepper):
        logging.info('CactusProbeEndstopWrapper event: "stepper:sync_mcu_position"')
        logging.info('CactusProbeEndstopWrapper stepper: '+stepper.get_name())

    def _handle_home_rails_begin(self, homing_state, rails):
        logging.info('CactusProbeEndstopWrapper event: "homing:home_rails_begin"')
        logging.info(f'CactusProbeEndstopWrapper homing_state axes: {homing_state.get_axes()}')
        for rail in rails:
            #logging.info(f'CactusProbeEndstopWrapper rail steppers: "{rail.get_steppers()}"')
            for stepper in rail.get_steppers():
                stepper_name = stepper.get_name()
                logging.info(f'CactusProbeEndstopWrapper stepper: "{stepper_name}"')
                logging.info(f'CactusProbeEndstopWrapper trigger_position: {homing_state.get_trigger_position(stepper_name)}')
        #logging.info(f'CactusProbeEndstopWrapper rails steppers: "{rails.get_steppers()}"')
        #logging.info(f'CactusProbeEndstopWrapper rails endstopt: "{rails.get_endstops()}"')

    def _handle_home_rails_end(self, homing_state, rails):
        logging.info('CactusProbeEndstopWrapper event: "homing:home_rails_end"')
        logging.info(f'CactusProbeEndstopWrapper homing_state axes: {homing_state.get_axes()}')
        #logging.info(f'CactusProbeEndstopWrapper rails steppers: "{rails.get_steppers()}"')
        #logging.info(f'CactusProbeEndstopWrapper rails endstopt: "{rails.get_endstops()}"')

    def _handle_homing_move_begin(self, homing_move):
        logging.info('CactusProbeEndstopWrapper event: "homing:homing_move_begin"')

    def _handle_homing_move_end(self, homing_move):
        logging.info('CactusProbeEndstopWrapper event: "homing:homing_move_end"')

    #def _handle_sync_print_time(self):
    #    logging.info('CactusProbeEndstopWrapper event: "toolhead:sync_print_time"')

    #def _handle_set_position(self):
    #    logging.info('CactusProbeEndstopWrapper event: "toolhead:set_position"')

    #def _handle_manual_move(self):
    #    logging.info('CactusProbeEndstopWrapper event: "toolhead:manual_move"')


def load_config(config):
    """This is a docstring"""
    # return CactusPrinterProbe(config, CactusProbeEndstopWrapper(config))
    cactus_probe = CactusPrinterProbe(config, CactusProbeEndstopWrapper(config))
    config.get_printer().add_object("probe", cactus_probe)
    return cactus_probe
