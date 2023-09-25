# -*- coding: utf-8 -*-


import os
from pathlib import Path
from shutil import make_archive, rmtree, unpack_archive

from simmate.database import connect
from simmate.database.workflow_results import StaticEnergy
from simmate.engine import Workflow

from warrenapp.workflows.population_analysis.bader_badelf import (
    PopulationAnalysis__Warren__BaderBadelf,
)
from warrenapp.workflows.population_analysis.base import VaspBaderBadElfBase


class PopulationAnalysis__Warren__BaderBadelfWrap(Workflow):
    use_database = False

    @staticmethod
    def run_config(
        structure,
        directory: Path,
        source: dict = None,
        **kwargs,
    ):
        static_directory = directory
        parent_directory = static_directory.parent.absolute()
        worker_directory = static_directory.parent.parent
        # unzip the results directory into the same worker directory to ensure
        # directory path is the same.
        # try to unzip the archive. If it fails stop the workflow
        try:
            unpack_archive(f"{parent_directory}.zip", worker_directory)
        except:
            breakpoint()
        elfcar_path = static_directory / "ELFCAR"
        # check if the ELFCAR was successfully unzipped. If it was remove the
        # zip folder to avoid excessive space
        if elfcar_path.exists():
            os.remove(f"{parent_directory}.zip")
        else:
            breakpoint()
        # Run the bader and BadELF analyses
        PopulationAnalysis__Warren__BaderBadelf().run_cloud(
            structure=structure,
            directory=static_directory,
            find_empties=True,
            source=None,
        )
        # re-zip the archive and remove the unzipped directory.
        make_archive(f"{parent_directory}", "zip")
        rmtree(parent_directory)
