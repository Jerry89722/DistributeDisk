import socket
import struct
import sys
from builtins import len

from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication, QWidget, QTreeView, QAbstractItemView, QHeaderView

host = "www.huiwanit.cn"
port = 9001


class TreeView(QTreeView):
    def __init__(self):
        super().__init__()
        self.model = QStandardItemModel(4, 2)
        self.model.setHeaderData(0, Qt.Horizontal, "service")
        self.model.setHeaderData(1, Qt.Horizontal, "Details")
        '''
        item1 = QStandardItem("avahi-daemon")
        item2 = QStandardItem("bluetooth")
        item3 = QStandardItem("crond")
        item4 = QStandardItem("cups")
        item5 = QStandardItem("fifth")

        self.model.setItem(0, 0, item1)
        self.model.setItem(1, 0, item2)
        self.model.setItem(2, 0, item3)
        self.model.setItem(3, 0, item4)
        item4.appendRow(item5)

        parent = QModelIndex()
        for i in range(0, 4):
            parent = self.model.index(0, 0, parent)
            self.model.insertRows(0, 1, parent)
            self.model.insertColumns(0, 1, parent)
            index = self.model.index(0, 0, parent)
            self.model.setData(index, i)
        '''
        self.setModel(self.model)

    def returnTheItems(self):
        return self.model.findItems("*", Qt.MatchWildcard | Qt.MatchRecursive)
        # item1.setIcon()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            index0 = self.currentIndex()
            print(index0.data().toString())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    view = TreeView()
    # view.setEditTriggers(QAbstractItemView.NoEditTriggers)
    # view.header().setResizeMode(QHeaderView.ResizeToContents)
    # view.resize(300, 280)

    # view.setWindowTitle("linux manager")
    view.show()
    sys.exit(app.exec_())




