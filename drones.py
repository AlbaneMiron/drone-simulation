"""Module describing the starting points of Drones."""

import numpy as np


STARTING_POINTS = {
    'Postes de commandement': np.genfromtxt('data/coords_pc.csv', delimiter=',', dtype=str),
    'Centres de secours': np.genfromtxt('data/coords_cs.csv', delimiter=',', dtype=str),
}
