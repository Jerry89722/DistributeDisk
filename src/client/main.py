import sys

from PyQt5.QtWidgets import QApplication, QMainWindow
from client_ui import Ui_MainWindow
from local_tree import LocalTree
from remote_tree import RemoteTree
from clnt_socket import ClntSocket
from file_view import FileView


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.clnt_socket = ClntSocket()
        self.local_tree = LocalTree(self.ui.localFileTv)
        self.remote_tree = RemoteTree(self.ui.remoteFileTv, self.clnt_socket)
        self.file_tv = FileView(self.ui.fileTabView)
        self.clnt_socket.send_tv_msg.connect(self.remote_tree.ui_event_handle)
        self.clnt_socket.send_lv_msg.connect(self.file_tv.ui_event_handle)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())



