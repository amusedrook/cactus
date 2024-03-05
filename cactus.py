#!/usr/bin/env python3

"""Adjust for thermal variablility of PINDA2 inductive probe"""

import logging

from .probe import PrinterProbe, ProbeEndstopWrapper
# from .probe import PrinterProbe, ProbeEndstopWrapper, HINT_TIMEOUT

KELVIN_TO_CELSIUS = -273.15


# CactusPrinterSensor class based on PrinterSensorGeneric
# PrinterSensorGeneric - Copyright (C) 2019  Kevin O'Connor <kevin@koconnor.net>
# https://github.com/Klipper3d/klipper/raw/master/klippy/extras/temperature_sensor.py
# Perhaps I can just inherit from PrinterSensorGeneric?
# Possible problem with how the parent class derives its name
class CactusPrinterSensor:
    """Thermistor for inductive z-probe themperature compensation"""

    def __init__(self, config):
        self.printer = config.get_printer()
        self.name = f"{config.get_name().replace(' ', '_')}_temp_sensor"
        pheaters = self.printer.load_object(config, "heaters")
        self.sensor = pheaters.setup_sensor(config)
        self.min_temp = config.getfloat(
            "min_temp", KELVIN_TO_CELSIUS, minval=KELVIN_TO_CELSIUS
        )
        self.max_temp = config.getfloat("max_temp", 99999999.9, above=self.min_temp)
        self.sensor.setup_minmax(self.min_temp, self.max_temp)
        self.sensor.setup_callback(self.temperature_callback)
        pheaters.register_sensor(config, self)
        self.last_temp = 0.0
        self.measured_min = 99999999.0
        self.measured_max = 0.0

    @classmethod
    def create_safe(cls, config):
        """Check sensor_type and sensor_pin exist before attempting creation"""
        if not (config.get("sensor_type", None) and config.get("sensor_pin", None)):
            return None
        return cls(config)

    def temperature_callback(self, read_time, temp):
        """Update minimum and maximum recorded temperature values"""
        self.last_temp = temp
        if temp:
            self.measured_min = min(self.measured_min, temp)
            self.measured_max = max(self.measured_max, temp)

    def get_temp(self, eventtime):
        """Sensor's last recorded temperature"""
        return self.last_temp, 0.0

    def stats(self, eventtime):
        """Retrieve sensor's name and last recorded temperature"""
        # return False, "%s: temp=%.1f" % (self.name, self.last_temp)
        return False, f"{self.name}: {self.last_temp}"

    def get_status(self, eventtime):
        """Dict of sensor's current state"""
        return {
            "temperature": round(self.last_temp, 2),
            "measured_min_temp": round(self.measured_min, 2),
            "measured_max_temp": round(self.measured_max, 2),
        }


class CactusPrinterProbe(PrinterProbe):
    """Inductive z probe with thermal z variablity compensation"""

    def __init__(self, config, mcu_probe):
        logging.info("CactusPP: init")
        super().__init__(config, mcu_probe)

    def _probe(self, speed):
        """Override PrinterProbe's internal '_probe' method to account for z variability"""
        self.gcode.respond_info("CactusPP _probe: override")
        self.printer.send_event("cactus:probing_move_begin", self)
        pos = super()._probe(speed)
        # TODO:
        # 1. Get temperature
        # 2. Get associated offset
        # 3. Apply offset
        self.gcode.respond_info(f"CactusPP _probe position: {pos}")
        self.printer.send_event("cactus:probing_move_end", self)
        # 3b. Apply offsets here?
        return pos


class CactusProbeEndstopWrapper(ProbeEndstopWrapper):
    """Inductive probe endstop-wrapper with thermal z variablity compensation"""

    def __init__(self, config):
        super().__init__(config)
        self.gcode = self.printer.lookup_object("gcode")
        self.sensor = CactusPrinterSensor.create_safe(config)
        if config.get("sensor_type", None) is None:
            raise config.error("Cactus: sensor_type and sensor_pin are required fields")
        # Event handlers
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
        logging.info("CactusPEW event: klippy:mcu_identify")

    def _handle_connect(self):
        logging.info("CactusPEW event: klippy:connect")

    def _handle_ready(self):
        logging.info("CactusPEW event: klippy:ready")

    def _handle_sync_mcu_position(self, stepper):
        self.gcode.respond_info('CactusPEW event: "stepper:sync_mcu_position"')
        self.gcode.respond_info("CactusPEW stepper: " + stepper.get_name())

    def _handle_home_rails(self, homing_state, rails):
        self.gcode.respond_info(
            f"CactusPEW - homing_state axes: {homing_state.get_axes()}"
        )
        for rail in rails:
            # Returns name of stepper (for cartesian - unknown for others)
            self.gcode.respond_info(f"CactusPEW - rail: {rail.get_name()}")
            for stepper in rail.get_steppers():
                # Returns name of stepper (same name as above for cartesian)
                # Possibly corexy/delta do not have one stepper per rail?
                stepper_name = stepper.get_name()
                self.gcode.respond_info(f"CactusPEW - stepper: {stepper_name}")
                try:
                    # 1. No idea what unit this value is in, nor what it represents
                    # Values fluctuate slightly
                    # x: -3256 (125mm): 3256/125 = 26.048 3dp
                    # y: -2850 (110mm): 2850/110 = 25.909 3dp
                    # z: -16545 (40mm?): 16545/40 = 413.625 3dp
                    #
                    # 2. Appears to be how far the rail moved before the endstop
                    # was triggerd. But still do not kno what unit; steps? microsteps?
                    # x axis currently configured with:
                    # - microstepping = 4
                    # - full steps = 200
                    # It's microsteps. Probably. Which makes sense.
                    trigger_pos = homing_state.get_trigger_position(stepper_name)
                    self.gcode.respond_info(
                        f"CactusPEW - trigger_position: {trigger_pos}"
                    )
                except:
                    self.gcode.respond_info("CactusPEW - trigger_position: N/A")
            for endstops in rail.get_endstops():
                self.gcode.respond_info(f"CactusPEW - endstops: {endstops}")
                try:
                    # Endstop position equals z_offset, which is distance between
                    # nozzle and bed-surface at probe's trigger point.
                    # i.e. "self.z_offset" in the "PrinterProbe" class or
                    # self.position_endstop in the "ProbeEndstopWrapper" class
                    # (parent of this class).
                    # ...so this is a silly way to get this value.
                    endstop_position = endstops[0].get_position_endstop()
                    self.gcode.respond_info(
                        f"CactusPEW - endstop_position: {endstop_position}"
                    )
                except:
                    pass

    def _handle_home_rails_begin(self, homing_state, rails):
        self.gcode.respond_info("CactusPEW event: homing:home_rails_begin")
        self._handle_home_rails(homing_state, rails)

    def _handle_home_rails_end(self, homing_state, rails):
        self.gcode.respond_info("CactusPEW event: homing:home_rails_end")
        self._handle_home_rails(homing_state, rails)

    def _handle_homing_move(self, homing_move):
        # Not sure there's much I can do with a HomingMove object.
        # Possible to use these events?
        self.gcode.respond_info(f"CactusPEW - homing_move: {homing_move}")

    def _handle_homing_move_begin(self, homing_move):
        self.gcode.respond_info("CactusPEW event: homing:homing_move_begin")
        self._handle_homing_move(homing_move)

    def _handle_homing_move_end(self, homing_move):
        self.gcode.respond_info("CactusPEW event: homing:homing_move_end")
        self._handle_homing_move(homing_move)


def load_config(config):
    """Load Cactus module and register as a 'probe'"""
    cactus_probe = CactusPrinterProbe(config, CactusProbeEndstopWrapper(config))
    config.get_printer().add_object("probe", cactus_probe)
    return cactus_probe
