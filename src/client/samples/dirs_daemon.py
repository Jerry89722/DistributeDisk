from PyQt5.QtCore import QDir

dris = QDir.drives()
print("-------", dris)
for dri in dris:
    print(dri.filePath())
    print(type(dri.filePath()))
print("------------------")
dir_path = QDir("C:/")
dirs = dir_path.entryInfoList(filters=QDir.Dirs)
for d in dirs:
    print(d.fileName())


