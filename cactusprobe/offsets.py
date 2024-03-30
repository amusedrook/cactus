#!/usr/bin/env python3

"""Interpolate probe measurement offsets from discrete temperature/offset points."""

from typing import Self
from dataclasses import dataclass, asdict

import numpy as np
import numpy.typing as npt
import numpy.polynomial as npp

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
            # if float(key) in calibration_data_parsed.keys():
            if float(key) in calibration_data_parsed:
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
            # if float(point[0]) in calibration_data_parsed.keys():
            if float(point[0]) in calibration_data_parsed:
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

    def temps_as_list(self) -> list[float]:
        """List of all the 'x' (temperature) calibrated data-points."""
        return list(self._calibration_points.keys())

    def offsets_as_list(self) -> list[float]:
        """List of all the 'y' (offset) calibrated data-points."""
        return list(self._calibration_points.values())

    def set_ro(self) -> None:
        """Set this set of calibration-points to 'read only'."""
        self._writable = False

    def is_writable(self) -> bool:
        """Can the data-set have new points added?"""
        return self._writable

    def is_valid(self) -> bool:
        """Do the data-poins represent a valid functioning calibration?"""
        return self._valid


@dataclass
class Range:
    """Verbose methhod to store max and min values."""

    __slots__ = ("min", "max")
    min: float
    max: float


class InterpolatedOffsets:
    """Interpolate between discrete calibrated data-points"""

    _calibration_temps: npt.NDArray = np.empty(0)
    _calibration_offsets: npt.NDArray = np.empty(0)
    _calibrated_temp: Range
    _calibrated_offset: Range
    _calibrated_curve: npp.Polynomial
    _poly: bool = False

    def __init__(self, cd: CalibrationData) -> None:
        if not cd.is_valid():
            raise RuntimeError(emsg.invalid_calibration_data)
        self._calibration_temps = np.array(cd.temps_as_list())
        self._calibration_offsets = np.array(cd.offsets_as_list())
        self._calibrated_temp = Range(
            min=np.min(self._calibration_temps).item(),
            max=np.max(self._calibration_temps).item(),
        )
        self._calibrated_offset = Range(
            min=np.min(self._calibration_offsets).item(),
            max=np.max(self._calibration_offsets).item(),
        )
        # scipy curve_fit uses 'sigma', where numpy Plynomial uses 'w' (weighting)
        # 'w' seems to be effectivly the inverse of sigma.
        # some discussion of deprecating numpy's 'w' in favour of using
        # the same nomecalature as scipy.
        sigma: npt.NDArray = np.ones(len(self._calibration_temps))
        sigma[[0]] = 0.01
        weights: npt.NDArray = np.empty(0)
        for s in sigma:
            weights = np.append(weights, 1 / (s**1))
        print(sigma)
        print(weights)
        max_poly_terms: int = min(
            defaults.max_poly_terms, len(self._calibration_temps) - 1
        )
        if max_poly_terms >= defaults.min_poly_terms:
            for terms in range(defaults.min_poly_terms, max_poly_terms + 1):
                # test_curve = npp.Polynomial.fit(
                #    self._calibration_temps, self._calibration_offsets, terms - 1
                # )
                test_curve = npp.Polynomial.fit(
                    self._calibration_temps,
                    self._calibration_offsets,
                    terms - 1,
                    w=weights,
                )
                residuals: npt.NDArray = self._calibration_offsets - test_curve(
                    self._calibration_temps
                )
                ss_res: np.float64 = np.sum(residuals**2)
                ss_tot: np.float64 = np.sum(
                    (self._calibration_offsets - np.mean(self._calibration_offsets))
                    ** 2
                )
                r_squared: float = 1.0 - (ss_res.item() / ss_tot.item())
                if r_squared >= defaults.min_r2:
                    self._calibrated_curve = test_curve
                    print(f"Found acceptible match at r2: {r_squared}")
                    print("Calibration offsets:\n" + f"{self._calibration_offsets}")
                    print(
                        "Calculated offsets:\n"
                        + f"{self._interpolate_poly(self._calibration_temps)}"
                    )
                    self._poly = True
                    break

    def _interpolate_linear(
        self, x: npt.NDArray | np.float64
    ) -> npt.NDArray | np.float64:
        """Linear interpolation between calibration points (fallback)."""
        return np.interp(x, self._calibration_temps, self._calibration_offsets)

    def _interpolate_poly(
        self, x: npt.NDArray | np.float64
    ) -> npt.NDArray | np.float64:
        """extrapolated offset using calibrated polynomial curve."""
        return self._calibrated_curve(x)

    def _clamp(self, temp: float) -> np.float64:
        """Clamp the imput temperature to the calibrated range."""
        return np.float64(
            max(min(temp, self._calibrated_temp.max), self._calibrated_temp.min)
        )

    def get_offset(self, temp: float) -> float:
        """Return temperature-induced offset interpolated from the calibration data."""
        if self._poly is True:
            return round(self._interpolate_poly(self._clamp(temp)).item(), 3)
        return round(self._interpolate_linear(self._clamp(temp)).item(), 3)

    def get_temp_range(self) -> tuple[float, float]:
        """Temperature range (min, max) over which the offsets are valid (as tuple)."""
        return (self._calibrated_temp.min, self._calibrated_temp.max)

    def get_temp_range_as_dict(self) -> dict[str, float]:
        """Temperature range (min, max) over which the offsets are valid (as dict)."""
        return asdict(self._calibrated_temp)

    def get_offset_range(self) -> tuple[float, float]:
        """Offset range (min, max) as tuple."""
        return (self._calibrated_offset.min, self._calibrated_offset.max)

    def get_offset_range_as_dict(self) -> dict[str, float]:
        """Offset range (min, max) as dict."""
        return asdict(self._calibrated_offset)


if __name__ == "__main__":
    print("Module has no standalone functionality.")
