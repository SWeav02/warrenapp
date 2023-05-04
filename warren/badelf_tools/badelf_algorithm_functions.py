#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 13:57:31 2023

@author: sweav
"""
import itertools
import math
from math import ceil
from math import prod as product

import numpy as np
from pymatgen.analysis.local_env import CrystalNN, VoronoiNN
from scipy.interpolate import RegularGridInterpolator
from scipy.signal import savgol_filter
from simmate.toolkit import Structure

##########################################################################
# This section defines functions that are used in the warren lab badelf
# algorithm
##########################################################################


def get_closest_neighbors(structure: Structure):
    """
    Function for getting the closest neighbors
    """
    c = CrystalNN(search_cutoff=5)
    closest_neighbors = {}
    for i in range(len(structure)):
        _, _, d = c.get_nn_data(structure, n=i)
        biggest = max(d)
        closest_neighbors[i] = d[biggest]
    return closest_neighbors


def get_voronoi_neighbors(structure: Structure):
    """
    Function for getting a list of all neibors to each atom based on voronoi
    partitions
    """
    # We use voronoi nearest neighbors because our algorithm will partition
    # based on a weighted voronoi. We need all possible nearby atoms that may
    # contribute
    return VoronoiNN().get_all_nn_info(structure=structure)


def get_lattice(partition_file: str):
    """
    This function gets several important things from the lattice defined in
    the partitioning file
    """
    lattice = {}
    lattice["coords"] = []
    lattice["num_atoms"] = 1000

    with open(partition_file) as f:
        for i, line in enumerate(f):
            if i == 2:
                lattice["a"] = [float(x) for x in line.split()]
            if i == 3:
                lattice["b"] = [float(x) for x in line.split()]
            if i == 4:
                lattice["c"] = [float(x) for x in line.split()]
            if i == 5:
                lattice["elements"] = line.split()
            if i == 6:
                lattice["num_atoms"] = sum([int(x) for x in line.split()])
                lattice["elements_num"] = [int(x) for x in line.split()]
            if 8 <= i < 8 + lattice["num_atoms"]:
                lattice["coords"].append([float(x) for x in line.split()])
            if i == 9 + lattice["num_atoms"]:
                lattice["grid_size"] = [int(x) for x in line.split()]
            if i == 10 + lattice["num_atoms"]:
                lattice["volume"] = np.dot(
                    np.cross(lattice["a"], lattice["b"]), lattice["c"]
                )
                lattice["lines"] = ceil(product(lattice["grid_size"]) / 10)
                break
    return lattice


def voxel_from_frac(site, lattice):
    """
    VASP voxel indices go from 1 to grid_size along each axis. (e.g., 1 to 70)
    Fractional coordinates go from 0 to 1 along each axis.

    Fractional coordinate (0,0,0) corresponds to the bottom left front corner
    of voxel (1,1,1).
    Fractional coordinate (1,1,1) cooresponds to the top right back corner
    of voxel (grid_size_a, grid_size_b, grid_size_c).

    This code maintains the VASP standards throughout.

    The quasi-exception is for grid interpolation.  For interpolation, a voxel
    should be identified based on its center rather than its corner.
    Thus, voxel (1,1,1) has a center at voxel coordinates (0.5,0.5,0.5) of
    at fractional coordinates ( (voxel_a/grid_size_a) - (0.5/grid_size_a) ),
    and so on for axes b and c.

    In addition, for the interpolation grid, I have to wrap around to the
    other side.  So the interpolation grid needs extra padding of 1 unit on
    each side. That allows the outer edges of the grid to have the correct
    values that transition smoothly when wrapping.
    """

    grid_size = lattice["grid_size"]
    frac = lattice["coords"][site]
    voxel_pos = [round(a * b + 1, 6) for a, b in zip(grid_size, frac)]
    # voxel positions go from 1 to (grid_size + 0.9999)
    return voxel_pos


def voxel_from_neigh(neigh, lattice):
    grid_size = lattice["grid_size"]
    frac = neigh["site"].frac_coords
    voxel_pos = [round(a * b + 1, 6) for a, b in zip(grid_size, frac)]
    # voxel positions go from 1 to (grid_size + 0.9999)
    return voxel_pos


def get_grid_axes(grid):
    a = np.linspace(0, grid.shape[0] + 1, grid.shape[0] + 2)
    b = np.linspace(0, grid.shape[1] + 1, grid.shape[1] + 2)
    c = np.linspace(0, grid.shape[2] + 1, grid.shape[2] + 2)
    return a, b, c


def get_line(site_pos, neigh_pos, grid):
    steps = 150
    slope = [b - a for a, b in zip(site_pos, neigh_pos)]
    slope_increment = [float(x) / steps for x in slope]

    # get a list of points along the connecting line
    position = site_pos
    line = [position]
    for i in range(steps):
        # move position by slope_increment
        position = [float(a + b) for a, b in zip(position, slope_increment)]

        # Wrap values back into cell
        # We must do (a-1) to shift the voxel index (1 to grid_max+1) onto a
        # normal grid, (0 to grid_max), then do the wrapping function (%), then
        # shift back onto the VASP voxel index.
        position = [
            round(float(((a - 1) % b) + 1), 6) for a, b in zip(position, grid.shape)
        ]

        line.append(position)

    # pad the grid with 1 voxel by wrapping the value from the opposite side.
    padded = np.pad(grid, 1, mode="wrap")

    # interpolate grid to find values that lie between voxels
    a, b, c = get_grid_axes(grid)
    fn = RegularGridInterpolator((a, b, c), padded)

    # get a list of the ELF values along the line
    values = []

    for pos in line:
        value = float(fn(pos))
        values.append(value)
    return values


def local_min(line):
    # minima function gives all local minima along the line
    minima = [
        [i, y]
        for i, y in enumerate(line)
        if ((i == 0) or (line[i - 1] >= y))
        and ((i == len(line) - 1) or (y < line[i + 1]))
    ]

    # then we grab the local minima closest to the midpoint of the line
    midpoint = len(line) / 2
    differences = []
    for pos, val in minima:
        diff = abs(pos - midpoint)
        differences.append(diff)
    min_pos = differences.index(min(differences))
    global_min_pos = minima[min_pos]

    # return the position of the minimum as a fraction between 0 and 1
    # we also return the actual value of the elf at the minimum
    global_min_pos[0] /= len(line)
    return global_min_pos


def get_position_from_min(minimum, site_pos, neigh_pos):
    frac_pos = minimum[0]
    difference = [b - a for a, b in zip(site_pos, neigh_pos)]
    min_pos = [x * frac_pos for x in difference]
    min_pos = [round(a + b, 6) for a, b in zip(min_pos, site_pos)]
    return min_pos


def get_real_from_vox(voxel_position: list, lattice: dict):
    """
    We need to turn voxel_position this into a real space position.
    First, to get fractional positions, we follow the VASP notation and
    subtract 1 from pos_vox, then divide by the grid_size.
    The rest is just standard geometry to get the x,y,z real-space positions.
    """
    size = lattice["grid_size"]
    fa, fb, fc = [(a - 1) / b for a, b in zip(voxel_position, size)]
    a, b, c = lattice["a"], lattice["b"], lattice["c"]
    x = fa * a[0] + fb * b[0] + fc * c[0]
    y = fa * a[1] + fb * b[1] + fc * c[1]
    z = fa * a[2] + fb * b[2] + fc * c[2]
    coords = [x, y, z]
    return coords


def get_frac_from_vox(voxel_position: list, lattice: dict):
    """
    Function that takes in a voxel position and returns the fractional
    coordinates.
    """
    size = lattice["grid_size"]
    fa, fb, fc = [(a - 1) / b for a, b in zip(voxel_position, size)]
    coords = [fa, fb, fc]
    return coords


def get_real_from_frac(frac_pos, lattice):
    """
    Function that takes in fractional coordinates and returns real coordinates
    """
    fa, fb, fc = frac_pos[0], frac_pos[1], frac_pos[2]
    a, b, c = lattice["a"], lattice["b"], lattice["c"]
    x = fa * a[0] + fb * b[0] + fc * c[0]
    y = fa * a[1] + fb * b[1] + fc * c[1]
    z = fa * a[2] + fb * b[2] + fc * c[2]
    coords = [x, y, z]
    return coords


def get_normal_vector(site_pos, neigh_pos, lattice):
    real_site_pos = get_real_from_vox(site_pos, lattice)
    real_neigh_pos = get_real_from_vox(neigh_pos, lattice)
    """
    The equation of a plane passing through (x1,y1,z1) with normal vector
    [a,b,c] is:
        a(x-x1) + b(y-y1) + c(z-z1) = 0
    """
    normal_vector = [b - a for a, b in zip(real_site_pos, real_neigh_pos)]
    return normal_vector


def get_sign(point, normal_vector, site_pos, lattice):
    x, y, z = get_real_from_vox(site_pos, lattice)
    a, b, c = normal_vector
    x1, y1, z1 = point
    value_of_plane_equation = a * (x - x1) + b * (y - y1) + c * (z - z1)
    if value_of_plane_equation > 0:
        return "positive"
    else:
        return "negative"


def get_radius(point, site_pos, lattice):
    real_site_pos = get_real_from_vox(site_pos, lattice)
    radius = sum([(b - a) ** 2 for a, b in zip(real_site_pos, point)]) ** (0.5)
    return radius


# We need to load the partition into a 3D numpy array
def get_grid(
    partition_file: str,
    lattice: dict,
):
    """
    Function for loading in the partition into file into a 3D numpy array
    """
    try:
        grid = np.loadtxt(
            partition_file,
            skiprows=10 + lattice["num_atoms"],
            max_rows=lattice["lines"],
        ).ravel()
    except:
        grid1 = np.loadtxt(
            partition_file,
            skiprows=10 + lattice["num_atoms"],
            max_rows=lattice["lines"] - 1,
        ).ravel()
        grid2 = np.loadtxt(
            partition_file,
            skiprows=10 + lattice["num_atoms"] + lattice["lines"] - 1,
            max_rows=1,
        ).ravel()
        grid = np.concatenate((grid1, grid2))

    grid = grid.ravel().reshape(lattice["grid_size"], order="F")
    return grid


def get_matching_site(pos, results, lattice):
    """
    Function for determining the site that a voxel should be applied to.
    """
    for site, neighs in results.items():
        matched = True
        for neigh, values in neighs.items():
            try:
                point = values["real_min_point"]
            except:
                breakpoint()
            normal_vector = values["normal_vector"]
            expected_sign = values["sign"]

            # use plane equation to find sign
            # if it doesn't, move to next site.
            sign = get_sign(point, normal_vector, pos, lattice)

            if sign != expected_sign:
                matched = False
                break
        if matched == True:
            return site
    return


def get_electride_sites(
    lattice: dict,
):
    """
    Function for getting the number of sites that are electrides
    """
    # Create list for electride site index
    electride_sites = []
    # Create integer values for the number of sites before the electride and
    # the number of electrides
    sites_before_electride = int(0)
    sites_of_electride = int()
    # When creating dummy atoms in electrides we usually use He because there
    # are so few materials that contain it.
    if "He" in lattice["elements"]:
        # iterates over element labels and finds the index for electride sites
        for i, element in enumerate(lattice["elements"]):
            if element == "He":
                # iterates over the number of each element. Since the electride
                # is always added at the end, we can just add up the number of
                # atoms before this point
                for j in range(i):
                    sites_before_electride += lattice["elements_num"][j]
            # We find the total number of electride sites
            sites_of_electride = lattice["elements_num"][i]
    for i in range(sites_of_electride):
        electride_sites.append(sites_before_electride + i)
    return electride_sites


def get_charge(
    charge_file: str,
    lattice: dict,
):
    """
    Loads the charge density into a 3D numpy array
    """
    try:
        chg1 = np.loadtxt(
            charge_file,
            skiprows=10 + lattice["num_atoms"],
            max_rows=lattice["lines"] * 2 - 1,
        ).ravel()
        chg2 = np.loadtxt(
            charge_file,
            skiprows=10 + lattice["num_atoms"] + lattice["lines"] * 2 - 1,
            max_rows=1,
        ).ravel()
        chg = np.concatenate((chg1, chg2))
    except:
        chg1 = np.loadtxt(
            charge_file,
            skiprows=10 + lattice["num_atoms"],
            max_rows=lattice["lines"] * 2 - 2,
        ).ravel()
        chg2 = np.loadtxt(
            charge_file,
            skiprows=10 + lattice["num_atoms"] + lattice["lines"] * 2 - 2,
            max_rows=1,
        ).ravel()
        chg = np.concatenate((chg1, chg2))

    chg = chg.reshape(lattice["grid_size"], order="F")
    return chg


def get_site_neighbor_results(neigh: list, lattice: dict, site_pos: dict, grid):
    """
    Function for getting the line, plane, and other information between a site
    and neighbor
    """
    # create dictionary index for each neighbor
    site_neigh_dict = {}
    neigh_pos = voxel_from_neigh(neigh, lattice)

    # get cartesian space coordinate of site and neighbor
    real_site_point = get_real_from_vox(site_pos, lattice)
    real_neigh_point = get_real_from_vox(neigh_pos, lattice)

    # we need a straight line between these two points.  get list of all ELF values
    elf_line = get_line(site_pos, neigh_pos, grid)
    # smooth the line
    smoothed_line = savgol_filter(elf_line, window_length=15, polyorder=3)

    # find the minimum position and value along the elf_line
    # the first element is the fractional position, measured from site_pos
    min_elf = local_min(smoothed_line)

    # convert the minimum in the ELF back into a position in the voxel grid
    min_pos_vox = get_position_from_min(min_elf, site_pos, neigh_pos)

    # a point and normal vector describe a plane
    # a(x-x1) + b(y-y1) + c(z-z1) = 0
    # a,b,c is the normal vecotr, x1,y1,z1 is the point

    # convert this voxel grid_pos back into the real_space
    min_pos_real = get_real_from_vox(min_pos_vox, lattice)
    # get the plane perpendicular to the position.
    normal_vector = get_normal_vector(site_pos, neigh_pos, lattice)

    """I also want to know which side of the plane is "inside"
    I substitute the site_pos into the plane equation.
    I record if this value is positive or negative."""
    sign = get_sign(min_pos_real, normal_vector, site_pos, lattice)

    # it is also helpful to know the distance of the minimum from the site
    radius = get_radius(min_pos_real, site_pos, lattice)

    site_neigh_dict["vox_site"] = site_pos
    site_neigh_dict["vox_neigh"] = neigh_pos
    site_neigh_dict["value_elf"] = min_elf[1]
    site_neigh_dict["pos_elf_frac"] = min_elf[0]
    site_neigh_dict["vox_min_point"] = min_pos_vox
    site_neigh_dict["real_min_point"] = min_pos_real
    site_neigh_dict["normal_vector"] = normal_vector
    site_neigh_dict["sign"] = sign
    site_neigh_dict["radius"] = radius
    site_neigh_dict["neigh"] = neigh
    site_neigh_dict["elf_line"] = smoothed_line
    site_neigh_dict["elf_line_raw"] = elf_line
    # adding some results for testing
    site_neigh_dict["neigh_index"] = neigh["site_index"]
    site_neigh_dict["neigh_distance"] = math.dist(real_site_point, real_neigh_point)

    return site_neigh_dict


def get_partitioning(
    voronoi_neighbors: dict,
    lattice: dict,
    electride_sites: list,
    grid
    # this needs more parameters for the functions it uses.
):
    """
    Function for partitioning the grid. Looks along a 1D line between each
    site and its closest and second closest neighbors. Finds the minimum
    along that line and creates a perpindicular plane. Returns a nested dictionary
    that goes: dict of sites > dict of each site/neighbor pair > dict of line
    and plane data.
    """
    results = {}
    # iterate through each site in the structure
    for site, neighs in enumerate(voronoi_neighbors):
        # create key for each site
        if site not in electride_sites:
            results[site] = {}

            # get voxel position from fractional site
            site_pos = voxel_from_frac(site, lattice)
            # iterate through each neighbor to the site
            for i, neigh in enumerate(neighs):
                if neigh["site_index"] not in electride_sites:
                    results[site][i] = get_site_neighbor_results(
                        neigh, lattice, site_pos, grid
                    )
    return results


def get_voxels_site(
    x,
    y,
    z,
    site,
    results,
    permutations,
    lattice,
    electride_sites,
):
    if site not in electride_sites:
        for t, u, v in permutations:
            new_pos = [x + t, y + u, z + v]
            site: int = get_matching_site(new_pos, results, lattice)
            # site returns none if no match, otherwise gives a number
            # The site can't return as an electride site as we don't include
            # electride sites in the partitioning results
            if site is not None:
                break
    return site


# we need to define a secondary function that runs the above voxel search
# across a pandas dataframe. This will allow us to run the function across
# the dask partitioned dataframe we make later
def get_voxels_site_dask(
    df, results: dict, permutations: list, lattice: dict, electride_sites: list
):
    return df.apply(
        lambda x: get_voxels_site(
            x["x"],
            x["y"],
            x["z"],
            x["site"],
            results,
            permutations,
            lattice,
            electride_sites,
        ),
        axis=1,
    )


def get_voxels_site_garbage(
    x,
    y,
    z,
    pdf,
    lattice: dict,
    electride_sites: list,
    results: dict,
):
    # create dictionary for counting number of sites and for the fraction
    # of sites
    site_count = {}
    site_frac = {}
    for site in results.keys():
        site_count[site] = int(0)

    # look at all neighbors and tally which site they belong to.
    for t, u, v in itertools.product([-1, 0, 1], [-1, 0, 1], [-1, 0, 1]):
        new_idx = [x - 1 + t, y - 1 + u, z - 1 + v]

        # wrap around for voxels on edge of cell
        new_idx = [a % b for a, b in zip(new_idx, lattice["grid_size"])]

        # get site from the sites that have already been found using the sites
        # index. This is much faster than searching by values. To get the index
        # we can utilize the fact that an increase in z will increase the index
        # by 1, an increase in y will increase the index by (range of z),
        # and an increase in x will increase the index by (range of z)*(range of y)
        zrange = lattice["grid_size"][2]
        yrange = lattice["grid_size"][1]
        index = int((new_idx[0]) * zrange * yrange + (new_idx[1]) * zrange + new_idx[2])
        site = pdf["site"].iloc[index]
        # If site exists and isn't an electride site, add to the count. This
        # will prevent the nearby sites from ever being mostly electride.
        if site is not None and site not in electride_sites:
            site_count[site] += 1
    # ensure that some sites were found
    if sum(site_count.values()) != 0:
        # get the fraction of each site. This will allow us to split the
        # charge of the voxel more evenly
        for site_index in site_count:
            site_frac[site_index] = site_count[site_index] / sum(site_count.values())
    return site_frac


def get_voxels_site_garbage_dask(
    df,
    pdf,
    results: dict,
    lattice: dict,
    electride_sites: list,
):
    return df.apply(
        lambda x: get_voxels_site_garbage(
            x["x"],
            x["y"],
            x["z"],
            pdf=pdf,
            lattice=lattice,
            electride_sites=electride_sites,
            results=results,
        ),
        axis=1,
    )
