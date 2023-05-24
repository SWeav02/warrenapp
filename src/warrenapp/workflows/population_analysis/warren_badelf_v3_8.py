#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 21:43:11 2023

@author: WarrenLab
"""

import itertools
import math
import time
import warnings
from pathlib import Path

import dask.dataframe as dd
import numpy as np
import pandas
import pandas as pd
import psutil
from dask.distributed import Client, LocalCluster
from simmate.engine import Workflow
from simmate.toolkit import Structure

from warrenapp.badelf_tools.badelf_algorithm_functions_1 import (
    get_charge,
    get_electride_sites,
    get_grid,
    get_lattice,
    get_max_voxel_dist,
    get_number_of_partitions,
    get_partitioning,
    get_real_from_frac,
    get_voronoi_neighbors,
    get_voxels_site_dask,
    get_voxels_site_garbage,
    get_voxels_site_garbage_dask,
)
from warrenapp.models import WarrenPopulationAnalysis

###############################################################################
# Now that we have functions defined, it's time to define the main workflow
###############################################################################


class PopulationAnalysis__Warren__BadelfIonicRadii(Workflow):
    description_doc_short = "BadELF based on ionic radii"

    database_table = WarrenPopulationAnalysis

    @classmethod
    def run_config(
        cls,
        directory: Path = None,
        structure_file: str = "POSCAR",
        partition_file: str = "ELFCAR",
        empty_partition_file: str = "ELFCAR_empty",
        charge_file: str = "CHGCAR",
        **kwargs,
    ):
        t0 = time.time()
        structure = Structure.from_file(directory / structure_file)
        # get dictionary of sites and closest neighbors. This always throws
        # the same warning about He's EN so we suppress that here
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            voronoi_neighbors = get_voronoi_neighbors(structure=structure)

        # read in lattice with and without electride sites
        lattice = get_lattice(partition_file=directory / partition_file)
        try:
            empty_lattice = get_lattice(directory / empty_partition_file)
        except:
            print("No ELFCAR_empty found. Continuing with no electride sites.")
            empty_lattice = lattice

        # We need to assign electride voxels based on the traditional Bader
        # method, then assign the remaining voxels in the hard-sphere division way.
        # get the indices for electride sites
        electride_sites = get_electride_sites(empty_lattice)

        # we'll need the volume of each voxel later to calculate the atomic
        # volumes for our output file
        voxel_volume = lattice["volume"] / np.prod(lattice["grid_size"])

        # read in partition grid
        grid = get_grid(partition_file=directory / partition_file, lattice=lattice)
        # The algorithm now looks at each site-neighbor pair.
        # Along the bond between the pair, we look at ELF values.
        # We find the position of the minimum ELF value.
        # We then find the plane that passes through this minimum and
        # that is perpendicular to the bond between the pair.

        results = get_partitioning(
            voronoi_neighbors=voronoi_neighbors,
            lattice=lattice,
            electride_sites=electride_sites,
            grid=grid,
        )
        # We will also need to find the maximum distance the center of a voxel
        # can be from a plane and still be intersected by it. That way we can
        # handle voxels near partitioning planes with more accuracy
        max_voxel_dist = get_max_voxel_dist(lattice)

        # Now that we've identified the planes that divide the ELF, we now need to
        # actually apply that knowledge, voxel by voxel.

        # For each neighbor of a site, we have a bounding plane.  Only those voxels
        # that are within all bounding planes of a site belong to that site.

        # I go across the elf grid voxel-by-voxel.
        # For each voxel, I get its real space position.
        # I then test if it is within the planes in each site.
        # Only when it matches all the planes do I record it as belonging to a site.

        # !!!!!!!!
        # In this iteration, I'm going to try and treat voxels that may intersect
        # 1 or more planes more rigorously
        #!!!!!!!!!

        # The output, then, is a list of voxels (x,y,z position) that belong
        # to each site.

        # Then, this list of voxels is applied to the total charge density to
        # add up all the incremental charge.

        # create dictionaries for each site's coordinates, charge, min-distance
        # to the surface, and total volume. These will be used to create a
        # summary folder later

        results_coords = {}
        results_charge = {}
        results_min_dist = {}
        results_volume = {}
        # fill site coords dictionary
        for site, site_coord in enumerate(empty_lattice["coords"]):
            results_coords[site] = get_real_from_frac(
                frac_pos=site_coord, lattice=lattice
            )
            # fill min_dist dictionary using the smallest partitioning radius
            if site not in electride_sites:
                results_min_dist[site] = results[site][0]["radius"]
            elif site in electride_sites:
                results_min_dist[site] = 0
            # create empty dictionary for other results that haven't been found yet
            results_charge[site] = float(0)
            results_volume[site] = float(0)

        # read in charge density file
        # make sure this file has same number of atoms as elfcar
        chg = get_charge(
            charge_file=directory / charge_file,
            lattice=lattice,
        )

        # We need to get the charge on each electride site and get the coordinates that
        # belong to the electride. We first get a dataframe that indexes all of the
        # coordinates. We'll remove the electride coordinates from this later.

        a, b, c = lattice["grid_size"]

        # Create lists that contain the coordinates of each voxel and their charges

        #!!!!
        # Why did I do this instead of keeping everything in an array so that
        # indexing is easier?
        voxel_coords = [idx for idx in itertools.product(range(a), range(b), range(c))]
        voxel_charges = [float(chg[idx[0], idx[1], idx[2]]) for idx in voxel_coords]

        # Create a dataframe that has each coordinate index and the charge as columns
        # Later we'll remove voxels that belong to electrides from this dataframe
        all_charge_coords = pd.DataFrame(voxel_coords, columns=["x", "y", "z"]).add(1)
        all_charge_coords["chg"] = voxel_charges
        all_charge_coords["site"] = None
        # Now iterate through the charge density coordinates for each electride
        for electride in electride_sites:
            # Pull in electride charge density from bader output file (BvAt####.dat format)
            electride_chg = get_charge(
                charge_file=directory / f"BvAt{str(electride+1).zfill(4)}.dat",
                lattice=empty_lattice,
            )
            electride_indices = []
            # For each voxel, check if the electride charge density file has any
            # charge. If it does add its index to the electride_indices list
            for count, idx in enumerate(voxel_coords):
                charge_density = float(electride_chg[idx[0], idx[1], idx[2]])
                if charge_density != 0:
                    # get indices of electride sites
                    electride_indices.append(count)
                    # results_charge[electride] += charge_density
            # add electride site to "site" column for every electride indice
            all_charge_coords.iloc[electride_indices, 4] = electride

        # get the permuations of possible shifts for each voxel.
        permutations = [
            (t, u, v)
            for t, u, v in itertools.product([-a, 0, a], [-b, 0, b], [-c, 0, c])
        ]
        # sort permutations. There may be a better way of sorting them. I
        # noticed that generally the correct site was found most commonly
        # for the original site and generally was found at permutations that
        # were either all negative/0 or positive/0
        permutations_sorted = []
        for item in permutations:
            if all(val <= 0 for val in item):
                permutations_sorted.append(item)
            elif all(val >= 0 for val in item):
                permutations_sorted.append(item)
        for item in permutations:
            if item not in permutations_sorted:
                permutations_sorted.append(item)
        permutations_sorted.insert(0, permutations_sorted.pop(7))

        # We want to open a local dask cluster with appropriate settings. I've
        # done some light testing and found that 1 thread per worker, 2GB mem,
        # and partition sizes of 128,000 voxel coords seems reasonable.
        # For smaller systems (<128,000) it was still benefitial to parallelize
        # though less efficient

        # Get the total number of cpus available and memory available
        cpu_count = math.floor(len(psutil.Process().cpu_affinity()) / 2)
        memory_gb = psutil.virtual_memory()[1] / (1e9)
        # Each worker needs at least 2GB of memory. We select either the number
        # of workers that could have at least this much memory or the number
        # of cores/threads, whichever is smaller
        nworkers = min(math.floor(memory_gb / 2), cpu_count)
        with LocalCluster(
            n_workers=nworkers,
            threads_per_worker=2,
            memory_limit="auto",
            processes=True,
        ) as cluster, Client(cluster) as client:
            # put list of indices in dask dataframe. Partition with the same
            # number of partitions as workers
            npartitions = get_number_of_partitions(
                df=all_charge_coords, nworkers=nworkers
            )
            ddf = dd.from_pandas(
                all_charge_coords,
                npartitions=npartitions,
            )

            # site search for all voxel positions.
            ddf["site"] = ddf.map_partitions(
                get_voxels_site_dask,
                results=results,
                permutations=permutations,
                lattice=lattice,
                electride_sites=electride_sites,
                max_distance=max_voxel_dist,
            )
            # run site search and save as pandas dataframe
            pdf = ddf.compute()

            # Group the results by site. Sum the charges and count the total number
            # of voxels for each site. Apply charges and volumes to dictionaries.
        pdf_grouped = pdf.groupby(by="site")
        pdf_grouped_charge = pdf_grouped["chg"].sum()
        pdf_grouped_voxels = pdf_grouped["site"].size()
        for site in results_charge:
            results_charge[site] = pdf_grouped_charge[site]
            results_volume[site] = pdf_grouped_voxels[site] * voxel_volume
        # some of the voxels will not return a site. For these we need to check the
        # nearby voxels to see which site is the most common and assign them to that
        # site. To do this we essentially repeat the previous several steps but with
        # the new site searching method.

        # find where the site search returned None
        garbage_index = np.where(pdf["site"].isnull())
        # We need to convert Nan in pdf to None type objects for when we are
        # iterating through them later
        pdf = pdf.replace({np.nan: None})
        # create new pandas dataframe only containing voxels with no site
        garbage_pdf = pdf.iloc[garbage_index].drop(columns=["site"])
        # get a reasonable number of partitions for the garbage dataframe. This
        # takes slightly more memory than the regular index finder so we increase
        # the number of partition.

        # with LocalCluster(
        #     n_workers=nworkers,
        #     threads_per_worker=2,
        #     memory_limit="auto",
        #     processes=True,
        # ) as cluster, Client(cluster) as client:
        #     garbage_npartitions = get_number_of_partitions(
        #         df=garbage_pdf,
        #         nworkers=nworkers)

        # switch from pandas dataframe to partitioned dask dataframe
        # garbage_ddf = dd.from_pandas(
        #     garbage_pdf,
        #     npartitions=garbage_npartitions,
        # )
        # assign function to search for nearby voxels accross dask partitions
        # garbage_ddf["site"] = garbage_ddf.map_partitions(
        # garbage_ddf["sites"] = garbage_ddf.map_partitions(
        #     get_voxels_site_garbage_dask,
        #     pdf=pdf,
        #     lattice=lattice,
        #     electride_sites=electride_sites,
        #     results=results,
        # )

        garbage_pdf["sites"] = garbage_pdf.apply(
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
        # compute and return to pandas
        # garbage_pdf = garbage_ddf.compute()

        for row in garbage_pdf.iterrows():
            for site in row[1][4]:
                results_charge[site] += row[1][4][site] * row[1][3]
                results_volume[site] += row[1][4][site] * voxel_volume

        # divide charge by volume to get true charge
        # this is a vasp convention
        for site, charge in results_charge.items():
            results_charge[site] = charge / (a * b * c)
        total_charge = sum(results_charge.values())

        ###############################################################################
        # Save information into ACF.dat like file
        ###############################################################################
        # We need to write a file that's the same format as the Henkelman group's
        # bader output files so that our database records properly. These lines
        # format our output information. It should be noted that our algorithm
        # currently doesn't give vacuum charges, vacuum volumes, or mininum
        # distances to partition surfaces the way that the Henkelman groups does
        acf_lines = []
        acf_lines.extend(
            [
                "    #         X           Y           Z       CHARGE      MIN DIST   ATOMIC VOL\n",
                " --------------------------------------------------------------------------------\n",
            ]
        )
        for site in results_charge:
            line = f"    {site}"
            for coord in results_coords[site]:
                line += "{:>12.6f}".format(coord)
            line += "{:>12.6f}".format(results_charge[site])
            line += "{:>13.6f}".format(results_min_dist[site])
            line += "{:>13.6f}".format(results_volume[site])
            line += "\n"
            acf_lines.append(line)
        acf_lines.extend(
            [
                " --------------------------------------------------------------------------------\n",
                "    VACUUM CHARGE:               0.0000\n",
                "    VACUUM VOLUME:               0.0000\n",
                f"    NUMBER OF ELECTRONS:{format(total_charge,'>15.4f')}\n",
            ]
        )

        with open(directory / "ACF.dat", "w") as file:
            file.writelines(acf_lines)
        t1 = time.time()
        print(t1 - t0)
