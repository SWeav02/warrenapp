# -*- coding: utf-8 -*-

from pathlib import Path

from simmate.engine import Workflow
from simmate.toolkit import Structure


class BaderBadelfRelaxationBase(Workflow):
    """
    Base class for running a PBE quality relaxation followed by a static energy
    and bader or badelf analysis.

    This should NOT be run on its own. It is meant to be inherited from in
    other workflows.
    """

    # We don't need to save anything from this parent workflow
    use_database = False
    relaxation_workflow = None  # This will be defined in inheriting workflows
    population_analysis_workflow = None  # This will be defined in inheriting workflows

    @classmethod
    def run_config(
        cls,
        structure: Structure,
        command: str = None,
        source: dict = None,
        find_empties: bool = True,
        directory: Path = None,
        **kwargs,
    ):
        # run a relaxation at PBE quality
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
        # I noticed that when I run these calculations sharing the same directory
        # it just reruns the first calculation twice. For now I'm just moving
        # everything to a new directory, but this shouldn't be the case. I'll
        # contact Jack about it. This is even more cluttered with the HSE calculations
        # which are seeded with a PBE calculation and require the same splitting
        # of folders.
        bader_result = cls.population_analysis_workflow.run(
            structure=relaxation_result,
            # copy_previous_directory = True,
            command=command,
            source=source,
            find_empties=find_empties,
            directory=static_energy_directory,
        ).result()
