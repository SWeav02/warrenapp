# -*- coding: utf-8 -*-

from warrenapp.workflows.relaxation.pbe_metal import Relaxation__Warren__PbeMetal
from warrenapp.workflows.static_energy.pbe import static_settings


class StaticEnergy__Warren__PbeMetal(Relaxation__Warren__PbeMetal):
    """
    Performs a static energy calculation based on the settings for Warren Lab
    Metal relaxations using the PBE functional.
    """

    incar = Relaxation__Warren__PbeMetal.incar.copy()
    incar.update(static_settings)
