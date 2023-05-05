# -*- coding: utf-8 -*-

from warrenapp.workflows.population_analysis.badelf_pbe import (
    StaticEnergy__Warren__PrebadelfPbe,
)
from warrenapp.workflows.population_analysis.base import (
    VaspBaderBase,
    prebader_incar_settings,
)
from warrenapp.workflows.static_energy.pbe import StaticEnergy__Warren__Pbe


class StaticEnergy__Warren__PrebaderPbe(StaticEnergy__Warren__Pbe):
    """
    Runs a static energy calculation with a high-density FFT grid setting.
    Results can be used for Bader analysis.

    We do NOT recommend running this calculation on its own. Instead, you should
    use the full workflow, which runs this calculation AND the following bader
    analysis for you. This S3Task is only the first step of that workflow.
    """

    # The key thing for bader analysis is that we need a very fine FFT mesh. Other
    # than that, it's the same as a static energy calculation.
    incar = StaticEnergy__Warren__Pbe.incar.copy()
    incar.update(prebader_incar_settings)


class PopulationAnalysis__Warren__BaderPbe(VaspBaderBase):
    """
    Runs a static energy calculation using an extra-fine FFT grid using vasp
    and then carries out Bader analysis on the resulting charge density.
    Uses the Warren lab settings PBE settings.
    """

    static_energy_prebader = StaticEnergy__Warren__PrebaderPbe
    static_energy_prebadelf = StaticEnergy__Warren__PrebadelfPbe
