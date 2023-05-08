# -*- coding: utf-8 -*-

import shutil
from pathlib import Path

from simmate.engine import Workflow
from simmate.toolkit import Structure

from warrenapp.workflows.static_energy import (
    StaticEnergy__Warren__Hse,
    StaticEnergy__Warren__Pbe,
)


class StaticEnergy__Warren__SeededHse(Workflow):
    """
    Runs an HSE quality static energy calculation seeded by a PBE static energy
    calculation. This is sometimes necessary for HSE calculations to succeed.
    This workflow can also be inherited fromt to create other seeded static
    energy calculations.
    """

    # Define which workflows to use. This is so we can use this workflow in other
    # places.
    use_database = False
    initial_calculation = StaticEnergy__Warren__Pbe
    second_calculation = StaticEnergy__Warren__Hse

    @classmethod
    def run_config(
        cls,
        structure: Structure,
        command: str = None,
        source: dict = None,
        directory: Path = None,
        **kwargs,
    ):

        # run the initial PBE calculation and save its results as a variable
        initial_directory = directory / "pbe_seed"
        initial_result = cls.initial_calculation.run(
            structure=structure,
            command=command,
            source=source,
            directory=initial_directory,
        ).result()

        # We want the WAVECAR to be present for the seeded calculation so we
        # copy it here.
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # I'm not sure why, but it seems I need to create seperate
        # directories or the nested workflow just reruns the initial calculation.
        # Based off of Jack's documentation I don't think this should be the case.
        # It should overwrite the previous calculation.
        shutil.copy(initial_directory / "WAVECAR", directory)
        # run the secondary calculation with the same structure but seperate directory
        final_result = cls.second_calculation.run(
            structure=initial_result,
            command=command,
            source=source,
            directory=directory,
        )
