# -*- coding: utf8 -*-
__author__ = 'Clemens Prescher'

from PyQt4 import QtCore, QtGui
from view.RoiWidget import RoiWidget
from view.SpectrumWidget import SpectrumWidget
from view.Widgets import FileGroupBox


class RamanWidget(QtGui.QWidget):
    def __init__(self, *args, **kwargs):
        super(RamanWidget, self).__init__(*args, **kwargs)
        self._main_layout = QtGui.QVBoxLayout()
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)
        self._main_splitter = QtGui.QSplitter(QtCore.Qt.Vertical)

        self._graph_control_widget = QtGui.QWidget()
        self._graph_control_layout = QtGui.QHBoxLayout()
        self._graph_control_layout.setContentsMargins(0, 0, 0, 0)

        self.graph_widget = SpectrumWidget()
        self.control_widget = ControlWidget()
        self.roi_widget = RoiWidget(1, roi_colors=[(255, 255, 255)])

        self._graph_control_layout.addWidget(self.graph_widget)
        self._graph_control_layout.addWidget(self.control_widget)

        self._graph_control_layout.setStretch(0, 1)
        self._graph_control_layout.setStretch(1, 0)

        self._graph_control_widget.setLayout(self._graph_control_layout)

        self._main_splitter.addWidget(self._graph_control_widget)
        self._main_splitter.addWidget(self.roi_widget)

        self._main_layout.addWidget(self._main_splitter)

        self._main_splitter.setStretchFactor(0, 3)
        self._main_splitter.setStretchFactor(1, 2)

        self.setLayout(self._main_layout)

        self.create_shortcuts()

    def create_shortcuts(self):
        pass


class ControlWidget(QtGui.QWidget):
    def __init__(self):
        super(ControlWidget, self).__init__()
        self._layout = QtGui.QVBoxLayout()
        self._file_gb = FileGroupBox()

        self._layout.addWidget(self._file_gb)
        self._layout.addSpacerItem(QtGui.QSpacerItem(QtGui.QSpacerItem(10, 10,
                                                                       QtGui.QSizePolicy.Fixed,
                                                                       QtGui.QSizePolicy.Expanding)))
        self.setLayout(self._layout)


if __name__ == '__main__':
    app = QtGui.QApplication([])
    widget = RamanWidget()
    widget.show()
    widget.raise_()
    app.exec_()