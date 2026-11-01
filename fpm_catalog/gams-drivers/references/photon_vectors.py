"""Independent exact-rational SI photon-energy oracle; no package imports.

MIT: ../licenses/state-ten-drivers-MIT.txt.
SI decimal values from NIST's 2022 CODATA complete listing:
https://physics.nist.gov/cuu/Constants/Table/allascii.txt
"""
from fractions import Fraction
import json
from pathlib import Path


def vectors():
    h = Fraction('6.62607015e-34')
    c = Fraction(299792458)
    e = Fraction('1.602176634e-19')
    rows = []
    for nm in [1,2,10,121,250,400,500,656,800,1064,10000,1000000]:
        energy = h*c/Fraction(nm,10**9)
        rows.append({'wavelength_nm':nm,'joules':float(energy),
                     'electron_volts':float(energy/e),
                     'joules_fraction':[str(energy.numerator),str(energy.denominator)],
                     'ev_fraction':[str((energy/e).numerator),str((energy/e).denominator)]})
    return {'schema':1,'reference':'Exact rational arithmetic from SI decimal definitions',
            'source':'https://physics.nist.gov/cuu/Constants/Table/allascii.txt','photons':rows}


if __name__ == '__main__':
    Path(__file__).with_name('photon-vectors.json').write_text(json.dumps(vectors(),indent=2)+'\n',encoding='utf-8')
