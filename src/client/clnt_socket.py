import copy
import os
import struct
import sys
import socket
import json
import uuid
import threading

from PyQt5.QtCore import QObject, pyqtSignal, QDir, QFile, QFileInfo, QIODevice
from settings import *

HW_SOCK_HEADER_LEN = 8


def print_hex(bt_data):
    li_hex = ['{:02x}'.format(i) for i in bt_data]
    print("".join(li_hex))


class ClntSocket(QObject):
    login_signal = pyqtSignal(object)
    mw_signal = pyqtSignal(object)

    def __init__(self):
        super(ClntSocket, self).__init__()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.t_sock = threading.Thread(target=self.start)
        self.t_sock.start()
        self.t_recv = None
        self.t_work = None
        self.t_send = None
        self.tx_event = threading.Event()
        self.work_event = threading.Event()
        self.tx_queue = list()
        self.sent_queue = list()
        self.rx_queue = list()
        self.task_queue = list()

    def __del__(self):
        print("delete itself")

    def ui_event_trigger(self, which, ui_data):
        if which is "mw":
            self.mw_signal.emit(ui_data)
        elif which is "login":
            self.login_signal.emit(ui_data)

    def start(self):
        try:
            ip = socket.gethostbyname(HW_HOST)
        except socket.gaierror:
            print("host name could not be resolved")
            sys.exit()
        try:
            self.sock.connect((ip, HW_PORT))
        except:
            print("connect failed")
            return

        print("start recv and send thread")
        self.t_recv = threading.Thread(target=self.recv_work)
        self.t_work = threading.Thread(target=self.do_work)
        self.t_send = threading.Thread(target=self.send_work, args=(self.tx_event,))
        self.t_recv.start()
        self.t_send.start()
        self.t_work.start()

    def recv_work(self):
        print("recv work thread start")
        while True:
            print("recv waiting ...")
            header = b''
            header_len = 0
            while header_len < HW_SOCK_HEADER_LEN:
                header += self.sock.recv(HW_SOCK_HEADER_LEN - header_len)
                header_len += len(header)
            # print("recv header, raw data:")
            # print_hex(header)
            header_tuple = struct.unpack('HHI', header)

            size = header_tuple[0]
            data_type = header_tuple[1]
            cid = header_tuple[2]
            print("recv: payload size[%d], payload type[%d], from clint[%d]" % (size, data_type, cid))

            total_size = 0
            payload = b''
            while total_size < size:
                payload += self.sock.recv(size - total_size)
                total_size = len(payload)
                # print("payload total_size: %d, size: %d" % (total_size, size))

            # print("recv body, raw data:")
            # print_hex(payload)
            print("binary data len: ", len(payload))
            # if data_type == HW_DATA_TYPE_BINARY:
            #     print("recv binary data:")
            #     print_hex(payload)
            self.push_back_rx_queue(size, data_type, cid, payload)

    def send_work(self, event):
        print("send work thread start")
        while True:
            event.wait()
            print("tx queue len: ", len(self.tx_queue))
            if len(self.tx_queue) > 0:
                node = self.tx_queue.pop(0)
                # print("send, raw data: ")
                # print_hex(node)
                print("send len: ", self.sock.send(node))
            else:
                event.clear()

    def push_back_tx_queue(self, cmd, data, size, cid=CLNT_ID):
        bin_data = struct.pack('HHI{}s'.format(size), size, cmd, cid, data)
        self.tx_queue.append(bin_data)
        self.tx_event.set()

    def push_back_rx_queue(self, size, data_type, cid, body):
        self.rx_queue.append([size, data_type, cid, body])
        self.work_event.set()

    def hw_cmd_login(self, user, pwd):
        payload = copy.deepcopy(payload_login)
        payload["uuid"] = uuid.uuid1().__str__()
        payload["user"] = user
        payload["pwd"] = pwd
        payload = json.dumps(payload)
        print("send cmd login: size: %d, data_type: %d, cid: %d, payload: %s" % (
            len(payload), HW_DATA_TYPE_LOGIN, CLNT_ID, payload))
        self.push_back_tx_queue(HW_DATA_TYPE_LOGIN, payload.encode("utf-8"), len(payload))

    def hw_cmd_list(self, cmd, cid, path):
        payload = copy.deepcopy(payload_list)
        payload["uuid"] = uuid.uuid1().__str__()
        payload["cmd"] = cmd
        payload["path"] = path
        self.sent_queue.append(payload)
        payload = json.dumps(payload)
        print("send cmd list request: size: %d, data_type: %d, cid: %d, payload: %s" % (
            len(payload), HW_DATA_TYPE_CMD, cid, payload))
        self.push_back_tx_queue(HW_DATA_TYPE_CMD, payload.encode("utf-8"), len(payload), cid)

    def hw_cmd_cp_mv(self, cid=0, cmd_str=None, from_cid=0, from_path=None, from_list=None, to_path=None):
        if cid == CLNT_ID and from_cid == cid:
            print("local task !!!")
            return
        payload = copy.deepcopy(payload_paste)
        payload["uuid"] = uuid.uuid1().__str__()
        payload["sponsor_cid"] = CLNT_ID
        payload["cmd"] = cmd_str
        payload["from_cid"] = from_cid
        payload["from_path"] = from_path
        payload["from_list"] = from_list
        payload["to_cid"] = cid
        payload["to"] = to_path
        self.sent_queue.append(payload)
        payload = json.dumps(payload)
        print("send cmd list request: size: %d, data_type: %d, cid: %d, payload: %s" % (
            len(payload), HW_DATA_TYPE_CMD, cid, payload))
        self.push_back_tx_queue(HW_DATA_TYPE_CMD, payload.encode("utf-8"), len(payload), from_cid)

    def hw_cmd_binary_reply(self, reply, bin_data):
        print("bin reply description: ", reply)
        payload = json.dumps(reply)
        json_len = len(payload)
        payload = payload.encode("utf-8")
        # payload_data = None
        bin_len = 0
        if bin_data is not None:
            bin_len = len(bin_data)
            print("bin data len: ", len(bin_data))
            # |size|type|cid|payload
            #                binary_len|binary|binary_description_json_str
            payload_data = struct.pack('H{}s{}s'.format(bin_len, json_len), bin_len, bin_data, payload)
        else:
            payload_data = struct.pack('H{}s'.format(json_len), 0, payload)

        self.push_back_tx_queue(HW_DATA_TYPE_BINARY, payload_data, bin_len + json_len + 2, reply["to_cid"])

    def do_work(self):
        # size | data_type | cid | payload
        #   0  |     1     |  2  |    3
        while True:
            if len(self.rx_queue) == 0:
                self.work_event.wait()
                self.work_event.clear()
            print("len rx queue: ", len(self.rx_queue))
            if len(self.rx_queue) <= 0:
                continue
            data = self.rx_queue.pop(0)
            size = data[0]
            data_type = data[1]
            cid = data[2]
            payload = data[3]
            if data_type == HW_DATA_TYPE_LOGIN:
                payload_tuple = struct.unpack('{}s'.format(size), payload)
                body_js = payload_tuple[0].decode()
                payload_dict = json.loads(body_js)
                recved_data = [data_type, cid, payload_dict]

                self.ui_event_trigger("login", recved_data)
            elif data_type == HW_DATA_TYPE_CMD:
                payload_js_str = struct.unpack('{}s'.format(size), payload)[0].decode()
                payload_dict = json.loads(payload_js_str)
                cmd = payload_dict.get("cmd")
                if cmd is None:
                    print("received data is command's reply data, uuid: ", payload_dict["uuid"])
                    for request in self.sent_queue:
                        if payload_dict["uuid"] == request["uuid"]:
                            recved_data = [data_type, cid, request["cmd"], request["path"], payload_dict["list"]]
                            self.ui_event_trigger("mw", recved_data)
                            break
                elif cmd == "tree" or cmd == "ls":
                    payload_reply = copy.deepcopy(payload_list_reply)
                    payload_reply["uuid"] = payload_dict["uuid"]
                    payload_reply["list"] = self.file_list_get(cmd, payload_dict["path"])
                    reply_js = json.dumps(payload_reply)
                    print("send cmd reply: size: %d, data_type: %d, cid: %d, payload: %s" % (
                        len(reply_js), HW_DATA_TYPE_CMD, CLNT_ID, reply_js))
                    self.push_back_tx_queue(HW_DATA_TYPE_CMD, reply_js.encode("utf-8"), len(reply_js), cid)
                elif cmd == "cp" or cmd == "mv":
                    print("get cmd[%s], and going to reply " % cmd)

                    t_file_opt = threading.Thread(target=self.file_opt_work, args=(cid, payload_dict))
                    t_file_opt.start()
                else:
                    print("unknow cmd: ", cmd)
            elif data_type == HW_DATA_TYPE_BINARY:
                print("binary data")
                # data[3]
                bin_len = int.from_bytes(data[3][0:2], byteorder='little', signed=False)
                bin_data = None
                print("binary data len :", bin_len)
                if bin_len > 0:
                    ret = struct.unpack('{}s{}s'.format(bin_len, len(data[3]) - 2 - bin_len), data[3][2:])
                    bin_data = ret[0]
                    print(ret[1])
                    print(ret[1].decode())
                    info = json.loads(ret[1].decode())
                else:
                    ret = struct.unpack('{}s'.format(len(data[3]) - 2), data[3][2:])
                    info = json.loads(ret[0].decode())
                print("binary description info: ", info)
                print("from: ", info["from"])
                print("to: ", info["to"])
                bn = self.get_basename(info["from"])
                print("basename: ", bn)
                full_path = info["to"] + bn
                print("full path: ", full_path)

                if bin_len == 0:    # is dir
                    self.mkdir(full_path)
                else:   # is regular file
                    finfo = None
                    task_info = None  # operating files info
                    for task_info in self.task_queue:
                        if task_info["uuid"] == info["uuid"]:
                            break
                    # {uuid, finfo[]}
                    # finfo {fp, dest_path}
                    if task_info is None:    # new file operation task
                        task_info = dict()
                        print("start a new task, uuid: ", info["uuid"])
                        task_info["uuid"] = info["uuid"]
                        task_info["finfo"] = list()
                        finfo = dict()
                        finfo["dest_path"] = full_path
                        finfo["fp"] = open(full_path, "wb")
                        if finfo["fp"] is not None:  # file open failed
                            print("new task open file ok")
                            finfo["fp"].truncate(info["file_size"])
                            task_info["finfo"].append(finfo)
                            self.task_queue.append(task_info)
                        else:
                            print("new task open file error")
                            finfo = None
                    else:   # existed file operation task
                        for finfo in task_info["finfo"]:
                            if finfo["dest_path"] == full_path:
                                break
                        if finfo is None:
                            finfo = dict()
                            finfo["fp"] = open(full_path, "wb")
                            finfo["fp"].truncate(info["file_size"])
                            if finfo["fp"] is not None:  # file open failed
                                task_info["finfo"].append(finfo)

                    finfo["fp"].write(bin_data)
                    print("offset: %d, size: %d, file_size: %d" % (info["offset"], info["size"], info["file_size"]))
                    if info["offset"] + info["size"] >= info["file_size"]:
                        finfo["fp"].close()
                        task_info["finfo"].remove(finfo)
                        if info["current"] == info["total"]:
                            self.task_queue.remove(task_info)

                '''
                {
                    "uuid": "6a3625a8-143c-11ea-8e47-2016d8d3481a", 
                    "sponsor_cid": 3, 
                    "cmd": "cp", 
                    "from_cid": 2, 
                    "from": "D:/workspace/frp_0.29.0_windows_amd64/frps_full.ini", 
                    "to_cid": 1, 
                    "to": "F:/", 
                    "total_size": 48658, 
                    "total": 2, 
                    "current": 1,
                    "file_size": 2365,
                    "offset": 0, 
                    "size": 2635
                }
                '''

        print("work done")

    @staticmethod
    def get_basename(path):
        bn = path.split("/")[-1]
        if len(bn) > 0:
            return bn
        bn = path.split("/")[-2]
        return bn

    def file_traverse_opt(self, path, reply):
        print("traverse operate path: ", path)
        for root, dirs, files in os.walk(path):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name).decode('gbk').encode('utf-8')
                if not os.listdir(dir_path):
                    dir_path += '/'
                    print("path is empty: ", dir_path)
                    self.file_data_reply(dir_path, reply)
            for file_name in files:
                file_path = os.path.join(root, file_name).decode('gbk').encode('utf-8')
                self.file_data_reply(file_path, reply)

    @staticmethod
    def file_count(path):
        print("file traverse path: ", path)
        cnt = 0
        total_size = 0
        for root, dirs, files in os.walk(path):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name).decode('gbk').encode('utf-8')
                if not os.listdir(dir_path):
                    cnt += 1
            for file_name in files:
                file_path = os.path.join(root, file_name).decode('gbk').encode('utf-8')
                total_size += os.path.getsize(file_path)
                cnt += 1
        print("file count: ", cnt)
        return cnt, total_size

    def file_opt_work(self, cid, cmd_info):
        print("sponsor[", cid, "]", cmd_info)
        reply = copy.deepcopy(payload_paste_reply)
        reply["uuid"] = cmd_info["uuid"]
        reply["sponsor_cid"] = cmd_info["sponsor_cid"]
        reply["cmd"] = cmd_info["cmd"]
        reply["from_cid"] = cmd_info["from_cid"]
        reply["to_cid"] = cmd_info["to_cid"]
        reply["to"] = cmd_info["to"]
        reply["current"] = 0
        # reply["total"] = len(cmd_info["from_list"])
        for f in cmd_info["from_list"]:
            full_path = cmd_info["from_path"] + f
            print("count full path: ", full_path)
            if os.path.isdir(full_path):
                print("is dir")
                total, total_size = self.file_count(full_path)
                reply["total"] += total
                reply["total_size"] += total_size
            else:
                print("is regular file")
                reply["total"] += 1
                reply["total_size"] += os.path.getsize(full_path)
        if reply["from_cid"] == reply["to_cid"]:
            print("local task, sponsor is: ", cid)
            return

        for f in cmd_info["from_list"]:
            full_path = cmd_info["from_path"] + f
            print("operate full path: ", full_path)
            if os.path.isdir(full_path):
                print("operate is dir")
                self.file_traverse_opt(full_path, reply)
            else:
                print("operate is regular file")
                self.file_data_reply(full_path, reply)

    def file_data_reply(self, path, reply):
        reply["from"] = path
        qf = QFile(path)
        ret = qf.open(QIODevice.ReadOnly)
        reply["file_size"] = qf.size()
        reply["current"] += 1
        offset = 0
        while ret:
            bin_data = qf.readData(4096)
            data_len = len(bin_data)
            reply["size"] = data_len
            reply["offset"] = offset
            self.hw_cmd_binary_reply(reply, bin_data)
            offset += data_len
            if data_len < 4096:
                return
        self.hw_cmd_binary_reply(reply, None)

    @staticmethod
    def file_list_get(cmd, path):
        file_list = list()
        abs_path = path
        if SYS_TYPE != "windows" and abs_path != "/":
            abs_path = "/" + abs_path
        print("absolute path: ", abs_path)
        if cmd == "tree":
            if abs_path == "/" and SYS_TYPE is "windows":
                dirs = QDir.drives()
                for d in dirs:
                    file_list.append(d.filePath().strip('/'))
            else:
                dirs = QDir(abs_path).entryInfoList(filters=QDir.Dirs | QDir.NoDotAndDotDot)
                for d in dirs:
                    print("dir name: ", d.fileName())
                    file_list.append(d.fileName())
        elif cmd == "ls":
            print(abs_path)
            if abs_path == "/" and SYS_TYPE is "windows":
                dirs = QDir.drives()
                for d in dirs:
                    file_list.append({"name": d.filePath().strip('/'), "type": QDir.Dirs, "size": 0})
            else:
                dirs = QDir(abs_path).entryInfoList(filters=QDir.AllEntries | QDir.NoDotAndDotDot)
                for d in dirs:
                    file_type = HW_FILE_TYPE_NONE
                    size = 0
                    if d.isDir():
                        file_type = HW_FILE_TYPE_DIR
                    elif d.isFile():
                        file_type = HW_FILE_TYPE_FILE
                        size = d.size()
                    elif d.isSymLink():
                        file_type = HW_FILE_TYPE_SYMLINK
                    file_list.append({"name": d.fileName(), "type": file_type, "size": size})
                    print(file_list)
        return file_list

    @staticmethod
    def mkdir(path):
        folder = os.path.exists(path)
        if not folder:
            os.makedirs(path)  # makedirs create the fold include the full path
            print("---  new folder...  ---")
            print("---  OK  ---")
        else:
            print("---  There is this folder!  ---")

