import time

from PyQt5.QtCore import QObject, Qt
from PyQt5.QtWidgets import QTreeView
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from clnt_socket import ClntSocket
from settings import *


class RemoteTree(QObject):
    def __init__(self, tv: QTreeView, clnt_socket: ClntSocket):
        super(RemoteTree, self).__init__()
        self.tv = tv
        self.clnt_socket = clnt_socket
        self.remote_model = QStandardItemModel(self)
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
        item9 = QStandardItem("MMMM")
        self.remote_model.appendRow(item9)
        item4 = QStandardItem("bbbb1")
        item3.appendRow(item4)
        item5 = QStandardItem("bbbb2")
        item3.appendRow(item5)
        item6 = QStandardItem("bbbb3")
        item3.appendRow(item6)
        print("aaaa: ", item3.rowCount())
        print("aa", len(self.remote_model.findItems("", flags=Qt.MatchContains)))
        '''

    def ui_event_handle(self, msg):
        print("get a signal: ", msg)
        if msg[0] == HW_DATA_TYPE_LOGIN:
            name_list = list()
            cid_list = list()
            for i in msg[2]:
                name_list.append(i["name"])
                cid_list.append(i["cid"])
                self.clnt_list.append(i)
            self.children_item_update(self.remote_model, name_list)
            for cid in cid_list:
                self.clnt_socket.hw_cmd_list("tree", cid, "/")

        if msg[0] == HW_DATA_TYPE_CMD:
            if msg[2] == "tree":
                # recved_data = [data_type, cid, act["cmd"], act["path"], act["list"]]
                root_item = self.remote_model.findItems(self.get_name_by_cid(msg[1]))[0]
                print("dest device item: ", root_item.text())  # dell
                tail_item = root_item
                if msg[3] is not "/":
                    tail_item = self.get_item_by_path(msg[3], root_item)
                print("tail item: ", tail_item.text())
                self.children_item_update(tail_item, msg[4])

    @staticmethod
    def children_item_update(item, name_list):
        item_type = type(item)

        children_item = list()
        if item_type == QStandardItemModel:
            children_item = item.findItems("", Qt.MatchContains)
        else:
            print("start update item: ", item.text())
            row_cnt = item.rowCount()
            for i in range(row_cnt):
                ic = item.child(i)
                if ic is None:
                    print("child item is None???")
                    continue
                children_item.append(ic)

        children = list()
        for child in children_item:
            child_name = child.text()
            children.append(child_name)
        print("children: ", children)

        for name in children:
            if name not in name_list:
                child_index = children.index(name)
                # print("child name: %s, index: %d" % (name, child_index))
                if item_type == QStandardItemModel:
                    item.takeChild(item.child(child_index))
                else:
                    item.takeChild(child_index)
        for name in name_list:
            if name not in children:
                item.appendRow(QStandardItem(name))
        print("children item update done")

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
        full_path = self.get_full_path(item)
        print("ls path: ", full_path)
        path_info = full_path.split('/', 2)
        print("clnt: %s, path: %s, path len: %d" % (path_info[1], path_info[2], len(path_info)))
        abs_path = "/" if len(path_info[2]) == 0 else path_info[2]
        self.clnt_socket.hw_cmd_list("ls", self.get_cid_by_name(path_info[1]), abs_path)

    def item_expand(self, index):
        item = self.remote_model.itemFromIndex(index)
        for ic in range(item.rowCount()):
            full_path = self.get_full_path(item.child(ic))
            print("expand path: ", full_path)
            path_info = full_path.split('/', 2)
            print("clnt: %s, path: %s, path len: %d" % (path_info[1], path_info[2], len(path_info)))
            abs_path = "/" if len(path_info[2]) == 0 else path_info[2]
            cid = self.get_cid_by_name(path_info[1])
            print("expand get tree list, abs path: %s, clint: %s, cid: %d" % (abs_path, path_info[1], cid))
            self.clnt_socket.hw_cmd_list("tree", cid, abs_path)

        '''
        item1 = QStandardItem(CLNT_NAME)
        self.remote_model.appendRow(item1)
        recv_datas = ["root", "home", "tmp", "bin", "lib", "mnt"]
        for i in recv_datas:
            item1.appendRow(QStandardItem(i))
        
        '''
