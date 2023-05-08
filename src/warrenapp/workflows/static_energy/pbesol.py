# -*- coding: utf-8 -*-

from warrenapp.workflows.relaxation.pbesol import Relaxation__Warren__Pbesol
from warrenapp.workflows.static_energy.pbe import static_settings


class StaticEnergy__Warren__Pbesol(Relaxation__Warren__Pbesol):
    """
    Performs a static energy calculation based on the settings for Warren Lab
    PBEsol functional relaxation. This functional is generally considered to
    be more accurate for solids.
    (Phys. Rev. Lett. 102, 039902 (2009))
    """

    incar = Relaxation__Warren__Pbesol.incar.copy()
    incar.update(static_settings)
