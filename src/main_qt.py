"""
author: Yudha Styawan
email: yudhastyawan26@gmail.com
"""

import sys
import os
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import uic
from PyQt5 import QtWebEngineWidgets
from hypoDD_compiler import hypoDDCompile
from hypoDD_relocator_qt import hypoDDrelocate
from ph2dt_compiler import ph2dtCompile
from ph2dt_run_qt import ph2dtRun
from bmkg2pha import bmkg2pha
from isc2pha import isc2pha
from lindutil import Haversine, seekstat

FILE_DIR = os.path.dirname(__file__)
opHtml = lambda filename: os.path.join(FILE_DIR, "html", filename)

def buffer_to_str(buf):
    codec = QtCore.QTextCodec.codecForName("UTF-8")
    return str(codec.toUnicode(buf))

class MainHypoDD(QtWidgets.QMainWindow):
    def __init__(self, parent = None):
        super(MainHypoDD, self).__init__(parent)
        self.setWindowTitle("Lindu Software")
        self.setWindowIcon(QtGui.QIcon(os.path.join(FILE_DIR, "figs", "icon.ico")))
        self.load_ui()
        self.params = {}
        self.settings()
    
    def load_ui(self):
        self.ui = uic.loadUi(os.path.join(FILE_DIR, "hypoDD.ui"))
        self.about = uic.loadUi(os.path.join(FILE_DIR, "about.ui"))
        self.about.setWindowIcon(QtGui.QIcon(os.path.join(FILE_DIR, "figs", "icon.ico")))
        self.bmkg2pha = uic.loadUi(os.path.join(FILE_DIR, "bmkg2pha.ui"))
        self.bmkg2pha.setWindowIcon(QtGui.QIcon(os.path.join(FILE_DIR, "figs", "icon.ico")))
        self.isc2pha = uic.loadUi(os.path.join(FILE_DIR, "isc2pha.ui"))
        self.isc2pha.setWindowIcon(QtGui.QIcon(os.path.join(FILE_DIR, "figs", "icon.ico")))
        
        self.setCentralWidget(self.ui)
        self.setGeometry(self.ui.geometry())
        center = QtWidgets.QApplication.primaryScreen().availableGeometry().center()
        frameGeom = self.frameGeometry()
        frameGeom.moveCenter(center)
        self.move(frameGeom.topLeft())

    def settings(self):
        self.bmkgDock = QtWidgets.QDockWidget("BMKG to PHA", self)
        self.bmkgDock.setWidget(self.bmkg2pha)
        self.ui.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.bmkgDock)
        self.bmkgDock.setFloating(True)
        self.bmkgDock.hide()

        self.iscDock = QtWidgets.QDockWidget("ISC to PHA", self)
        self.iscDock.setWidget(self.isc2pha)
        self.ui.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.iscDock)
        self.iscDock.setFloating(True)
        self.iscDock.hide()

        self.webDock = QtWidgets.QDockWidget("Web Help", self)
        self.webWid = QtWebEngineWidgets.QWebEngineView()
        self.webDock.setWidget(self.webWid)
        self.ui.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.webDock)

        self.ui.tabifyDockWidget(self.ui.dock_stdout, self.ui.dock_stderr)
        self.ui.dock_stdout.raise_()

        pix = QtGui.QPixmap(os.path.join(FILE_DIR,"figs","about.png"))
        self.about.labelAbout.setPixmap(pix)

        self.actSeis = QtWidgets.QAction(QtGui.QIcon(os.path.join(FILE_DIR,"figs","plot.png")),"Open/Plot Seismic Waves",self)
        self.actSeis.setStatusTip("Open and plot seismic waves")
        self.actSeis.setEnabled(False)
        self.ui.toolBar.addAction(self.actSeis)

        self.actGAD = QtWidgets.QAction(QtGui.QIcon(os.path.join(FILE_DIR,"figs","location.png")),"GAD",self)
        self.actGAD.setStatusTip("location - GAD")
        self.actGAD.setEnabled(False)
        self.ui.toolBar.addAction(self.actGAD)

        self.actHypoDD = QtWidgets.QAction(QtGui.QIcon(os.path.join(FILE_DIR,"figs","relocation.png")),"hypoDD",self)
        self.actHypoDD.setStatusTip("relocation - hypoDD")
        self.ui.toolBar.addAction(self.actHypoDD)

        self.actTomo = QtWidgets.QAction(QtGui.QIcon(os.path.join(FILE_DIR,"figs","tomography.png")),"Tomography",self)
        self.actTomo.setStatusTip("Tomography")
        self.actTomo.setEnabled(False)
        self.ui.toolBar.addAction(self.actTomo)

        self.ui.toolBar.setIconSize(QtCore.QSize(32, 32))

        self.ui.treeParams.expandAll()
        self.ui.treePh2dt.expandAll()
        self.ui.treeParams.header().resizeSection(0,300)
        self.ui.treePh2dt.header().resizeSection(0,300)
        self.dataTypeComboBox = QtWidgets.QComboBox(self)
        self.dataTypeComboBox.addItems(["cross correlation data only",
                                        "absolute (catalog) data only",
                                        "cross corr. and catalog"])
        self.dataTypeComboBox.setCurrentIndex(1)
        self.ui.treeParams.setItemWidget(
            self.ui.treeParams.findItems("Relocator", QtCore.Qt.MatchFlag.MatchExactly)[0].child(0),
            1,
            self.dataTypeComboBox
            )
        self.phaseTypeComboBox = QtWidgets.QComboBox(self)
        self.phaseTypeComboBox.addItems(["P-wave",
                                         "S-wave",
                                         "P- & S-wave"])
        self.ui.treeParams.setItemWidget(
            self.ui.treeParams.findItems("Relocator", QtCore.Qt.MatchFlag.MatchExactly)[0].child(1),
            1,
            self.phaseTypeComboBox
            )
        self.initialLocationComboBox = QtWidgets.QComboBox(self)
        self.initialLocationComboBox.addItems(["start from cluster centroid",
                                               "start from catalog locations"])
        self.initialLocationComboBox.setCurrentIndex(1)
        self.ui.treeParams.setItemWidget(
            self.ui.treeParams.findItems("Relocator", QtCore.Qt.MatchFlag.MatchExactly)[0].child(5),
            1,
            self.initialLocationComboBox
            )
        self.LSComboBox = QtWidgets.QComboBox(self)
        self.LSComboBox.addItems(["singular value decomposition (SVD)",
                                  "conjugate gradients (LSQR)"])
        self.LSComboBox.setCurrentIndex(1)
        self.ui.treeParams.setItemWidget(
            self.ui.treeParams.findItems("Relocator", QtCore.Qt.MatchFlag.MatchExactly)[0].child(6),
            1,
            self.LSComboBox
            )
        self.ui.treeParams.itemClicked.connect(lambda item, column: self.onItemClicked(item, column))
        self.ui.treePh2dt.itemClicked.connect(lambda item, column: self.onItemPh2dtClicked(item, column))
        self.targetDirectoryWidget = QtWidgets.QWidget(self)
        tDW_layout = QtWidgets.QHBoxLayout()
        tDW_layout.setSpacing(0)
        tDW_layout.setContentsMargins(0,0,0,0)
        self.targetDirectoryWidget.setLayout(tDW_layout)
        self.tDW_lineEdit = QtWidgets.QLineEdit()
        self.tDW_browse = QtWidgets.QPushButton("...")
        self.tDW_browse.setFixedWidth(25)
        self.tDW_check = QtWidgets.QPushButton("check!")
        self.tDW_check.setEnabled(False)
        self.tDW_check.setFixedWidth(45)
        tDW_layout.addWidget(self.tDW_lineEdit)
        tDW_layout.addWidget(self.tDW_browse)
        tDW_layout.addWidget(self.tDW_check)
        self.ui.treeParams.setItemWidget(
            self.ui.treeParams.findItems("Path", QtCore.Qt.MatchFlag.MatchExactly)[0].child(0),
            1,
            self.targetDirectoryWidget
        )
        self.targetDirectoryWidgetPh2dt = QtWidgets.QWidget(self)
        tDW_layoutPh2dt = QtWidgets.QHBoxLayout()
        tDW_layoutPh2dt.setSpacing(0)
        tDW_layoutPh2dt.setContentsMargins(0,0,0,0)
        self.targetDirectoryWidgetPh2dt.setLayout(tDW_layoutPh2dt)
        self.tDW_lineEditPh2dt = QtWidgets.QLineEdit()
        self.tDW_browsePh2dt = QtWidgets.QPushButton("...")
        self.tDW_browsePh2dt.setFixedWidth(25)
        self.tDW_checkPh2dt = QtWidgets.QPushButton("check!")
        self.tDW_checkPh2dt.setEnabled(False)
        self.tDW_checkPh2dt.setFixedWidth(45)
        tDW_layoutPh2dt.addWidget(self.tDW_lineEditPh2dt)
        tDW_layoutPh2dt.addWidget(self.tDW_browsePh2dt)
        tDW_layoutPh2dt.addWidget(self.tDW_checkPh2dt)
        self.ui.treePh2dt.setItemWidget(
            self.ui.treePh2dt.findItems("Path", QtCore.Qt.MatchFlag.MatchExactly)[0].child(0),
            1,
            self.targetDirectoryWidgetPh2dt
        )
        self.dictInOut = {}
        for i, name in enumerate(['dt.cc', 'dt.ct', 'event.sel', 'station.dat', 'hypoDD.loc', 'hypoDD.reloc', 'hypoDD.sta', 'hypoDD.res', 'hypoDD.src']):
            self.dictInOut[name] = QtWidgets.QCheckBox(self)
            self.dictInOut[name].setChecked(False)
            if name.split('.')[0] == 'hypoDD':
                self.dictInOut[name].setChecked(True)
            if name in ('hypoDD.loc', 'hypoDD.reloc'):
                self.dictInOut[name].setEnabled(False)
            self.ui.treeParams.setItemWidget(
                self.ui.treeParams.findItems("In/Output", QtCore.Qt.MatchFlag.MatchExactly)[0].child(i),
                1,
                self.dictInOut[name]
            )
        self.dictInOutPh2dt = {}
        for i, name in enumerate(['station.dat', 'phase.dat', 'dt.ct', 'event.dat', 'event.sel']):
            self.dictInOutPh2dt[name] = QtWidgets.QCheckBox(self)
            self.dictInOutPh2dt[name].setChecked(False)
            if name.split('.')[0] == 'event' or name == 'dt.ct':
                self.dictInOutPh2dt[name].setChecked(True)
                self.dictInOutPh2dt[name].setEnabled(False)
            self.ui.treePh2dt.setItemWidget(
                self.ui.treePh2dt.findItems("In/Output", QtCore.Qt.MatchFlag.MatchExactly)[0].child(i),
                1,
                self.dictInOutPh2dt[name]
            )
        self.LSComboBox = QtWidgets.QComboBox(self)
        self.LSComboBox.addItems(["singular value decomposition (SVD)",
                                  "conjugate gradients (LSQR)"])
        self.LSComboBox.setCurrentIndex(1)
        self.ui.treeParams.setItemWidget(
            self.ui.treeParams.findItems("Relocator", QtCore.Qt.MatchFlag.MatchExactly)[0].child(6),
            1,
            self.LSComboBox
            )
        self.ui.actionOpen_hypoDD_inp.triggered.connect(self.actionOpen_hypoDD_inpClicked)
        self.ui.actionOpen_ph2dt_inp.triggered.connect(self.actionOpen_ph2dt_inpClicked)
        self.ui.btnCompile.clicked.connect(self.onBtnCompileClicked)
        self.ui.btnRun.clicked.connect(self.onBtnRunClicked)
        self.ui.btnCompRun.clicked.connect(self.onBtnCompRunClicked)
        self.ui.btnClearLog.clicked.connect(self.onBtnClearLogClicked)
        self.ui.btnCompilePh2dt.clicked.connect(self.onBtnCompilePh2dtClicked)
        self.ui.btnRunPh2dt.clicked.connect(self.onBtnRunPh2dtClicked)
        self.ui.btnCompRunPh2dt.clicked.connect(self.onBtnCompRunPh2dtClicked)
        self.ui.btnClearLogPh2dt.clicked.connect(self.onBtnClearLogClicked)
        self.tDW_browse.clicked.connect(self.onTDW_browseClicked)
        self.tDW_lineEdit.textChanged.connect(self.tDW_lineEditChanged)
        self.tDW_check.clicked.connect(self.onTDW_checkClicked)
        self.tDW_browsePh2dt.clicked.connect(self.onTDW_browsePh2dtClicked)
        self.tDW_lineEditPh2dt.textChanged.connect(self.tDW_lineEditPh2dtChanged)
        self.tDW_checkPh2dt.clicked.connect(self.onTDW_checkPh2dtClicked)
        self.ui.btnNSet.clicked.connect(lambda: self.ui.tableNSet.setRowCount(int(self.ui.lineNSet.text())))
        self.ui.btnVel.clicked.connect(lambda: self.ui.tableVel.setColumnCount(int(self.ui.lineVel.text())))
        self.ui.btnVel.clicked.connect(self.ui.tableVel.resizeColumnsToContents)
        self.ui.actionAbout.triggered.connect(lambda: self.about.show())
        self.ui.actionbmkg2pha.triggered.connect(self.bmkgDock.show)
        self.ui.actionisc2pha.triggered.connect(self.iscDock.show)
        self.ui.btnSearchVel.clicked.connect(lambda: self.ui.lineSearchVel.setText(
                str(QtWidgets.QFileDialog.getOpenFileName(self, "Open text file", 'c:\\', "All Files (*.*)")[0])
            ))
        self.ui.btnOpenVel.clicked.connect(self.btnOpenVelClicked)
        self.bmkg2pha.btn_bmkgOpen.clicked.connect(lambda: self.bmkg2pha.line_bmkgpath.setText(
                str(QtWidgets.QFileDialog.getOpenFileName(self, "Open text file", 'c:\\', "All Files (*.*)")[0])
            ))
        self.bmkg2pha.btn_bmkgOpen.clicked.connect(lambda: self.bmkg2pha.line_phasepath.setText(
                os.path.join(os.path.split(self.bmkg2pha.line_bmkgpath.text())[0], "phase.dat")
            ))
        self.bmkg2pha.btn_bmkgConvert.clicked.connect(self.btn_bmkgConvertClicked)
        self.isc2pha.btn_iscOpen.clicked.connect(lambda: self.isc2pha.line_iscpath.setText(
                str(QtWidgets.QFileDialog.getOpenFileName(self, "Open text file", 'c:\\', "All Files (*.*)")[0])
            ))
        self.isc2pha.btn_iscOpen.clicked.connect(lambda: self.isc2pha.line_phasepath.setText(
                os.path.join(os.path.split(self.isc2pha.line_iscpath.text())[0], "phase.dat")
            ))
        self.isc2pha.btn_iscConvert.clicked.connect(self.btn_iscConvertClicked)
        self.ui.btnNSetHelp.clicked.connect(lambda: self.ui.textHelp.setPlainText("""Weighting scheme:
"NITER -> Number of iterations for the set of weighting parameters that follow.
WTCCP, WTCCS -> Weight for cross-corr P-wave, S-wave data. –9 = data not used.
WTCTP, WTCTS -> Weight for catalog P-wave, S-wave data. –9 = data not used.
WRCC, WRCT -> Cutoff threshold for outliers located on the tails of the cross-corr, catalog data.
    0<1 = absolute threshold in sec (static cutoff). ≥1 = factor to multiply standard deviation (dynamic cutoff).
    -9 = no outlier removed.
WDCC, WDCT -> Max. event separation distance [km] for x-corr data, catalog data. -9 = not activated.
DAMP -> Damping (only for ISOLV= 2)."""))
        self.ui.btnNSetHelp.clicked.connect(lambda: self.webWid.setHtml(open(opHtml('weighting.html'), 'r').read()))

        self.ui.tableVel.setColumnCount(6)
        self.ui.tableVel.resizeColumnsToContents()
        self.ui.tableNSet.resizeColumnsToContents()
        top = [0.0, 1.0, 3.0, 6.0, 14.0, 25.0]
        vel = [3.77, 4.64, 5.34, 5.75, 6.22, 7.98]
        self.ui.lineVel.setText(str(len(top)))
        for i in range(len(top)):
            self.ui.tableVel.setItem(0,i,QtWidgets.QTableWidgetItem(str(top[i])))
            self.ui.tableVel.setItem(1,i,QtWidgets.QTableWidgetItem(str(vel[i])))
    
    def onTDW_checkClicked(self):
        necessary_files = [
            'dt.cc', 'dt.ct', 'event.sel', 'station.dat'
        ]

        for i, name in enumerate(necessary_files):
            if os.path.isfile(os.path.join(self.tDW_lineEdit.text(), name)):
                self.dictInOut[name].setChecked(True)
                if name == 'station.dat':
                    with open(os.path.join(self.tDW_lineEdit.text(), name)) as f:
                        data = f.readlines()
                        data = [line for line in data if line != []]
                        self.ui.textMsg.appendPlainText(f'[msg] stations = {len(data)}')
                if name == 'event.sel':
                    with open(os.path.join(self.tDW_lineEdit.text(), name)) as f:
                        data = f.readlines()
                        data = [line.split() for line in data if line.split() != []]
                        self.ui.textMsg.appendPlainText(f'[msg] events = {len(data)}')
            else:
                self.dictInOut[name].setChecked(False)
    
    def onTDW_checkPh2dtClicked(self):
        necessary_files = [
            'station.dat', 'phase.dat'
        ]

        for i, name in enumerate(necessary_files):
            if os.path.isfile(os.path.join(self.tDW_lineEditPh2dt.text(), name)):
                self.dictInOutPh2dt[name].setChecked(True)
                if name == 'station.dat':
                    with open(os.path.join(self.tDW_lineEditPh2dt.text(), name)) as f:
                        data = f.readlines()
                        data = [line for line in data if line != []]
                        self.ui.textMsg.appendPlainText(f'[msg] stations = {len(data)}')
                if name == 'phase.dat':
                    with open(os.path.join(self.tDW_lineEditPh2dt.text(), name)) as f:
                        data = f.readlines()
                        data = [line.split() for line in data if line.split() != []]
                        evs = [line for line in data if line[0] == '#']
                        stpair_p = []
                        stpair_s = []
                        ipp, iss = [0, 0]
                        for il, line in enumerate(data):
                            if line[0] == '#' or il == (len(data) - 1):
                                stpair_p.append(ipp)
                                stpair_s.append(iss)
                                ipp, iss = [0, 0]
                            else:
                                if line[-1] == 'P': ipp += 1
                                else: iss += 1
                        stpair_p, stpair_s = [stpair_p[1::], stpair_s[1::]]
                        self.ui.textMsg.appendPlainText(f'[msg] events = {len(evs)}')
                        self.ui.textMsg.appendPlainText(f'[msg] min. P for an event = {min(stpair_p)}')
                        self.ui.textMsg.appendPlainText(f'[msg] max. P for an event = {max(stpair_p)}')
                        self.ui.textMsg.appendPlainText(f'[msg] min. S for an event = {min(stpair_s)}')
                        self.ui.textMsg.appendPlainText(f'[msg] max. S for an event = {max(stpair_s)}')

            else:
                self.dictInOutPh2dt[name].setChecked(False)

    def tDW_lineEditChanged(self):
        if self.tDW_lineEdit.text() != "" and os.path.isdir(self.tDW_lineEdit.text()):
            self.tDW_check.setEnabled(True)
            self.ui.btnRun.setEnabled(True)
            self.ui.btnCompRun.setEnabled(True)
        else:
            self.tDW_check.setEnabled(False)
            self.ui.btnRun.setEnabled(False)
            self.ui.btnCompRun.setEnabled(False)
    
    def tDW_lineEditPh2dtChanged(self):
        if self.tDW_lineEditPh2dt.text() != "" and os.path.isdir(self.tDW_lineEditPh2dt.text()):
            self.tDW_checkPh2dt.setEnabled(True)
            self.ui.btnRunPh2dt.setEnabled(True)
            self.ui.btnCompRunPh2dt.setEnabled(True)
        else:
            self.tDW_checkPh2dt.setEnabled(False)
            self.ui.btnRunPh2dt.setEnabled(False)
            self.ui.btnCompRunPh2dt.setEnabled(False)

    def onTDW_browseClicked(self):
        dir = str(QtWidgets.QFileDialog.getExistingDirectory(self, "select a target directory"))
        self.tDW_lineEdit.setText(dir)
        self.params["relocate_dir"] = dir
        if dir != "" and os.path.isdir(dir):
            self.tDW_check.setEnabled(True)
            self.ui.btnRun.setEnabled(True)
            self.ui.btnCompRun.setEnabled(True)
        else:
            self.tDW_check.setEnabled(False)
            self.ui.btnRun.setEnabled(False)
            self.ui.btnCompRun.setEnabled(False)
    
    def onTDW_browsePh2dtClicked(self):
        dir = str(QtWidgets.QFileDialog.getExistingDirectory(self, "select a target directory"))
        self.tDW_lineEditPh2dt.setText(dir)
        self.params["ph2dt_dir"] = dir
        if dir != "" and os.path.isdir(dir):
            self.tDW_checkPh2dt.setEnabled(True)
            self.ui.btnRunPh2dt.setEnabled(True)
            self.ui.btnCompRunPh2dt.setEnabled(True)
        else:
            self.tDW_checkPh2dt.setEnabled(False)
            self.ui.btnRunPh2dt.setEnabled(False)
            self.ui.btnCompRunPh2dt.setEnabled(False)

    def onItemPh2dtClicked(self, item, column):
        prevFlags = item.flags()
        if column == 0:
            item.setFlags(prevFlags & ~QtCore.Qt.ItemIsEditable)
            if item.text(0) == "Target Directory":
                self.ui.textHelp.setPlainText("""The directory must contain 'station.dat' and 'phase.dat'""")
            
            if item.text(0) == "station.dat":
                self.ui.textHelp.setPlainText("""Station input (e.g. station.dat)
This file stores station location information. File is in free format.
One station per line, in either 1) decimal degree format: 
STA, LAT, LON
For example: ABC 35.5000 –122.3333

or in 2) degrees and minutes: 
STA, LAT-DEG:LAT-MIN, LON-DEG:LON-MIN 
For example: ABC 35:30 –122:20

Parameter Description: 
STA Station label.""")
                self.webWid.setHtml(open(opHtml('station_dat.html'), 'r').read())

            if item.text(0) == "phase.dat":
                self.ui.textHelp.setPlainText("""Catalog (absolute) travel time data (e.g. file phase.dat)
This file includes travel time information for P- and S-waves for each earthquake. All fields are separated by spaces and can be read in free format.
ph2dt accepts hypocenter, followed by its travel time data in the following format: 
#, YR, MO, DY, HR, MN, SC, LAT, LON, DEP, MAG, EH, EZ, RMS, ID
followed by nobs lines of observations: 
STA, TT, WGHT, PHA

Parameter Description:
’#’ -> Event pair flag.
YR, MO, DY -> Origin data (4-digit year, month, day).
HR, MI, SC -> Origin time (hour, minute, second).
LAT, LON, DEP -> Latitude (degrees N), longitude (degrees E), depth (km).
MAG -> Magnitude
EH, EZ -> Horizontal error, depth error (km). Set to 0 in not available.
RMS -> RMS travel time residual. Set to 0 if not available.
ID -> Event ID. Each event must have a unique event ID.
STA -> Station label.
TT -> Absolute travel time from event to station STA.
WGHT -> Weight assigned to the time pick. They have values between 1 (best) and 0 (worst). Weights less than 10-5 are not used. Ph2dt uses negative values of WGHT as a flag indicating that this reading should be selected. This is useful in insuring that critical data for constraining the hypocenter are retained, even if of relatively low quality. PHA Phase (P = P-wave; S = S-wave).""")
            if item.text(0) == "dt.ct":
                self.ui.textHelp.setPlainText("""Catalog travel time input (e.g. file dt.ct)
This file stores absolute travel times from earthquake catalogs for pairs of earthquakes.
Each event pair is listed by a header line (in free format)
#, ID1, ID2
followed by nobs lines of observations (in free format):
STA, TT1, TT2, WGHT, PHA

Parameter Description: 
’#’ -> Event pair flag. 
ID1, ID2 -> ID of event 1, event 2 
STA -> Station label
TT1, TT2 -> Absolute travel time from event 1, event 2 to station STA. 
WGHT -> Weight of the time pick (0-1). 
PHA -> Phase (P = P-wave; S = S-wave).""")
            if item.text(0) == "event.dat":
                self.ui.textHelp.setPlainText("""A summary of all events""")
            if item.text(0) == "event.sel":
                self.ui.textHelp.setPlainText("""A summary of selected events""")
            
            if item.text(0) == "Max number of events":
                self.ui.textHelp.setPlainText("""MEV:   Max number of events.""")
            if item.text(0) == "Max number of stations":
                self.ui.textHelp.setPlainText("""MSTA:  Max number of stations.""")
            if item.text(0) == "Max number of phases (P&S) per event":
                self.ui.textHelp.setPlainText("""MOBS:  Max number of phases (P&S) per event""")
            
            if item.text(0) == "Min pick weight":
                self.ui.textHelp.setPlainText("""(MINWGHT) Minimum pick weight [0 – 1 (best)]. 
Note that weights less than 10-5 are not considered in hypoDD""")
            if item.text(0) == "Max distance (km): event pair - station":
                self.ui.textHelp.setPlainText("""(MAXDIST) Maximum distance (in km) between event pair and station.""")
            if item.text(0) == "Max hypo separation between event pairs":
                self.ui.textHelp.setPlainText("""(MAXSEP) Max. hypocentral separation between event pairs in km.""")
            if item.text(0) == "Max number of neighbors per event":
                self.ui.textHelp.setPlainText("""(MAXNGH) Max. number of neighbors per event.""")
            if item.text(0) == "Min number of links to define a neighbor":
                self.ui.textHelp.setPlainText("""(MINLNK) Min. number of links required to define a neighbor.""")
            if item.text(0) == "Min number of links per pair saved":
                self.ui.textHelp.setPlainText("""(MINOBS) Min. number of links per pair saved.""")
            if item.text(0) == "Max number of links per pair saved":
                self.ui.textHelp.setPlainText("""(MAXOBS) Max. number of links per pair saved (ordered by distance from event pair).""")
            
        else:
            item.setFlags(prevFlags | QtCore.Qt.ItemIsEditable)

    def onItemClicked(self, item, column):
        prevFlags = item.flags()
        if column == 0:
            item.setFlags(prevFlags & ~QtCore.Qt.ItemIsEditable)
            if item.text(0) == "Data Type":
                self.ui.textHelp.setPlainText("""Data Type (IDAT)
1 = cross correlation data only 
2 = absolute (catalog) data only
3 = cross correlation & catalog""")
            if item.text(0) == "Phase Type":
                self.ui.textHelp.setPlainText("""Phase Type (IPHA)
1 = P-wave
2 = S-wave
3 = P-& S-wave""")
            if item.text(0) == "Max. distance: centroid - stations (km)":
                self.ui.textHelp.setPlainText("""Max. distance: centroid - stations (km) (DIST)
Max. distance between centroid of event cluster and stations.""")
            if item.text(0) == "Min. number of x-corr links":
                self.ui.textHelp.setPlainText("""Min. number of x-corr links (OBSCC) per event pair to form a continuous cluster.
0 = no clustering performed.
If IDAT = 3, the sum of OBSCC and OBSCT is taken and used for both.""")
            if item.text(0) == "Min. number of catalog links":
                self.ui.textHelp.setPlainText("""Min. number of catalog links (OBSCT) per event pair to form a continuous cluster.
0 = no clustering performed.
If IDAT = 3, the sum of OBSCC and OBSCT is taken and used for both.""")
            if item.text(0) == "Initial locations":
                self.ui.textHelp.setPlainText("""Initial locations (ISTART)
1 = start from cluster centroid; 2 = start from catalog locations.""")
            if item.text(0) == "Least squares solution":
                self.ui.textHelp.setPlainText("""Least squares solution (ISOLV)
1 = singular value decomposition (SVD)
2 = conjugate gradients (LSQR)""")
            if item.text(0) == "Index of cluster to be relocated":
                self.ui.textHelp.setPlainText("""Index of cluster to be relocated (CID) (0 = all).""")
            if item.text(0) == "vp/vs ratio":
                self.ui.textHelp.setPlainText("""vp/vs ratio (RATIO)
This ratio is constant for all layers.""")
            
            if item.text(0) == "Max number of events":
                self.ui.textHelp.setPlainText("""MAXEVE: Max number of events (must be at least the size of the number of events listed in the event file)""")
            if item.text(0) == "Max number of observations":
                self.ui.textHelp.setPlainText("""Max number of observations (must be at least the size of the number of observations).""")
            if item.text(0) == "Max number of events used for SVD":
                self.ui.textHelp.setPlainText("""MAXEVE0: Max number of events used for SVD. If only LSQR is used, MAXEVE0 can be set to 2 to free up memory.""")
            if item.text(0) == "Max number of observations used for SVD":
                self.ui.textHelp.setPlainText("""MAXDATA0: Max number of observations used for SVD. If only LSQR is used, MAXDATA0 can be set to 1 to free up memory.""")
            if item.text(0) == "Max number of model layers":
                self.ui.textHelp.setPlainText("""MAXLAY: Max number of model layers.""")
            if item.text(0) == "Max number of stations":
                self.ui.textHelp.setPlainText("""MAXSTA: Max number of stations.""")
            if item.text(0) == "Max number of clusters allowed":
                self.ui.textHelp.setPlainText("""MAXCL: Max number of clusters allowed.""")
            
            if item.text(0) == "Target Directory":
                self.ui.textHelp.setPlainText("""The directory must contain 'dt.cc', 'dt.ct', 'event.sel', and 'station.dat'""")
            if item.text(0) == "dt.cc":
                self.ui.textHelp.setPlainText("""Cross correlation differential time input (e.g. file dt.cc)
This file stores differential travel times from cross correlation for pairs of earthquakes.
Each event pair is listed by a header line (in free format) 
#, ID1, ID2, OTC
followed by lines with observations (in free format): 
STA, DT, WGHT, PHA

Parameter Description: 
’#’ -> Event pair flag. 
ID1, ID2 -> ID of event 1, event 2. 
OTC -> Origin time correction relative to the event origin time reported in the catalog data. If not known for all available data, then cross correlation data can not be used in combination with catalog data. Set OTC to -999 if not known for individual observations; Set to 0.0 if cross-correlation and catalog origin times are identical, or if only cross-correlation data is used.
STA -> Station label.
DT -> Differential time (s) between event 1 and event 2 at station STA. DT = T1-T2.
WGHT -> Weight of measurement (0 -1; e.g. squared coherency).
PHA -> Phase (P = P-wave; S = S-wave)""")
            if item.text(0) == 'dt.ct':
                self.ui.textHelp.setPlainText("""Catalog travel time input (e.g. file dt.ct)
This file stores absolute travel times from earthquake catalogs for pairs of earthquakes.
Each event pair is listed by a header line (in free format)
#, ID1, ID2
followed by nobs lines of observations (in free format):
STA, TT1, TT2, WGHT, PHA

Parameter Description: 
’#’ -> Event pair flag. 
ID1, ID2 -> ID of event 1, event 2 
STA -> Station label
TT1, TT2 -> Absolute travel time from event 1, event 2 to station STA. 
WGHT -> Weight of the time pick (0-1). 
PHA -> Phase (P = P-wave; S = S-wave).""")
            if item.text(0) == 'event.sel':
                self.ui.textHelp.setPlainText("""Initial hypocenter input (e.g. file event.dat)
This file stores the initial hypocenter locations. Lines are written in fixed format by the program ph2dt. This makes locating fields such as parts of the date and time easier. Lines are read in free format by hypoDD, however.
One event per line:
DATE, TIME, LAT, LON, DEP, MAG, EH, EV, RMS, ID

Parameter Description: 
DATE -> Concatenated origin date (YYYYMMDD; year, month and day). 
TIME -> Concatenated origin time (HHMMSSSS; hour, minute and seconds). 
LAT, LON, DEP -> Latitude, longitude, depth (km). 
MAG -> Magnitude (set to 0.0 if not available). 
EH, EV -> Horizontal and vertical error (km) of original location (set to 0.0 if not available). 
RMS -> Residual rms (s) (set to 0.0 is not available). 
ID -> Event identification.""")
            if item.text(0) == 'station.dat':
                self.ui.textHelp.setPlainText("""Station input (e.g. station.dat)
This file stores station location information. File is in free format.
One station per line, in either 1) decimal degree format: 
STA, LAT, LON
For example: ABC 35.5000 –122.3333

or in 2) degrees and minutes: 
STA, LAT-DEG:LAT-MIN, LON-DEG:LON-MIN 
For example: ABC 35:30 –122:20

Parameter Description: 
STA Station label.""")
            if item.text(0) == 'hypoDD.loc':
                self.ui.textHelp.setPlainText("""Initial hypocenter output (e.g. file hypoDD.loc)
One event per line (written in fixed, but may be read in free format): 
ID, LAT, LON, DEPTH, X, Y, Z, EX, EY, EZ, YR, MO, DY, HR, MI, SC, MAG, CID

Parameter Description: 
ID -> Event identification. 
LAT, LON, DEP -> Latitude, longitude (decimal degrees), depth (km). 
X, Y, Z -> East-west, north-south, depth location (m) relative to cluster centroid. 
EX, EY, EZ -> East-west, north-south, depth error (m). 
YR, MO, DY -> Origin data (year, month, day). 
HR, MI, SC -> Origin time (hour, minute, second). 
MAG -> Magnitude 
CID -> Cluster index.""")
            if item.text(0) == 'hypoDD.reloc':
                self.ui.textHelp.setPlainText("""Relocated hypocenter output (e.g. file hypoDD.reloc)
One event per line (written in fixed, but may be read in free format): 
ID, LAT, LON, DEPTH, X, Y, Z, EX, EY, EZ, YR, MO, DY, HR, MI, SC, MAG, NCCP, NCCS, NCTP, NCTS, RCC, RCT, CID

Parameter Description: 
ID -> Event identification. 
LAT, LON, DEP -> Latitude, Longitude (decimal degrees), Depth (km). 
X, Y, Z -> East-west, north-south, depth location (m) relative to cluster centroid. 
EX, EY, EZ -> East-west, north-south, depth error (m). NOT MEANINGFUL if computed with LSQR (see Paige and Saunders) 
YR, MO, DY -> Origin data (year, month, day).
HR, MI, SC -> Origin time (hour, minute, second).
MAG -> Magnitude
NCCP, NCCS -> Number of cross-correlated P-and S-wave data.
NCTP, NCTS -> Number of catalog P-and S-wave data.
RCC, RCT -> Rms residual for cross-correlated, catalog data.
CID -> Cluster index.

Note: If CID in the control file is set to 0, hypoDD relocates all possible clusters, one after the other, and reports the relocated events with an index CID of the corresponding cluster. In this case, the cartesian coordinates X, Y, and Z are relative to the centroid of each cluster and do not describe the relative distance between the clusters. The events are represented in a global coordinate system only by LAT, LON, DEP.

Results for each iteration and each cluster are stored in files named hypoDD.reloc.c.i, where c is the cluster number and i is the iteration number. You can relocate an individual cluster if you only want its set of converging relocation files.""")
            if item.text(0) == 'hypoDD.sta':
                self.ui.textHelp.setPlainText("""Station residual output (e.g. file hypoDD.sta)
Output of this file is optional. One station per line:
STA, LAT, LON, DIST (NA), AZ (NA), NCCP, NCCS, NCTP, NCTS, RCC, RCT, CID

Parameter Description: 
STA -> Station label 
LAT, LON -> Latitude, longitude 
DIST, AZ -> Distance [m] and azimuth between cluster centroid and station. 
NCCP, NCCS -> Number of cross–correlation P-, S-phases recorded. 
NCTP, NCTS -> Number of catalog P-, S-phases recorded. 
RCC, RCT -> Residual rms (s) for cross-correlation, catalog data. 
CID -> Cluster index.

Note: This information is only written out for the last iteration. DIST and AZ are not calculated by hypoDD and these values are set to 0.0.""")
            if item.text(0) == 'hypoDD.res':
                self.ui.textHelp.setPlainText("""Data residual output (e.g. file hypoDD.res)
Output of this file is optional. One observation per line: 
STA, DT, ID1, ID2, IDX, WGHT, RES, WT, DIST

Parameter Description: 
STA -> Station label. 
DT -> Delay time. 
ID1, ID2 -> ID of event 1, event 2. 
IDX -> Data type (1=ccP; 2=ccS; 3=ctP; 4=ctS). 
WGHT -> A priori weight.
RES -> Data residual (ms).
WT -> Weight after last iteration.
DIST -> Inter-event distance (m).

Note: This information is only written out for the last iteration.""")
            if item.text(0) == 'hypoDD.src':
                self.ui.textHelp.setPlainText("""Takeoff angle output (e.g. file hypoDD.src)
File with takeoff angle and azimuth information for each relocated event. Can be used to recalculate focal mechanisms. Output of this file is optional.""")
        else:
            item.setFlags(prevFlags | QtCore.Qt.ItemIsEditable)

    def setParams(self):
        itemParamsFunc = lambda parent, loc, col: self.ui.treeParams.findItems(parent, QtCore.Qt.MatchFlag.MatchExactly)[0].child(loc).text(col)
        itemPh2dtFunc = lambda parent, loc, col: self.ui.treePh2dt.findItems(parent, QtCore.Qt.MatchFlag.MatchExactly)[0].child(loc).text(col)
        self.params['MAXEVE'] = int(itemParamsFunc("Compiler", 0, 1))
        self.params['MAXDATA'] = int(itemParamsFunc("Compiler", 1, 1))
        self.params['MAXEVE0'] = int(itemParamsFunc("Compiler", 2, 1))
        self.params['MAXDATA0'] = int(itemParamsFunc("Compiler", 3, 1))
        self.params['MAXLAY'] = int(itemParamsFunc("Compiler", 4, 1))
        self.params['MAXSTA'] = int(itemParamsFunc("Compiler", 5, 1))
        self.params['MAXCL'] = int(itemParamsFunc("Compiler", 6, 1))
        self.params['IDAT'] = self.dataTypeComboBox.currentIndex() + 1
        self.params['IPHA'] = self.phaseTypeComboBox.currentIndex() + 1
        self.params['DIST'] = float(itemParamsFunc("Relocator", 2, 1))
        self.params['OBSCC'] = int(itemParamsFunc("Relocator", 3, 1))
        self.params['OBSCT'] = int(itemParamsFunc("Relocator", 4, 1))
        self.params["MINDS"] = -999
        self.params["MAXDS"] = -999
        self.params["MAXGAP"] = -999
        self.params["ISTART"] = self.initialLocationComboBox.currentIndex() + 1
        self.params["ISOLV"] = self.LSComboBox.currentIndex() + 1
        self.params["NSET"] = int(self.ui.lineNSet.text()) if self.ui.lineNSet.text() != "" else 0
        self.params["IAQ"] = 2
        self.params["CID"] = int(itemParamsFunc("Relocator", 7, 1))
        self.params["ID"] = ""
        self.params["TOP"] = [float(self.ui.tableVel.item(0,i).text()) for i in range(int(self.ui.lineVel.text()))],
        self.params['TOP'] = self.params['TOP'][0]
        self.params["VEL"] = [float(self.ui.tableVel.item(1,i).text()) for i in range(int(self.ui.lineVel.text()))],
        self.params["VEL"] = self.params["VEL"][0]
        self.params["DATA_WEIGHTING_AND_REWEIGHTING"] = [[self.ui.tableNSet.item(j,i).text() for i in range(10)] for j in range(int(self.ui.lineNSet.text()))],
        self.params["DATA_WEIGHTING_AND_REWEIGHTING"] = self.params["DATA_WEIGHTING_AND_REWEIGHTING"][0]
        self.params['RATIO'] = float(itemParamsFunc("Relocator", 8, 1))
        self.params['relocate_dir'] = self.tDW_lineEdit.text()
        for i, name in enumerate(['dt.cc', 'dt.ct', 'event.sel', 'station.dat', 'hypoDD.loc', 'hypoDD.reloc', 'hypoDD.sta', 'hypoDD.res', 'hypoDD.src']):
            self.params["_".join(name.split('.'))] = name if self.dictInOut[name].isChecked() else ""
        self.params["ph2dt_dir"] = self.tDW_lineEditPh2dt.text()
        for i, name in enumerate(['station.dat', 'phase.dat', 'dt.ct', 'event.dat', 'event.sel']):
            self.params["_".join(name.split('.') + ['ph2dt'])] = name if self.dictInOutPh2dt[name].isChecked() else ""
        self.params['MEV_ph2dt'] = int(itemPh2dtFunc("Compiler", 0, 1))
        self.params['MSTA_ph2dt'] = int(itemPh2dtFunc("Compiler", 1, 1))
        self.params['MOBS_ph2dt'] = int(itemPh2dtFunc("Compiler", 2, 1))
        self.params['MINWGHT_ph2dt'] = int(itemPh2dtFunc("Run", 0, 1))
        self.params['MAXDIST_ph2dt'] = int(itemPh2dtFunc("Run", 1, 1))
        self.params['MAXSEP_ph2dt'] = int(itemPh2dtFunc("Run", 2, 1))
        self.params['MAXNGH_ph2dt'] = int(itemPh2dtFunc("Run", 3, 1))
        self.params['MINLNK_ph2dt'] = int(itemPh2dtFunc("Run", 4, 1))
        self.params['MINOBS_ph2dt'] = int(itemPh2dtFunc("Run", 5, 1))
        self.params['MAXOBS_ph2dt'] = int(itemPh2dtFunc("Run", 6, 1))
    
    def actionOpen_hypoDD_inpClicked(self):
        itemParamsFunc = lambda parent, loc, col, txt: self.ui.treeParams.findItems(parent, QtCore.Qt.MatchFlag.MatchExactly)[0].child(loc).setText(col, txt)
        filename = str(QtWidgets.QFileDialog.getOpenFileName(self, "Open text file", 'c:\\', "All Files (*.inp)")[0])
        if filename != "":
            with open(filename, 'r') as f:
                content = f.readlines()
                content = [line.split() for line in content if line[0] != "*"]
                content = [line for line in content if (line == [] or line[0] != "*")]
            n = 0
            for i, name in enumerate(['dt.cc', 'dt.ct', 'event.sel', 'station.dat', 'hypoDD.loc', 'hypoDD.reloc', 'hypoDD.sta', 'hypoDD.res', 'hypoDD.src']):
                n = i
                self.dictInOut[name].setChecked(True if content[n] != [] else False)
            
            n += 1
            self.dataTypeComboBox.setCurrentIndex(int(content[n][0]) - 1) 
            self.phaseTypeComboBox.setCurrentIndex(int(content[n][1]) - 1)
            itemParamsFunc("Relocator", 2, 1, content[n][2])

            n += 1
            itemParamsFunc("Relocator", 3, 1, content[n][0])
            itemParamsFunc("Relocator", 4, 1, content[n][1])

            n += 1
            self.initialLocationComboBox.setCurrentIndex(int(content[n][0]) - 1)
            self.LSComboBox.setCurrentIndex(int(content[n][1]) - 1)
            self.ui.lineNSet.setText(content[n][2])

            n += 1
            nn = 0
            r = 0
            for i in range(n, len(content)):
                nn = i
                if len(content[i]) == 10:
                    # for j in range(10):
                        # self.ui.tableNSet.item(r,j).setText(content[i][j])
                    r += 1
                else: break

            self.ui.tableNSet.setRowCount(r)
            for i in range(r):
                for j in range(10):
                    self.ui.tableNSet.setItem(i,j, QtWidgets.QTableWidgetItem(content[n + i][j]))
                    # self.ui.tableNSet.item(i,j).setText(content[n + i][j])

            n = nn
            nlay = int(content[n][0])
            itemParamsFunc("Relocator", 8, 1, content[n][1])

            n += 1
            self.ui.tableVel.setColumnCount(nlay)
            self.ui.lineVel.setText(str(nlay))
            for i in range(nlay):
                self.ui.tableVel.setItem(0,i, QtWidgets.QTableWidgetItem(content[n][i]))
                self.ui.tableVel.setItem(1,i, QtWidgets.QTableWidgetItem(content[n + 1][i]))
                # self.ui.tableVel.item(0,i).setText(content[n][i])
                # self.ui.tableVel.item(1,i).setText(content[n + 1][i])
            self.ui.tableVel.resizeColumnsToContents()

            n += 2
            itemParamsFunc("Relocator", 7, 1, content[n][0])
    
    def actionOpen_ph2dt_inpClicked(self):
        itemPh2dtFunc = lambda parent, loc, col, txt: self.ui.treePh2dt.findItems(parent, QtCore.Qt.MatchFlag.MatchExactly)[0].child(loc).setText(col, txt)
        filename = str(QtWidgets.QFileDialog.getOpenFileName(self, "Open text file", 'c:\\', "All Files (*.inp)")[0])
        if filename != "":
            with open(filename, 'r') as f:
                content = f.readlines()
                content = [line.split() for line in content if line[0] != "*"]
                content = [line for line in content if (line == [] or line[0] != "*")]
            n = 0
            for i, name in enumerate(['station.dat', 'phase.dat']):
                n = i
                self.dictInOutPh2dt[name].setChecked(True if content[n] != [] else False)
            
            n += 1
            itemPh2dtFunc("Run", 0, 1,content[n][0])
            itemPh2dtFunc("Run", 1, 1,content[n][1])
            itemPh2dtFunc("Run", 2, 1,content[n][2])
            itemPh2dtFunc("Run", 3, 1,content[n][3])
            itemPh2dtFunc("Run", 4, 1,content[n][4])
            itemPh2dtFunc("Run", 5, 1,content[n][5])
            itemPh2dtFunc("Run", 6, 1,content[n][6])

    def btnOpenVelClicked(self):
        filename = self.ui.lineSearchVel.text()
        if filename != "" and os.path.isfile(filename):
            with open(filename, 'r') as f:
                content = f.readlines()
                content = [line.split() for line in content if line[0] != "*"]
                content = [line for line in content if (line != [] and line[0] != "*")]
            
            nlay = len(content)
            self.ui.tableVel.setColumnCount(nlay)
            self.ui.lineVel.setText(str(nlay))
            for i in range(nlay):
                self.ui.tableVel.setItem(0,i, QtWidgets.QTableWidgetItem(content[i][0]))
                self.ui.tableVel.setItem(1,i, QtWidgets.QTableWidgetItem(content[i][1]))
                # self.ui.tableVel.item(0,i).setText(content[n][i])
                # self.ui.tableVel.item(1,i).setText(content[n + 1][i])
            self.ui.tableVel.resizeColumnsToContents()


    def onBtnCompileClicked(self):
        self.setParams()
        self.hypoDDThread = QtCore.QThread()
        self.hypoDDWorker = HypoDDWorker(self.params)
        self.hypoDDWorker.moveToThread(self.hypoDDThread)
        self.hypoDDThread.started.connect(self.hypoDDWorker.compile)
        self.hypoDDWorker.finished.connect(self.hypoDDThread.quit)
        self.hypoDDWorker.finished.connect(self.hypoDDWorker.deleteLater)
        self.hypoDDThread.finished.connect(self.hypoDDThread.deleteLater)
        self.hypoDDWorker.progressOut.connect(self.ui.textStdout.appendPlainText)
        self.hypoDDWorker.progressErr.connect(self.ui.textStderr.appendPlainText)
        self.hypoDDWorker.progressMsg.connect(self.ui.textMsg.appendPlainText)
        self.hypoDDThread.start()
    
    def onBtnCompilePh2dtClicked(self):
        self.setParams()
        self.ph2dtThread = QtCore.QThread()
        self.ph2dtWorker = Ph2dtWorker(self.params)
        self.ph2dtWorker.moveToThread(self.ph2dtThread)
        self.ph2dtThread.started.connect(self.ph2dtWorker.compile)
        self.ph2dtWorker.finished.connect(self.ph2dtThread.quit)
        self.ph2dtWorker.finished.connect(self.ph2dtWorker.deleteLater)
        self.ph2dtThread.finished.connect(self.ph2dtThread.deleteLater)
        self.ph2dtWorker.progressOut.connect(self.ui.textStdout.appendPlainText)
        self.ph2dtWorker.progressErr.connect(self.ui.textStderr.appendPlainText)
        self.ph2dtWorker.progressMsg.connect(self.ui.textMsg.appendPlainText)
        self.ph2dtThread.start()
    
    def onBtnRunClicked(self):
        self.setParams()
        self.hypoDDRunProcess = QtCore.QProcess()
        self.hypoDDRunProcess.readyReadStandardOutput.connect(
            lambda: self.ui.textStdout.appendPlainText(
                buffer_to_str(self.hypoDDRunProcess.readAllStandardOutput())
                ))
        self.hypoDDRunProcess.readyReadStandardError.connect(
            lambda: self.ui.textStderr.appendPlainText(
                buffer_to_str(self.hypoDDRunProcess.readAllStandardError())
                ))
        self.hypoDDRunProcess.finished.connect(lambda: self.ui.textMsg.appendPlainText('[msg] FINISHED . . .'))  # Clean up once complete.
        newHypoDD = hypoDDrelocate( working_dir=self.params["relocate_dir"],
                                stdout_function = self.ui.textStdout.appendPlainText, 
                                stderr_function = self.ui.textStderr.appendPlainText, 
                                msg_function = self.ui.textMsg.appendPlainText)
        newHypoDD.configure_hypodd(**self.params)
        self.hypoDDRunProcess.setWorkingDirectory(self.params["relocate_dir"])
        self.hypoDDRunProcess.start(newHypoDD.relocate_hypodd())
        # self.hypoDDRunThread = QtCore.QThread()
        # self.hypoDDRunWorker = HypoDDWorker(self.params)
        # self.hypoDDRunWorker.moveToThread(self.hypoDDRunThread)
        # self.hypoDDRunThread.started.connect(self.hypoDDRunWorker.relocate)
        # self.hypoDDRunWorker.finished.connect(self.hypoDDRunThread.quit)
        # self.hypoDDRunWorker.finished.connect(self.hypoDDRunWorker.deleteLater)
        # self.hypoDDRunThread.finished.connect(self.hypoDDRunThread.deleteLater)
        # self.hypoDDRunWorker.progressOut.connect(self.ui.textStdout.appendPlainText)
        # self.hypoDDRunWorker.progressErr.connect(self.ui.textStderr.appendPlainText)
        # self.hypoDDRunWorker.progressMsg.connect(self.ui.textMsg.appendPlainText)
        # self.hypoDDRunThread.start()
    
    def onBtnRunPh2dtClicked(self):
        self.setParams()
        self.ph2dtRunProcess = QtCore.QProcess()
        self.ph2dtRunProcess.readyReadStandardOutput.connect(
            lambda: self.ui.textStdout.appendPlainText(
                buffer_to_str(self.ph2dtRunProcess.readAllStandardOutput())
                ))
        self.ph2dtRunProcess.readyReadStandardError.connect(
            lambda: self.ui.textStderr.appendPlainText(
                buffer_to_str(self.ph2dtRunProcess.readAllStandardError())
                ))
        self.ph2dtRunProcess.finished.connect(lambda: self.ui.textMsg.appendPlainText('[msg] FINISHED . . .'))  # Clean up once complete.
        newPh2dt = ph2dtRun(working_dir=self.params["ph2dt_dir"],
                                stdout_function = self.ui.textStdout.appendPlainText, 
                                stderr_function = self.ui.textStderr.appendPlainText, 
                                msg_function = self.ui.textMsg.appendPlainText)
        newPh2dt.configure_ph2dt(**self.params)
        self.ph2dtRunProcess.setWorkingDirectory(self.params["ph2dt_dir"])
        self.ph2dtRunProcess.start(newPh2dt.run_ph2dt())

        # self.ph2dtRunThread = QtCore.QThread()
        # self.ph2dtRunWorker = Ph2dtWorker(self.params)
        # self.ph2dtRunWorker.moveToThread(self.ph2dtRunThread)
        # self.ph2dtRunThread.started.connect(self.ph2dtRunWorker.run)
        # self.ph2dtRunWorker.finished.connect(self.ph2dtRunThread.quit)
        # self.ph2dtRunWorker.finished.connect(self.ph2dtRunWorker.deleteLater)
        # self.ph2dtRunThread.finished.connect(self.ph2dtRunThread.deleteLater)
        # self.ph2dtRunWorker.progressOut.connect(self.ui.textStdout.appendPlainText)
        # self.ph2dtRunWorker.progressErr.connect(self.ui.textStderr.appendPlainText)
        # self.ph2dtRunWorker.progressMsg.connect(self.ui.textMsg.appendPlainText)
        # self.ph2dtRunThread.start()
    
    def onBtnCompRunClicked(self):
        self.setParams()
        self.hypoDDThread = QtCore.QThread()
        self.hypoDDWorker = HypoDDWorker(self.params)
        self.hypoDDWorker.moveToThread(self.hypoDDThread)
        self.hypoDDThread.started.connect(self.hypoDDWorker.compile)
        self.hypoDDWorker.finished.connect(self.hypoDDThread.quit)
        self.hypoDDWorker.finished.connect(self.onBtnRunClicked)
        self.hypoDDWorker.finished.connect(self.hypoDDWorker.deleteLater)
        self.hypoDDThread.finished.connect(self.hypoDDThread.deleteLater)
        self.hypoDDWorker.progressOut.connect(self.ui.textStdout.appendPlainText)
        self.hypoDDWorker.progressErr.connect(self.ui.textStderr.appendPlainText)
        self.hypoDDWorker.progressMsg.connect(self.ui.textMsg.appendPlainText)
        self.hypoDDThread.start()
    
    def onBtnCompRunPh2dtClicked(self):
        self.setParams()
        self.ph2dtThread = QtCore.QThread()
        self.ph2dtWorker = Ph2dtWorker(self.params)
        self.ph2dtWorker.moveToThread(self.ph2dtThread)
        self.ph2dtThread.started.connect(self.ph2dtWorker.compile)
        self.ph2dtWorker.finished.connect(self.ph2dtThread.quit)
        self.ph2dtWorker.finished.connect(self.onBtnRunPh2dtClicked)
        self.ph2dtWorker.finished.connect(self.ph2dtWorker.deleteLater)
        self.ph2dtThread.finished.connect(self.ph2dtThread.deleteLater)
        self.ph2dtWorker.progressOut.connect(self.ui.textStdout.appendPlainText)
        self.ph2dtWorker.progressErr.connect(self.ui.textStderr.appendPlainText)
        self.ph2dtWorker.progressMsg.connect(self.ui.textMsg.appendPlainText)
        self.ph2dtThread.start()
    
    def onBtnClearLogClicked(self):
        self.ui.textStdout.setPlainText("")
        self.ui.textStderr.setPlainText("")
        self.ui.textMsg.setPlainText("")
    
    def btn_bmkgConvertClicked(self):
        self.bmkgThread = QtCore.QThread()
        self.bmkgWorker = BmkgWorker(self.bmkg2pha.line_bmkgpath.text(), self.bmkg2pha.line_phasepath.text())
        self.bmkgWorker.moveToThread(self.bmkgThread)
        self.bmkgThread.started.connect(self.bmkgWorker.run)
        self.bmkgWorker.finished.connect(self.bmkgThread.quit)
        self.bmkgWorker.finished.connect(self.bmkgWorker.deleteLater)
        self.bmkgThread.finished.connect(self.bmkgThread.deleteLater)
        self.bmkgWorker.progressMsg.connect(self.ui.textMsg.appendPlainText)
        self.bmkgThread.start()
    
    def btn_iscConvertClicked(self):
        self.bmkgThread = QtCore.QThread()
        self.bmkgWorker = IscWorker(self.isc2pha.line_iscpath.text(), self.isc2pha.line_phasepath.text())
        self.bmkgWorker.moveToThread(self.bmkgThread)
        self.bmkgThread.started.connect(self.bmkgWorker.run)
        self.bmkgWorker.finished.connect(self.bmkgThread.quit)
        self.bmkgWorker.finished.connect(self.bmkgWorker.deleteLater)
        self.bmkgThread.finished.connect(self.bmkgThread.deleteLater)
        self.bmkgWorker.progressMsg.connect(self.ui.textMsg.appendPlainText)
        self.bmkgThread.start()

class HypoDDWorker(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    progressOut = QtCore.pyqtSignal(str)
    progressErr = QtCore.pyqtSignal(str)
    progressMsg = QtCore.pyqtSignal(str)

    def __init__(self, params, parent = None):
        super().__init__(parent)
        self.params = params

    def compile(self):
        newHypoDD = hypoDDCompile(stdout_function = self.progressOut.emit, 
                                  stderr_function = self.progressErr.emit, 
                                  msg_function = self.progressMsg.emit)
        newHypoDD.configure_hypodd(**self.params)
        newHypoDD.compile_hypodd()
        self.finished.emit()
    
    def relocate(self):
        newHypoDD = hypoDDrelocate( working_dir=self.params["relocate_dir"],
                                    stdout_function = self.progressOut.emit, 
                                    stderr_function = self.progressErr.emit, 
                                    msg_function = self.progressMsg.emit)
        newHypoDD.configure_hypodd(**self.params)
        newHypoDD.relocate_hypodd()
        self.finished.emit()

class Ph2dtWorker(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    progressOut = QtCore.pyqtSignal(str)
    progressErr = QtCore.pyqtSignal(str)
    progressMsg = QtCore.pyqtSignal(str)

    def __init__(self, params, parent = None):
        super().__init__(parent)
        self.params = params

    def compile(self):
        newPh2dt = ph2dtCompile(stdout_function = self.progressOut.emit, 
                                  stderr_function = self.progressErr.emit, 
                                  msg_function = self.progressMsg.emit)
        newPh2dt.configure_ph2dt(**self.params)
        newPh2dt.compile_ph2dt()
        self.finished.emit()
    
    def run(self):
        newPh2dt = ph2dtRun(working_dir=self.params["ph2dt_dir"],
                                  stdout_function = self.progressOut.emit, 
                                  stderr_function = self.progressErr.emit, 
                                  msg_function = self.progressMsg.emit)
        newPh2dt.configure_ph2dt(**self.params)
        newPh2dt.run_ph2dt()
        self.finished.emit()

class BmkgWorker(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    progressMsg = QtCore.pyqtSignal(str)

    def __init__(self, filein, fileout, parent = None):
        super().__init__(parent)
        self.finout = [filein, fileout]
    
    def run(self):
        self.progressMsg.emit("[msg] BMKG to PHA converter is running...")
        main = bmkg2pha(self.finout[0])
        main.read()
        main.write(self.finout[1])
        self.progressMsg.emit("[msg] BMKG to PHA converter finished")
        self.finished.emit()

class IscWorker(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    progressMsg = QtCore.pyqtSignal(str)

    def __init__(self, filein, fileout, parent = None):
        super().__init__(parent)
        self.finout = [filein, fileout]
    
    def run(self):
        self.progressMsg.emit("[msg] ISC to PHA converter is running...")
        main = isc2pha(self.finout[0])
        main.read()
        main.write(self.finout[1])
        self.progressMsg.emit("[msg] ISC to PHA converter finished")
        self.finished.emit()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = MainHypoDD()
    main.show()
    sys.exit(app.exec_())