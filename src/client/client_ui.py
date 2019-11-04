# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'client.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(778, 550)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.funcLayout = QtWidgets.QHBoxLayout()
        self.funcLayout.setObjectName("funcLayout")
        self.pathLayout = QtWidgets.QHBoxLayout()
        self.pathLayout.setSpacing(0)
        self.pathLayout.setObjectName("pathLayout")
        self.pathLab = QtWidgets.QLabel(self.centralwidget)
        self.pathLab.setObjectName("pathLab")
        self.pathLayout.addWidget(self.pathLab)
        self.pathLe = QtWidgets.QLineEdit(self.centralwidget)
        self.pathLe.setObjectName("pathLe")
        self.pathLayout.addWidget(self.pathLe)
        self.pathBtn = QtWidgets.QPushButton(self.centralwidget)
        self.pathBtn.setObjectName("pathBtn")
        self.pathLayout.addWidget(self.pathBtn)
        self.pathLayout.setStretch(1, 10)
        self.funcLayout.addLayout(self.pathLayout)
        self.searchLayout = QtWidgets.QHBoxLayout()
        self.searchLayout.setSpacing(0)
        self.searchLayout.setObjectName("searchLayout")
        self.searchLab = QtWidgets.QLabel(self.centralwidget)
        self.searchLab.setObjectName("searchLab")
        self.searchLayout.addWidget(self.searchLab)
        self.searchLe = QtWidgets.QLineEdit(self.centralwidget)
        self.searchLe.setObjectName("searchLe")
        self.searchLayout.addWidget(self.searchLe)
        self.searchBtn = QtWidgets.QPushButton(self.centralwidget)
        self.searchBtn.setObjectName("searchBtn")
        self.searchLayout.addWidget(self.searchBtn)
        self.searchLayout.setStretch(1, 10)
        self.funcLayout.addLayout(self.searchLayout)
        self.funcLayout.setStretch(0, 1)
        self.verticalLayout_2.addLayout(self.funcLayout)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.localLab = QtWidgets.QLabel(self.centralwidget)
        self.localLab.setObjectName("localLab")
        self.verticalLayout.addWidget(self.localLab)
        self.localFileTv = QtWidgets.QTreeView(self.centralwidget)
        self.localFileTv.setObjectName("localFileTv")
        self.verticalLayout.addWidget(self.localFileTv)
        self.remoteLab = QtWidgets.QLabel(self.centralwidget)
        self.remoteLab.setObjectName("remoteLab")
        self.verticalLayout.addWidget(self.remoteLab)
        self.remoteFileTv = QtWidgets.QTreeView(self.centralwidget)
        self.remoteFileTv.setObjectName("remoteFileTv")
        self.verticalLayout.addWidget(self.remoteFileTv)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.fileLv = QtWidgets.QListView(self.centralwidget)
        self.fileLv.setObjectName("fileLv")
        self.horizontalLayout.addWidget(self.fileLv)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 778, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pathLab.setText(_translate("MainWindow", "Path:"))
        self.pathBtn.setText(_translate("MainWindow", "Go"))
        self.searchLab.setText(_translate("MainWindow", "Key:"))
        self.searchBtn.setText(_translate("MainWindow", "search"))
        self.localLab.setText(_translate("MainWindow", "local files:"))
        self.remoteLab.setText(_translate("MainWindow", "remote files:"))
