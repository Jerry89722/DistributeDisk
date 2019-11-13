CLNT_NAME = "dell"
CLNT_ID = 2

SYS_TYPE = "windows"

HW_HOST = "www.huiwanit.cn"
HW_PORT = 9001

HW_DATA_TYPE_LOGIN = 0
HW_DATA_TYPE_HEARTBEAT = 1
HW_DATA_TYPE_ACK = 2
HW_DATA_TYPE_CMD = 3
HW_DATA_TYPE_BINARY = 4

HW_FILE_TYPE_NONE = 0
HW_FILE_TYPE_FILE = 1
HW_FILE_TYPE_DIR = 2
HW_FILE_TYPE_SYMLINK = 3

payload_login = {"uuid": None, "name": CLNT_NAME}
# [{"name": "hp", "cid":1}, {"name":"dell", "cid":2}]

payload_tree = {"uuid": None, "cmd": "tree", "path": None}
payload_list_reply = {"uuid": None, "list": []}
# tree list ["name1", "name2", "namex"]
# ls list [{"name":"name1", "type":HW_FILE_TYPE_FILE}]

payload_list = {"uuid": None, "cmd": "list", "path": None}

'''
protocol:
2 bytes: size
2 bytes: data_type
4 bytes: cid
n bytes: cmd_json_string or binary_data
-----------------------*cp*-----------------------
request:
{
    "uuid":"2d2b708a-0081-11ea-a7b9-00a0c6000023",
    "cmd":"cp",
    "from_path":"$hp/d/",
    "to_path":"/home/zjay/"
}

reply:
{
    "uuid":"2d2b708a-0081-11ea-a7b9-00a0c6000023",
    "cmd":"cp",
    "from_path":"$hp/d/",
    "to_path":"/home/zjay/",
    "cur_file":"dir/file1.bin",
    "start":0,
    "offset":1024
}
bin_data
'''
