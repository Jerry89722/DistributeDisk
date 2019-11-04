import struct
import sys
import socket
import time
from settings import *

import threading


class ClntSocket:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.t_sock = threading.Thread(target=self.start())
        self.t_recv = None
        self.t_send = None
        self.tx_queue = list()
        self.rx_queue = list()

    def start(self):
        try:
            ip = socket.gethostbyname(HW_HOST)
        except socket.gaierror:
            print("host name could not be resolved")
            sys.exit()

        self.sock.connect((ip, HW_PORT))

        self.t_recv = threading.Thread(target=self.recv_work)
        self.t_send = threading.Thread(target=self.send_work)

    def recv_work(self):
        while True:
            recv_buf = self.sock.recv(4096)
            content = struct.unpack('HHI{}s'.format(len(recv_buf) - 8), recv_buf)
            print("recved content: ", content)

    def send_work(self):
        while True:
            time.sleep(2)
            if len(self.tx_queue) > 0:
                self.sock.send(self.tx_queue.pop(0))

    def pack(self, cmd):
        if cmd == HW_DATA_TYPE_LOGIN:
            bin_data = struct.pack('HHI{}s'.format(len(CLNT_NAME)), len(CLNT_NAME), cmd, CLNT_ID,
                                   CLNT_NAME.encode("ascii"))
            self.tx_queue.append(bin_data)

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

