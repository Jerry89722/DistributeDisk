import copy
import struct
import sys
import socket
import json
import time
import uuid
import threading

from PyQt5.QtCore import QObject, pyqtSignal, QDir
from settings import *

HW_SOCK_HEADER_LEN = 8


class ClntSocket(QObject):
    send_tv_msg = pyqtSignal(object)
    send_lv_msg = pyqtSignal(object)

    def __init__(self):
        super(ClntSocket, self).__init__()
        # self.setParent(parent)
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

    def __del__(self):
        print("delete itself")

    def ui_event_trigger(self, who, ui_data):
        if who is "tv":
            self.send_tv_msg.emit(ui_data)
        else:
            self.send_lv_msg.emit(ui_data)

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
            # self.ui_event_trigger()
            return

        print("start recv and send thread")
        self.t_recv = threading.Thread(target=self.recv_work)
        self.t_work = threading.Thread(target=self.do_work)
        self.t_send = threading.Thread(target=self.send_work, args=(self.tx_event,))
        self.t_recv.start()
        self.t_send.start()
        self.t_work.start()
        payload = copy.deepcopy(payload_login)
        payload["uuid"] = uuid.uuid1().__str__()
        payload = json.dumps(payload)
        print("send cmd login: size: %d, data_type: %d, cid: %d, payload: %s" % (len(payload), HW_DATA_TYPE_LOGIN, CLNT_ID, payload))
        self.push_back_tx_queue(HW_DATA_TYPE_LOGIN, payload.encode("ascii"), len(payload))

    def recv_work(self):
        print("recv work thread start")
        while True:
            print("recv waiting ...")
            header = self.sock.recv(HW_SOCK_HEADER_LEN)
            header_tuple = struct.unpack('HHI', header)

            size = header_tuple[0]
            data_type = header_tuple[1]
            cid = header_tuple[2]
            total_size = 0
            payload = b''
            while total_size < size:
                payload += self.sock.recv(size - total_size)
                total_size = len(payload)
                print("total_size: %d, size: %d" % (total_size, size))

            print("recv: payload size[%d], payload type[%d], from clint[%d]" % (size, data_type, cid))
            # if data_type != HW_DATA_TYPE_BINARY:
            print("recved payload: %s" % struct.unpack('{}s'.format(size), payload)[0].decode())
            self.push_back_rx_queue(size, data_type, cid, payload)

    def send_work(self, event):
        print("send work thread start")
        while True:
            event.wait()
            print("tx queue len: ", len(self.tx_queue))
            if len(self.tx_queue) > 0:
                node = self.tx_queue.pop(0)
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

    def hw_cmd_list(self, cmd, cid, path):
        payload = copy.deepcopy(payload_list)
        payload["uuid"] = uuid.uuid1().__str__()
        payload["cmd"] = cmd
        payload["path"] = path
        self.sent_queue.append(payload)
        payload = json.dumps(payload)
        print("send cmd list request: size: %d, data_type: %d, cid: %d, payload: %s" % (
            len(payload), HW_DATA_TYPE_CMD, cid, payload))
        self.push_back_tx_queue(HW_DATA_TYPE_CMD, payload.encode("ascii"), len(payload), cid)

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
                self.ui_event_trigger("tv", recved_data)
            elif data_type == HW_DATA_TYPE_CMD:
                payload_js_str = struct.unpack('{}s'.format(size), payload)[0].decode()
                payload_dict = json.loads(payload_js_str)
                cmd = payload_dict.get("cmd")
                if cmd is None:
                    print("cmd reply handle, uuid: ", payload_dict["uuid"])
                    for request in self.sent_queue:
                        if payload_dict["uuid"] == request["uuid"]:
                            recved_data = [data_type, cid, request["cmd"], request["path"], payload_dict["list"]]
                            if request["cmd"] == "tree":
                                self.ui_event_trigger("tv", recved_data)
                            else:
                                self.ui_event_trigger("lv", recved_data)
                            break
                elif cmd == "tree" or cmd == "ls":
                    payload_reply = copy.deepcopy(payload_list_reply)
                    payload_reply["uuid"] = payload_dict["uuid"]
                    payload_reply["list"] = self.file_list_get(cmd, payload_dict["path"])
                    reply_js = json.dumps(payload_reply)
                    print("send cmd reply: size: %d, data_type: %d, cid: %d, payload: %s" % (
                        len(reply_js), HW_DATA_TYPE_CMD, CLNT_ID, reply_js))
                    self.push_back_tx_queue(HW_DATA_TYPE_CMD, reply_js.encode("ascii"), len(reply_js), cid)
                else:
                    print("unknow cmd: ", cmd)
            elif data_type == HW_DATA_TYPE_BINARY:
                '''
                {
                    "uuid": "2d2b708a-0081-11ea-a7b9-00a0c6000023",
                    "total":908647,
                    "start":13456,
                    "end":23456
                }
                '''
                print("")

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
