from PyQt5.QtCore import QModelIndex, QObject, pyqtSignal
from PyQt5.QtWidgets import QTreeView
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from clnt_socket import ClntSocket
from settings import *


class RemoteTree(QObject):
    def __init__(self, tv: QTreeView, clnt_socket: ClntSocket):
        super(RemoteTree, self).__init__()
        self.tv = tv
        self.clnt_socket = clnt_socket
        self.remote_model = QStandardItemModel()
        self.tv.header().hide()
        self.tv.setModel(self.remote_model)

    def ui_event_handle(self, msg):
        print("get a signal: ", msg)
        if msg[0] == HW_DATA_TYPE_LOGIN:
            for i in msg[2]:
                item = QStandardItem(i["name"])
                self.remote_model.appendRow(item)

        '''
        item1 = QStandardItem(CLNT_NAME)
        self.remote_model.appendRow(item1)
        recv_datas = ["root", "home", "tmp", "bin", "lib", "mnt"]
        for i in recv_datas:
            item1.appendRow(QStandardItem(i))
        '''

