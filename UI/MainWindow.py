# Form implementation generated from reading ui file 'UI\mainWindow.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(845, 250)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setContentsMargins(5, 5, 5, 5)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(0, -1, 0, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.camListLayout = QtWidgets.QVBoxLayout()
        self.camListLayout.setObjectName("camListLayout")
        self.camListLabel = QtWidgets.QLabel(self.centralwidget)
        self.camListLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.camListLabel.setObjectName("camListLabel")
        self.camListLayout.addWidget(self.camListLabel)
        self.camListArea = QtWidgets.QScrollArea(self.centralwidget)
        self.camListArea.setWidgetResizable(True)
        self.camListArea.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignTop)
        self.camListArea.setObjectName("camListArea")
        self.camList = QtWidgets.QWidget()
        self.camList.setGeometry(QtCore.QRect(0, 0, 201, 174))
        self.camList.setObjectName("camList")
        self.camListArea.setWidget(self.camList)
        self.camListLayout.addWidget(self.camListArea)
        self.horizontalLayout.addLayout(self.camListLayout)
        self.deviceInfoArea = QtWidgets.QScrollArea(self.centralwidget)
        self.deviceInfoArea.setWidgetResizable(True)
        self.deviceInfoArea.setObjectName("deviceInfoArea")
        self.deviceInfoList = QtWidgets.QWidget()
        self.deviceInfoList.setGeometry(QtCore.QRect(0, 0, 409, 195))
        self.deviceInfoList.setObjectName("deviceInfoList")
        self.deviceInfoArea.setWidget(self.deviceInfoList)
        self.horizontalLayout.addWidget(self.deviceInfoArea)
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName("verticalLayout")
        self.stopButton = QtWidgets.QPushButton(self.frame)
        self.stopButton.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stopButton.sizePolicy().hasHeightForWidth())
        self.stopButton.setSizePolicy(sizePolicy)
        self.stopButton.setAutoFillBackground(False)
        self.stopButton.setAutoDefault(False)
        self.stopButton.setDefault(False)
        self.stopButton.setFlat(False)
        self.stopButton.setObjectName("stopButton")
        self.verticalLayout.addWidget(self.stopButton)
        self.displayButton = QtWidgets.QPushButton(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.displayButton.sizePolicy().hasHeightForWidth())
        self.displayButton.setSizePolicy(sizePolicy)
        self.displayButton.setObjectName("displayButton")
        self.verticalLayout.addWidget(self.displayButton)
        self.recordButton = QtWidgets.QPushButton(self.frame)
        self.recordButton.setObjectName("recordButton")
        self.verticalLayout.addWidget(self.recordButton)
        self.horizontalLayout.addWidget(self.frame)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 2)
        self.horizontalLayout.setStretch(2, 1)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 845, 21))
        self.menubar.setNativeMenuBar(False)
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuEdit = QtWidgets.QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        self.menuView = QtWidgets.QMenu(self.menubar)
        self.menuView.setObjectName("menuView")
        self.menuProject = QtWidgets.QMenu(self.menubar)
        self.menuProject.setObjectName("menuProject")
        self.menuOperate = QtWidgets.QMenu(self.menubar)
        self.menuOperate.setObjectName("menuOperate")
        self.menuTools = QtWidgets.QMenu(self.menubar)
        self.menuTools.setObjectName("menuTools")
        self.menuWindow = QtWidgets.QMenu(self.menubar)
        self.menuWindow.setObjectName("menuWindow")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionNew = QtGui.QAction(MainWindow)
        self.actionNew.setObjectName("actionNew")
        self.actionOpen = QtGui.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionSave = QtGui.QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionSave)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuProject.menuAction())
        self.menubar.addAction(self.menuOperate.menuAction())
        self.menubar.addAction(self.menuTools.menuAction())
        self.menubar.addAction(self.menuWindow.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.camListLabel.setText(_translate("MainWindow", "Available Cameras"))
        self.stopButton.setText(_translate("MainWindow", "Stop"))
        self.displayButton.setText(_translate("MainWindow", "Display"))
        self.recordButton.setText(_translate("MainWindow", "Record"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuEdit.setTitle(_translate("MainWindow", "Edit"))
        self.menuView.setTitle(_translate("MainWindow", "View"))
        self.menuProject.setTitle(_translate("MainWindow", "Project"))
        self.menuOperate.setTitle(_translate("MainWindow", "Operate"))
        self.menuTools.setTitle(_translate("MainWindow", "Tools"))
        self.menuWindow.setTitle(_translate("MainWindow", "Window"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.actionNew.setText(_translate("MainWindow", "New"))
        self.actionOpen.setText(_translate("MainWindow", "Open"))
        self.actionSave.setText(_translate("MainWindow", "Save"))
