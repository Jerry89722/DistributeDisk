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
        self.t_send = None
        self.tx_event = threading.Event()
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
        self.t_send = threading.Thread(target=self.send_work, args=(self.tx_event,))
        self.t_recv.start()
        self.t_send.start()
        self.push_cmd_tx_queue(HW_DATA_TYPE_LOGIN)

    def recv_work(self):
        print("recv work thread start")
        while True:
            header = self.sock.recv(HW_SOCK_HEADER_LEN)

            header_tuple = struct.unpack('HHI', header)
            print("recved content: ", header_tuple)

            size = header_tuple[0]
            data_type = header_tuple[1]
            cid = header_tuple[2]

            body = self.sock.recv(size)
            body_tuple = struct.unpack('{}s'.format(size), body)
            body_js = body_tuple[0].decode()

            clnt_objs = json.loads(body_js)
            for clnt in clnt_objs:
                print("clnt details: ", clnt)

            if data_type == HW_DATA_TYPE_LOGIN:
                recved_data = [data_type, cid, clnt_objs]
                # self.rx_queue.append(recved_data)
                self.ui_event_trigger(recved_data)

    def send_work(self, event):
        print("send work thread start")
        while True:
            event.wait()
            print("tx queue len: ", len(self.tx_queue))
            if len(self.tx_queue) > 0:
                node = self.tx_queue.pop(0)
                self.sent_queue.append(node)
                self.sock.send(node)
            else:
                event.clear()

    def push_cmd_tx_queue(self, cmd):
        if cmd == HW_DATA_TYPE_LOGIN:
            cmd_uuid = uuid.uuid1().__str__()
            clnt_info = {"uuid": cmd_uuid, "name": CLNT_NAME}
            clnt_info_string = json.dumps(clnt_info)
            bin_data = struct.pack('HHI{}s'.format(len(clnt_info_string)), len(clnt_info_string), cmd, CLNT_ID,
                                   clnt_info_string.encode("ascii"))
            print("push login info to tx queue")
            self.tx_queue.append(bin_data)

        print("trigger tx event")
        self.tx_event.set()

    '''
    payload_content = "ls $/"
    payload_size = len(payload_content)
    payload_type = 3
    cid = 2
    data = struct.pack('HHI{}s'.format(payload_size), payload_size, payload_type, cid, payload_content.encode("ascii"))

    slen = s.send(data)
    print("send cmd payload, len: ", slen)

    data = s.recv(4096)

    res = struct.unpack('HHI{}s'.format(len(data) - 8), data)

    '''


'''
protocol:
2 bytes: size
2 bytes: data_type
4 bytes: cid
n bytes: cmd_json_string or binary_data
-----------------------*login*-----------------------
request:
{
    "uuid":"2d2b708a-0081-11ea-a7b9-00a0c6000023"
    "name":"dell"
}

reply:
[
    {"name":"hp","cid":1}, 
    {"name":"toshiba","cid":3}
]

-----------------------*ls*-----------------------
request:
{
    "uuid":"2d2b708a-0081-11ea-a7b9-00a0c6000023",
    "cmd":"ls",
    "path":"$hp/d/"
}
reply:
{
    "uuid":"2d2b708a-0081-11ea-a7b9-00a0c6000023",
    "cmd":"ls",
    "list":[{"name":"Programs","type":0}, {"name":"cz-lora-daemon.tar","type":1}]
}

'''
