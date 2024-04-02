#!/usr/bin/env python3

"""Tests for CalibrationData and InterpolatedOffseta."""

import unittest

import numpy as np
import matplotlib.pyplot as mplt

from cactusprobe.constants import Defaults
from cactusprobe.offsets import CalibrationData as cdat
from cactusprobe.offsets import InterpolatedOffsets as intoffs


class TestDefaults(unittest.TestCase):
    """Defaults tests."""

    def test_min_calibration_points(self) -> None:
        """Test min_calibration_points type and value."""
        self.assertTrue(isinstance(Defaults.min_calibration_points, int))
        self.assertTrue(Defaults.min_calibration_points >= 3)

    def test_r2(self) -> None:
        """Test min_r2 type and value."""
        self.assertTrue(isinstance(Defaults.min_r2, float))
        self.assertTrue(Defaults.min_r2 >= 0.0)
        self.assertTrue(Defaults.min_r2 <= 1.0)

    def test_min_poly_terms(self) -> None:
        """Test min_poly_terms type and value."""
        self.assertTrue(isinstance(Defaults.min_poly_terms, int))
        self.assertTrue(Defaults.min_poly_terms >= 2)

    def test_max_poly_terms(self) -> None:
        """Test max_poly_terms type and value."""
        self.assertTrue(isinstance(Defaults.max_poly_terms, int))
        self.assertTrue(Defaults.max_poly_terms >= 2)
        self.assertTrue(Defaults.max_poly_terms >= Defaults.min_poly_terms)

    def test_calibrated_offsets(self) -> None:
        """Test calibrated_offsets type."""
        self.assertTrue(isinstance(Defaults.calibrated_offsets, str))


class TestCalibrationData(unittest.TestCase):
    """CalibrationData tests."""

    data_as_dict: dict[float, float] = {0.0: 5.0, 10.0: 15.0, 20.0: 25.0}
    data_as_list: list[tuple[float, float]] = [
        (0.0, 5.0),
        (10.0, 15.0),
        (20.0, 25.0),
    ]
    data_as_str: str = "\t0.0, 5.0\n\t10.0, 15.0\n\t20.0, 25.0"

    def test_01_direct_init(self) -> None:
        """Direct accss to __init__ should raise an exception."""
        self.assertRaises(RuntimeError, cdat, {})

    def test_02_create_empty(self) -> None:
        """Test CalibrationData.create_empty alt' init method."""
        _ = cdat.create_empty()

    def test_03_create_from_dict(self) -> None:
        """Test CalibrationData.create_from_dict alt' init method."""
        _ = cdat.create_from_dict(self.data_as_dict)

    def test_04_create_from_list(self) -> None:
        """Test CalibrationData.create_from_list alt' init method."""
        _ = cdat.create_from_list(self.data_as_list)

    def test_05_create_from_str(self) -> None:
        """Test CalibrationData.create_from_str alt' init method."""
        _ = cdat.create_from_str(self.data_as_str)

    def test_06_create_from_default(self) -> None:
        """Test CalibrationData.create_from_str alt' init method using Defaults."""
        _ = cdat.create_from_str(Defaults.calibrated_offsets)


class TestInterpolatedOffsets(unittest.TestCase):
    """InterpolatedOffsets tests."""

    def setUp(self) -> None:
        self._cd: cdat = cdat.create_from_str(Defaults.calibrated_offsets)
        self._offsets: intoffs = intoffs(self._cd)

    def test_01_temp_import(self) -> None:
        """Test calibration temperatures are correctly imported."""
        self.assertCountEqual(
            self._offsets._calibration_temps.tolist(), self._cd.temps_as_list()
        )

    def test_02_offset_import(self) -> None:
        """Test calibration offsetss are correctly imported."""
        self.assertCountEqual(
            self._offsets._calibration_offsets.tolist(), self._cd.offsets_as_list()
        )

    def test_03_linear_c_points(self) -> None:
        """Test linear method returns correct offsets for calibrated temperatures."""
        calculated_offsets_linear = self._offsets._interpolate_linear(
            self._offsets._calibration_temps
        )
        self.assertCountEqual(
            calculated_offsets_linear, self._offsets._calibration_offsets
        )

    def test_04_poly_c_points(self) -> None:
        """Test poly function method correct offsets for calibrated temperatures."""
        for a, b in zip(
            self._offsets._calibration_offsets,
            self._offsets._calibrated_curve(self._offsets._calibration_temps),
        ):
            # self.assertGreater(1-(a-b)**2,Defaults.min_r2)
            self.assertGreater(1 - abs(a - b), Defaults.min_r2)

    def test_05_plot_some_stuff(self) -> None:
        """Linear and polynomial interpolations plotted with callibration points."""
        t_min, t_max = self._offsets.get_temp_range()
        interpolation_temps = np.linspace(t_min, t_max, 50)
        interpolated_offsets_linear = self._offsets._interpolate_linear(
            interpolation_temps
        )
        interpolated_offsets_poly = self._offsets._calibrated_curve(interpolation_temps)
        mplt.figure(num=None, figsize=(6, 4), dpi=310, facecolor="w", edgecolor="k")
        mplt.plot(
            self._offsets._calibration_temps,
            self._offsets._calibration_offsets,
            "o",
            color="#88c999",
            label="Calibration points",
        )
        mplt.plot(
            interpolation_temps,
            interpolated_offsets_linear,
            linestyle="dotted",
            color="#c98899",
            label="Linear interpolation",
        )
        mplt.plot(
            interpolation_temps,
            interpolated_offsets_poly,
            linestyle="dashed",
            color="#9988c9",
            label="Polynomial interpolation",
        )
        mplt.show()


if __name__ == "__main__":
    unittest.main()
