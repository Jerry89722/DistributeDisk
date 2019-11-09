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
        self.clnt_list = list()
        self.tv.clicked.connect(self.item_click)
        self.tv.expanded.connect(self.item_expand)
        '''
        item1 = QStandardItem("AAAA")
        self.remote_model.appendRow(item1)
        item2 = QStandardItem("aaaa")
        item1.appendRow(item2)

        item3 = QStandardItem("BBBB")
        self.remote_model.appendRow(item3)
        # item9 = QStandardItem("MMMM")
        # self.remote_model.appendRow(item9)
        item4 = QStandardItem("bbbb1")
        item3.appendRow(item4)
        item5 = QStandardItem("bbbb2")
        item3.appendRow(item5)
        # item6 = QStandardItem("bbbb3")
        # item3.appendRow(item6)
        print("aaaa: ", item3.rowCount())
        '''

    def ui_event_handle(self, msg):
        print("get a signal: ", msg)
        if msg[0] == HW_DATA_TYPE_LOGIN:
            for i in msg[2]:
                item = QStandardItem(i["name"])
                self.remote_model.appendRow(item)
                self.clnt_list.append(i)
                self.clnt_socket.hw_cmd_tree(i["cid"], "/")

        if msg[0] == HW_DATA_TYPE_CMD:
            if msg[2] == "tree":
                # recved_data = [data_type, cid, act["cmd"], act["path"], act["list"]]
                item = self.remote_model.findItems(self.get_name_by_cid(msg[1]))[0]
                if msg[3] == "/":
                    for m in msg[4]:
                        item.appendRow(QStandardItem(m))
                else:
                    tail_item = self.get_item_by_path(msg[3], item)
                    for m in msg[4]:
                        tail_item.appendRow(QStandardItem(m))

    def get_item_by_path(self, path: str, item: QStandardItem):
        item_name_list = path.strip('/').split('/')
        des_item = item
        for i in item_name_list:
            des_item = self.get_item_by_name(i, des_item)
            if des_item is None:
                return None
        return des_item

    @staticmethod
    def get_item_by_name(name: str, item: QStandardItem):
        cnt = item.rowCount()
        for i in range(cnt):
            if item.child(i).text() == name:
                return item.child(i)
        return None

    @staticmethod
    def get_full_path(item: QStandardItem):
        full_path = "/" + item.text() + "/"
        pitem = item
        while True:
            pitem = pitem.parent()
            if pitem is None:
                break
            full_path = "/" + pitem.text() + full_path
        return full_path

    def get_cid_by_name(self, name: str):
        for c in self.clnt_list:
            if c["name"] == name:
                return c["cid"]
        return 0

    def get_name_by_cid(self, cid: int):
        for c in self.clnt_list:
            if c["cid"] == cid:
                return c["name"]
        return None

    def item_click(self, index):
        item = self.remote_model.itemFromIndex(index)
        print("clicked: ", item.text())
        print("parent item: ", self.get_full_path(item))

    def item_expand(self, index):
        item = self.remote_model.itemFromIndex(index)
        for ic in range(item.rowCount()):
            print(item.child(ic).text())
            full_path = self.get_full_path(item.child(ic))
            print("tree get, full path: ", full_path)
            path_info = full_path.split('/', 2)
            print("clnt: %s, path: %s" % (path_info[-2], path_info[-1]))
            self.clnt_socket.hw_cmd_tree(self.get_cid_by_name(path_info[-2]), path_info[-1])

        '''
        item1 = QStandardItem(CLNT_NAME)
        self.remote_model.appendRow(item1)
        recv_datas = ["root", "home", "tmp", "bin", "lib", "mnt"]
        for i in recv_datas:
            item1.appendRow(QStandardItem(i))
        
        '''
