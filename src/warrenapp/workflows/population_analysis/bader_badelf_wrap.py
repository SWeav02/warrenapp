# -*- coding: utf-8 -*-


from warrenapp.workflows.population_analysis.base import VaspBaderBadElfBase
from warrenapp.workflows.population_analysis.bader_badelf import PopulationAnalysis__Warren__BaderBadelf
from pathlib import Path
from warrenapp.workflows.population_analysis.bader_badelf import PopulationAnalysis__Warren__BaderBadelf
from simmate.database import connect
from simmate.database.workflow_results import StaticEnergy
from shutil import unpack_archive, make_archive
import os
from simmate.engine import Workflow

class PopulationAnalysis__Warren__BaderBadelfWrap(Workflow):
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
        unpack_archive(f"{parent_directory}.zip",worker_directory)
        os.remove(f"{parent_directory}.zip")
        
        PopulationAnalysis__Warren__BaderBadelf().run_cloud(
            structure=structure,
            directory=static_directory,
            find_empties=True,
            source = None,
            )
        make_archive(f"{parent_directory}","zip")