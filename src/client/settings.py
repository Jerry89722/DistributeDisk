CLNT_NAME = "hp"
CLNT_ID = 1

SYS_TYPE = "windows"

HW_HOST = "www.huiwanit.cn"
HW_PORT = 9001
DATE_FORMAT = "yyyy/M/d h:m:s"
HW_DATA_TYPE_LOGIN = 0
HW_DATA_TYPE_HEARTBEAT = 1
HW_DATA_TYPE_ACK = 2
HW_DATA_TYPE_CMD = 3
HW_DATA_TYPE_BINARY = 4

HW_FILE_TYPE_NONE = 0
HW_FILE_TYPE_FILE = 1
HW_FILE_TYPE_DIR = 2
HW_FILE_TYPE_SYMLINK = 3

HW_LOGIN_OK = 0
HW_LOGIN_FAILED = 1
HW_LOGIN_OVERTIME = 2

LOGO_PATH = "./res/spider_net.png"

TYPE_FILE_PATH = "./res/type_files/type"

payload_login = {"uuid": None, "name": CLNT_NAME, "user": None, "pwd": None}
# [{"name": "hp", "cid":1}, {"name":"dell", "cid":2}]
# {"code": n}

payload_list = {"uuid": None, "cmd": "list", "path": None}
payload_list_reply = {"uuid": None, "list": []}
# tree list ["name1", "name2", "namex"]
# ls list [{"name":"name1", "size":1024, "type":HW_FILE_TYPE_FILE, "Modified": "2019-12-22 10:8:34"}]

# paste(cp/mv)
payload_paste = {
    "uuid": None,
    "sponsor_cid": None,
    "cmd": None,
    "from_cid": 0,
    "from_path": None,
    "from_list": [],
    "to_cid": 0,
    "to": None
}

payload_paste_reply = {
    "uuid": None,
    "sponsor_cid": 0,
    "cmd": None,
    "from_cid": 0,
    "from": None,
    "to_cid": 0,
    "to": None,
    "total_size": 0,
    "total": 0,     # file_count
    "offset": 0,    # file offset
    "size": 0       # file data size in this send
}

# rm attribution
payload_opt = {"uuid": None, "active": None, "src_path": None}
'''
protocol:
2 bytes: size
2 bytes: data_type
4 bytes: cid (toshiba)
n bytes: [binary_data] <cmd_json_string>
-----------------------*cp*-----------------------
request:
{
    "uuid":"2d2b708a-0081-11ea-a7b9-00a0c6000023",
    "sponsor_cid":1,
    "cmd":"cp",
    "from_path":"D:/Downloads/"
    "from_list":["a.rar", "b.rar", dir1], 
    "to":"$toshiba/home/zjay/"
}

reply to dest:
bin_data 
|start|offset|data_segment|
|  2  |   2  |   offset   |
{
    "uuid":"2d2b708a-0081-11ea-a7b9-00a0c6000023",
    "sponsor_cid":1,
    "cmd":"cp",
    "from":"$dell/D:/Downloads/a.rar",
    "to":"/home/zjay/a.rar",
    "total_size":19249632,
    "total":3,    # file_count
}

dest reply to sponsor
{
    "uuid":"2d2b708a-0081-11ea-a7b9-00a0c6000023",
    "sponsor_cid":1,
    "cmd":"cp",
    "from_path":"$hp/d/",
    "to_path":"/home/zjay/",
    "cur_file":"dir/file1.bin",
    "start":0,
    "offset":1024
}
'''
