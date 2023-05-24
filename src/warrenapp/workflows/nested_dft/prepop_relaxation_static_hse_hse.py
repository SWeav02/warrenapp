# -*- coding: utf-8 -*-
from warrenapp.workflows.nested_dft.relaxation_static_base import RelaxationStaticBase
from warrenapp.workflows.population_analysis.prebader_badelf_dft import (
    StaticEnergy__Warren__PrebadelfHse,
)
from warrenapp.workflows.relaxation.hse import Relaxation__Warren__Hse


# We want to run an HSE relaxation followed by an HSE static energy calculation.
# Copying the WAVECAR will make this much faster, but this requires that a
# WAVECAR exists. However, we generally don't want all relaxation calculations
# to save the WAVECAR so we make a custom workflow here.
class Relaxation__Warren__HseWithWavecar(Relaxation__Warren__Hse):
    """
    This workflow is the same as the typical HSE relaxation but with the added
    tag in the INCAR for writing the WAVECAR. This is intended to be used with
    nested workflows to increase the speed of the static energy calculation
    """

    incar = Relaxation__Warren__Hse().incar.copy()
    incar.update(dict(LWAVE=True))


class Nested__Warren__RelaxationStaticHseHse(RelaxationStaticBase):
    """
    Runs an HSE quality structure relaxation and HSE quality static energy
    calculation.
    """

    static_energy_workflow = StaticEnergy__Warren__PrebadelfHse
    relaxation_workflow = Relaxation__Warren__HseWithWavecar
