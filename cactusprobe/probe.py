#!/usr/bin/env python3

"""V2 P.I.N.D.A. style inductive z-probe with temperature compensation."""

from typing import Self

from .constants import ErrorMessages as emsg
from .constants import Defaults as defaults


class CalibrationData:
    """Parse and store the raw calibration data."""

    _calibration_points: dict[float, float]
    _valid: bool = False
    _writable: bool = True

    def __init__(
        self, calibration_points: dict[float, float], direct_init: bool = True
    ) -> None:
        if direct_init:
            raise RuntimeError(emsg.use_alt_init)
        self._calibration_points = calibration_points
        if len(calibration_points) > defaults.min_calibration_points:
            self._valid = True

    @classmethod
    def create_empty(cls) -> Self:
        """Create an empty - invalid - object, to store new calibration points."""
        return cls({}, False)

    @classmethod
    def create_from_dict(cls, data_as_dict: dict[float | int, float | int]) -> Self:
        """Create - with checking - a CactusCalibrationData from data as dict."""
        if not isinstance(data_as_dict, dict):
            raise TypeError(emsg.requires_dict)
        if len(data_as_dict) < defaults.min_calibration_points:
            raise ValueError(emsg.too_few_points)
        calibration_data_parsed: dict[float, float] = {}
        for key, value in data_as_dict.items():
            if not isinstance(key, float | int) or not isinstance(value, float | int):
                raise TypeError(emsg.wrong_data_type)
            if float(key) in calibration_data_parsed.keys():
                # This should not be possible
                raise RuntimeError(emsg.duplicate_calibration_point)
            calibration_data_parsed[float(key)] = float(value)
        calibration_data_parsed = dict(sorted(calibration_data_parsed.items()))
        return cls(calibration_data_parsed, False)

    @classmethod
    def create_from_list(
        cls, data_as_list: list[tuple[float | int, float | int]]
    ) -> Self:
        """Create - with checking - a CactusCalibrationData from a list of tupls."""
        if not isinstance(data_as_list, list):
            raise TypeError(emsg.requires_list_of_tuples)
        if len(data_as_list) < defaults.min_calibration_points:
            raise ValueError(emsg.too_few_points)
        calibration_data_parsed: dict[float, float] = {}
        for point in data_as_list:
            if not isinstance(point, tuple):
                # Could this happily accept other iterables?
                raise TypeError(emsg.requires_list_of_tuples)
            if len(point) != 2:
                raise ValueError(emsg.requires_data_pair)
            if not isinstance(point[0], float | int) or not isinstance(
                point[1], float | int
            ):
                raise TypeError(emsg.wrong_data_type)
            if float(point[0]) in calibration_data_parsed.keys():
                # This should not be possible
                raise RuntimeError(emsg.duplicate_calibration_point)
            calibration_data_parsed[float(point[0])] = float(point[1])
        calibration_data_parsed = dict(sorted(calibration_data_parsed.items()))
        return cls(calibration_data_parsed, False)

    @classmethod
    def create_from_str(cls, data_as_str_blob: str) -> Self:
        """Create a CactusCalibrationData object from calibration data as a string."""
        if not isinstance(data_as_str_blob, str):
            raise TypeError(emsg.requires_string)
        data_as_str_split = [
            row.split(",", 1) for row in data_as_str_blob.split("\n") if row.strip()
        ]
        data_as_list = [
            (float(r[0].strip()), float(r[1].strip())) for r in data_as_str_split
        ]
        return cls.create_from_list(data_as_list)

    def temps_as_list(self) -> list[float] | None:
        """List of all the 'x' (temperature) calibrated data-points."""
        if self._valid is True:
            return list(self._calibration_points.keys())
        return None

    def offsets_as_list(self) -> list[float] | None:
        """List of all the 'y' (offset) calibrated data-points."""
        if self._valid is True:
            return list(self._calibration_points.values())
        return None

    def set_ro(self) -> None:
        """Set this set of calibration-points to 'read only'."""
        self._writable = False

    def is_writable(self) -> bool:
        """Can the data-set have new points added?"""
        return self._writable

    def is_valid(self) -> bool:
        """Do the data-poins represent a valid functioning calibration?"""
        return self._valid


def _test() -> None:
    """Test the probe code functionality"""
    # python -m cactusprobe.probe
    import traceback

    test_data_as_dict: dict[float, float] = {0.0: 5.0, 10.0: 15.0, 20.0: 25.0}
    test_data_as_list: list[tuple[float, float]] = [
        (0.0, 5.0),
        (10.0, 15.0),
        (20.0, 25.0),
    ]
    test_data_as_str: str = "\t0.0, 5.0\n\t10.0, 15.0\n\t20.0, 25.0"
    print("CalibrationData: init methods - basic tests")
    print("CalibrationData.create_empty()...")
    try:
        _ = CalibrationData.create_empty()
    except Exception as exc:
        traceback.print_exception(exc)
    else:
        print("\tPASSED")
    print("CalibrationData.create_from_dict()...")
    try:
        _ = CalibrationData.create_from_dict(test_data_as_dict)
    except Exception as exc:
        traceback.print_exception(exc)
    else:
        print("\tPASSED")
    print("CalibrationData.create_from_list()...")
    try:
        _ = CalibrationData.create_from_list(test_data_as_list)
    except Exception as exc:
        traceback.print_exception(exc)
    else:
        print("\tPASSED")
    print("CalibrationData.create_from_str()...")
    try:
        _ = CalibrationData.create_from_str(test_data_as_str)
    except Exception as exc:
        traceback.print_exception(exc)
    else:
        print("\tPASSED")
    print("CalibrationData: create from default calibration data")
    test_data: CalibrationData
    try:
        test_data = CalibrationData.create_from_str(defaults.calibrated_offsets)
    except Exception as exc:
        traceback.print_exception(exc)
    else:
        print("\tPASSED")
        print(f"\tTemps: {test_data.temps_as_list()}")
        print(f"\tOffsets: {test_data.offsets_as_list()}")


if __name__ == "__main__":
    _test()
