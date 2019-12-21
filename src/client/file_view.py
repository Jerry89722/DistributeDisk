from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QTableView, QMenu

from clnt_socket import ClntSocket
from settings import *


class FileView(QObject):
    send_lv_msg = pyqtSignal(object)

    def __init__(self, file_tv: QTableView, clnt_socket: ClntSocket):
        super(FileView, self).__init__()
        self.cmd = ""
        self.from_cid = 0
        self.from_path = ""
        self.from_list = []
        self.cur_path = ""
        self.cur_cid = 0
        self.file_tv = file_tv
        self.clnt_socket = clnt_socket
        self.menu = QMenu()
        self.cut_opt = self.menu.addAction("cut")
        self.cp_opt = self.menu.addAction("copy")
        self.paste_opt = self.menu.addAction("paste")
        self.rm_opt = self.menu.addAction("remove")
        self.attr_opt = self.menu.addAction("attribution")
        self.item_model = None
        self.file_tv.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_tv.customContextMenuRequested.connect(self.custom_right_menu)
        self.file_tv.verticalHeader().setHidden(True)

        self.file_tv.clicked.connect(self.item_click)

        # self.item_model.setItem(0, 0, QStandardItem("file1"))
        # self.item_model.setItem(0, 1, QStandardItem("32k"))
        # self.item_model.setItem(1, 0, QStandardItem("file2"))
        # self.item_model.setItem(1, 1, QStandardItem("64k"))

    def switch_to_local(self, model, index):
        if self.item_model is not model:
            print("switch to local file view")
            self.item_model = model
            self.cur_cid = CLNT_ID
            self.file_tv.setModel(model)

        self.cur_path = self.item_model.filePath(index) + "/"
        self.file_tv.setRootIndex(index)

    def custom_right_menu(self, pos):
        print("right click, pos type: ", type(pos))
        cur = self.file_tv.currentIndex()
        if cur is None:
            return
        print("current index: ", cur)
        print("current file: ", cur.data())
        print("current path cid[%d]: %s" % (self.cur_cid, self.cur_path))
        action = self.menu.exec_(self.file_tv.mapToGlobal(pos))
        if action == self.cut_opt:
            print("cut: %s%s" % (self.cur_path, cur.data()))
            self.cmd = "mv"
            self.from_path = self.cur_path
            self.from_list = [cur.data()]
            return
        elif action == self.cp_opt:
            print("cp: %s%s" % (self.cur_path, cur.data()))
            self.cmd = "cp"
            self.from_cid = self.cur_cid
            self.from_path = self.cur_path
            self.from_list = [cur.data()]
            return
        elif action == self.paste_opt:
            print("paste: ", self.cur_path)
            # cid, cmd_str, sponsor_cid, from_path, from_list, to_path
            self.clnt_socket.hw_cmd_cp_mv(self.cur_cid, self.cmd,
                                          self.from_cid, self.from_path, self.from_list,
                                          self.cur_path)
            return
        elif action == self.rm_opt:
            print("rm: %s%s" % (self.cur_path, cur.data()))
            return
        elif action == self.attr_opt:
            print("attribution: %s%s" % (self.cur_path, cur.data()))
            return
        else:
            return

    def file_view_update(self, msg):
        print(msg)
        # msg:  [data_type, cid, act["cmd"], act["path"], act["list"]]
        data_type = msg[0]
        self.cur_cid = msg[1]
        cmd = msg[2]
        self.cur_path = msg[3]
        files = msg[4]
        i = 0
        if data_type == HW_DATA_TYPE_CMD:
            if cmd == "ls":
                self.item_model.removeRows(0, self.item_model.rowCount())
                for file in files:
                    self.item_model.setItem(i, 0, QStandardItem(file["name"]))
                    self.item_model.setItem(i, 1, QStandardItem(str(file["size"])))
                    i += 1

    def item_click(self, index):
        print("lv item clicked")
        if self.cur_cid == CLNT_ID:
            print("local file view")
            item = self.item_model.fileName(index)
        else:
            print("remote file view")
            item = self.item_model.itemFromIndex(index).text()
        print("lv item clicked: ", item)
