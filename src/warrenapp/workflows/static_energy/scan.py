# -*- coding: utf-8 -*-

from warrenapp.workflows.relaxation.scan import Relaxation__Warren__Scan
from warrenapp.workflows.static_energy.pbe import static_settings


class StaticEnergy__Warren__Scan(Relaxation__Warren__Scan):
    """
    Performs a static energy calculation based on the settings for Warren Lab
    SCAN functional relaxation.
    """

    incar = Relaxation__Warren__Scan.incar.copy()
    incar.update(static_settings)
