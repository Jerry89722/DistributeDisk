import sys
from PyQt5.QtWidgets import QApplication
from login_dialog import LoginDialog

if __name__ == "__main__":
    app = QApplication([])
    login_dialog = LoginDialog()
    login_dialog.show()
    sys.exit(app.exec_())
