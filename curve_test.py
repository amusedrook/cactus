#!/usr/bin/env python3

"""Shut up Pylint"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# https://github.com/Klipper3d/klipper/blob/048baeb5b6e0664c2b575e161d3c3cbda01ecc54/klippy/extras/pinda2.py
BLOB_01 = (
    "    0, 0.00\n"
    + "    30, -0.00\n"
    + "    35, -0.05\n"
    + "    40, -0.15\n"
    + "    45, -0.4\n"
    + "    50, -0.8\n"
    + "    55, -1.7\n"
    + "    60, -2.6\n"
    + "    100, -2.00\n"
)

# Same as BLOB_01 but slightly mangled
# Two out of order, one of which is duplicate
BLOB_02 = (
    "    21, 0.00\n"
    + "    40, -0.15\n"
    + "    30, -0.00\n"
    + "    35, -0.05\n"
    + "    40, -0.15\n"
    + "    45, -0.4\n"
    + "    55, -1.7\n"
    + "    60, -2.6\n"
    + "    50, -0.8\n"
    + "    100, -2.00\n"
)

# Do not use
BLOB_03 = (
    "    21, 0.00\n"
    + "    40, 0.15\n"
    + "    30, 0.00\n"
    + "    35, 0.05\n"
    + "    40, 0.15\n"
    + "    45, 0.4\n"
    + "    55, 1.7\n"
    + "    60, 2.6\n"
    + "    50, 0.8\n"
    + "    100, 2.00\n"
)

# As 02, but without crazy 100 degree point
BLOB_04 = (
    "    21, 0.00\n"
    + "    40, -0.15\n"
    + "    30, -0.00\n"
    + "    35, -0.05\n"
    + "    40, -0.15\n"
    + "    45, -0.4\n"
    + "    55, -1.7\n"
    + "    60, -2.6\n"
    + "    50, -0.8\n"
)

# As 04, but without extranious "0" offset point
BLOB_05 = (
    "    40, -0.15\n"
    + "    30, -0.00\n"
    + "    35, -0.05\n"
    + "    40, -0.15\n"
    + "    45, -0.4\n"
    + "    55, -1.7\n"
    + "    60, -2.6\n"
    + "    50, -0.8\n"
)


def func_poly1d(x, *p):
    """poly1d"""
    return np.poly1d(p)(x)


def func_a(x, a, b):
    """ax + b"""
    return a * np.power(x, 1) + b


def func_b(x, a, b, c):
    """ax^2 + bx + c"""
    return a * np.power(x, 2) + b * np.power(x, 1) + c


def func_c(x, a, b, c, d):
    """ax^3 + bx^2 + cx + d"""
    return a * np.power(x, 3) + b * np.power(x, 2) + c * np.power(x, 1) + d


def func_d(x, a, b, c, d, e):
    """ax^4 + bx^3 + cx^2 + dx + e"""
    # return a * x**4 + b * x**3 + c * x**2 + d * x + e
    return (
        a * np.power(x, 4)
        + b * np.power(x, 3)
        + c * np.power(x, 2)
        + d * np.power(x, 1)
        + e
    )


def func_e(x, a, b, c, d, e, f):
    """ax^5 + bx^4 + cx^3 + dx^2 + ex + f"""
    # return a * x**5 + b * x**4 + c * x**3 + d * x**2 + e * x + f
    return (
        a * np.power(x, 5)
        + b * np.power(x, 4)
        + c * np.power(x, 3)
        + d * np.power(x, 2)
        + e * np.power(x, 1)
        + f
    )


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
    # https://stackoverflow.com/questions/15191088/how-to-do-a-polynomial-fit-with-fixed-points
    sigma = np.ones(len(temps))
    sigma[[0]] = 0.01
    # params, _ = curve_fit(func_test, temps, offsets)
    # params, _ = curve_fit(func_test, temps, offsets, sigma=sigma)
    # params, _ = curve_fit(func_test, temps, offsets, (0, 0, 0), sigma=sigma)
    degrees = (0,) * 4
    params, _ = curve_fit(func_test, temps, offsets, degrees, sigma=sigma)
    temps_new = np.linspace(temps[0], temps[-1], 50)
    offsets_new = func_test(temps_new, *params)
    plt.plot(temps_new, offsets_new, "b-", label="mike")
    print(params)
    # https://stackoverflow.com/questions/19189362/getting-the-r-squared-value-using-curve-fit
    residuals = offsets - func_test(temps, *params)
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((offsets - np.mean(offsets)) ** 2)
    r_squared = 1 - (ss_res / ss_tot)
    print(r_squared)
    plt.show()


process_blob(BLOB_05)
