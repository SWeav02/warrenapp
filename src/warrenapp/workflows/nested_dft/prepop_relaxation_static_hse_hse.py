# -*- coding: utf-8 -*-
from warrenapp.workflows.nested_dft.relaxation_static_base import RelaxationStaticBase
from warrenapp.workflows.population_analysis.prebader_badelf_dft import (
    StaticEnergy__Warren__PrebadelfHse,
)
from warrenapp.workflows.relaxation.hse import Relaxation__Warren__Hse


# This workflow will run
class Nested__Warren__RelaxationStaticHseHse(RelaxationStaticBase):
    """
    Runs an HSE quality structure relaxation and HSE quality static energy
    calculation.
    """

    static_energy_workflow = StaticEnergy__Warren__PrebadelfHse
    # We use pbesol as our default relaxation functional because it doesn't take
    # much more time than pbe and is considered to be more accurate for solids
    # (Phys. Rev. Lett. 102, 039902 (2009))
    relaxation_workflow = Relaxation__Warren__Hse
