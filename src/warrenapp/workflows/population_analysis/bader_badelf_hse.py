# -*- coding: utf-8 -*-

from simmate.engine.workflow import Workflow

from warrenapp.workflows.population_analysis.base import (
    VaspBaderBadElfBase,
    prebadelf_incar_settings,
)
from warrenapp.workflows.static_energy import (
    StaticEnergy__Warren__Hse,
    StaticEnergy__Warren__SeededHse,
)


class StaticEnergy__Warren__PrebaderbadelfHse(StaticEnergy__Warren__Hse):
    """
    Runs a static energy calculation with a high-density FFT grid under HSE
    settings from the Warren Lab. Results can be used for BadELF analysis.

    We do NOT recommend running this calculation on its own. Instead, you should
    use the full workflow, which runs this calculation AND the following bader
    analysis for you. This S3Task is only the first step of that workflow.
    """

    # The key thing for bader analysis is that we need a very fine FFT mesh. Other
    # than that, it's the same as a static energy calculation.
    incar = StaticEnergy__Warren__Hse.incar.copy()
    incar.update(prebadelf_incar_settings)


# We prefer to use a workflow that seeds the HSE calculation with a PBE calculation.
# This is inherited from our static energy seeded_hse workflow.
class StaticEnergy__Warren__PrebaderbadelfSeededHse(StaticEnergy__Warren__SeededHse):

    second_calculation = StaticEnergy__Warren__PrebaderbadelfHse


class PopulationAnalysis__Warren__BaderBadelfHse(VaspBaderBadElfBase):
    """
    Runs a static energy calculation using an extra-fine FFT grid using vasp
    and then carries out Badelf and Bader analysis on the resulting charge density.
    Uses the Warren lab settings HSE settings.
    """

    static_energy_prebadelf: Workflow = StaticEnergy__Warren__PrebaderbadelfSeededHse
