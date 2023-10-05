#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  4 16:49:49 2023

@author: sweav
"""

"""
This file contains an extension to pymatgen's Elfcar class to allow for the calculation
of the badelf radius for a specific set of ions.
"""

from pymatgen.io.vasp import Elfcar as PymatgenElfcar
from warrenapp.badelf_tools.badelf_algorithm_functions import(
      get_closest_neighbors,
      get_real_from_vox,
      get_voxel_from_frac,
      get_voxel_from_neigh_CrystalNN,
      get_partitioning_line_rough,
      get_partitioning_line_fine,
      get_line_frac_min_rough,
      get_position_from_min,
      get_radius,
      )


class Elfcar(PymatgenElfcar):
    # Leave docstring blank and inherit from pymatgen
    
    def get_lattice_from_elfcar(self):
        """
        This function gets the important lattice information from a structure object
        """
        
        structure = self.structure
        pymatgen_lattice = structure.lattice
        lattice = {}
        lattice["coords"] = [i.coords for i in structure]
        lattice["num_atoms"] = len(structure)
        lattice["a"] = pymatgen_lattice.matrix[0]
        lattice["b"] = pymatgen_lattice.matrix[1]
        lattice["c"] = pymatgen_lattice.matrix[2]
        lattice["elements"] = [i.name for i in structure.composition]
        lattice["coords"] = [i.coords for i in structure]
        lattice["grid_size"] = list(self.dim)
        lattice["volume"] = structure.volume
        return lattice

    def get_neighbor_elf_line(self, site: int, method: str = "rough"):
        """
        This method gets the ELF values between an atom and its closest neighbor.
        It interpolates the ELF between the atoms and returns them as a list.
        
        site: An integer value referencing an atom in the structure
        method: Rough or fine interpolation (linear or cubic)
        """
        structure = self.structure
        lattice = self.get_lattice_from_elfcar()
        closest_neighbors = get_closest_neighbors(structure)
        neigh = closest_neighbors[site][0]
        grid = self.data["total"]
        
        site_pos = get_voxel_from_frac(site, lattice)
        neigh_coords = get_voxel_from_neigh_CrystalNN(neigh, lattice)
        
        if method == "rough":
            elf_positions, elf_values = get_partitioning_line_rough(
                site_pos,
                neigh_coords,
                grid
                )
        elif method == "fine":
            elf_positions, elf_values = get_partitioning_line_fine(
                site_pos,
                neigh_coords,
                grid
                )
        return elf_positions, elf_values
    
    def get_elf_ionic_radius(self, site: int, method: str = "rough"):
        """
        This method gets the ELF ionic radius. It interpolates the ELF values
        between a site and it's closest neighbor and returns the distance between
        the atom and the minimum in this line. This has been shown to be very
        similar to the Shannon Crystal Radius, but gives more specific values
        
        site: An integer value referencing an atom in the structure
        method: Rough or fine interpolation (linear or cubic)
        """        
        lattice = self.get_lattice_from_elfcar()
        elf_positions, elf_values = self.get_neighbor_elf_line(site, method)
        site_pos = elf_positions[0]
        neigh_pos = elf_positions[200]
        global_min_pos = get_line_frac_min_rough(elf_values, rough_partitioning=True)
        min_pos = get_position_from_min(global_min_pos[2], site_pos, neigh_pos)
        min_coord = get_real_from_vox(min_pos, lattice)
        return get_radius(min_coord, site_pos, lattice)
        
            
            