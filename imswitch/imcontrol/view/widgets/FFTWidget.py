import pyqtgraph as pg
from qtpy import QtCore, QtWidgets

from imswitch.imcontrol.view import guitools as guitools
from .basewidgets import Widget

from imswitch.imcommon.framework import Thread, Worker, Timer
import numpy as np

class FFTWidget(guitools.NapariBaseWidget):
    """ Displays the FFT transform of the image. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Graphical elements
        self.showCheck = QtWidgets.QCheckBox('Show FFT')
        self.showCheck.setCheckable(True)

        # Add elements to GridLayout
        grid = QtWidgets.QGridLayout()
        self.setLayout(grid)
        grid.addWidget(self.showCheck, 1, 0, 1, 1)

        # Connect signals
        self.showCheck.toggled.connect(self.setShowFFT)

        self.updateRate = 100

        # Prepare image computation worker
        self.imageComputationWorker = self.FFTImageComputationWorker(self, self.updateRate)
        self.imageComputationThread = Thread()
        self.imageComputationWorker.moveToThread(self.imageComputationThread)
        self.imageComputationThread.started.connect(self.imageComputationWorker.run)
        self.imageComputationThread.finished.connect(self.imageComputationWorker.stop)

    def setShowFFT(self, enabled):
            """ Show or hide FFT. """
            #if enabled: self.imageComputationThread.start()
            if enabled:
                image = self.viewer.layers['Camera'].data
                fft = np.fft.fftshift(np.log10(abs(np.fft.fft2(image))))
                self.viewer.add_image(fft)
                self.imageComputationThread.start()
            else:
                self.imageComputationThread.stop()


    class FFTImageComputationWorker(Worker):

        def __init__(self, fftController, updatePeriod):
            super().__init__()
            self._fftController = fftController
            self._updatePeriod = updatePeriod
            self._vtimer = None
        
        def run(self):
            self._vtimer = Timer()
            self._vtimer.timeout.connect(self.computeFFTImage)
            self._vtimer.start(self._updatePeriod)

        def computeFFTImage(self):
            """ Compute FFT of an image. """
            # Skip this frame in order to catch up
            image = self._fftController.viewer.layers['Camera'].data
            fftImage = np.fft.fftshift(np.log10(abs(np.fft.fft2(image))))
            self._fftController.viewer.layers['fft'].data = fftImage

        def stop(self):
            if self._vtimer is not None:
                self._vtimer.stop()

# Copyright (C) 2020, 2021 TestaLab
# This file is part of ImSwitch.
#
# ImSwitch is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ImSwitch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
