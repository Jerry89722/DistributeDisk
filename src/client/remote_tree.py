from PyQt5.QtCore import QModelIndex
from PyQt5.QtWidgets import QTreeView
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from clnt_socket import ClntSocket
from settings import *


class RemoteTree:
    def __init__(self, tv: QTreeView, clnt_socket: ClntSocket):
        self.tv = tv
        self.clnt_socket = clnt_socket
        self.remote_model = QStandardItemModel()
        self.tv.header().hide()
        self.tv.setModel(self.remote_model)

    def do_work(self):
        print("a")
        '''
        item1 = QStandardItem(CLNT_NAME)
        self.remote_model.appendRow(item1)
        recv_datas = ["root", "home", "tmp", "bin", "lib", "mnt"]
        for i in recv_datas:
            item1.appendRow(QStandardItem(i))
        '''

