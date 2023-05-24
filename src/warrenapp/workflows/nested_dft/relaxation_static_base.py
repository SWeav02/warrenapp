# -*- coding: utf-8 -*-

import os
import shutil
from pathlib import Path

from simmate.engine import Workflow
from simmate.toolkit import Structure


class RelaxationStaticBase(Workflow):
    """
    Base class for running a relaxation followed by a static energy
    calculation.

    This should NOT be run on its own. It is meant to be inherited from in
    other workflows.
    """

    # We don't want to save anything from the parent workflow, only the
    # sub workflows (relaxation and static energy) so we set use_database=False
    use_database = False
    relaxation_workflow = None  # This will be defined in inheriting workflows
    static_energy_workflow = None  # This will be defined in inheriting workflows

    @classmethod
    def run_config(
        cls,
        structure: Structure,
        command: str = None,
        source: dict = None,
        directory: Path = None,
        **kwargs,
    ):
        # run a relaxation
        relaxation_directory = directory / "relaxation"
        relaxation_result = cls.relaxation_workflow.run(
            structure=structure,
            command=command,
            source=source,
            directory=relaxation_directory,
        ).result()

        static_energy_directory = directory / "static_energy"
        # run a static energy and bader/badelf analysis using the same structure
        # as above.
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # We need to make a new directory because only one vasp workflow can
        # be run in each directory.
        os.mkdir(static_energy_directory)
        shutil.copyfile(
            relaxation_directory / "WAVECAR", static_energy_directory / "WAVECAR"
        )
        static_energy_result = cls.static_energy_workflow.run(
            structure=relaxation_result,
            command=command,
            source=source,
            directory=static_energy_directory,
            # copy_previous_directory=True,
        )
