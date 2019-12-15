import sys

from PyQt5.QtWidgets import QMainWindow
from client_ui import Ui_MainWindow
from local_tree import LocalTree
from remote_tree import RemoteTree
from file_view import FileView
from settings import *


class MainWindow(QMainWindow):
    def __init__(self, clnt_socket):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.clnt_socket = clnt_socket
        self.local_tree = LocalTree(self.ui.localFileTv)
        self.remote_tree = RemoteTree(self.ui.remoteFileTv, self.clnt_socket)
        self.file_tv = FileView(self.ui.fileTabView, self.clnt_socket)

        self.clnt_socket.mw_signal.connect(self.mw_update)

    def mw_update(self, ui_data):
        if self.isHidden():
            self.show()
        if ui_data[0] == HW_DATA_TYPE_LOGIN:
            # [data_type, cid, [{"name":"hp", "cid":1}, {"name":"dell", "cid":2}]]  login
            self.remote_tree.tree_view_update(ui_data)
        elif ui_data[0] == HW_DATA_TYPE_CMD:
            # [data_type, cid, cmd, path, list]     tree/list
            if ui_data[2] is "tree":
                self.remote_tree.tree_view_update(ui_data)
            else:
                self.file_tv.file_view_update(ui_data)
