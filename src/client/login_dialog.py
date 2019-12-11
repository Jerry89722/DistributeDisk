from PyQt5.QtCore import pyqtSignal, QTimer, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDialog, QMessageBox

from clnt_socket import ClntSocket
from login_ui import Ui_Login
from main_window import MainWindow
from settings import *


class LoginDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.timer = QTimer()
        self.ui = Ui_Login()
        self.ui.setupUi(self)
        self.ui.logoLab.setFixedSize(120, 120)
        logo = QPixmap(LOGO_PATH)
        logo = logo.scaled(self.ui.logoLab.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        self.ui.logoLab.setPixmap(logo)

        self.clnt_socket = ClntSocket()
        self.mw = MainWindow(self.clnt_socket)
        self.ui.signInBtn.clicked.connect(self.login_request)
        self.timer.timeout.connect(self.login_failed)
        self.clnt_socket.login_signal.connect(self.login_handle)

    def login_request(self):
        print("[%s] login with pwd[%s]..." % (self.ui.usernameLe.text(), self.ui.pwdLe.text()))
        self.clnt_socket.hw_cmd_login(self.ui.usernameLe.text(), self.ui.pwdLe.text())
        self.timer.start(10 * 1000)  # 10s

    def login_failed(self):
        QMessageBox.warning(self, "Warning", "LOGIN OVERTIME!!!", QMessageBox.Yes)

    def login_handle(self, result):
        if result is not None:
            if self.isHidden() is False:
                self.timer.stop()
                self.hide()

            self.mw.mw_update(result)
