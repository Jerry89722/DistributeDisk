import struct
import sys
import socket
import time
from settings import *

import threading


class ClntSocket:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.t_sock = threading.Thread(target=self.run)
        self.t_recv = None
        self.t_send = None
        self.tx_queue = list()
        self.rx_queue = list()

    def run(self):
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
            buf = self.sock.recv(4096)

    def send_work(self):
        while True:
            self.sock.send(data)

# str_a = "aaaaa"
# data = struct.pack('HHI5s', 5, 2, 32, bytes(str_a.encode()))
#
# dest = struct.unpack('HHI{}s'.format(len(data) - 8), data)
#
# print(dest)

if __name__ == "__main__":

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        remote_ip = socket.gethostbyname(HW_HOST)
    except socket.gaierror:
        print("host name could not be resolved")
        sys.exit()

    s.connect((remote_ip, HW_PORT))
    payload_content = "hp"
    payload_size = len(payload_content)
    payload_type = 0  # HW_DATA_TYPE_LOGIN
    cid = 1
    data = struct.pack('HHI{}s'.format(payload_size), payload_size, payload_type, cid, payload_content.encode("ascii"))

    slen = s.send(data)
    print("send len: ", slen)

    input("pause: ")

    payload_content = "ls $/"
    payload_size = len(payload_content)
    payload_type = 3
    cid = 2
    data = struct.pack('HHI{}s'.format(payload_size), payload_size, payload_type, cid, payload_content.encode("ascii"))

    slen = s.send(data)
    print("send cmd payload, len: ", slen)

    data = s.recv(4096)

    res = struct.unpack('HHI{}s'.format(len(data) - 8), data)

    print(res)

    input("done: ")

