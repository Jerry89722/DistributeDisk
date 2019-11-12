from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QTableView

from settings import *


class FileView(QObject):
    send_lv_msg = pyqtSignal(object)

    def __init__(self, file_tv: QTableView):
        super(FileView, self).__init__()
        self.cur_path = ""
        self.cur_cid = 0
        self.file_tv = file_tv
        self.item_model = QStandardItemModel()
        self.item_model.setColumnCount(2)
        self.item_model.setHeaderData(0, Qt.Horizontal, "name")
        self.item_model.setHeaderData(1, Qt.Horizontal, "size")

        self.file_tv.setModel(self.item_model)
        self.file_tv.verticalHeader().setHidden(True)

        self.file_tv.clicked.connect(self.item_click)

        # self.item_model.setItem(0, 0, QStandardItem("file1"))
        # self.item_model.setItem(0, 1, QStandardItem("32k"))

    def ui_event_handle(self, msg):
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
                for file in files:
                    self.item_model.setItem(i, 0, QStandardItem(file["name"]))
                    self.item_model.setItem(i, 1, QStandardItem(str(file["size"])))
                    i += 1

    def item_click(self, index):
        item = self.item_model.itemFromIndex(index)
        print("lv item clicked: ", item.text())
