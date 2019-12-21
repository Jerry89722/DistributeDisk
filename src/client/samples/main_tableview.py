import sys
from PyQt5.QtWidgets import QApplication, QFileSystemModel, QTreeView, QWidget, QVBoxLayout, QTableView
from PyQt5.QtGui import QIcon


class App(QWidget):

    def __init__(self):
        super().__init__()
        self.tabview = QTableView()
        self.model = QFileSystemModel()
        # self.model.setRootPath("F:/")
        # self.model.setReadOnly(True)
        self.title = 'PyQt5 file system view - pythonspot.com'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.model.setRootPath('')
        self.tabview.setModel(self.model)
        self.tabview.setRootIndex(self.model.index("F:\Downloads\迅雷下载"))
        # self.lv.setAnimated(False)
        # self.lv.setIndentation(20)
        # self.lv.setSortingEnabled(True)
        self.tabview.setWindowTitle("Dir View")
        self.tabview.resize(640, 480)
        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.tabview)
        self.setLayout(windowLayout)
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
