"""Module describing the starting points of Drones."""

import numpy as np


STARTING_POINTS = {
    'PC le plus proche': np.genfromtxt('data/coords_pc.csv', delimiter=',', dtype=str),
    'CS le plus proche': np.genfromtxt('data/coords_cs.csv', delimiter=',', dtype=str),
}
