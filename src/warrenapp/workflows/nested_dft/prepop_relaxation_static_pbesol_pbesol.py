# -*- coding: utf-8 -*-
from warrenapp.workflows.nested_dft.relaxation_static_base import RelaxationStaticBase
from warrenapp.workflows.population_analysis.prebader_badelf_dft import (
    StaticEnergy__Warren__PrebadelfPbesol,
)
from warrenapp.workflows.relaxation.pbesol import Relaxation__Warren__Pbesol


class Nested__Warren__RelaxationStaticPbePbe(RelaxationStaticBase):
    """
    Runs an PBEsol quality structure relaxation and PBEsol quality static energy
    calculation.
    """

    static_energy_workflow = StaticEnergy__Warren__PrebadelfPbesol
    # We use pbesol as our default relaxation functional because it doesn't take
    # much more time than pbe and is considered to be more accurate for solids
    # (Phys. Rev. Lett. 102, 039902 (2009))
    relaxation_workflow = Relaxation__Warren__Pbesol
