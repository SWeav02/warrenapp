# -*- coding: utf-8 -*-
from warrenapp.workflows.nested_dft.double_relaxation_static_base import (
    RelaxationRelaxationStaticBase,
)
from warrenapp.workflows.nested_dft.prepop_relaxation_static_hse_hse import (
    Relaxation__Warren__HseWithWavecar,
)
from warrenapp.workflows.nested_dft.prepop_relaxation_static_pbesol_hse import (
    Relaxation__Warren__PbeWithWavecar,
)
from warrenapp.workflows.population_analysis.prebader_badelf_dft import (
    StaticEnergy__Warren__PrebadelfHse,
)


class Nested__Warren__RelaxationStaticPbeHseHse(RelaxationRelaxationStaticBase):
    """
    Runs a PBEsol quality structure relaxation, an HSE quality relaxation, and
    an HSE static energy calculation.
    """

    static_energy_workflow = StaticEnergy__Warren__PrebadelfHse
    # We use pbesol as our default relaxation functional because it doesn't take
    # much more time than pbe and is considered to be more accurate for solids
    # (Phys. Rev. Lett. 102, 039902 (2009))
    low_quality_relaxation_workflow = Relaxation__Warren__PbeWithWavecar
    high_quality_relaxation_workflow = Relaxation__Warren__HseWithWavecar
