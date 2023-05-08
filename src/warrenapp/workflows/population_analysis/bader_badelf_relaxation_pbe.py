# -*- coding: utf-8 -*-

from warrenapp.workflows.population_analysis import (
    PopulationAnalysis__Warren__BaderBadelfPbe,
)
from warrenapp.workflows.population_analysis.relaxation_base import (
    BaderBadelfRelaxationBase,
)
from warrenapp.workflows.relaxation.pbesol import Relaxation__Warren__Pbesol


class PopulationAnalysis__Warren__BaderBadelfRelaxationPbe(BaderBadelfRelaxationBase):
    """
    Runs a PBE quality structure relaxation, a PBE quality static energy
    calculation, and a bader and badelf analysis.

    """

    population_analysis_workflow = PopulationAnalysis__Warren__BaderBadelfPbe
    # We use pbesol as our default relaxation functional because it doesn't take
    # much more time than pbe and is considered to be more accurate for solids
    # (Phys. Rev. Lett. 102, 039902 (2009))
    relaxation_workflow = Relaxation__Warren__Pbesol
