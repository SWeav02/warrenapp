# -*- coding: utf-8 -*-

from simmate.engine.workflow import Workflow

from warrenapp.workflows.population_analysis.base import VaspBaderBadElfBase
from warrenapp.workflows.population_analysis.prebader_badelf_dft import (
    StaticEnergy__Warren__PrebadelfHse,
)


class PopulationAnalysis__Warren__BaderBadelfHse(VaspBaderBadElfBase):
    """
    Runs a static energy calculation using an extra-fine FFT grid using vasp
    and then carries out Badelf and Bader analysis on the resulting charge density.
    Uses the Warren lab settings HSE settings.
    """

    static_energy_prebadelf: Workflow = StaticEnergy__Warren__PrebadelfHse
