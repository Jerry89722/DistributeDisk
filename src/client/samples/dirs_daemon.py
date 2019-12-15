import time

from PyQt5.QtCore import QDir, QFile
import threading

dris = QDir.drives()
print("-------", dris)
for dri in dris:
    print(dri.filePath())
    print(type(dri.filePath()))
print("------------------")
dirs = QDir("C:/").entryInfoList(filters=QDir.NoDotAndDotDot | QDir.AllEntries)
for d in dirs:
    print(d.fileName())


def test():
    time.sleep(1)
    t_qf = QFile("D:/visio.iso")
    while True:
        time.sleep(1)
        print("file size: ", t_qf.size())


t_test = threading.Thread(target=test)
t_test.start()

qf = QFile("D:/BaiduNetdiskDownload/SW_DVD5_Visio_Pro_2013_64Bit_ChnSimp_MLF_X18-61013.ISO")
qf.copy("D:/visio.iso")


