from PyQt5.QtCore import QModelIndex, QDir
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QFileSystemModel, QTreeView
from file_view import FileView


class LocalTree:
    def __init__(self, tv: QTreeView, fv: FileView):
        self.tv = tv
        self.fv = fv
        self.local_model = QFileSystemModel()
        # self.ui.localFileTv.header().hide()
        # self.local_model.setFilter(self.local_model.filter() & (~QDir.Files))
        self.local_model.setRootPath('/')
        self.tv.setModel(self.local_model)
        self.tv.clicked.connect(self.item_click)

    def item_click(self, index):
        print("local item clicked")
        self.fv.switch_to_local(self.local_model, index)




