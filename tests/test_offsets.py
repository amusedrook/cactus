#!/usr/bin/env python3

"""Tests for CalibrationData and InterpolatedOffseta."""

import unittest

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

    def test_direct_init(self) -> None:
        """Direct accss to __init__ should raise an exception."""
        self.assertRaises(RuntimeError, cdat, {})

    def test_create_empty(self) -> None:
        """Test CalibrationData.create_empty alt' init method."""
        _ = cdat.create_empty()

    def test_create_from_dict(self) -> None:
        """Test CalibrationData.create_from_dict alt' init method."""
        _ = cdat.create_from_dict(self.data_as_dict)

    def test_create_from_list(self) -> None:
        """Test CalibrationData.create_from_list alt' init method."""
        _ = cdat.create_from_list(self.data_as_list)

    def test_create_from_str(self) -> None:
        """Test CalibrationData.create_from_str alt' init method."""
        _ = cdat.create_from_str(self.data_as_str)

    def test_create_from_default(self) -> None:
        """Test CalibrationData.create_from_str alt' init method using Defaults."""
        _ = cdat.create_from_str(Defaults.calibrated_offsets)


class TestInterpolatedOffsets(unittest.TestCase):
    """InterpolatedOffsets tests."""

    test_default_cd: cdat
    test_offsets: intoffs

    def test_init(self) -> None:
        """Test init of InterpolatedOffsets using CalibrationData created from Defaults."""
        self.test_default_cd = cdat.create_from_str(Defaults.calibrated_offsets)
        self.test_offsets = intoffs(self.test_default_cd)


if __name__ == "__main__":
    unittest.main()
