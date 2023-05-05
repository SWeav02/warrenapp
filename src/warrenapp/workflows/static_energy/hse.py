# -*- coding: utf-8 -*-

from warrenapp.workflows.relaxation.hse import Relaxation__Warren__Hse
from warrenapp.workflows.static_energy.pbe import static_settings


class StaticEnergy__Warren__Hse(Relaxation__Warren__Hse):
    """
    Performs a static energy calculation based on the settings for Warren Lab
    HSE functional relaxation.
    """

    incar = Relaxation__Warren__Hse.incar.copy()
    incar.update(static_settings)
