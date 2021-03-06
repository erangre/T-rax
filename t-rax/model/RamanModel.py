# -*- coding: utf8 -*-
# T-Rax - GUI program for analysis of spectroscopy data during
# diamond anvil cell experiments
# Copyright (C) 2016 Clemens Prescher (clemens.prescher@gmail.com)
# Institute for Geology and Mineralogy, University of Cologne
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import numpy as np

from .BaseModel import SingleSpectrumModel


class RamanModel(SingleSpectrumModel, object):
    REVERSE_CM_MODE = 0
    WAVELENGTH_MODE = 1

    def __init__(self):
        super(RamanModel, self).__init__()
        self._laser_line = 532
        self._mode = RamanModel.REVERSE_CM_MODE

    @property
    def spectrum(self):
        spec = super(RamanModel, self).spectrum
        if self._mode is RamanModel.REVERSE_CM_MODE:
            spec._x = convert_wavelength_to_reverse_cm(spec.x, self.laser_line)
        return spec

    @property
    def laser_line(self):
        return self._laser_line

    @laser_line.setter
    def laser_line(self, value):
        self._laser_line = value
        if self.spe_file is not None:
            self.spectrum_changed.emit(*self.spectrum.data)

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        self._mode = value
        if self.spe_file is not None:
            self.spectrum_changed.emit(*self.spectrum.data)


def convert_wavelength_to_reverse_cm(wavelength, laser_line):
    return (1.0 / laser_line - 1 / np.array(wavelength)) * 1.0e7
