from PyQt5.QtCore import QDir

dris = QDir.drives()
print("-------", dris)
for dri in dris:
    print(dri.filePath())
    print(type(dri.filePath()))
print("------------------")
dirs = QDir("C:/").entryInfoList(filters=QDir.NoDotAndDotDot | QDir.AllEntries)
for d in dirs:
    print(d.fileName())


