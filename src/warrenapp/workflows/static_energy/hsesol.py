# -*- coding: utf-8 -*-

from warrenapp.workflows.relaxation.hsesol import Relaxation__Warren__Hsesol
from warrenapp.workflows.static_energy.pbe import static_settings


class StaticEnergy__Warren__Hsesol(Relaxation__Warren__Hsesol):
    """
    Performs a static energy calculation based on the settings for Warren Lab
    HSEsol functional relaxation.
    """

    incar = Relaxation__Warren__Hsesol.incar.copy()
    incar.update(static_settings)
