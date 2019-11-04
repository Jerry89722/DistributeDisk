from PyQt5.QtCore import QModelIndex
from PyQt5.QtWidgets import QFileSystemModel, QTreeView


class LocalTree:
    def __init__(self, tv: QTreeView):
        self.tv = tv
        local_model = QFileSystemModel()
        # self.ui.localFileTv.header().hide()
        local_model.setRootPath('/')
        self.tv.setModel(local_model)

