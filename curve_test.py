#!/usr/bin/env python3

"""Shut up Pylint"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Minimum and maximum polynomial terms
# "2" is linear, anything more than "MAX" should be interpolated pont-by-point
P_DEG_MIN = 2
P_DEG_MAX = 4

# https://github.com/Klipper3d/klipper/blob/048baeb5b6e0664c2b575e161d3c3cbda01ecc54/klippy/extras/pinda2.py
# Minus a suspicious 100°C measurement
BLOB_01 = (
    "    0, 0.00\n"
    + "    30, -0.00\n"
    + "    35, -0.05\n"
    + "    40, -0.15\n"
    + "    45, -0.4\n"
    + "    50, -0.8\n"
    + "    55, -1.7\n"
    + "    60, -2.6\n"
)

# As BLOB_01, but without the 0°C point
# Effectivly normalised to 30°C
BLOB_02 = (
    "    30, -0.00\n"
    + "    35, -0.05\n"
    + "    40, -0.15\n"
    + "    45, -0.4\n"
    + "    50, -0.8\n"
    + "    55, -1.7\n"
    + "    60, -2.6\n"
)

# Real-world data from genuine P.I.N.D.A V2 minus the "interpolated"
# values (everything over 50°C)
# https://marlinfw.org/docs/features/probe_temp_compensation.html
BLOB_03 = (
    "    30,  0.000\n"
    + "    35, -0.005\n"
    + "    40, -0.027\n"
    + "    45, -0.046\n"
    + "    50, -0.057\n"
)

# Supposedly an ideal response-curve
# https://forum.prusa3d.com/forum/
# original-prusa-i3-mk3s-mk3-hardware-firmware-and-software-help/
# pinda-v2-temp-compensation-graph/
BLOB_04 = "    10, 0.0\n" + "    70, -0.1\n" + "    100, -0.2\n"

# Following data is generated from a three-term polynomial describing
# the above "ideal" response
# a*x^2+b*x+c
# a: -1.85185185e-05
# b: -1.85185185e-04
# c: 3.70370370e-03
#
# In theory a three-term polynomial curve matched to the following datasets
# will have identical 'a' and 'b' terms, but different 'c'.
# They do not.
# Very close, so I think that's ok.

# Ideal response normalised to room-temperature (21°C)
BLOB_11 = (
    "    21, 0.000\n"
    + "    25, -0.004\n"
    + "    35, -0.017\n"
    + "    45, -0.034\n"
    + "    55, -0.054\n"
    + "    65, -0.078\n"
    + "    75, -0.106\n"
)

# Ideal response normalised to 25°C
BLOB_12 = (
    "    25, 0.000\n"
    + "    35, -0.013\n"
    + "    45, -0.030\n"
    + "    55, -0.050\n"
    + "    65, -0.074\n"
    + "    75, -0.102\n"
)

# Ideal response normalised to 30°C
BLOB_13 = (
    "    30, 0.000\n"
    + "    40, -0.015\n"
    + "    50, -0.033\n"
    + "    60, -0.056\n"
    + "    70, -0.081\n"
    + "    80, -0.111\n"
)

# Ideal response normalised to 35°C
BLOB_14 = (
    "    35, 0.000\n"
    + "    45, -0.017\n"
    + "    55, -0.037\n"
    + "    65, -0.061\n"
    + "    75, -0.089\n"
    + "    85, -0.120\n"
)


def func_poly1d(x, *p):
    """poly1d"""
    return np.poly1d(p)(x)


# The following "func_X" functions are redundant. Replaced with above.
# def func_a(x, a, b):
#    """a*x + b"""
#    return a * np.power(x, 1) + b
#
#
# def func_b(x, a, b, c):
#    """a*x^2 + b*x + c"""
#    return a * np.power(x, 2) + b * np.power(x, 1) + c
#
#
# def func_c(x, a, b, c, d):
#    """a*x^3 + b*x^2 + c*x + d"""
#    return a * np.power(x, 3) + b * np.power(x, 2) + c * np.power(x, 1) + d
#
#
# def func_d(x, a, b, c, d, e):
#    """a*x^4 + b*x^3 + c*x^2 + d*x + e"""
#    return (
#        a * np.power(x, 4)
#        + b * np.power(x, 3)
#        + c * np.power(x, 2)
#        + d * np.power(x, 1)
#        + e
#    )
#
#
# def func_e(x, a, b, c, d, e, f):
#    """a*x^5 + b*x^4 + c*x^3 + d*x^2 + e*x + f"""
#    return (
#        a * np.power(x, 5)
#        + b * np.power(x, 4)
#        + c * np.power(x, 3)
#        + d * np.power(x, 2)
#        + e * np.power(x, 1)
#        + f
#    )


def process_blob(blob):
    """Extract data-points from string blob"""
    print("Processing blob:")
    print(blob)
    print("----------------")
    blob_rows = [row.split(",", 1) for row in blob.split("\n") if row.strip()]
    blob_lists = [(float(r[0].strip()), float(r[1].strip())) for r in blob_rows]
    print("Unsorted list:")
    print(blob_lists)
    print("----------------")
    print("Sorted list:")
    blob_lists.sort(key=lambda tup: tup[0])
    print(blob_lists)
    print("----------------")
    print("Seaching for duplicates:")
    blob_filtered = []
    temps = []
    offsets = []
    for temp, offset in blob_lists:
        if temp in temps:
            print(f"Error: Duplicate temperature entry: {temp}, {offset}")
        else:
            temps.append(temp)
            offsets.append(offset)
            blob_filtered.append([temp, offset])
    print("----------------")
    print(blob_filtered)
    print("----------------")
    print("Temps:")
    print(temps)
    print("----------------")
    print("offsets:")
    print(offsets)
    print("----------------")
    func_test = func_poly1d
    plt.plot(temps, offsets, "o", label="data")
    # Give more weight to the first point (need it fixed-ish)
    # https://stackoverflow.com/questions/15191088/
    # how-to-do-a-polynomial-fit-with-fixed-points
    sigma = np.ones(len(temps))
    sigma[[0]] = 0.01
    # params, _ = curve_fit(func_test, temps, offsets)
    # params, _ = curve_fit(func_test, temps, offsets, sigma=sigma)
    # params, _ = curve_fit(func_test, temps, offsets, (0, 0, 0), sigma=sigma)
    degrees = (0,) * 3
    # This gets W0632 - unbalanced-tuple-unpacking
    # params, _ = curve_fit(func_test, temps, offsets, degrees, sigma=sigma)
    # This gets W0612 - Unused variable 'remaining_vals'
    # params, *remaining_vals = curve_fit(func_test, temps, offsets, degrees, sigma=sigma)
    # This is acceptible, but less than clear
    # params = curve_fit(func_test, temps, offsets, degrees, sigma=sigma)[0]
    # ...but is this really any better? Pylint says 'yes' [shrugs]
    cf_return = curve_fit(func_test, temps, offsets, degrees, sigma=sigma)
    params = cf_return[0]
    temps_new = np.linspace(temps[0], temps[-1], 50)
    offsets_new = func_test(temps_new, *params)
    plt.plot(temps_new, offsets_new, "b-", label="mike")
    print(params)
    # https://stackoverflow.com/questions/19189362/
    # getting-the-r-squared-value-using-curve-fit
    residuals = offsets - func_test(temps, *params)
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((offsets - np.mean(offsets)) ** 2)
    r_squared = 1 - (ss_res / ss_tot)
    print(r_squared)
    plt.show()


process_blob(BLOB_04)
