import struct
import sys
import socket
import json
import time
import uuid

from PyQt5.QtCore import QObject, pyqtSignal

from settings import *

import threading

HW_SOCK_HEADER_LEN = 8


class ClntSocket(QObject):
    send_msg = pyqtSignal(object)

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

    def ui_event_trigger(self, ui_data):
        self.send_msg.emit(ui_data)

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
        cmd_uuid = uuid.uuid1().__str__()
        payload = {"uuid": cmd_uuid, "name": CLNT_NAME}
        payload = json.dumps(payload)
        payload_len = len(payload)
        payload = payload.encode("ascii")
        self.push_back_tx_queue(HW_DATA_TYPE_LOGIN, payload, payload_len)

    def recv_work(self):
        print("recv work thread start")
        while True:
            print("recv waiting ...")
            header = self.sock.recv(HW_SOCK_HEADER_LEN)
            print("recved header: ", header)
            header_tuple = struct.unpack('HHI', header)
            print("recved content: ", header_tuple)

            size = header_tuple[0]
            data_type = header_tuple[1]
            cid = header_tuple[2]
            body = self.sock.recv(size)
            self.push_back_rx_queue(size, data_type, cid, body)

    def send_work(self, event):
        print("send work thread start")
        while True:
            event.wait()
            print("tx queue len: ", len(self.tx_queue))
            if len(self.tx_queue) > 0:
                node = self.tx_queue.pop(0)
                self.sent_queue.append(node)
                s_len = self.sock.send(node)
                print("send len: ", s_len)
            else:
                event.clear()

    def push_back_tx_queue(self, cmd, data, size, cid=CLNT_ID):
        # print("size: %d, cmd: %d, cid: %d, data: %s" % (size, cmd, cid, data.decode()))
        bin_data = struct.pack('HHI{}s'.format(size), size, cmd, cid, data)
        self.tx_queue.append(bin_data)
        self.tx_event.set()
        print("push back data into tx queue")

    def push_back_rx_queue(self, size, data_type, cid, body):
        self.rx_queue.append([size, data_type, cid, body])
        self.work_event.set()
        print("push back recved data into rx queue")

    def hw_cmd_tree(self, cid, path):
        cmd_uuid = uuid.uuid1().__str__()
        payload = {"uuid": cmd_uuid, "cmd": "tree", "path": path}
        payload = json.dumps(payload)
        payload_len = len(payload)
        payload = payload.encode("ascii")
        self.push_back_tx_queue(HW_DATA_TYPE_CMD, payload, payload_len, cid)

    def do_work(self):
        # size | data_type | cid | payload
        #   0  |     1     |  2  |    3
        while True:
            if len(self.rx_queue) == 0:
                self.work_event.wait()
                self.work_event.clear()
            data = self.rx_queue.pop(0)
            size = data[0]
            data_type = data[1]
            cid = data[2]
            payload = data[3]
            if data_type == HW_DATA_TYPE_LOGIN:
                body_tuple = struct.unpack('{}s'.format(size), payload)
                body_js = body_tuple[0].decode()
                clnt_objs = json.loads(body_js)
                recved_data = [data_type, cid, clnt_objs]
                self.ui_event_trigger(recved_data)

            elif data_type == HW_DATA_TYPE_CMD:
                '''
                {
                    "uuid": "2d2b708a-0081-11ea-a7b9-00a0c6000023",
                    "cmd": "tree",
                    "cid": 1,  # from client
                    "path":"/",
                    "list": ["Programs", "cz-lora-daemon"]
                }
                '''
                # parse
                print("tree payload: ", payload)
            elif data_type == HW_DATA_TYPE_BINARY:
                '''
                {
                    
                    "uuid": "2d2b708a-0081-11ea-a7b9-00a0c6000023",
                    "path":"/home/zjay/file.bin",
                    "total":908647,
                    "start":13456,
                    "end":23456
                }
                '''
                print("")


'''
protocol:
2 bytes: size
2 bytes: data_type
4 bytes: cid
n bytes: cmd_json_string or binary_data
-----------------------*login*-----------------------
request:
{
    "uuid":"2d2b708a-0081-11ea-a7b9-00a0c6000023",
    "name":"dell"
}

reply:
[
    {"name":"hp","cid":1}, 
    {"name":"toshiba","cid":3}
]

-----------------------*tree*-----------------------
request:
{
    "uuid":"2d2b708a-0081-11ea-a7b9-00a0c6000023",
    "cmd":"tree",
    "path":"$hp/d/",
}
reply:
{
    "uuid":"2d2b708a-0081-11ea-a7b9-00a0c6000023",
    "path":"$hp/d/",
    "list":[{"name":"Programs","type":0}, {"name":"cz-lora-daemon.tar","type":1}],
}

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
