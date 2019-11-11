CLNT_NAME = "dell"
CLNT_ID = 2
HW_HOST = "www.huiwanit.cn"
HW_PORT = 9001

HW_DATA_TYPE_LOGIN = 0
HW_DATA_TYPE_HEARTBEAT = 1
HW_DATA_TYPE_ACK = 2
HW_DATA_TYPE_CMD = 3
HW_DATA_TYPE_BINARY = 3

SYS_TYPE = "windows"

payload_login = {"uuid": None, "name": CLNT_NAME}
# [{"name": "hp", "cid":1}, {"name":"dell", "cid":2}]

payload_tree = {"uuid": None, "cmd": "tree", "path": None}
payload_tree_reply = {"uuid": None, "list": []}

payload_ls = {"uuid": None, "cmd": "ls", "path": None}

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
