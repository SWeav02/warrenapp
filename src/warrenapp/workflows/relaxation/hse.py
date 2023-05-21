# -*- coding: utf-8 -*-

from warrenapp.workflows.relaxation.pbe import Relaxation__Warren__Pbe


class Relaxation__Warren__Hse(Relaxation__Warren__Pbe):
    """
    Runs a VASP relaxation calculation using Warren Lab HSE settings.
    """

    description_doc_short = "Warren Lab presets for HSE geometry optimization"

    incar = Relaxation__Warren__Pbe.incar.copy()
    incar.update(
        ALGO="Damped",  # We use Damped because it is the recommended setting by
        # by VASP (https://www.vasp.at/wiki/index.php/LHFCALC)
        HFSCREEN=0.2,
        ICHARG=1,
        LHFCALC=True,
        PRECFOCK="Fast",
        TIME=0.1,  # This is lower than the recommended setting when using the 
        # Damped tag because calculations typically take much longer with the
        # recommended 0.5 setting.
        # VASP also suggests lowering it if convergence isn't reached so there
        # is precedence for this.
        VDW_S8=2.310,  # these three tags are necessary for IVDW 12 with HSE06
        VDW_A1=0.383,
        VDW_A2=5.685,
    )
