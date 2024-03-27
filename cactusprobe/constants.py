"""Constants and error-messages for the cactusprobe package."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Defaults:
    """Default configuration(s) for cactusprobe package classes."""

    min_calibration_points: int = 3
    min_r2: float = 0.998
    min_poly_terms: int = 2
    max_poly_terms: int = 5
    calibrated_offsets: str = (
        "    30, 0.000\n"
        + "    40, -0.015\n"
        + "    50, -0.033\n"
        + "    60, -0.056\n"
        + "    70, -0.081\n"
        + "    80, -0.111\n"
    )


@dataclass(frozen=True)
class ErrorMessages:
    """Error message strings - for brevity."""

    use_alt_init: str = (
        "\nCalibrationData __init__ method used directly."
        + "\n\tPlease consider using one of the alternative init methods "
        + "\n\trather than accessing the classes __init__ method directly:"
        + "\n\t- create_empty()"
        + "\n\t- create_from_dict()"
        + "\n\t- create_from_list()"
        + "\n\t- create_from_str()"
        + "\n\t"
        + "\n\tPass 'direct_init = False' to the class constructor "
        + "\n\tif you want to disable this error and are willing to "
        + "\n\tcomplete most of the checking yourself."
    )
    duplicate_calibration_point: str = (
        "\nDuplicate calibration-point detected."
        + "\n\tPlease check your configuration and ensure all temperature points are unique."
    )
    wrong_data_type: str = (
        "\nCalibration data must be in the form of ints or floats."
        + "\n\tPlease check your configuration file to ensure all calibration data is "
        + "\n\tin the form of numerical temperature/distance-offset pairs."
    )
    too_few_points: str = (
        "\nInsufficent calibration points."
        + "\n\tCactusProbe calibration requires a minimum of "
        + f"'{Defaults.min_calibration_points}' points."
    )
    requires_dict: str = (
        "\nCactusCalibrationData.create_from_dict() method expects data as a dict."
    )
    requires_list_of_tuples: str = (
        "\nCactusCalibrationData.create_from_list() "
        + "method expects data as a list of tuples."
    )
    requires_string: str = (
        "\nCactusCalibrationData.create_from_str() method expects data as a string."
    )
    requires_data_pair: str = (
        "\nCalibration data must be in the form of temperature/offset pairs"
        + "Please ensure your calibration data is in the format 'temp', 'offset'."
    )
