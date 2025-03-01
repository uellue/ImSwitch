import numpy as np

from ..basecontrollers import ImConWidgetController


class ULensesController(ImConWidgetController):
    """ Linked to ULensesWidget. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plotAdded = False

        # Connect ULensesWidget signals
        self._widget.sigULensesClicked.connect(self.updateGrid)
        self._widget.sigUShowLensesChanged.connect(self.toggleULenses)

    def addPlot(self):
        """ Adds ulensesPlot to ImageWidget viewbox through the CommunicationChannel. """
        if not self.plotAdded:
            self._commChannel.sigAddItemToVb.emit(self._widget.getPlotGraphicsItem())
            self.plotAdded = True

    def updateGrid(self):
        """ Updates plot with new parameters. """
        x, y, px, up = self._widget.getParameters()
        size_x, size_y = self._master.detectorsManager.execOnCurrent(lambda c: c.shape)
        pattern_x = np.arange(x, size_x, up / px)
        pattern_y = np.arange(y, size_y, up / px)
        grid = np.array(np.meshgrid(pattern_x, pattern_y)).T.reshape(-1, 2)
        self._widget.setData(x=grid[:, 0], y=grid[:, 1])

    def toggleULenses(self, show):
        """ Shows or hides grid. """
        if show:
            self.addPlot()
        self._widget.setULensesVisible(show)


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
