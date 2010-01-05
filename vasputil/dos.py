# vim: set fileencoding=latin-1
# Copyright (c) 2008, 2009 Janne Blomqvist

#  This file is part of Vasputil.

#  Vasputil is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.

#  Vasputil is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with vasputil.  If not, see <http://www.gnu.org/licenses/>.


"""Module for doing stuff with density-of-states."""

try:
    import numpy as np
except:
    import pylab as np

import sys
import warnings

class LDOS(object):
    """Class for representing a set of local DOS.
    
    DOS data is stored in the instance variable self.dos, which is a 3D 
    ndarray, as follows:
    1st dim: Which atom.
    2nd dim: Selects the DOS grid point.
    3rd dim: 0 is the energy, 1-3 s, p, d DOS.
        
    """

    def __init__(self, doscar="DOSCAR", efermi=0.0):
        """Initialize LDOS."""
        warnings.warn('vasputil.dos.LDOS is deprecated, please use \
 ase.calculators.vasp.VaspDos instead, which is an improved version if this \
 class', DeprecationWarning)
        self._efermi = 0.0
        self.read_doscar(doscar)
        self.efermi = efermi

    def read_doscar(self, fname="DOSCAR"):
        """Read a VASP DOSCAR file."""
        f = open(fname)
        natoms = int(f.readline().split()[0])
        [f.readline() for nn in range(4)]  # Skip next 4 lines.
        dos = []
        for na in xrange(natoms + 1):
            try:
                line = f.readline()
                if line == "":
                    raise Exception
            except Exception, e:
                errstr = "Failed reading " + str(na) + ":th DOS block, probably " \
                        + "this DOSCAR is from some old version of VASP that " \
                        + "doesn't " \
                        + "first produce a block with integrated DOS. Inserting " \
                        + "empty 0:th block."
                sys.stderr.write(errstr)
                dos.insert(0, np.zeros((ndos, dos[1].shape[1])))
                continue
            try:
                ndos = int(line.split()[2])
            except:
                print "Error, line is: " + line + "ENDLINE"
            line = f.readline().split()
            cdos = np.zeros((ndos, len(line)))
            cdos[0] = np.array(line)
            for nd in xrange(1, ndos):
                line = f.readline().split()
                cdos[nd] = np.array(line)
            dos.append(cdos)
        f.close()
        if dos[0].shape != dos[1].shape:
            dos0 = np.zeros(dos[1].shape)
            dos0[:,:dos[0].shape[1]] = dos[0]
            dos[0] = dos0
        self.dos = np.array(dos)

    def _set_efermi(self, efermi):
        """Set the Fermi level."""
        if self._efermi != 0.0:
            self.dos[:,:,0] = self.dos[:,:,0] + self._efermi
        self._efermi = efermi
        self.dos[:,:,0] = self.dos[:,:,0] - efermi

    def _get_efermi(self):
        return self._efermi

    def _del_efermi(self):
        raise AttributeError, "Can't delete attribute."

    efermi = property(_get_efermi, _set_efermi, _del_efermi, "Fermi energy.")

    def get_energygrid(self):
        """Return the array with the energies."""
        return self.dos[1, :, 0]

    def get_dos(self, atom, orbital):
        """Return an NDOSx1 array with dos for the chosen atom and orbital.
        
        If spin-unpolarized calculation, no phase factors:
        s = 1, p = 2, d = 3
        Spin-polarized, no phase factors:
        s-up = 1, s-down = 2, p-up = 3, p-down = 4, d-up = 5, d-down = 6
        If phase factors have been calculated, orbitals are
        s, py, pz, px, dxy, dyz, dz2, dxz, dx2
        double in the above fashion if spin polarized.
        
        """
        return self.dos[atom, :, orbital]


def set_labels(fsz=16, show_legend=True):
    """Utility function to set default parameters for DOS plots."""
    import pylab as pl
    pl.xlabel("E-E$_\mathrm{f}$ (eV)", size=fsz)
    pl.figtext(0.03, 0.35, "LDOS (arb. units)", rotation='vertical', size=fsz)
    pl.xticks(size=fsz)
    pl.yticks(size=fsz)
    if show_legend:
        pl.legend()
    pl.subplots_adjust(hspace=0.0)

def showdp(fsz=16, show_legend=True):
    """Set labels etc. and show the plot."""
    import pylab as pl
    set_labels(fsz, show_legend)
    pl.show()

def save_and_show(fname, fsz=16, show_legend=True, figure=None):
    """Set labels etc., save the file to .eps and .pdf and show plot."""
    import pylab as pl
    import os
    if not figure:
        f = pl.figure()
    else:
        f = figure
    set_labels(fsz, show_legend)
    if fname.endswith('.eps'):
        fn = fname
    else:
        fn = fname + '.eps'
    f.savefig(fn)
    os.system('epstopdf ' + fn)
    pl.show()
